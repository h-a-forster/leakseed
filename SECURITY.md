# Security policy

Security fixes are made for the latest release.

## Reporting

Report vulnerabilities privately through the repository's **Security** tab ("Report a
vulnerability"). Do not open a public issue. Include the leakseed version, the operating
system, the impact, and steps that reproduce it.

## Scope

leakseed generates Python scripts and imports them to check their labels. `verify` and
`impact` import only files whose SHA-256 matches the manifest; `scripts/probes.py` imports the
fixed files in `corpus/probes`. A corpus you did not generate is code you are about to run:
read it first. The linters run statically over the corpus and execute none of it. leakseed
makes no network requests and calls no models.

In scope:

- leakseed executing a corpus file that does not match its manifest;
- leakseed reading, writing or deleting files outside the paths given on the command line;
- local absolute paths or other machine details written to committed outputs
  (`results/`, `corpus/`).

Out of scope:

- vulnerabilities in dependencies, including the pinned linters (report those upstream);
- disagreements about a label or a scorecard number (open an ordinary issue; see
  CONTRIBUTING.md).
