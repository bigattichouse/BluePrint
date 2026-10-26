#!/usr/bin/env python3
"""Lint BluePrint requirements for EARS patterns and Verify/Expect structure.

Reads Markdown or text files that use the format in
prompts/blueprint-specification.md. Uses only the Python standard library.

    python3 -I ears-lint.py FILE...        text report
    python3 -I ears-lint.py --json FILE... JSON report
    python3 -I ears-lint.py --selftest     run the built-in tests

Exit status: 0 when there are no errors, 1 when there are errors (or
warnings with --strict), 2 when a file cannot be read.
"""
import argparse
import json
import re
import sys

PATTERNS = ("ubiquitous", "event", "state", "unwanted", "optional", "complex")

# Clause keywords in Verify blocks and experiments, with their order rank.
CLAUSE_RANK = {"given": 1, "while": 1, "when": 2, "measure": 3, "expect": 4, "if": 5}
META_KEYWORDS = ("verifies", "because")

VAGUE = re.compile(
    r"\b(fast|quick|quickly|easy|easily|simple|appropriate|as needed|"
    r"as appropriate|if possible|user-friendly|adequate|sufficient|efficient|"
    r"flexible|reasonable|etc|and/or|normally|usually)\b")
RANGE = re.compile(
    r"\d[^\n]*?\s(to|–)\s*-?\d|\d\s*[-–]\s*\d|±|\+/-|\b(less|more|fewer|greater) than\b|"
    r"\bat (least|most)\b|\b(maximum|minimum)\b|[<>≤≥]|\(exact\)")
SOURCE = re.compile(r"\bsource:", re.I)
REQ_HEAD = re.compile(r"^Requirement\s+([\w.-]+)\s*(?:\[([^\]]*)\])?\s*:\s*$")
EXP_HEAD = re.compile(r"^Experiment\s+([\w.-]+)\s*(?:\[([^\]]*)\])?\s*:\s*$")
VERIFY_HEAD = re.compile(r"^(Verify|Validate)\b.*:\s*$")
FIELD_WORDS = 25

# A quoted or `code` span mentions a word; it does not use it.
QUOTED = re.compile(r'"[^"]*"|\u201c[^\u201d]*\u201d|`[^`]*`')
# An ID: letters, then "-<letters or digits>" parts, an optional Examples row.
ID_TOKEN = re.compile(r"(?<![\w-])[A-Za-z]+(?:-[A-Za-z0-9]+(?:\.[A-Za-z0-9]+)*)+(?:\[\d+\])?")
# A status marker such as "(M)" after the last sentence is not a sentence.
MARKER = re.compile(r"\(\w{1,3}\)")
SENTENCE_SPLIT = re.compile(r"(?<=[.?!])\s+(?=[A-Z0-9(])")
PASSIVE = re.compile(r"\bshall\s+(?:not\s+)?be\s+([a-z][\w-]*)")
IRREGULAR = set(
    "given taken made done found seen known shown written built sent set run read kept held "
    "left put shut cut brought bought caught taught told sold paid laid led".split())
# Verbs for compound-obligation, in addition to the glossary verbs.
VERBS = set(
    "accept acknowledge activate adjust alert allow apply assign calculate cancel check clear "
    "close command compare compute confirm connect contain continue control convert create "
    "deactivate decrease delete deliver detect disable disconnect display enable encrypt enter "
    "erase execute export generate give hold identify ignore import increase indicate initiate "
    "inform keep limit load lock log maintain measure monitor notify open operate parse permit "
    "prevent print process produce prompt provide read receive record reject release remove "
    "report request reset respond restart restore retain return save select send set show shut "
    "start stop store supervise supply switch terminate transmit trigger unlock update validate "
    "verify write".split())


