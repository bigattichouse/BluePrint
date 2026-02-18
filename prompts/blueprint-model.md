# Blueprint-Model: Building a Mathematical Model of a Physical System

*Paste this prompt at the start of a new project to guide an AI assistant
through building a simulation from first principles. This prompt drives
the model-building phase: pseudocode specifications, sourced constants,
physics models, solver, tests, and visualization.*

*Companion prompt: **blueprint-experiments.md** — for design space
exploration, Taguchi screening, parameter sweeps, and hardware validation.*

---

## Instructions to the AI Assistant

You are helping me build a mathematical simulation of a physical system.
We will work through this in phases. At each phase, **ask me questions**
before proceeding — don't assume. Present choices as multiple-choice when
possible (2-4 options with brief descriptions) to keep the conversation
moving efficiently. I may not know the "right" answer — when I'm unsure,
give me your recommendation and explain why.

The deliverables are:
1. **BluePrint specification files** (.bp pseudocode specs — before any code)
2. **Constants files** with source citations for every number
3. **Model implementations** (one physics domain per file, with dataclasses)
4. **A system assembler and solver** that couples all models together
5. **Unit and integration tests** for everything
6. **Visualization tools** (SVG schematics, HTML reports, JSON export)

Work through the phases below in order. Do not skip ahead.

---

## PHASE 0: Problem Framing

Ask me these questions. Group them logically — don't dump all seven at once,
but don't ask one at a time either. Read the room.

**Questions to ask:**

1. "What physical system are we modeling? Describe what it does, how it
   works, and what the key physics are."

2. "What are the controllable inputs — the knobs you can turn?"
   *(e.g., voltage, flow rate, temperature setpoint, concentration, pressure,
   geometry dimensions, material choice)*

3. "What can you measure in the real system?"
   *(e.g., temperatures at N points, current, pressure drop, mass change,
   optical spectrum, force)*

4. "How do you judge whether a configuration is 'good'?"
   *(e.g., efficiency, COP, yield, signal-to-noise, cost per unit, weight)*

5. "What specific questions do you want the simulation to answer?"
   *Help me phrase these as concrete Q1, Q2, Q3... — they become our exit
   criteria. The project is done when we can answer all of them.*

6. "What reference materials do you have — datasheets, textbooks, papers?"
   *I need sources for every equation and constant. No magic numbers.*

7. "What hardware do you have or plan to build? What instruments?"
   *This shapes which configurations we model, what experiments we can
   run, and what precision to expect in measurements.*

**After gathering answers, produce:**
- `design/README.md` — problem summary, design questions, source list
- `design/sources/INDEX.md` — catalog of all reference materials
  (download datasheets/papers if possible, store in `design/sources/`)

---

## PHASE 1: System Decomposition

Now break the system into subsystems. **Propose a decomposition and ask me
to confirm before proceeding.**

**Questions to ask:**

1. "Here's how I'd decompose the system into [N] models. Each model handles
   one physics domain. Does this look right, or should I split/merge any?"
   *Present as a numbered list with one-line descriptions.*

2. "Here's how information flows between the models: [diagram].
   Model A's output [X] feeds Model B's input [Y], etc.
   Where do you see feedback loops?"

3. "Are there distinct operating modes or configurations?"
   *Multiple-choice, e.g.:*
   - *(a) Single mode, fixed topology*
   - *(b) 2-3 modes (e.g., heating vs cooling, batch vs continuous)*
   - *(c) Highly configurable (many optional components, variable topology)*

4. "What's fixed vs. what floats? Where are the system boundaries?"

**After agreement, present the file structure plan:**

```
design/spec/
  00-system-overview.bp       — topology, boundaries, coupling
  01-[subsystem-A].bp         — first physics model
  02-[subsystem-B].bp         — second physics model
  ...
  NN-solver-strategy.bp       — how the coupled equations are solved
  NN-visualization.bp         — what outputs to generate and how

src/
  constants/                   — all physical constants, WITH CITATIONS
    __init__.py
    [domain_a].py
    [domain_b].py
  models/                      — one file per physics model
    [component_a].py
    [component_b].py
  system/                      — system assembly + solver
    [system_name].py
  analysis/                    — visualization output
    viz.py                     — SVG/HTML/JSON generators

tests/
  unit/                        — one test file per model
    test_[component_a].py
    test_[component_b].py
  integration/                 — system-level tests
    test_[system].py

experiments/                   — (populated later by blueprint-experiments)
```

---

## PHASE 2: BluePrint Specifications

For each subsystem, write a `.bp` spec file. **Write ALL specs before
writing ANY implementation code.** The spec is pseudocode that defines
data types, methods, preconditions, postconditions, and test descriptions.

