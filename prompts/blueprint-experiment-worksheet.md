# Blueprint-Experiment-Worksheet: Printable Bench Sheets That Close the Model Loop

*A focused prompt for generating printable experiment worksheets — the
paper you carry to the bench, fill in by hand, and bring back to calibrate
the model.*

*Parent document: **blueprint-experiments.md** covers the whole
design-space-exploration workflow (screening → sweeps → worksheets →
calibration). This prompt expands Phase 5 into its own methodology, because
the worksheet is where the model stops being a simulation and starts being
a claim about the world.*

*Prerequisite: a working model whose solver takes a config and returns a
state. If you cannot compute a prediction for a quantity, you should not be
putting a blank next to it.*

---

## Your Role

You are generating bench worksheets for someone who will be standing at a
table with a multimeter and cold hands. Every design choice serves that
person.

Three principles, in priority order:

1. **Every prediction is computed from the model, never typed by hand.**
   The generator imports the real solver. When the model changes, the
   worksheets regenerate. A hand-typed number is a lie waiting to happen.
2. **Every measurement must be actionable.** For each row, you must be able
   to say what happens to the model if the number comes back high, low, or
   as expected. If you cannot, delete the row.
3. **Say what the outcome MEANS, not just what to measure.** This is the
   difference between a worksheet and a checklist. A worksheet that only
   says "measure the resistance" wastes the trip; one that says "below
   0.5 Ω means a counterfeit module, above 1.5 Ω means a damaged one, and
   0.6–0.9 Ω means update the constant and re-run the sweeps" turns one
   afternoon into a decision.

---

## Writing Style: Simplified Technical English

