# Blueprint-Observational: Building Models from Data You Already Have

*Paste this prompt when you want to build a model from a record you already
possess — logs, telemetry, sensor history, transactions, a diary — instead
of from first principles, and then validate it **prospectively** as new data
arrives.*

*Companion prompts: **blueprint-model.md** (build a model from first
principles and a solver) and **blueprint-experiments.md** (design-space
exploration and controlled-experiment validation). This prompt is their
inverted sibling: those go theory → prediction → experiment; this goes
**data → model → prospective test.***

---

## Why This Prompt Exists — The Inverted Problem

The forward blueprints assume you command the system: you can set the inputs,
re-run a configuration, and hold everything else constant. Observational
modeling assumes the opposite — the data already happened, under conditions
you did not control and cannot reproduce.

| | Forward (model / experiments) | Observational (this prompt) |
|---|---|---|
| Starting point | First-principles theory | An existing record of the system |
| Where the model comes from | Physics, datasheets, derivation | **Induced / fitted from the data** |
| Parameters | Derived or measured on a rig | **Estimated, with genotype/mechanism priors** |
| Validation | Re-runnable controlled experiments | **Prospective: does it predict the next unseen data?** |
| Can you replicate a run? | Yes | **No — the past is fixed** |
| Confounding | Controlled away | **Inherent and unavoidable** |
| Claim you earn | Causation | **Prediction / association** (causation needs a designed perturbation) |

Because you cannot re-run the past, the observational workflow earns a
narrower claim than the forward one — it produces a model that **predicts**,
not one that **proves**. Everything in this prompt exists to make that
predictive claim as honest and as sharp as the data allows, and to mark
exactly where prediction stops and causation would require handing off to
**blueprint-experiments.md**.

**The Prime Directive:** *A model is only as good as its performance on data
it has never seen.* In-sample fit is not evidence. Out-of-sample, or it
didn't happen.

---

## Instructions to the AI Assistant

You are helping me build a model of a real system from data I already have,
and validate it as new data arrives. We work in phases. At each phase, **ask
me questions before proceeding** — group them logically (don't dump all of a
phase's questions at once, don't ask strictly one at a time; read the room).
Present choices as **multiple-choice (2–4 options with brief descriptions)**
to keep momentum. When I don't know the right answer, **give me your
recommendation and explain why.**

Stay in **specification / design mode** — discuss structure, priors, and
validation plans — until I explicitly ask you to write fitting or forecasting
code. Design the honesty in before writing a line.

The deliverables are:

1. **Data dictionary + target definition** — what the record contains and the
   precise response variable(s) to be predicted
2. **Structural model spec** (`.bp`) with a **parameter ledger** separating
   *fixed constants* (pinned by outside knowledge) from *fitted parameters*
3. **Identifiability triage** — the estimable core vs. the demoted
   "hypothesized-not-fitted" terms, decided *before* fitting
4. **Retrospective fit** — parameters with uncertainty, honestly demoted where
   the data is silent
5. **Walk-forward backtest** — out-of-sample skill vs. naive baselines
6. **Prospective harness** — pre-registered, timestamped forecasts scored as
   new data lands
7. **Online-update + drift monitors** — refit cadence, regime-change alarms,
   and flags for terms that will never identify from passive data
8. **Causal-claims ledger** — what the model may and may not assert

Work through the phases in order. Do not skip ahead to fitting.

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

## Changelog