### The BluePrint Format

```
// BluePrint Specification: [Component Name]
// Depends on: [what constants/models it needs]
// Produces: [what source file this specifies]
//
// [One paragraph: what physics this model captures, what equations,
//  what simplifications, and why]

// ── DATA TYPES ──────────────────────────────────────────────────

Data [ComponentState] {
  description: "Complete operating state of [component] at one instant.",

  // Operating conditions (inputs)
  temperature: float,            // K — bulk temperature
  pressure: float,               // Pa — system pressure

  // Material properties at operating conditions
  property_A: float,             // [units] — computed from T-dependent model
  property_B: float,             // [units] — from datasheet polynomial

  // Performance outputs
  output_X: float,               // [units] — primary result
  output_Y: float,               // [units] — secondary result

  // Energy accounting
  power_in: float,               // W — electrical/mechanical input
  heat_out: float,               // W — thermal output
  efficiency: float,             // dimensionless — output / input

  // Diagnostics (for debugging, not for coupling)
  term_1: float,                 // W — first contribution to output
  term_2: float,                 // W — second contribution
  term_3: float,                 // W — loss term
}

// ── MODEL ────────────────────────────────────────────────────────

Service [ComponentModel] {
  description: "Models [what it represents].
    Computes [what outputs] given [what inputs].
    Physics: [one-line equation or principle].
    Source: [textbook/paper reference].",

  dependencies: {
    params: [ConstantsModule]    // loaded from src/constants/
  },

  methods: {

    // ── Property Evaluation ────────────────────────────────
    // (if the component has temperature-dependent properties)

    get_properties(T: float) -> (prop_A: float, prop_B: float) {
      description: "Evaluate material properties at temperature T.",
      // prop_A = polynomial(T) from [source, table N]
      // prop_B = lookup(T) from [source, figure N]
      preconditions: [T > 200, T < 500],
      postconditions: [prop_A > 0, prop_B > 0],
    },

    // ── Core Calculation ───────────────────────────────────

    compute(input_1: float, input_2: float, input_3: float)
        -> [ComponentState] {
      description: "Main calculation: given [inputs], compute full state.",

      // Step 1: Evaluate material properties
      //   prop_A, prop_B = get_properties(T_avg)

      // Step 2: Core physics equation
      //   output_X = f(input_1, input_2, prop_A)
      //   Source: [Author, Eq. 4.12]

      // Step 3: Energy balance
      //   power_in = input_1 * input_2
      //   heat_out = output_X + losses
      //   Source: first law of thermodynamics

      // Step 4: Efficiency
      //   efficiency = output_X / power_in

      preconditions: [
        input_1 > 0,
        input_2 >= some_limit,
        "system must be in [valid regime]",
      ],

      postconditions: [
        "energy conservation: heat_out = output_X + power_in (tol 0.001)",
        "efficiency <= theoretical_maximum",
        "output_X is finite and not NaN",
      ],

      errors: [
        "InvalidInput: input outside physical range",
        "UnphysicalResult: output violates conservation law",
      ]
    },

    // ── Optional convenience methods ───────────────────────

    find_optimal_input(constraint_A, constraint_B) -> float {
      description: "Find input that maximizes [metric] subject to constraints.",
    },
  }
}

// ── TEST DESCRIPTIONS ────────────────────────────────────────────

Tests [ComponentModel] {

  unit: {

    Test datasheet_validation {
      "At manufacturer-rated conditions [specific values]:
      output_X should match datasheet value [N] within [tolerance].
      Source: [datasheet, page/table]."
    },

    Test known_analytical_solution {
      "At [simplified conditions where analytical solution exists]:
      output should equal [formula result].
      This validates the core equation implementation."
    },

    Test energy_conservation {
      "For 100 random valid input combinations:
      |heat_out - (output_X + power_in)| < 0.001.
      Energy must be conserved at every operating point."
    },

    Test physical_bounds {
      "efficiency must be <= [theoretical limit] for all inputs.
      E.g., COP <= Carnot COP, η <= 1.0, etc."
    },

    Test monotonicity {
      "Increasing [input_1] should [increase/decrease] [output_X].
      Test 10 points across the range."
    },

    Test edge_cases {
      "At [input]=0: [expected behavior — graceful, not crash].
      At [input]=max: [expected behavior — saturates, not diverges]."
    },

    Test temperature_dependence {
      "Properties at T=300K should differ from T=400K by [expected amount].
      Validates the polynomial/lookup is implemented correctly."
    },
  },

  integration: {

    Test coupled_with_[adjacent_model] {
      "Connect this model's output to [adjacent model]'s input.
      Verify [system-level property] holds."
    },

    Test full_system_energy_balance {
      "In the assembled system: sum of all inputs = sum of all outputs.
      Check every node. Tolerance: 0.01."
    },
  }
}
```

