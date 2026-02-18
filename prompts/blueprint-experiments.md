# Blueprint-Experiments: Design Space Exploration and Hardware Validation

*Paste this prompt after completing **blueprint-model.md**. It guides the AI
through Taguchi screening, parameter sweeps, experiment worksheet generation,
and the theory-to-hardware calibration loop.*

*Prerequisite: a working mathematical model with passing tests, built using
the blueprint-model methodology. The model must have a solver that accepts
a configuration object and returns a state object with performance metrics.*

---

## Instructions to the AI Assistant

You are helping me explore the design space of a mathematical model and
validate it against real hardware experiments. We will work through this
in phases. At each phase, **ask me questions** before proceeding — present
choices as multiple-choice when possible.

The deliverables are:
1. **Taguchi screening array** — identify which factors matter most
2. **Focused parameter sweeps** — find optimal configurations
3. **Grand sweep** — comprehensive results across all use cases
4. **Experiment worksheets** — printable HTML sheets with model predictions
5. **Experiment protocol** — maps experiment codes to calibration actions
6. **Calibration loop** — compare measurements to predictions, update model

The goal is to close the gap between simulation and reality. The model
tells us what to measure. The measurements tell us where the model is wrong.

---

## PHASE 1: Factor Identification

**Ask me these questions:**

1. "What are all the knobs we can turn in the model? I see these
   configurable parameters in the system config: [list them].
   Which ones do you want to explore?"

2. "For each factor, what levels should we test?"
   *Help me choose levels:*
   - *For continuous params: suggest 3-9 levels spanning the practical range*
   - *For categorical params: list all options*
   - *For boolean params: true/false*

3. "What are the response metrics we care about?"
   *Multiple-choice:*
   - *(a) Single metric (e.g., just efficiency)*
   - *(b) 2-3 metrics (e.g., efficiency + cost + temperature)*
   - *(c) Record everything, filter later (Recommended)*

4. "Are there different use cases or operating scenarios?"
   *e.g., cooling vs heating, batch vs continuous, day vs night*
   *Each use case may have different "best" configurations.*

5. "What hardware constraints should I respect?"
   *e.g., max voltage from your power supply, physical space limits,
   available component sizes*

**After gathering answers, produce:**
- A summary table of factors, levels, and ranges
- A list of response metrics to record
- Use case definitions (filter criteria for "good" in each scenario)

---

## PHASE 2: Taguchi Screening

### 2.1 — Array Selection

**Ask me:**
"You have [N] factors at [M] levels. I recommend:
- (a) L27 array (up to 13 factors at 3 levels, 27 runs)
- (b) L81 array (up to 40 factors at 3 levels, 81 runs)
- (c) L9 array (up to 4 factors at 3 levels, 9 runs — if few factors)
Which should we use?"

### 2.2 — The .tgu File Format

Create a Taguchi definition file:

```yaml
# [project_name].tgu — Taguchi screening array definition
#
# Factors and their levels for orthogonal array screening.
# Each factor maps to a list of values to test.
# The array type (L9, L27, L81) determines how many runs
# and how factors are assigned to columns.

factors:
  factor_A: value1, value2, value3
  factor_B: value1, value2, value3
  factor_C: level1, level2, level3
  factor_D: true, false
  factor_E: small, standard, large
  factor_F: 0.1, 0.5, 1.0, 2.0, 5.0
array: L27
```

### 2.3 — Run Script

Create `experiments/taguchi/run_single.py`:

```python
#!/usr/bin/env python3
"""Run a single experiment point from Taguchi array.

Reads factor values from TAGUCHI_* environment variables
(for use with taguchi CLI tool) or command-line arguments.
Outputs metrics as JSON to stdout.
"""
import os, sys, json

def get_factor(name, default=None):
    """Get from TAGUCHI_ env var or argparse."""
    return os.environ.get(f'TAGUCHI_{name}', default)

def main():
    # Read all factors
    factor_A = float(get_factor('factor_A', '1.0'))
    factor_B = get_factor('factor_B', 'default')
    # ... etc

    # Build config and solve
    config = SystemConfig(param_A=factor_A, param_B=factor_B, ...)
    state = solve(config)

    # Output metrics as JSON
    result = {
        'converged': state.converged,
        'primary_metric': state.metric_A,
        'secondary_metric': state.metric_B,
        # ... all relevant outputs
    }
    print(json.dumps(result))
```