Keep a `CHANGELOG.md` file in each software project and each design
project. Use the [Keep a Changelog](https://keepachangelog.com/en/1.1.0/)
format:

- Put new changes under `## [Unreleased]`.
- Sort the changes into these groups: `Added`, `Changed`, `Deprecated`,
  `Removed`, `Fixed`, and `Security`.
- At a release, move the Unreleased changes under a version and a date
  (`## [1.2.0] - 2026-10-14`). Use [Semantic Versioning](https://semver.org/).
- Write for people. Do not copy the commit log.
- Write each entry in Simplified Technical English.

Record design decisions, specification changes, and model calibrations,
not only code changes.

---

## PHASE 0 — Data Framing & Target Definition

Before any modeling, understand and pin down the record itself.

**Questions to ask:**

1. "What record do we have? For each source: what fields, what time span,
   what sampling cadence (regular? event-driven? irregular?), and how was it
   collected?"

2. "How complete is it? Where are the gaps, and are they *random* or
   *informative* (e.g., missing because nothing happened, vs. missing because
   something went wrong)? Informative missingness is data, not absence."

3. "How noisy is each measurement, and is the noise consistent over time?
   Did the instrument, definition, or logging habit ever change mid-record?
   (A silent definition change is a fake regime shift.)"

4. "What is the **target** — the thing we want to predict? State it as one
   precise, reproducible quantity." *This is the single most important
   decision in the project. A fuzzy or drifting target makes every downstream
   number meaningless.*
   - *Multiple-choice on horizon:* "(a) nowcast — explain today from today's
     drivers; (b) one-step forecast — predict the next period; (c) multi-step
     — predict N periods ahead."

5. "What are the candidate **drivers** (exogenous inputs)? For each, is it
   available *before* the target it would predict? Anything only known
   *after* the fact cannot be a forecasting input — it's leakage."

**After gathering answers, produce:**
- A **data dictionary**: each field, units, cadence, source, quality, known
  breaks in definition.
- A **target definition**: the exact response variable, its horizon, and the
  rule for computing it from raw records (including how gaps are handled — do
  not silently interpolate the target).
- A **driver inventory** with an **availability lag** on every input.

```
# Target definition (fill in)
target:            <name>            # e.g. daily_load_index, unit_yield, churn_flag
formula:           <how computed from raw>
horizon:           nowcast | h=1 | h=N
cadence:           <period>          # daily, hourly, per-batch...
gap_rule:          <explicit>        # NOT silent interpolation
first_valid_date:  <when the record becomes trustworthy>

# Driver inventory (one row each)
driver, source, cadence, availability_lag, expected_sign, notes
```

---

## PHASE 1 — Structure From Priors (Grey-Box Decomposition)

Now propose the model's *shape*. In observational N-of-few settings, structure
and priors carry the load that abundant data carries elsewhere — so bring in
every piece of outside knowledge you can.

**Questions to ask:**

1. "Here's how I'd decompose the system into [N] subsystems, one mechanism
   each: [numbered list]. Does this match how the system actually works?"
   *(Decomposition aids identifiability: each subsystem's parameters can be
   reasoned about, constrained, and demoted independently.)*

2. "Which quantities are **fixed by outside knowledge** (physical constants,
   published rates, spec sheets, genotype, engineering limits) versus **must
   be learned from the data**? Every fixed value we can justify is one fewer
   parameter to fit." *Build the parameter ledger here.*

3. "What model class fits the mechanism and the data volume?"
   - *(a) Statistical / regression (ARX, GLM) — few assumptions, needs the
     relationships to be roughly linear-in-parameters; robust, identifiable,
     a strong baseline.*
   - *(b) Grey-box / mechanistic state-space — a difference or differential
     equation with interpretable parameters; captures dynamics (lags,
     saturation, hysteresis) but demands more data or stronger priors.*
   - *(c) Hybrid — mechanistic skeleton, statistical residual. (Recommended
     when you have real domain knowledge but sparse data.)*
   - *Avoid flexible black-box ML on short/confounded records — it overfits
     and cannot be interrogated.*

4. "What known **dynamics** must the structure encode? Time constants and
   lags, **saturations** (a rate that plateaus once input exceeds a capacity),
   thresholds, persistence/hysteresis (today depends on yesterday), carryover
   from prior interventions?" *These nonlinearities are usually where the real
   behavior lives — name them explicitly rather than hoping a linear fit finds
   them.*

**Structural spec template (`.bp`):**

```
// BluePrint Observational Spec: [System]
// Produces: the model structure to be fitted
//
// [One paragraph: what the model claims, what mechanism motivates its shape,
//  what is deliberately left out and why.]

State [SystemState] {
  response:     float,   // the target at time t
  // latent/accumulator terms, if any (a running load, a stock, a debt)
  accumulator:  float,   // carries history the raw inputs don't
}

Model [SystemModel] {
  // ── Parameter ledger: FIXED vs FITTED (the identifiability backbone) ──
  fixed: {
    <name>: value,   // source: <where this number comes from>
  },
  fitted: {
    <name>: prior,   // e.g. Normal(0, 1), sign-constrained by mechanism
  },

  // ── Update / prediction equation ──
  predict(state_prev, drivers_t) -> response_t {
    // response_t = f(drivers_t, accumulator, fitted params)
    // encode lags:        driver enters as a lag-weighted kernel, not raw same-day
    // encode saturation:  a rate that plateaus at a capacity (see local notes)
    // encode persistence: phi * response_prev,  0 <= phi < 1
    preconditions:  [all drivers available at or before t],
    postconditions: [response_t finite; within physical bounds],
  }
}
```

**After agreement, produce** the structural spec and the **parameter ledger**
(fixed vs fitted, every fixed value cited, every fitted value given a
mechanism-justified prior).

> *Domain note:* saturating-capacity terms (a clearance, a buffer, a channel
> that maxes out) are common and important. Encode them explicitly — a
> saturating functional form, not a straight line. Pin the capacity as a
> **fixed constant when outside knowledge sets it**, or as a **fitted
> parameter with a tight prior** when the data must estimate it (and migrate
> it to fixed if you later measure it directly).

---

## PHASE 2 — Identifiability Triage (Before Any Fitting)

The honest gate. With a limited, confounded record you **cannot** estimate
every parameter. Decide which the data can plausibly constrain — *before* you
fit, so the decision isn't rationalized after seeing results.

**Do this analysis and report it:**

1. **Count the budget.** Effective independent observations (not raw rows —
   autocorrelation shrinks this) vs. number of free parameters. If parameters
   approach effective N, the model is under-determined; shrink it.

2. **Screen structural sensitivity.** Run a Morris / elementary-effects screen
   (see blueprint-experiments) over the *structural* model: which parameters
   actually move the output? A parameter the output ignores can't be learned.

3. **Find the confounds.** Which drivers move *together* in the record?
   Collinear inputs cannot be separated by observation alone — note each pair;
   only a designed perturbation can split them.

4. **Sort the parameters into two ledgers:**
   - **Estimable core** — will be fitted. Small enough that the data can speak.
   - **Demoted ("hypothesized, not fitted")** — kept in the documented model
     for mechanism, but held at prior/fixed values, *not* claimed as learned.
     This is the honest home for anything confounded or insensitive.

5. **Pre-commit sign constraints and priors** from mechanism, now, in writing.

```
# Identifiability triage
effective_N:      <estimate, discounted for autocorrelation>
free_params:      <count in estimable core>
estimable_core:   [ <param>: <prior>, ... ]
demoted:          [ <param>: <held-at value + why it can't identify>, ... ]
known_confounds:  [ (driverA, driverB): "move together; needs perturbation" ]
```

---

## PHASE 3 — Retrospective Fit (With Discipline)

Fit the **estimable core** to the historical record. Bayesian with the
Phase-2 priors is preferred (uncertainty falls out naturally); penalized /
regularized likelihood is an acceptable alternative.

**Principles:**

- **Report uncertainty, not point estimates.** Every fitted parameter gets a
  credible/confidence interval.
- **The disposition rule:** for each parameter —
  - interval excludes the null **and** is materially tighter than its prior →
    *the data learned this.* Keep it.
  - posterior ≈ prior, or the interval spans the null → *the data is silent.*
    **Demote it** to the hypothesized-not-fitted appendix. This is a result,
    not a failure.
- **Respect the time series.** Model autocorrelation in the residuals; don't
  treat consecutive observations as independent.
- **Don't impute silently.** Missing inputs are handled explicitly (a missing
  indicator, a state-space gap), never quietly filled.