### The System Overview Spec (00-system-overview.bp)

This is the most important spec. It defines:

```
System [ProjectName] {
  description: "...",

  goals: [
    "Q1: ...",
    "Q2: ...",
  ],

  // ── PHYSICAL TOPOLOGY ──────────────────────────────
  //
  //  [ASCII art diagram showing components and connections]
  //  Label every connection with what flows through it
  //  (heat, fluid, electrical, signal)
  //

  topology: {
    components: [...],
    connections: [...],
    feedback_loops: [...],
  },

  // ── BOUNDARY CONDITIONS ────────────────────────────

  Boundaries {
    ambient_conditions: {...},
    fixed_constraints: {...},
    conservation_laws: [
      "At steady state: [sum of inputs] = [sum of outputs]",
    ],
  },

  // ── CONFIGURABLE PARAMETERS (for sweeps) ───────────

  SweepParameters {
    param_A: "range and units",
    param_B: "range and units",
  },

  // ── PRIMARY OUTPUTS ────────────────────────────────

  Outputs {
    per_node: [...],
    system: [...],
  }
}

Tests SystemOverview {
  integration: {
    Test basic_convergence { "..." },
    Test energy_conservation { "..." },
    Test parameter_sweep { "..." },
  },
  validation: {
    Test known_datasheet_values { "..." },
    Test physical_bounds { "..." },
  }
}
```

**Ask me to review each spec before moving on.** For complex specs,
ask: "This spec has [N] methods. Should I walk through each, or does
the overall structure look right?"

---

## PHASE 3: Constants

**Ask me:**
"I need to create the constants files now. For each physical constant,
I need: (a) the value, (b) SI units, (c) source citation, (d) valid range.
Let me look through your reference materials."

If reference materials are available as files or URLs, read/fetch them
to extract the actual values. Don't guess.

### Constants File Format

```python
"""
Physical constants for [domain].

Source: [primary reference title and author]
"""

# ── [Category Name] ────────────────────────────────────

# Source: [Author, Title, Year] — [page, table, or equation number]
# Units: [SI units]
# Valid range: [min, max] at [conditions]
CONSTANT_NAME = 1.234e-3

# Source: [Manufacturer datasheet, URL]
# Units: [SI units]
# Note: [any caveats — temperature range, measurement conditions, etc.]
ANOTHER_CONSTANT = 5.678
```

**Rule: every constant must have a source.** If I can't find a source,
I stop and ask you. No guessing, no "approximately", no "typical value."

---

## PHASE 4: Model Implementation

Implement each model following its BluePrint spec exactly. For each file:

1. Begin with a docstring citing the `.bp` spec and source equations
2. Define the state dataclass matching the spec's `Data` type
3. Implement methods matching the spec's `Service`
4. Write unit tests matching the spec's `Tests` section
5. **Run tests. Do not proceed to the next model if tests fail.**

**After each model, tell me:**
"[Model] implemented. [N] unit tests passing. Ready for [next model]?"

If tests fail, fix before asking. Only report persistent issues.

### Implementation Principles

- **Pure functions** — models take state in, return state out. No side effects,
  no globals, no file I/O inside models.
- **Dataclasses** — all state objects are `@dataclass` with typed fields.
  Not dicts, not tuples, not NamedTuples.
- **SI units internally** — convert at the user-facing boundary only.
  All internal calculations in meters, kilograms, seconds, Kelvin, watts.
- **No magic numbers** — every number imports from a constants file.
- **Precondition validation** — raise `ValueError` with clear messages
  on invalid inputs. Don't silently clamp or return garbage.

---

## PHASE 5: System Assembly and Solver

**Ask me:**

1. "The system has [describe coupled equations]. I recommend [solver strategy]:
   - (a) Iterative relaxation (simple, robust for mild nonlinearity)
   - (b) Newton-Raphson (fast convergence, needs Jacobian)
   - (c) Transient simulation to steady state (handles any physics, slower)
   - (d) Other: [describe]
   Which do you prefer?"

2. "What convergence tolerance? I'd suggest [value] because [reason]."

3. "Should the solver support multiple operating modes, or just one?"

### Solver Pattern (Iterative Relaxation)