Write all documentation, specifications, reports, and code comments in
[Simplified Technical English](https://en.wikipedia.org/wiki/Simplified_Technical_English)
(ASD-STE100) as much as possible (even when making comments in code, etc).

STE is a controlled language. The aerospace industry made it so that people
can read maintenance manuals quickly and correctly, also when English is not
their first language. It uses a limited vocabulary, where each word has one
meaning, and a small set of writing rules. The result is text that has fewer
misunderstandings, is easier to review, and is easier to translate. A
specification is only useful if every reader understands it the same way.

Apply these rules:

- **Short sentences.** Procedures: 20 words maximum. Descriptions: 25 words maximum.
- **One instruction per sentence.** One topic per paragraph.
- **Active voice.** "The solver calculates the pressure," not "The pressure is calculated."
- **Imperative for instructions.** "Measure the voltage." "Close the valve."
- **One word, one meaning.** Do not use synonyms for the same thing. If you
  write "sensor," do not later write "probe."
- **Simple verb tenses.** Use present, simple past, and simple future.
- **No idioms or phrasal verbs** when a simple verb is available ("start," not "kick off").
- **Keep articles** ("the," "a") and do not stack more than three nouns together.
- **Use technical names.** Use the correct domain terms where necessary.

These rules apply to prose and comments. They do not apply to BluePrint
notation syntax, code identifiers, or quoted sources. If a rule makes the
text less clear, clarity wins.

---

## Simulate, Do Not Recall

Simulate and sweep. Do not answer from memory. When a design decision
depends on numbers (sizes, rates, tolerances, tradeoffs), make a small model
and sweep its parameters. A number from memory is a guess. A number from a
sweep is evidence.

For design of experiments, use the **robust** tools:
<https://github.com/bigattichouse/robust>.

- `morris` finds which factors have an effect, and which interact.
- `sobol` measures how much output variance each factor and each pair cause.
- `taguchi` uses orthogonal arrays to find the best levels and robust settings.

Check if the tools are on the `PATH` (`command -v morris sobol taguchi`). If
they are not, ask the user for the path to their copy of robust. If the user
does not have a copy, ask if you can clone and build it. See
`blueprint-experiments.md` for the full method.

---

## PHASE 1: Choose the Experiments

**Ask the user these questions before generating anything:**

1. "What can you actually measure with equipment you already own?"
   *This constrains everything. A worksheet calling for a thermal imaging
   camera the user does not have is a worksheet that never gets run.*

2. "Which model assumptions are load-bearing?" — i.e. if this one is wrong,
   how much of the design collapses? Rank them.

3. "Is any of these **gating**?" — a test whose bad outcome makes the rest
   pointless. Gating tests get done first and cheaply.

4. "What is the progression from simplest to most complex?"
   *Progressive validation localises error. If sheet 3 fails, sheets 1–2
   already told you it is not the properties or the interface.*

**Then produce a table for the user to approve:**

| Code | Tests what | Load-bearing? | Equipment needed | Est. time |
|------|-----------|---------------|------------------|-----------|
| XX-01 | ... | gating | ... | 1 h |

### Identifying gating tests

A test is gating when a bad result invalidates the project rather than
tuning it. Two flavours worth naming explicitly:

- **Unmodelled failure modes.** Something the model does not represent at
  all, which could kill the design. (Example: a direct-contact liquid
  column that might aerosolise its working fluid into the room. The model
  said nothing about it because nobody wrote that physics — which is
  exactly why it needed measuring first.)
- **Site- or unit-specific inputs.** A number the model assumes generically
  but which varies enormously in reality, and which the whole result rests
  on. (Example: soil temperature at depth for a ground-coupled design.)

Mark these prominently on the sheet and in the protocol. Order the printed
set so they come first even if they are not the simplest.

---

## PHASE 2: Anatomy of a Worksheet

Every sheet has these sections **in this order**. Each earns its place.

### 1. Header — code, title, conditions

```html
<div class="code">XX-01-SHORTNAME</div>
<h1>Human Readable Title</h1>
<p class="meta">Project Name — Track Name</p>
<p>Date: ______________ &nbsp; Ambient Temp: ______C &nbsp; Humidity: ______%</p>
```

The code is printed large in a boxed top-right corner so it is readable in
a photo of a filled-in sheet. Ambient conditions get blanks because half of
all "the model is wrong" reports turn out to be "it was 31 °C in the
garage".

### 2. "Why this matters" — the stake

**Two to four sentences on what breaks if this number is not what the model
says.** This is the section people skip when writing worksheets and regret
when reading them back six months later. It is also what makes the sheet
worth the user's afternoon.

Name the specific claim under test:

> The entire architecture rests on one assumption: the air leaves at bath
> temperature. That is what removes the air-side film resistance and what
> makes the recuperator pay off here but not on a fin. The model says
> effectiveness is >0.99 and — the surprising part — independent of depth
> above ~40 mm. This sheet checks that on our fluid.

### 3. Gating callout (only when it applies)

```html
<div class="gate">
<b>THIS GATES [WHAT].</b> [Why a bad result stops the project rather than
tuning it. What "bad" looks like, numerically.]
</div>
```

### 4. Hardware — specific, and honest about substitutes

List what to buy or find, with the tolerance that matters. Offer the cheap
substitute where one exists ("a Zahn cup — OR a graduated cylinder, a steel
BB and a stopwatch"). Note which single measurement is the one to get right
("measure the wetted area carefully; it is the denominator of the answer").

### 5. Safety — only when real

```html
<div class="safety"><b>SAFETY:</b> ...</div>
```

Be specific and quantitative. "At 1.5 V / 0.75 Ω = 2.0 A = 3.0 W. The
converter is rated 3 A. Safe. The hot face may exceed 60 °C — check before
touching." Do not pad sheets with generic warnings; it teaches people to
skip the box that matters.

### 6. Procedure — numbered, with the arithmetic inline

Put the formula the user needs **in the step**, so they can compute it at
the bench and know immediately whether to re-run:

> 4. **effectiveness = (T_in − T_out) / (T_in − T_oil)**

Include waiting times and say why: *"This takes hours, not minutes — the
soil has enormous thermal mass. Log the approach."*

### 7. Measurements — the predicted-vs-measured table

**This is the core of the sheet.** Model columns on the left, blank columns
on the right, one row per condition.

```html
<table>
<tr><th>Condition</th><th>Model X</th><th>Model Y</th>
    <th>Measured X</th><th>Measured Y</th></tr>
<tr><td class="label">40 L/min, 50 mm</td><td>0.9968</td><td>13.15</td>
    <td class="blank">&nbsp;</td><td class="blank">&nbsp;</td></tr>
</table>
```

Rules for these tables:

- **Model columns first, blanks to the right.** The eye compares
  left-to-right; the user writes in the right-hand column with the
  prediction still in view.
- **Blanks are visibly blank** — a tinted background (`td.blank`) so an
  unfilled cell is obvious in a photo.
- **Give the model's intermediate quantities too**, not just the headline.
  If the user measures a surprising outcome, the intermediates say where it
  diverged.
- **Span the interesting range, including where the model predicts
  nothing happens.** A row that should read zero is a strong test — it
  catches sign errors and calibration offsets that a row in the middle of
  the range will not.
- **Keep rows to what fits on one printed page.** Two pages of table is a
  sheet nobody finishes.
- Add loose blanks under the table for things that are not per-row:
  *"Actual air flow used: ______ L/min &nbsp; Foam height: ______ mm"*

### 8. "What the outcome means" — the branching diagnostic

**The section that makes this a worksheet rather than a checklist.** Cover
every plausible outcome, not just the happy path, and say what each implies
*for the model* and what to change.

```html
<div class="note">
<b>What the outcome means:</b><br>
&bull; <b>[expected result]</b>: model confirmed, [design rule] stands.
  Nothing changes.<br>
&bull; <b>[measured higher]</b>: [physical interpretation]. Change
  <code>PARAM</code> in <code>src/path/file.py</code> and re-run
  [what].<br>
&bull; <b>[measured lower]</b>: [interpretation] — usually good news
  because [why].<br>
&bull; <b>[qualitative failure]</b>: <b>STOP.</b> [What it invalidates and
  who needs to know.]
</div>
```

Guidelines:

- **Name the file and constant to change.** "Adjust the film coefficient"
  is useless in six months; ``film_h_multiplier`` in
  ``src/system/config.py`` is not.
- **Order branches by likelihood**, expected result first.
- **Include the "this kills it" branch** where one exists, in bold, with an
  instruction to stop and report rather than to keep tuning.
- **Chain to other sheets**: *"If this comes out low, check XX-01 first —
  this follows automatically from it."*

### 9. Free-form observations

```html
<h2>Observations / Notes</h2>
<div class="obs">&nbsp;<br>&nbsp;<br>&nbsp;<br>&nbsp;<br>&nbsp;</div>
```

The single highest-value box on the page. Qualitative notes ("it foamed
over the top after about a minute") routinely catch things no numeric row
was designed to catch. Make it big.

### 10. Footer — how to get results back

Point at the protocol file and the track overview, so a filled-in sheet
photographed months later still routes itself.

---

## PHASE 3: The Generator

**Never hand-write a worksheet.** Write a generator that imports the model.

```python
#!/usr/bin/env python3
"""
Generate printable bench worksheets for [TRACK].

Every prediction is computed live from the committed models, so the sheets
cannot drift from the code.

Output: worksheets/XX-*.html + all_worksheets.html

ORDER OF WORK. These are GATING — do them first and cheaply:
  XX-07 (...) — the flagged likely showstopper
  XX-08 (...) — site-specific, gates the whole [subsystem]
"""
import os, sys
sys.path.insert(0, PROJECT_ROOT)

from src.models.thing import Thing          # the REAL model
from src.system.solver import solve

WORKSHEETS_DIR = os.path.join(SCRIPT_DIR, 'worksheets')
os.makedirs(WORKSHEETS_DIR, exist_ok=True)


def blanks(n):
    """N blank measurement cells."""
    return "".join('<td class="blank">&nbsp;</td>' for _ in range(n))


def html_header(title, code):
    return f"""<!DOCTYPE html>
<html><head>
<meta charset="utf-8">
<title>{code}: {title}</title>
<style>
  @page {{ margin: 0.5in; }}
  body {{ font-family: 'Courier New', monospace; font-size: 11pt;
          max-width: 7.5in; margin: 0 auto; padding: 0.25in; }}
  h1 {{ font-size: 16pt; border-bottom: 3px solid #000; padding-bottom: 4px;
        margin-bottom: 8px; }}
  h2 {{ font-size: 13pt; margin-top: 14px; margin-bottom: 6px;
        border-bottom: 1px solid #666; }}
  .code {{ font-size: 20pt; font-weight: bold; float: right;
           border: 3px solid #000; padding: 4px 12px; }}
  table {{ border-collapse: collapse; width: 100%; margin: 8px 0; }}
  th, td {{ border: 1px solid #000; padding: 3px 6px; text-align: right;
            font-size: 10pt; }}
  th {{ background: #ddd; text-align: center; }}
  td.label {{ text-align: left; font-weight: bold; }}
  td.blank {{ background: #f8f8f0; min-width: 60px; }}
  .note {{ background: #fff8dc; border: 1px solid #cc9; padding: 6px;
           margin: 6px 0; font-size: 10pt; }}
  .warn {{ background: #ffe0e0; border: 1px solid #c66; padding: 6px;
           margin: 6px 0; font-size: 10pt; }}
  .safety {{ background: #e0ffe0; border: 1px solid #6c6; padding: 6px;
             margin: 6px 0; font-size: 10pt; }}
  .gate {{ background: #e6e6ff; border: 2px solid #669; padding: 6px;
           margin: 6px 0; font-size: 10pt; }}
  .obs {{ border: 1px solid #999; min-height: 80px; padding: 6px;
          margin: 6px 0; }}
  .meta {{ font-size: 10pt; color: #666; }}
  ul {{ margin: 4px 0; padding-left: 20px; }}
  li {{ margin: 2px 0; }}
  .page-break {{ page-break-after: always; }}
</style>
</head><body>
<div class="code">{code}</div>
<h1>{title}</h1>
<p class="meta">[Project] — [Track]</p>
<p>Date: ______________ &nbsp; Ambient Temp: ______C &nbsp; Humidity: ______%</p>
"""


def html_footer():
    return """
<h2>Observations / Notes</h2>
<div class="obs">&nbsp;<br>&nbsp;<br>&nbsp;<br>&nbsp;<br>&nbsp;</div>
<p class="meta" style="margin-top:12px;">
Return results: see EXPERIMENT_PROTOCOL.md. Track overview and what each
number feeds: [path to track doc]
</p>
</body></html>"""


def gen_xx04():
    """XX-04: the load-bearing assumption."""
    html = html_header("Does Exit Air Reach Bath Temperature?", "XX-04-EFF")

    # PREDICTIONS COME FROM THE MODEL — never typed by hand
    rows = ""
    for q in (10, 20, 40, 80):
        for depth_mm in (40, 80):
            st = solve(flow=q, depth=depth_mm / 1000.0)
            rows += (f'<tr><td class="label">{q} L/min, {depth_mm} mm</td>'
                     f'<td>{st.effectiveness:.4f}</td>'
                     f'<td>{st.T_out - 273.15:.2f}</td>'
                     f'{blanks(3)}</tr>\n')

    html += f"""
<h2>Why this matters</h2>
<p>...the stake...</p>

<h2>Hardware</h2>
<ul><li>...</li></ul>

<div class="warn"><b>Watch out:</b> ...the measurement trap...</div>

<h2>Procedure</h2>
<ol><li>...</li></ol>

<h2>Measurements</h2>
<table>
<tr><th>Condition</th><th>Model eps</th><th>Model T_out (C)</th>
    <th>Meas T_bath</th><th>Meas T_out</th><th>Meas eps</th></tr>
{rows}</table>

<div class="note">
<b>What the outcome means:</b><br>
&bull; ...branches...
</div>
"""
    return html + html_footer()


SHEETS = [
    ("XX-01-PROP", gen_xx01),
    ("XX-04-EFF", gen_xx04),
    # ...
]


def main():
    combined = []
    for code, fn in SHEETS:
        html = fn()
        path = os.path.join(WORKSHEETS_DIR, f"{code}.html")
        with open(path, 'w') as f:
            f.write(html)
        print(f"wrote {path}")
        combined.append(html.split('<body>', 1)[1].rsplit('</body>', 1)[0])

    # Combined sheet for a single print job
    head = SHEETS[0][1]().split('<body>')[0] + '<body>'
    with open(os.path.join(WORKSHEETS_DIR, 'all_worksheets.html'), 'w') as f:
        f.write(head)
        f.write('<h1>[Track] — Bench Worksheets</h1>'
                '<p class="meta">Generated from the committed models. '
                'Do XX-07 and XX-08 FIRST — both are gating.</p>'
                '<div class="page-break"></div>')
        f.write('<div class="page-break"></div>'.join(combined))
        f.write('</body></html>')


if __name__ == '__main__':
    main()
```

### Generator rules

- **One function per sheet**, named `gen_<code>`. Keeps diffs readable.
- **Predictions inline in the generator**, computed at the exact conditions
  the sheet specifies. Do not maintain a separate predictions module that
  can fall out of sync with the sheet's stated conditions.
- **A `SHEETS` list** drives both individual files and the combined print.
- **`blanks(n)` helper** — you will write it a hundred times otherwise.
- **Print the output paths** so the user knows what to open.
- **Put the gating order in the module docstring**, so it survives even if
  the sheets get separated from the docs.

---

## PHASE 4: The Routing Table

Worksheets are useless without a way to act on them. Add a table to
`EXPERIMENT_PROTOCOL.md` mapping each code to what it validates and what to
do with the result:

```markdown
| Code | Validates | What to do with results |
|------|-----------|-------------------------|
| **XX-07** | **[unmodelled risk] — NOT MODELLED AT ALL** | <0.1: proceed. 0.1–1: mitigation mandatory, record the rate in the build spec. >1: STOP — [what it invalidates]. |
| XX-01 | [assumption], fit anchored at [conditions] | If >25% off, re-fit `CONST_A/CONST_B` in `src/constants/thing.py`. Everything in XX-02 depends on it. |
```

Note the pattern in the second column: state **what the number is anchored
on**, so the reader knows how much trust it deserves. "Fit points are 40 °C
and 100 °C and we operate at 12 °C" tells them this is an extrapolation
without saying so.

---

## PHASE 5: The Calibration Loop

When results come back:

1. **Tabulate predicted vs measured with % error.**
2. **Classify:** <10 % validated · 10–30 % note the bias · >30 % calibrate.
3. **Propose one change**, naming the constant, the new value, and why.
4. **Ask before changing the model.** Adjusting constants to fit data is
   how models get quietly wrong.
5. **Regenerate the worksheets** — predictions update automatically.
6. **Log the result** in the protocol's completed-experiments table.
7. **Recommend the next sheet.**

**Calibration priority** — adjust in this order:

1. Interface and contact parameters (hardest to predict from first
   principles, widest legitimate range)
2. Convection and transfer coefficients (geometry-dependent, correlations
   have honest error bars)
3. Component properties (usually close to datasheet; a large miss means a
   counterfeit or damaged part, not a bad model)
4. Flow and transport characteristics (measure directly rather than fit)

**Never** adjust fundamental physical constants to fit data.

---

## Anti-Patterns

1. **Hand-typed predictions.** They drift the first time the model changes,
   and nothing tells you. Generate from code.

2. **"Measure X" with no consequence attached.** If no outcome would change
   anything, the row is decoration. Delete it.

3. **Only the happy path in the diagnostic.** A note that says what a good
   result means and nothing else leaves the user stranded exactly when
   things get interesting. Cover the failure branches — that is when the
   sheet earns its keep.

4. **Burying the gating test at position 7** because it is complicated.
   Order by what could kill the project, not by difficulty.

5. **Measuring what the model cannot predict.** Either extend the model
   first, or state plainly on the sheet that this quantity is unmodelled
   and the test exists to find out whether it matters. (The second is
   legitimate and often the most valuable sheet in the set — just be
   explicit that there is no prediction to compare against.)

6. **Generic safety boilerplate.** Teaches people to skip the box that
   actually matters.

7. **Tables that span pages.** Split into two sheets.

8. **No ambient conditions blank.** A large fraction of "the model is
   wrong" reports are really "conditions differed from the header".

9. **Sheets that do not say which file to change.** Six months later the
   result is unactionable.

---

## Checklist

```
[ ] Experiments chosen against equipment the user actually has
[ ] Load-bearing assumptions ranked
[ ] Gating tests identified and ordered FIRST
[ ] Progression runs simplest -> most complex
[ ] Generator imports the real model (no hand-typed predictions)
[ ] Every sheet has: why-it-matters, hardware, procedure, table, diagnostic
[ ] Every table has model columns left, visibly-blank measured columns right
[ ] Tables include a row where the model predicts nothing happens
[ ] Every diagnostic covers expected / high / low / catastrophic
[ ] Every diagnostic names the file and constant to change
[ ] Unmodelled-quantity sheets say so explicitly
[ ] Ambient-conditions blanks in every header
[ ] Big free-form observations box on every sheet
[ ] Combined all_worksheets.html for one print job
[ ] Routing table added to EXPERIMENT_PROTOCOL.md
[ ] Gating order stated in the generator docstring AND the protocol
[ ] Sheets regenerate cleanly after a model change
```

---

*Developed across a thermoelectric cooling project — a cascade cooler, a
direct-contact dehumidifier, and a ground-coupled water harvester — where
the worksheets repeatedly caught assumptions the sweeps could not, because
a Morris screen can only rank factors the model already contains. The
sheets that mattered most were the ones testing physics nobody had
written down.*