### 2.4 — Analysis Script

Create `experiments/taguchi/analyze_results.py`:

```python
"""Analyze Taguchi results: factor importance, main effects, S/N ratios."""

def compute_main_effects(results, factor_name, metric_name):
    """Average metric at each level of a factor."""
    # Group by factor level, compute mean metric
    # Return: {level: mean_metric}

def compute_sn_ratio(results, factor_name, metric_name, target='larger'):
    """Signal-to-noise ratio per factor level.
    target: 'larger' (maximize), 'smaller' (minimize), 'nominal' (target value)
    """

def rank_factor_importance(results, factors, metric_name):
    """Rank factors by their influence on the metric.
    Importance = max(main_effect) - min(main_effect) across levels.
    """

def generate_report_html(results, factors, metrics):
    """Self-contained HTML report with:
    - Factor importance ranking (bar chart SVG)
    - Main effects plots (inline SVG per metric)
    - Best configuration summary
    - Convergence statistics
    """
```

### 2.5 — Interpretation

**Ask me after the screening runs:**
"Here are the Taguchi results. The factors ranked by importance are:
1. [factor] — [metric range across levels]
2. [factor] — [metric range across levels]
...

The top 3 factors explain [X]% of the variation. I recommend we focus
the detailed sweep on these. Sound right?"

---

## PHASE 3: Focused Grid Sweeps

### 3.1 — Sweep Design

**Ask me:**
"Based on Taguchi screening, the most important factors are [list].
I'd like to do a dense grid sweep. Here's what I propose:

| Factor     | Values                              | Count |
|------------|-------------------------------------|-------|
| [top 1]    | [fine-grained list]                 | N     |
| [top 2]    | [fine-grained list]                 | N     |
| [top 3]    | [fine-grained list]                 | N     |

Total: [product] configurations. Estimated time: [X minutes].
Should I adjust any ranges or add/remove factors?"

### 3.2 — Sweep Implementation

```python
#!/usr/bin/env python3
"""Focused parameter sweep on top factors from Taguchi screening."""
import csv
from multiprocessing import Pool, cpu_count

# Fixed parameters (from Taguchi: best levels for non-swept factors)
FIXED = {
    'factor_D': best_level_D,
    'factor_E': best_level_E,
}

def build_configs():
    """Generate all sweep configurations."""
    configs = []
    for a in FACTOR_A_VALUES:
        for b in FACTOR_B_VALUES:
            for c in FACTOR_C_VALUES:
                configs.append({**FIXED, 'factor_A': a, 'factor_B': b, 'factor_C': c})
    return configs

def run_one(cfg):
    """Run single config. Must be picklable for multiprocessing."""
    try:
        state = build_and_solve(cfg)
        return {**cfg, **extract_metrics(state)}
    except Exception as e:
        return {**cfg, 'converged': False, 'error': str(e)}

def main():
    configs = build_configs()
    print(f"Running {len(configs)} configurations on {cpu_count()} cores...")

    with Pool(cpu_count()) as pool:
        results = []
        for i, r in enumerate(pool.imap_unordered(run_one, configs)):
            results.append(r)
            if (i + 1) % 100 == 0:
                print(f"  {i+1}/{len(configs)} done...")

    # Write CSV
    with open('sweep_results.csv', 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=results[0].keys())
        w.writeheader()
        w.writerows(results)

    # Print top results
    converged = [r for r in results if r.get('converged')]
    by_metric = sorted(converged, key=lambda r: r['primary_metric'], reverse=True)
    print(f"\nTop 5 by primary metric:")
    for r in by_metric[:5]:
        print(f"  {r}")
```