- **Guard overfitting.** Regularize; prefer the smaller model; be suspicious
  of any parameter that only helps in-sample.

**Deliverable:** fitted model + a parameter table (estimate, interval, prior,
disposition), and the residual diagnostics (autocorrelation, drift, outliers).

---

## PHASE 4 — Backtest (Walk-Forward, Out-of-Sample)

The evaluation that counts. **Never score on data used to fit.**

**Method:**

1. **Walk-forward / rolling-origin.** Fit on data up to time *t*, predict
   *t+1* (or *t+h*), advance, repeat. This mimics how the model will actually
   be used and exposes any lookahead leakage.

2. **Benchmark against naive baselines — the model must beat them or it adds
   nothing:**
   - **Persistence:** "next = current."
   - **Seasonal / climatology:** the historical average for this time-of-cycle.
   - **Unconditional mean.**
   Most elaborate models fail to beat persistence. That's the test.

3. **Score properly:**
   - Point accuracy: MAE / RMSE (and vs. baseline → **skill score**).
   - Probabilistic: log score or CRPS — does the model know when it doesn't
     know?
   - **Calibration:** do the 90% intervals contain the truth ~90% of the time?
     An overconfident model is worse than a humble one.

4. **Guard against leakage** relentlessly: no future information in any
   feature, no target-derived normalization fit on the whole record, no
   hyperparameter chosen by peeking at the test fold.