class Finding:
    def __init__(self, path, line, severity, rule, message, text=""):
        self.path, self.line = path, line
        self.severity, self.rule = severity, rule
        self.message, self.text = message, text

    def as_dict(self):
        return dict(path=self.path, line=self.line, severity=self.severity,
                    rule=self.rule, message=self.message, text=self.text)

    def __str__(self):
        tail = f" [{self.text}]" if self.text else ""
        return f"{self.path}:{self.line}: {self.severity} {self.rule}: {self.message}{tail}"


def first_word(line):
    word = line.split(None, 1)[0] if line.split() else ""
    return word.rstrip(":.,").lower()


def short(text, limit=60):
    text = " ".join(text.split())
    return text if len(text) <= limit else text[:limit - 3] + "..."


def detect_pattern(sentence, names=()):
    """Return the EARS pattern of one requirement sentence, or None.

    A comma can follow the keyword ("If, as a result, ..."). A glossary name
    can start a ubiquitous requirement ("ETCS shall ...")."""
    s = sentence.lower()

    def starts(word):
        return re.match(word + r"[ ,]", s) is not None

    if starts("while"):
        return "complex" if re.search(r",\s*when ", s) else "state"
    if starts("when"):
        return "event"
    if starts("if"):
        return "unwanted"
    if starts("where"):
        return "optional"
    if starts("the"):
        return "ubiquitous"
    for name in sorted(names, key=len, reverse=True):
        if s.startswith(name + " ") and re.match(r"shall\b", s[len(name) + 1:]):
            return "ubiquitous"
    return None


def mask(text):
    """Blank quoted and `code` spans, so that a mentioned keyword is not counted."""
    return QUOTED.sub(lambda m: " " * len(m.group(0)), text)


def sentences(text):
    """Split a requirement into sentences. A final status marker is not one."""
    parts = SENTENCE_SPLIT.split(text)
    return [p for p in parts if not MARKER.fullmatch(p.strip())] or [text]


def glossary(text):
    """The names and verbs of the Glossary blocks in ```blueprint fences."""
    names, verbs = set(), set()
    for fence in re.findall(r"```blueprint\n(.*?)```", text, re.S):
        for key, out in (("names", names), ("verbs", verbs)):
            m = re.search(key + r":\s*\[(.*?)\]", fence, re.S)
            if m:
                out.update(" ".join(w.strip().strip('"').lower().split())
                           for w in m.group(1).split(",") if w.strip())
    return names, verbs


class Group:
    """One Verify block, or the clauses of one experiment."""

    def __init__(self, line, is_experiment):
        self.line = line
        self.is_experiment = is_experiment
        self.counts = {k: 0 for k in CLAUSE_RANK}
        self.last_rank = 0
        self.ranged_expects = 0