### 3.3 — Reporting

**After the sweep, tell me:**
"Sweep complete. [N] configs, [M]% converged. Top results:

| Rank | [Factor A] | [Factor B] | [Factor C] | [Metric] | [Other] |
|------|-----------|-----------|-----------|----------|---------|
| 1    | ...       | ...       | ...       | ...      | ...     |

Key findings:
- [Factor A] optimal at [value] — because [physics reason]
- [Unexpected discovery about Factor B]
- [Hardware implication]

Should I run a grand sweep covering all use cases?"

---

## PHASE 4: Grand Sweep

### 4.1 — Design

**Ask me:**
"I want to run one comprehensive sweep that covers all use cases.
Here's the design:

**Core sweep:** [N_core] configs
| Factor | Values | Count |
|--------|--------|-------|
| ...    | ...    | ...   |

**Hardware variants:** [N_hw] configs (at a representative subset)
| Variant          | Options    |
|------------------|------------|
| ...              | ...        |

**Use-case specific:** [N_uc] configs
| Use case    | Extra factors                     |
|-------------|-----------------------------------|
| ...         | ...                               |

**Grand total: ~[N] configs. Estimated time: [X hours].**

Every config records ALL metrics. We filter by use case afterward:
- Use case A: filter by [criterion], rank by [metric]
- Use case B: filter by [criterion], rank by [metric]

Does this coverage look right?"

### 4.2 — Output CSV Schema

```
# Grand sweep results — one row per configuration
# Inputs
section, factor_A, factor_B, factor_C, ...

# Primary metrics
primary_metric, secondary_metric, tertiary_metric, ...

# Diagnostics
converged, iterations, max_residual, ...
```

### 4.3 — Reporting Sections

After the grand sweep completes, generate a report with:

1. **Per use case:** Top 30 by primary metric, top 20 by secondary
2. **Hardware head-to-head:** Side-by-side comparison of variant options
3. **Environmental sensitivity:** Best config at each ambient condition
4. **Factor importance:** Which parameter matters most per use case
5. **Build recommendation:** Optimal config with full BOM and instructions

---

## PHASE 5: Experiment Worksheet Design

### 5.1 — Progressive Validation Strategy

**Ask me:**
"I've designed a progression of experiments from simplest to most complex.
Each one validates specific model parameters. If an early experiment fails,
we know exactly which model parameter is wrong.

| Code     | Tests What              | Components Needed        |
|----------|-------------------------|--------------------------|
| EXP-01   | Basic property check    | 1 component + meter      |
| EXP-02   | Single element active   | 1 component + power      |
| EXP-03   | Two elements coupled    | 2 components + interface |
| EXP-04   | Add passive subsystem   | + thermal mass / fluid   |
| EXP-05   | Add active transport    | + pump / fan / actuator  |
| EXP-06   | Multi-element system    | partial assembly         |
| EXP-07   | Full system             | complete prototype       |

Does this progression make sense for your hardware? Which experiments
can you run with what you have right now?"

### 5.2 — Experiment Code Convention

```
CODE = CATEGORY-nUNITS-DETAILS[-VARIANT]

Categories: PROP (property check), SINGLE, PAIR, MULTI, FULL
Units:      1X (one unit), 2XS (two in series), 2XP (two parallel), 5X
Details:    VSWEEP (voltage sweep), STATIC (no flow), FLOW, etc.
Variant:    optional suffix (-INSUL, -NOFLOW, -HIGH-V, etc.)

Examples:
  PROP-OHMS     — resistance check, no power
  SINGLE-VSWEEP — single element, voltage sweep
  PAIR-2XS      — two elements in series
  FULL-5X-FLOW  — full 5-element system with flow
```

### 5.3 — Worksheet Generator

Create `experiments/generate_worksheets.py`:

```python
#!/usr/bin/env python3
"""Generate printable experiment worksheets as HTML files.

Each worksheet has:
  - Experiment code (printed large, top-right corner)
  - Hardware list and setup instructions
  - Safety warnings
  - Step-by-step procedure
  - Model predictions table with blank "Measured" column
  - Diagnostic notes (what to look for, what it means)
  - Free-form observations space

Output: experiments/worksheets/[CODE].html
        experiments/worksheets/all_worksheets.html (combined)
"""

# Import the model's prediction functions
from model_predictions import predict_experiment_01, predict_experiment_02, ...

def html_header(title, code):
    return f"""<!DOCTYPE html>
<html><head><meta charset="utf-8">
<title>{code}: {title}</title>
<style>
  @page {{ margin: 0.5in; }}
  body {{ font-family: 'Courier New', monospace; font-size: 11pt;
          max-width: 7.5in; margin: 0 auto; padding: 0.25in; }}
  h1 {{ font-size: 16pt; border-bottom: 3px solid #000; }}
  .code {{ font-size: 20pt; font-weight: bold; float: right;
           border: 3px solid #000; padding: 4px 12px; }}
  table {{ border-collapse: collapse; width: 100%; }}
  th, td {{ border: 1px solid #000; padding: 3px 6px; text-align: right; }}
  th {{ background: #ddd; text-align: center; }}
  td.blank {{ background: #f8f8f0; min-width: 60px; }}
  .note {{ background: #fff8dc; border: 1px solid #cc9; padding: 6px; }}
  .warn {{ background: #ffe0e0; border: 1px solid #c66; padding: 6px; }}
  .safety {{ background: #e0ffe0; border: 1px solid #6c6; padding: 6px; }}
  .obs {{ border: 1px solid #999; min-height: 80px; padding: 6px; }}
</style></head><body>
<div class="code">{code}</div>
<h1>{title}</h1>
<p>Date: __________ &nbsp; Ambient: ______ &nbsp; Humidity: ______%</p>
"""

def measurements_table(predictions):
    """Generate predicted-vs-measured table from model output."""
    html = """<table>
<tr><th>Parameter</th><th>Predicted</th><th>Measured</th></tr>"""
    for name, value, unit in predictions:
        html += f"""
<tr><td style="text-align:left; font-weight:bold">{name} ({unit})</td>
    <td>{value:.2f}</td><td class="blank">&nbsp;</td></tr>"""
    html += "</table>"
    return html

def gen_experiment(code, title, hardware, safety, procedure,
                   predictions, diagnostics):
    """Generic worksheet generator."""
    html = html_header(title, code)
    html += "<h2>Hardware</h2><ul>"
    for item in hardware:
        html += f"<li>{item}</li>"
    html += "</ul>"

    if safety:
        html += f'<div class="safety"><b>SAFETY:</b> {safety}</div>'

    html += "<h2>Procedure</h2><ol>"
    for step in procedure:
        html += f"<li>{step}</li>"
    html += "</ol>"

    html += "<h2>Measurements</h2>"
    html += measurements_table(predictions)

    html += '<div class="note">'
    for note in diagnostics:
        html += f"{note}<br>"
    html += "</div>"

    html += """<h2>Observations</h2>
<div class="obs">&nbsp;<br>&nbsp;<br>&nbsp;<br></div>
</body></html>"""
    return html
```

### 5.4 — Prediction Functions

Create `experiments/model_predictions.py` (or equivalent):

```python
"""Generate model predictions for each experiment configuration.

This file imports the actual model and runs it at the specific
conditions each experiment will use. When the model is updated,
regenerate worksheets to get updated predictions.
"""
from src.system.solver import solve
from src.constants import HARDWARE_PARAMS

def predict_experiment_01():
    """Predictions for basic property check."""
    return [
        ('Resistance', 0.75, 'ohm'),
    ]

def predict_experiment_02(voltages=[0.75, 1.0, 1.5]):
    """Predictions for single-element voltage sweep."""
    results = []
    for V in voltages:
        state = solve(voltage=V, ...)
        results.append({
            'V': V,
            'predictions': [
                ('Cold side temp', state.T_cold - 273.15, 'C'),
                ('Hot side temp', state.T_hot - 273.15, 'C'),
                ('Current', state.I, 'A'),
            ]
        })
    return results
```