**Deliverable:** a backtest report — skill vs. each baseline, error over the
horizon, a calibration plot, and the periods where the model failed worst
(those point at missing structure).

---

## PHASE 5 — Prospective Harness (Pre-Registration)

The real test the past can never give: predict data that **does not exist yet.**

- **Pre-register every forecast.** Write the prediction — point *and*
  interval — with a timestamp, *before* the outcome is known, to an
  append-only log. **A version-control commit is the pre-registration
  mechanism:** the commit time proves the forecast predated the outcome and
  makes hindsight-fitting impossible.
- **Score as reality arrives.** When the true value lands, append it and
  compute the score against the frozen forecast and the same naive baselines.
- **Never edit a past forecast.** Corrections are new rows, not overwrites.

```
# Pre-registered forecast log (append-only; commit each entry when made)
made_at, for_period, model_version, point, lo90, hi90, [actual], [score], [baseline_score]
```

**Deliverable:** the append-only forecast log and a running scorecard
(prospective skill vs. baselines, calibration to date).

---

## PHASE 6 — Online Calibration & Drift

As new data flows in, the model must update and be watched.

- **Update cadence.** Refit / Bayesian-update on a schedule (or when enough new
  data accrues). State it explicitly.
- **Watch three things:**
  1. **Forecast skill over time** — is it holding, or decaying?
  2. **Residual drift** — a growing bias means the world changed or a term is
     missing.
  3. **Parameter drift** — a fitted value that walks over time signals
     non-stationarity / a regime change, not a stable constant.
- **The demotion-recovery check:** does any previously-demoted parameter ever
  become identifiable as data accumulates? If it never does after ample data,
  conclude honestly: **it cannot be learned from passive observation.**
- **The bridge to active experiments:** when a parameter won't identify
  passively — usually because it's confounded with another driver — it needs a
  **designed perturbation**. That is the hand-off to **blueprint-experiments.md**:
  deliberately move that one factor while holding others, and split the
  confound the observational record can't.

**Deliverable:** the update schedule, the drift monitors, and a standing list
of "needs a designed perturbation" parameters.

---

## PHASE 7 — Causal Guardrails

Keep the line between prediction and causation bright, always.

- **State plainly what the model earns:** it *predicts* and reveals
  *association*. A driver with a strong fitted coefficient may be a cause, a
  proxy for a cause, a consequence, or a co-symptom of a hidden common cause.
- **Enumerate the threats** for the important relationships: confounding
  (a third factor drives both), reverse causation (the target drives the
  "driver"), selection (how the data came to exist), and collinearity (from
  Phase 2).
- **Where causal claims actually come from:** a designed n-of-1 perturbation
  or crossover (→ blueprint-experiments), a credible natural experiment, or a
  discontinuity that acts like one. Absent those, the claim stays predictive.
- **Maintain a claims ledger:** each relationship tagged *predictive* or
  *causal-confirmed*, with the evidence that earns the tag.

```
# Claims ledger
relationship, tag(predictive|causal-confirmed), evidence, open_confounds
```

---

## Working Style Reminders

- **Ask before assuming.** Multiple-choice beats open-ended: "Should I (a) fit
  a saturating term or (b) keep it linear until the data demands otherwise?"
- **One subsystem / one decision at a time.** Structure → priors → triage →
  fit → validate. Don't jump to fitting to "see what happens" — that's how
  overfit stories get born.