class Linter:
    def __init__(self, path, names=(), verbs=()):
        self.path = path
        self.names, self.verbs = set(names), set(verbs)
        self.findings = []
        self.block = None      # "req" or "exp"
        self.group = None
        self.clause = None     # [keyword, text, line]
        self.in_examples = False
        self.ids = {}          # requirement and Verify IDs -> first line

    def add(self, line, severity, rule, message, text=""):
        self.findings.append(Finding(self.path, line, severity, rule, message, short(text)))

    # Clause handling -----------------------------------------------------

    def flush_clause(self):
        if not self.clause or not self.group:
            self.clause = None
            return
        kw, text, line = self.clause
        self.clause = None
        if kw in META_KEYWORDS:
            return
        g = self.group
        g.counts[kw] += 1
        rank = CLAUSE_RANK[kw]
        if rank < g.last_rank:
            self.add(line, "warning", "clause-order",
                     "Put clauses in this order: Given/While, When, Measure, Expect, If.", text)
        g.last_rank = max(g.last_rank, rank)
        low = text.lower()
        if kw == "if" and not re.search(r"\bthen\b", low):
            self.add(line, "error", "if-then", "An 'If' clause must have 'then'.", text)
        if kw == "expect":
            if re.search(r"\band\b", low):
                self.add(line, "warning", "one-assertion",
                         "Possible two assertions. Write one Expect for each check.", text)
            body = re.sub(r"\(source:[^)]*\)", "", text, flags=re.I)
            body = ID_TOKEN.sub(" ", body)  # the digits of an ID are not a number
            if re.search(r"\d", body):
                if not RANGE.search(body):
                    self.add(line, "warning", "numeric-range",
                             "Give a range or a tolerance, or mark the value '(exact)'.", text)
                elif not re.search(r"\(exact\)", body):
                    g.ranged_expects += 1
                    if not SOURCE.search(text):
                        self.add(line, "warning", "numeric-source",
                                 "Give the source of the number: '(source: ...)'.", text)

    # Group handling ------------------------------------------------------

    def end_group(self):
        self.flush_clause()
        g = self.group
        if not g:
            return
        self.group = None
        where = "experiment" if g.is_experiment else "Verify block"
        if g.counts["when"] == 0:
            self.add(g.line, "error", "no-when", f"The {where} has no 'When' clause.")
        elif g.counts["when"] > 1:
            self.add(g.line, "warning", "many-when", f"The {where} has more than one 'When' clause.")
        if g.counts["expect"] == 0:
            self.add(g.line, "error", "no-expect", f"The {where} has no 'Expect' clause.")
        if g.counts["measure"] > g.counts["expect"]:
            self.add(g.line, "warning", "measure-expect", "Each 'Measure' needs an 'Expect'.")
        if g.is_experiment and g.ranged_expects and g.counts["if"] < 2:
            self.add(g.line, "warning", "branches",
                     "Give 'If ... then' clauses for results above and below the range.")

    # Requirement handling ------------------------------------------------

    def end_requirement(self):
        r = self.req
        sentence = " ".join(r["text"].split())
        line = r["line"]
        if not sentence:
            self.add(line, "error", "no-sentence", "The requirement has no sentence.")
        else:
            low = sentence.lower()
            masked = mask(low)
            n_shall = len(re.findall(r"\bshall\b", masked))
            if n_shall != 1:
                self.add(line, "error", "one-shall",
                         f"Use exactly one 'shall' (found {n_shall}).", sentence)
            pattern = detect_pattern(sentence, self.names)
            if pattern is None:
                self.add(line, "error", "ears-pattern",
                         "Start with 'The', 'When', 'While', 'If', or 'Where'.", sentence)
            if pattern == "unwanted" and not re.search(r",\s*then\b", low):
                self.add(line, "error", "if-then", "An 'If' requirement must have ', then'.", sentence)
            tag = (r["tag"] or "").strip().lower()
            if tag and tag not in PATTERNS:
                self.add(line, "warning", "unknown-tag",
                         f"Unknown pattern tag '{tag}'. Use one of: {', '.join(PATTERNS)}.")
            elif tag and pattern and tag != pattern:
                self.add(line, "warning", "tag-mismatch",
                         f"The tag is '{tag}', but the sentence is '{pattern}'.", sentence)
            if pattern and re.search(r"(^|[\s,])it\s+shall\b", masked):
                self.add(line, "warning", "name-system", "Name the system. Do not write 'it'.", sentence)
            m = VAGUE.search(low)
            if m:
                self.add(line, "warning", "vague-word",
                         f"'{m.group(0)}' is not observable. Use a number and a unit.", sentence)
            parts = sentences(sentence)
            if len(parts) > 1:
                self.add(line, "warning", "one-sentence",
                         "More than one sentence. Write one requirement for each.", sentence)
            if max(len(p.split()) for p in parts) > FIELD_WORDS:
                self.add(line, "warning", "long-sentence",
                         f"More than {FIELD_WORDS} words. Divide the requirement.", sentence)
            m = PASSIVE.search(masked)
            if m and ((len(m.group(1)) > 3 and m.group(1).endswith("ed"))
                      or m.group(1) in IRREGULAR):
                self.add(line, "warning", "passive-response",
                         "The response is passive. Name the system that acts.", sentence)
            m = re.search(r"\bshall\b", masked)
            if m:
                response = re.split(r"[.;](?:\s|$)", masked[m.end():])[0]
                for verb in re.findall(r"\band\s+([a-z][\w-]*)", response):
                    if verb != "shall" and (verb in VERBS or verb in self.verbs):
                        self.add(line, "warning", "compound-obligation",
                                 "The response joins two verbs with 'and'. "
                                 "Write one requirement for each.", sentence)
                        break
        if not r["because"]:
            self.add(line, "warning", "no-because", "Add a 'Because' sentence for the reviewer.")
        if r["verify"] == 0:
            self.add(line, "error", "no-verify",
                     "The requirement has no 'Verify' or 'Validate' block.")

    def check_id(self, ident, line):
        if ident in self.ids:
            self.add(line, "error", "duplicate-id",
                     f"The ID {ident} is also used at line {self.ids[ident]}.")
        else:
            self.ids[ident] = line

    def end_block(self):
        self.end_group()
        if self.block == "req":
            self.end_requirement()
        self.block = None

    # Main loop -----------------------------------------------------------

    def run(self, lines):
        for number, raw in enumerate(lines, 1):
            line = raw.strip()
            if line.startswith("```") or line.startswith("#"):
                self.end_block()
                continue
            m = REQ_HEAD.match(line)
            if m:
                self.end_block()
                self.check_id(m.group(1), number)
                self.block = "req"
                self.req = dict(line=number, id=m.group(1), tag=m.group(2),
                                text="", because=False, verify=0, in_head=True)
                continue
            m = EXP_HEAD.match(line)
            if m:
                self.end_block()
                self.block = "exp"
                self.group = Group(number, is_experiment=True)
                continue
            if not self.block or not line:
                continue
            kw = first_word(line)
            if self.block == "req" and VERIFY_HEAD.match(line):
                self.end_group()
                self.req["in_head"] = False
                self.req["verify"] += 1
                self.group = Group(number, is_experiment=False)
                self.in_examples = False
                words = line.split()
                # "Verify V-012 name:" — an ID is optional; a used ID is unique
                if len(words) > 2 and re.fullmatch(r"[A-Za-z]+-[\w.-]*\w", words[1]):
                    self.check_id(words[1], number)
                continue
            if self.group and kw == "examples":
                self.flush_clause()
                self.in_examples = True
                continue
            if self.in_examples and line.startswith("|"):
                continue  # an Examples row is data, not text of a clause
            self.in_examples = False
            if kw == "because":
                self.flush_clause()
                if self.block == "req":
                    self.req["because"] = True
                self.clause = ["because", line, number]
                continue
            if self.block == "req" and self.req["in_head"]:
                if not (self.clause and self.clause[0] == "because"):
                    self.req["text"] += " " + line
                continue
            if self.group and (kw in CLAUSE_RANK or kw in META_KEYWORDS):
                self.flush_clause()
                self.clause = [kw, line, number]
            elif self.clause:
                self.clause[1] += " " + line
        self.end_block()
        return self.findings


