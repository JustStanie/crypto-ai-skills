# Automated Skill Inventory & Technical Audit

This repository is a **Skill library**, not a software product requiring builds for ordinary advisory questions. The audit workflow runs for repository maintenance, not for normal conversations.

## What is regenerated?

| File | Source of truth | Automatically updated? |
|---|---|---|
| `SKILL_INDEX.md` | Actual `.agents/skills/*/SKILL.md` frontmatter and manual category mapping | Yes |
| `audit-register.json` | File hashes, structural checks and historical review baseline | Yes |
| `AUDIT_VALIDATION_RESULTS.json` | Actual static-validation findings and review-state counts | Yes |
| `TECHNICAL_AUDIT.md` | Current inventory and **historical** review status | Yes |
| `README.md` (marked summary block) | Current inventory and review status | Yes, summary only |
| `docs/audit/category-map.json` | Curated category for each specialist | **No**: edit when adding/reclassifying skills |
| `docs/audit/review-baseline.json` | Human-supplied review record and reviewed SHA-256 | **No**: update only after a real review |
| `docs/audit/HISTORICAL_TECHNICAL_AUDIT.md` | Detailed original static audit | **No**: historical evidence, never silently rewritten |

**Automated checks do not mean the technical methodology has been independently verified.** The generator checks the mandatory frontmatter fields, folder identity, H1 heading and balanced Markdown code fences. It does **not** compile examples, check complete YAML semantics, contact APIs, verify market prices, validate legal advice, or prove the correctness of numerical assumptions.

## Run locally on Windows 11

From the repository root, in PowerShell:

```powershell
python .\scripts\sync_skill_audit.py --write
python .\scripts\sync_skill_audit.py --check
python -m unittest discover -s tests -p "test_*.py" -v
```

If `python` is unavailable on Windows, use `py -3` instead. The generator has **no third-party dependencies**.

`--write` regenerates the five synchronized files listed above. `--check` detects missing or outdated files without writing anything and returns a failing exit code, suitable for CI.

## Automatic GitHub workflow

`.github/workflows/sync-skill-audit.yml` runs when:

- A pull request is opened or updated: **checks** synchronized artifacts and runs regression tests. It does not edit the contributor's branch.
- A push lands on `main` or `master`, or the workflow is started manually: **regenerates** artifacts and commits changes back automatically when needed.

The push job requests `contents: write` for its `GITHUB_TOKEN`. A protected branch or repository policy may block the bot commit. In that case, regenerate locally and commit the files; inspect the failing Action. No secrets, personal access token or external API credentials are required.

## What happens when a Skill changes?

1. The Skill's SHA-256 changes.
2. `audit-register.json` marks it `review_required_content_changed` instead of silently retaining a valid expert-review flag.
3. The static checks run and the current reports are regenerated.
4. A human/AI-assisted reviewer must **actually assess** relevant technical claims, versions, API integrations, security, examples and evidence.
5. Only after that review should `docs/audit/review-baseline.json` receive the new reviewed SHA-256 and an evidence-backed summary. Then regenerate the reports.

A newly added Skill appears automatically in the index and audit register as `review_required_new_or_unreviewed`. Add it to `docs/audit/category-map.json` to give it a category. Deleted Skills disappear from the current register; their historical entries stay in the baseline for provenance.

## Chat workflow

- New topic: create a **new chat in this repository**; no context-init is required to start working.
- Existing topic: continue the existing chat if prior decisions are relevant.
- `*-context-init` is optional and reads the compact generated `SKILL_INDEX.md` and router; it does not pre-load all detailed Skills or reconstruct previous chats.
- Select specialists based on the current user request only. Previous chat references, assets and preferences cannot become implicit requirements.
- The files in this repository cannot turn off built-in application memory; they are behavioral instructions and inspection aids.

The review baseline represents a **historical static inspection**, not a certificate of correctness or a live test report.
