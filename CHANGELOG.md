# Changelog

This file records all notable changes to this project.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

There is no released version yet. All changes are in the Unreleased section.

## [Unreleased]

### Added

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

- The README is in Simplified Technical English. It lists all prompt files.
- The main prompt is a dialectic process: one question at a time, then a
  section-by-section review with derived tests (2025-12-14).