**Key principle:** Predictions come from the model, not from hand
calculations. When the model changes, `python generate_worksheets.py`
regenerates everything automatically.

---

## PHASE 6: Experiment Protocol

### 6.1 — Protocol File

Create `experiments/EXPERIMENT_PROTOCOL.md`:

```markdown
# Experiment Protocol

## Session Resumption

When returning with experimental results, tell the AI:

> I'm working on [PROJECT] at [PATH].
> I have results from experiment [CODE].
> Please read experiments/EXPERIMENT_PROTOCOL.md for context.

## Experiment Codes

| Code      | Description             | Validates          | If Wrong, Adjust           |
|-----------|-------------------------|--------------------|----------------------------|
| PROP-OHMS | Resistance check        | R_internal         | Update constant in src/    |
| SINGLE-V  | Single element, V sweep | Core physics model | Adjust coupling coefficient|
| PAIR-2XS  | Two in series           | Coupling model     | Thermal interface params   |
| ...       | ...                     | ...                | ...                        |

## Completed Experiments

| Code      | Date       | Result                    | Action Taken                |
|-----------|------------|---------------------------|-----------------------------|
| (filled in as experiments are completed)                                         |

## Calibration Priority

When predictions don't match, adjust in this order:
1. Interface/contact parameters (hardest to predict)
2. Convection/transfer coefficients (geometry-dependent)
3. Component properties (usually close to datasheet)
4. Flow/transport characteristics (measure directly)

Never adjust fundamental physics constants.

## Data Entry Format

When reporting results:
> [CODE] Results:
> Ambient: ___
> Time running: ___
> Settings: ___
>
> Measurements:
>   [quantity]: [value] [unit]
>   [quantity]: [value] [unit]
> Notes: [anything unusual]
```

### 6.2 — What the AI Does With Results

When the user returns with experimental data:

1. **Parse** the reported measurements
2. **Compare** each measurement to the model prediction:
   ```
   | Quantity  | Predicted | Measured | Error (%) |
   |-----------|-----------|----------|-----------|
   ```
3. **Classify** errors:
   - < 10%: Validated. No change needed.
   - 10-30%: Acceptable. Note the bias.
   - > 30%: Needs calibration. Identify the constant.
4. **Propose calibration** — which constant to change, new value, rationale
5. **Update the model** if the user approves
6. **Regenerate** worksheets (predictions update automatically)
7. **Recommend** next experiment in the progression
8. **Log** the result in the Completed Experiments table

---

## PHASE 7: Reporting and Build Guide

### 7.1 — SVG Schematics

Generate SVGs for the best configurations from the grand sweep:

```python
"""Generate SVG schematics for best configurations."""
from src.analysis.viz import render_schematic, SVGRenderer

for use_case, config in best_configs.items():
    state = solve(config)

    # System layout schematic
    schematic = render_schematic(state, title=f"Best {use_case}")
    save(f"experiments/best_{use_case}_schematic.svg", schematic)

    # Performance charts
    renderer = SVGRenderer()
    save(f"experiments/best_{use_case}_profile.svg",
         renderer.render_profile(state))
```

### 7.2 — Build Recommendation HTML

Self-contained HTML report with:
- Summary cards (metric, temperature, power for each use case)
- Inline SVG schematics
- Factor importance chart
- Hardware head-to-head table
- Bill of materials with costs
- Step-by-step assembly guide
- Top configurations table from grand sweep
- Model validation status

### 7.3 — Data Archival