def lint_text(path, text):
    names, verbs = glossary(text)
    return Linter(path, names, verbs).run(text.splitlines())


SELFTEST_GOOD = """\
Requirement R1 [event]:
  When a login attempt fails for the third time in sequence,
  the authentication service shall lock the account for the lockout period.
  Because repeated failures can show a password attack.

  Verify lockout:
    Given an active account.
    When three login attempts fail in sequence.
    Expect the account state to be locked.
    Expect no session token in the response.

Experiment E3 [thermal]:
  Verifies: R1.
  Given the module at 25 °C.
  When you apply 12 V for 60 s.
  Measure the current.
  Expect a current of 1.8 A to 2.1 A (source: model thermal.solve).
  If the current is more than 2.1 A, then examine the module.
  If the current is less than 1.8 A, then update R_internal.

```blueprint
Glossary Train { names: [ETCS], verbs: [supervise] }
```

Requirement R5 [ubiquitous]:
  ETCS shall supervise the shunting speed.
  Because a fast shunting move can derail the train.
  Level: software.
  Derives: R1.

  Verify V-005 speed:
    Given a train in shunting mode.
    When the speed is <speed>.
    Expect the brake state to be <state>.
    Examples:
      | speed | state | note and comment |
      | 30 km/h | released | below the limit |

  Validate V-006 driver:
    When a driver moves the train in a yard.
    Expect the driver to stop the train before the limit (source: trial T-1).
    Expect the trace row for V-005 to have the status PASS.

Requirement R6 [unwanted]:
  If, after a reset, the sensor fails, then the linter shall report the rule `one-shall` once.
  Because a quoted keyword is a mention. (M)

  Verify V-007 mention:
    When the linter reads the sentence.
    Expect one finding.
"""