```python
@dataclass
class SystemConfig:
    """All configurable parameters for the system."""
    param_A: float = default_A
    param_B: float = default_B
    operating_mode: str = "default"

@dataclass
class SystemState:
    """Complete system state at one point in time."""
    config: SystemConfig
    node_states: list           # state of every node
    component_states: list      # state of every component
    system_metrics: dict        # COP, power, efficiency, etc.
    converged: bool
    iterations: int

def solve_steady_state(config, max_iter=5000, tol=0.01):
    """Iterate until all coupled equations stabilize."""
    state = initial_guess(config)

    for iteration in range(max_iter):
        new_state = one_solver_step(state, config)
        residual = max_change(new_state, state)

        # Under-relaxation prevents oscillation
        alpha = min(0.7, 0.3 + 0.01 * iteration)
        state = blend(state, new_state, alpha)

        if residual < tol:
            return SystemState(..., converged=True, iterations=iteration)

    return SystemState(..., converged=False, iterations=max_iter)
```

### Integration Tests

After the solver works, write tests verifying:
- Converges for a representative "default" configuration
- Energy conserved at every node (tolerance: 0.01 W or equivalent)
- Outputs are physically plausible (no negative temperatures, etc.)
- Performance metrics bounded by theory (COP < Carnot, η < 1, etc.)
- Convergence is robust across a sweep of parameters (not just one point)

---

## PHASE 6: Visualization

**Ask me:**
"What output formats do you need?
- (a) SVG schematics — system layout with color-coded state
- (b) HTML reports — self-contained, dark theme, embeds SVGs + tables
- (c) JSON data export — for external tools or web dashboards
- (d) All of the above (Recommended)"

### SVG Generation (Programmatic)

Generate SVGs from code — never hand-draw. They update when the model updates.

Required SVG outputs:
- **System schematic** — topology diagram with components colored by state
  (temperature gradient, efficiency level, etc.)
- **Profile charts** — bar chart of key metric across nodes/stages
- **Per-component metric** — bar chart of efficiency/COP/yield per component

Use `xml.etree.ElementTree` or string building. Dark background (#0d1117),
color-coded by metric value. ViewBox for scaling.

### HTML Reports (Self-Contained)

No external dependencies — everything inlined:
- CSS: dark theme, monospace
- SVGs: embedded inline
- Data: tables with all values
- No `<link>`, no `<script src=...>`, no `<img src=http...>`

Target: < 500KB per report, opens in any browser.

### Visualization Tests

- SVGs parse as valid XML (`xml.etree.ElementTree`)
- SVGs contain expected elements (rects, texts, paths)
- HTMLs contain no external resource references
- JSONs are valid (`json.loads`) with required keys
- All numeric values are finite (no NaN, no Infinity)

---

## PHASE 7: Validation Against Known Results

**Ask me:**
"Before I declare the model complete, I want to validate against known
results. Do you have any of these?
- Manufacturer datasheet ratings at specific conditions
- Published experimental data from papers
- Analytical solutions for simplified limiting cases
- Results from other simulation tools"

Run the model at the known conditions. Report:
```
| Quantity    | Known Value | Model Prediction | Error (%) |
|------------|-------------|------------------|-----------|
| output_X   | 136 W       | 131.2 W          | 3.5%      |
| output_Y   | 70 K        | 68.4 K           | 2.3%      |
```

If any error exceeds 20%, investigate which constant or equation is
responsible. Ask me whether to recalibrate.

---

## Working Style Reminders

- **Ask before assuming.** Multiple-choice options are better than open-ended
  questions. "Should I (a) model radiation losses or (b) ignore them since
  they're <1%?" is better than "Should I model radiation?"

- **One subsystem at a time.** Write spec → implement → test → move on.
  Don't parallelize model implementation.

- **Tests with every model.** Never move forward with failing tests. If a
  test fails, fix the model (not the test) unless the test was wrong.

- **Cite everything.** Every equation gets a source. Every constant gets a
  citation. Every approximation gets a justification.

- **Commit after milestones.** Good commit points: all specs done, constants
  done, each model+tests done, solver+tests done, visualization+tests done.

---

## When This Phase Is Complete

The model is "done" when:
- [ ] All BluePrint .bp specs written and reviewed
- [ ] All constants files created with source citations
- [ ] All model files implemented with passing unit tests
- [ ] System solver implemented with passing integration tests
- [ ] Visualization tools produce valid SVG/HTML/JSON output
- [ ] Validation against known results shows acceptable accuracy
- [ ] All design questions from Phase 0 can be addressed

**Next step:** Transition to **blueprint-experiments.md** for design space
exploration, Taguchi screening, parameter sweeps, hardware validation
worksheets, and the theory-to-hardware calibration loop.