```
experiments/
  taguchi/
    [project].tgu                  — array definition
    run_single.py                  — single-point runner
    analyze_results.py             — analysis script
    results.csv                    — raw L27/L81 results
    results_report.html            — analysis report

  [sweep_name]_results.csv         — each sweep's raw data
  grand_sweep_results.csv          — comprehensive results
  build_recommendation.html        — build guide

  worksheets/
    [CODE].html                    — individual worksheets
    all_worksheets.html            — combined for printing

  EXPERIMENT_PROTOCOL.md           — protocol + completed log
  generate_worksheets.py           — worksheet generator
  model_predictions.py             — prediction functions
  generate_best_config_svgs.py     — SVG generator
```

---

## The Dialectic: How Questions Drive the Process

The power of this methodology is the **back-and-forth**. The AI doesn't
just execute — it proposes, asks, listens, and adapts. Key question points:

| Phase | AI Asks | User Decides |
|-------|---------|--------------|
| Factor ID | "Which params to sweep?" | Practical constraints |
| Taguchi | "L27 or L81?" | Time budget |
| Levels | "These ranges cover your hardware?" | Physical limits |
| Screening results | "Factor X dominates. Focus here?" | Domain intuition |
| Sweep design | "These [N] configs, [T] hours?" | Patience budget |
| Grand sweep | "One run, three views?" | Use case definitions |
| Experiment design | "This progression works?" | What hardware you have |
| Worksheet review | "Predictions look reasonable?" | Gut-check from experience |
| Results analysis | "Error is 25% — adjust [param]?" | Accept calibration? |
| Next experiment | "Ready for EXP-03?" | Time + materials |

**Multiple-choice questions** are faster than open-ended ones. When the AI
asks "Should I (a) sweep 5 levels or (b) 9 levels?", you can answer in one
word. This keeps momentum.

---

## Anti-Patterns

1. **Don't full-factorial when Taguchi works.** 9 factors × 3 levels =
   19,683 full factorial. L81 tests 81. Screen first, then focus.

2. **Don't hand-write worksheet predictions.** Generate from code. When
   the model updates, the predictions update automatically.

3. **Don't jump to the full system experiment.** Progressive validation
   localizes errors. If EXP-03 fails, you know which model is wrong.

4. **Don't ignore failed convergence.** If 30% of your sweep didn't
   converge, the solver needs fixing before the results mean anything.

5. **Don't adjust fundamental constants to fit data.** Adjust interface
   parameters and geometry-dependent coefficients. The Seebeck coefficient
   is what it is.

6. **Don't run experiments the model can't predict.** Every measurement
   on the worksheet must have a corresponding model prediction. If the
   model can't predict it, either extend the model first or don't measure it.

7. **Don't skip the steady-state wait.** Transient measurements are harder
   to compare to steady-state predictions. Wait for equilibrium (or model
   the transient explicitly and compare at the same time point).

---

## Checklist

```
[ ] Factors and levels identified
[ ] Taguchi .tgu file created
[ ] Run script (run_single.py) working
[ ] Taguchi screening complete — factor importance ranked
[ ] Focused sweep designed and run
[ ] Grand sweep designed and run (all use cases)
[ ] CSV results archived
[ ] Experiment progression designed (simple → complex)
[ ] Prediction functions written (import the actual model)
[ ] Worksheet generator written
[ ] All worksheets generated from model
[ ] Experiment protocol file created
[ ] First experiment completed
[ ] Predicted vs measured compared
[ ] Model calibrated (if needed)
[ ] Worksheets regenerated with calibrated model
[ ] Next experiment run
[ ] Build recommendation report generated
[ ] SVGs generated for best configurations
[ ] Completed experiments logged in protocol
```

---

*This methodology was developed through a peltier cascade cooler project
that built a 6,420-point parameter space, validated against hardware, and
iterated through the model-experiment loop. The same process applies to
any physical system: battery cells, RF circuits, chemical reactors,
optical systems, fluid networks, structural assemblies — anywhere theory
meets hardware.*