SELFTEST_BAD = """\
Requirement R2 [state]:
  When it fails, it shall lock the account quickly and shall send an email.

Requirement R3:
  Accounts are locked by the service.
  Because of attacks.
  Verify:
    Expect the account to be locked and an email to be sent.
    Given an account.

Requirement R4:
  The account shall be locked and send an email. The service records the event.
  Because of attacks.

  Verify V-008 a:
    When it fails.
    Expect a lock.

Requirement R4:
  The service shall lock the account.
  Because of attacks.

  Verify V-008 b:
    When it fails.
    Expect a lock.

Experiment E4:
  When you apply 12 V.
  Measure the current.
  Expect a current of 2 A.
  Expect a voltage of 1.8 V to 2.1 V.
"""

SELFTEST_EXPECTED = {
    # R2
    "one-shall", "tag-mismatch", "name-system", "vague-word", "no-because", "no-verify",
    # R3
    "ears-pattern", "one-assertion", "clause-order", "no-when",
    # R4 (twice)
    "passive-response", "compound-obligation", "one-sentence", "duplicate-id",
    # E4
    "numeric-range", "numeric-source", "branches",
}


def selftest():
    good = lint_text("good", SELFTEST_GOOD)
    bad = lint_text("bad", SELFTEST_BAD)
    ok = True
    if good:
        ok = False
        print("selftest: the good sample has findings:")
        for f in good:
            print("  ", f)
    rules = {f.rule for f in bad}
    if rules != SELFTEST_EXPECTED:
        ok = False
        print("selftest: missing rules:", sorted(SELFTEST_EXPECTED - rules))
        print("selftest: extra rules:", sorted(rules - SELFTEST_EXPECTED))
    print("selftest OK" if ok else "selftest FAILED")
    return 0 if ok else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("files", nargs="*", metavar="FILE")
    ap.add_argument("--json", action="store_true", help="print findings as JSON")
    ap.add_argument("--strict", action="store_true", help="fail on warnings too")
    ap.add_argument("--selftest", action="store_true", help="run the built-in tests")
    args = ap.parse_args(argv)
    if args.selftest:
        return selftest()
    sources = args.files or ["-"]
    findings = []
    for path in sources:
        try:
            text = sys.stdin.read() if path == "-" else open(path, encoding="utf-8").read()
        except OSError as e:
            print(f"ears-lint: {e}", file=sys.stderr)
            return 2
        findings += lint_text("<stdin>" if path == "-" else path, text)
    errors = sum(f.severity == "error" for f in findings)
    warnings = len(findings) - errors
    if args.json:
        json.dump({"tool": "ears-lint", "schema": 1, "errors": errors, "warnings": warnings,
                   "findings": [f.as_dict() for f in findings]}, sys.stdout, indent=2)
        print()
    else:
        for f in findings:
            print(f)
        print(f"\n{errors} errors, {warnings} warnings")
    return 1 if errors or (args.strict and warnings) else 0


if __name__ == "__main__":
    sys.exit(main())
