# Changelog

This file records all notable changes to this project.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

There is no released version yet. All changes are in the Unreleased section.

## [Unreleased]

### Added

- `ste-lint --blueprint-spec` (`tools/asd-ste100-skill`): reads
  a `blueprint-specification` file. A block heading (`Requirement REQ-001
  [event]:`, `Verify V-012 name:`) is markup and ends the prose block,
  text in double quotes is cited evidence and is not checked, and
  *verify* and *validate* are two keywords, not synonyms. Without the
  flag, nothing changes. From the assurance project, where `ste-lint` is
  a gate.
- `ears-lint` rules `one-sentence`, `passive-response`,
  `compound-obligation`, and `duplicate-id`. They come from the
  `required` project, which tested them on 712 public requirements (PURE)
  and on 539 Zephyr RTOS requirements.
- `blueprint-specification.md`: optional `Verify` IDs, `Validate` blocks,
  `Level:` and `Derives:` lines, and `Examples:` tables. `ears-lint`
  accepts them.

- `blueprint` command that lists the installed prompts, references, and tools,
  with their paths and a one-sentence summary. `blueprint path NAME` and
  `blueprint show NAME` give one item.
- `blueprint install` (also `install-skills`): installs the prompts for coding agents. It
  writes Claude Code skills, Agent Skills in `~/.agents/skills` (Codex,
  Gemini CLI, pi, OpenCode), and nanocoder commands (`/blueprint:NAME`). A
  `blueprint` entry lists all of them. It asks before it installs in each location that
  it finds. `--target` selects one agent. `--yes` does not ask.
- `blueprint copy NAME...` copies prompts into the `spec/` directory of the
  current project. It does not replace a copy that is different from the
  source unless you use `--force`.
- `blueprint show NAME -o FILE` writes one prompt to a file.
- `blueprint update`: fetches BluePrint from GitHub and shows the new
  changelog entries. Then it pulls and installs again. `--check` only shows
  the changes.
- `blueprint version`: shows the installed version and commit.
- `Makefile` with `install`, `link`, `uninstall`, and `test` targets.
  `make install` records the source checkout in `SOURCE`.
- `catalog.tsv`: the name, path, skill name, and summary of each item.
- `blueprint-specification.md`: requirements and tests in Simplified
  Technical English, with a glossary, EARS patterns, `Verify` blocks, and
  `Expect` clauses.
- `tools/ears-lint`: a linter for the `blueprint-specification` format. It
  uses only the Python standard library.
- `tools/asd-ste100-skill`: the STE linter and skill, as a Git submodule.
- A Simplified Technical English (ASD-STE100) writing section in each role
  prompt.
- A "Simulate, Do Not Recall" section in the prompts, with the `robust`
  design-of-experiments tools (`morris`, `sobol`, `taguchi`).
- A changelog section in the prompts that recommends this format for
  software and design projects.
- `blueprint-experiment-worksheet.md`: printable bench worksheets that close
  the model loop (2026-08-31).
- `blueprint-observational.md`: models from data that already exists
  (2026-07-23).
- `blueprint-model.md` and `blueprint-experiments.md`: mathematical models
  of physical systems and design-space exploration (2026-02-18).
- Security references `security-considerations.md` and `security-mini.md`
  (2025-05-20).
- `maker-blueprint.md`: physical design (2025-05-18).
- `blueprint-mini.md` for small and local LLMs, `database-patterns.md`, and
  the `debug` prompt (2025-05-16).
- The core BluePrint prompt and user instructions (2025-05-15).


### Fixed

- `ears-lint`: a comma after the first keyword ("If, as a result, …")
  no longer gives `ears-pattern`. A glossary name can start a ubiquitous
  requirement. A quoted or `code` "shall" is not counted. `name-system`
  does not repeat an `ears-pattern` finding. The digits of an ID in an
  `Expect` are not a number. `long-sentence` counts each sentence.

### Changed

- `tools/asd-ste100-skill` is a copy of
  [asd-ste100-skill](https://github.com/danyuchn/asd-ste100-skill) (MIT),
  not a Git submodule. BluePrint can change it (`--blueprint-spec`) and
  push without write access to the upstream repository. `VENDORED.md`
  and the header of each changed file give the origin and the changes.
  `git clone` needs no `--recurse-submodules`.
- Hardware prompts, from building a yogurt maker with them (dogfood, 22
  flaws). `blueprint-openscad.md`: every named clearance states its intent;
  virtual (bought) parts in assemblies, never exported; an explicit export
  list; reproducible renders that each answer a stated question; a compile
  gate; the assembly sequence as one data list that the collision sweeps,
  the exploded view, and the step pictures read; geometry checks on solids,
  run as a script, with probes sized from the mating part and one seeded
  fault per kind of check; OpenSCAD 2021.01 behavior to test. Examples are
  generic.
- `blueprint-electronics.md`: a part ledger with source, revision, fetch
  date, and status; each safety layer has a location; datasheet limits go to
  the mechanical design; size a heating element at the supply voltage,
  estimate the stuck-on rise, and check the layer list again when the
  element changes.
- `blueprint-prompt.md`: compile entry conditions, no requirement changed to
  match a model without a human decision, and a brief trace so a brief item
  cannot disappear.
- `blueprint-openscad.md` and `blueprint-electronics.md` are in
  `catalog.tsv` and the README. `blueprint list` shows them, and
  `blueprint install` makes them skills. `make install` also installs
  `guides/`, which the two prompts refer to. Before this, neither prompt
  was a skill, and the guide references did not resolve.
- Calculate first, in `blueprint-prompt.md`, `maker-blueprint.md`,
  `blueprint-openscad.md`, `blueprint-electronics.md`, and (short form)
  `blueprint-mini.md`. Each number comes from a measurement, a datasheet, a
  calculation, or a simulation. Calculations are code. Sweep the range, not
  one point. An assumption is the last choice, and an assumption on a
  safety, fit, or power path stops the build. Test the design in the model
  with a robust sweep before a build. From the yogurt-maker dogfood, flaws
  23 to 41.
- `blueprint-electronics.md`: ngspice is the simulator, run in batch mode as
  a scripted test at the corners, before the user builds. Help ngspice find
  the operating point with `.nodeset` from a fixed rule. A safety layer on a
  candidate part counts as planned, not closed. Check the low side of a heater (too
  weak is a hazard too). Find which limit acts when two parts limit the
  same temperature.
- `blueprint-model.md`: Phase 0 asks for hazards (both directions) and
  separates scenarios from factors. An unsourced constant becomes a labeled
  assumption with a range. The sweep tests the range, and the ranking becomes
  the measurement list. New sections: a transient pattern with discrete
  control, phases, and an independent cross-check (a heat network as an
  ngspice circuit). Also one pass flag for each requirement with a seeded
  fault, and an in-process sweep driver. Read the confidence intervals (also in
  `blueprint-experiments.md`).
- `blueprint-experiments.md`: the robust tools read one bare number from
  stdout, not JSON.
- `blueprint-openscad.md`: a render script replaces the pictures only after
  it renders every view. The evidence records the date, tool version, and
  model commit. Each model part traces to a specification entry. Each virtual
  part has a clearance to nearby printed features.
- Changelog rules in the prompts: use each group heading one time, and after
  a merge compare the entries with both parents.
- `blueprint-specification.md`: if `ste-lint` rejects `--blueprint-spec`,
  run `make install` again.
- The README is in Simplified Technical English. It lists all prompt files.
- The main prompt is a dialectic process: one question at a time, then a
  section-by-section review with derived tests (2025-12-14).
