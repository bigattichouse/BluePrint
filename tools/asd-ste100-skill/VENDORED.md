# Where this directory comes from

This directory is a copy of
[danyuchn/asd-ste100-skill](https://github.com/danyuchn/asd-ste100-skill)
(MIT License, copyright 2026 Dustin Yuchen Teng; see `LICENSE`). Until
2026-11-04 it was a Git submodule. It is now ordinary files in BluePrint,
so that BluePrint can change it and push the change without write access
to the upstream repository.

- Upstream commit of the copy: `3944283` (Merge pull request #24).
- BluePrint change on top of it: `ste-lint --blueprint-spec`, for
  `blueprint-specification` files. A block heading is markup, text in
  double quotes is cited evidence, and *verify* and *validate* are two
  keywords, not synonyms. The selftest covers each rule with the flag and
  without it.

To take a newer upstream version, copy its files over this directory,
keep `VENDORED.md`, and apply the BluePrint change again. The change can
also go upstream as a pull request.