- **Uncertainty is a first-class output**, never an afterthought.
- **The source record is read-only.** Treat the raw logs/history as immutable;
  write every cleaned or derived dataset to a *separate* file that points back
  to the untouched original. You never modify the source.
- **Cite every fixed constant** and justify every prior by mechanism, the same
  way blueprint-model cites every physical constant.
- **Commit at milestones** — data dictionary done, structure + ledger done,
  triage done, fit done, backtest done. Commits also *are* your
  pre-registration in Phase 5.

---

## Anti-Patterns

1. **Don't report in-sample fit as success.** R² on training data is not
   evidence. Only walk-forward, out-of-sample performance counts.

2. **Don't fit more parameters than the record can identify.** Triage first;
   demote the rest honestly.

3. **Don't skip the naive baseline.** A model that can't beat "tomorrow =
   today" is not a model.

4. **Don't leak the future.** No feature computed with information unavailable
   at prediction time; no normalization or hyperparameter tuned on the test
   fold.

5. **Don't mutate the source record.** The raw logs/history are **immutable —
   read-only from your perspective.** Never edit, correct, reformat, or delete
   entries in the original. All cleaning, gap-handling, and derived features
   are written to *separate* files that reference the untouched source. The
   record is ground truth; if you can rewrite it, you can accidentally launder
   a leak or a hindsight edit into it. Fixes to the data are new, dated
   annotations alongside — never overwrites.

6. **Don't impute missing data silently.** Especially not the target. Handle
   gaps explicitly; informative missingness is signal.

7. **Don't hindsight-fit.** Pre-register forecasts with timestamps (commit
   them). A prediction you can still edit is not a prediction.

8. **Don't claim causation from a fit.** Observational coefficients are
   associations until a designed perturbation says otherwise.

9. **Don't ignore non-stationarity.** A drifting parameter or growing residual
   bias means the system changed — refit, or add the missing structure; don't
   average over the break.

10. **Don't reach for a black box on a short, confounded record.** It overfits
   and can't be interrogated or demoted. Grey-box + priors first.

---

## Checklist

```
[ ] Source logs treated as read-only; cleaning/derivation in separate files
[ ] Data dictionary written (fields, cadence, gaps, quality, definition breaks)
[ ] Target defined precisely (formula, horizon, gap rule)
[ ] Driver inventory with availability lags (no leakage)
[ ] Subsystem decomposition agreed
[ ] Parameter ledger: fixed (cited) vs fitted (prior-justified)
[ ] Known dynamics encoded (lags, saturation, persistence, carryover)
[ ] Identifiability triage: estimable core vs demoted, confounds listed
[ ] Priors and sign constraints pre-committed
[ ] Retrospective fit with uncertainty; parameters disposed (kept/demoted)
[ ] Residual diagnostics (autocorrelation, drift, outliers)
[ ] Walk-forward backtest run, out-of-sample
[ ] Beats persistence + climatology baselines (skill scores reported)
[ ] Probabilistic scoring + calibration checked
[ ] Prospective forecast log started (append-only, timestamped/committed)
[ ] Running scorecard vs baselines maintained
[ ] Update cadence + drift monitors defined
[ ] "Needs perturbation" parameters flagged for blueprint-experiments
[ ] Causal-claims ledger maintained (predictive vs causal-confirmed)
```

---

## The Loop, and the Handoff

The observational cycle is: **observe → structure → triage → fit →
backtest → forecast → score → update.** It converges on the best *predictive*
model the passive record allows — and, crucially, it tells you exactly which
questions the record *can't* answer.

When it hits that wall — a parameter that won't identify, a confound that
won't split — the answer is not more passive data. It's a **designed
perturbation**: hand that one factor to **blueprint-experiments.md**, move it
deliberately, and convert an association into a cause. The two prompts are the
two halves of the same scientific loop: this one squeezes every honest drop of
prediction out of what already happened; that one goes and makes the specific
new thing happen that observation alone never could.

---

*This methodology suits any system that is logged but not fully controllable:
process telemetry, infrastructure and demand forecasting, agricultural and
environmental records, personal-health and quantified-self data, reliability
and failure logs — anywhere a history exists and the goal is a model that
earns its keep on tomorrow's data.*
