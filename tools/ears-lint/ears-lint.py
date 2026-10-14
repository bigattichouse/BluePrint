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
VERIFY_HEAD = re.compile(r"^Verify\b.*:\s*$")
FIELD_WORDS = 25


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


def detect_pattern(sentence):
    """Return the EARS pattern of one requirement sentence, or None."""
    s = sentence.lower()
    if s.startswith("while "):
        return "complex" if re.search(r",\s*when ", s) else "state"
    if s.startswith("when "):
        return "event"
    if s.startswith("if "):
        return "unwanted"
    if s.startswith("where "):
        return "optional"
    if s.startswith("the "):
        return "ubiquitous"
    return None


class Group:
    """One Verify block, or the clauses of one experiment."""

    def __init__(self, line, is_experiment):
        self.line = line
        self.is_experiment = is_experiment
        self.counts = {k: 0 for k in CLAUSE_RANK}
        self.last_rank = 0
        self.ranged_expects = 0


class Linter:
    def __init__(self, path):
        self.path = path
        self.findings = []
        self.block = None      # "req" or "exp"
        self.group = None
        self.clause = None     # [keyword, text, line]

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
            n_shall = len(re.findall(r"\bshall\b", low))
            if n_shall != 1:
                self.add(line, "error", "one-shall",
                         f"Use exactly one 'shall' (found {n_shall}).", sentence)
            pattern = detect_pattern(sentence)
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
            if re.search(r"(^|[\s,])it\s+shall\b", low):
                self.add(line, "warning", "name-system", "Name the system. Do not write 'it'.", sentence)
            m = VAGUE.search(low)
            if m:
                self.add(line, "warning", "vague-word",
                         f"'{m.group(0)}' is not observable. Use a number and a unit.", sentence)
            if len(sentence.split()) > FIELD_WORDS:
                self.add(line, "warning", "long-sentence",
                         f"More than {FIELD_WORDS} words. Divide the requirement.", sentence)
        if not r["because"]:
            self.add(line, "warning", "no-because", "Add a 'Because' sentence for the reviewer.")
        if r["verify"] == 0:
            self.add(line, "error", "no-verify", "The requirement has no 'Verify' block.")

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
                continue
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
    return Linter(path).run(text.splitlines())


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
