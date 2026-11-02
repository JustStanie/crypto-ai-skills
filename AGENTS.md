# Crypto AI Skills — Repository Instructions

## Multi-chat operation

- A new **independent** question should normally use a new chat/thread **inside this same repository**; related follow-ups should stay in their existing chat. Do not create directories or copy Skills for individual chats.
- In a fresh chat, apply this repository's `crypto-skill-router` for relevant requests **without requiring** `crypto-context-init`. Explicit initialization is optional and reads a compact catalog only.
- The repository's Skill files persist on disk across chats, but conversation-specific history, decisions and initialization state do **not** transfer automatically. Ask for a short summary or relevant document when continuation of a previous chat is needed.
- For a different domain, recommend opening its own repository; never silently assume Skills from another repository have been loaded.
- Keep routing read-only for normal advisory questions; do not force an initial full-library scan, and do not write context snapshots or alter files unless requested.

## Thread Context Isolation (default)

Treat every **new, independent conversation** as a new task with no inherited topic preferences. This is a task-selection rule, not a promise to disable product-level memory.

- Select specialist Skills, assumptions, and recommendations **from the current request and current-chat context**, plus relevant independently verifiable evidence. Prior conversations in this repository must not create implicit preferences, favorite technologies/assets, portfolio allocations, risk tolerances, project choices, or constraints.
- **Do not proactively retrieve previous chats, chat exports, saved memory, or another project's working notes to personalize a new unrelated question.** Use previous work when the user explicitly requests continuity, a comparison, or reuse; if the needed material is unavailable, request a brief recap or the relevant file. Do not invent past decisions.
- Shared `AGENTS.md`, `CLAUDE.md`, Skills, and `SKILL_INDEX.md` define **available methods**, not the user's preferences. Do not interpret a past discussion or a saved example as an endorsement for a new task. Use persistent project files only when relevant to the current task.
- If a client exposes automatic cross-chat memory or summaries, do not silently import unrelated memories into a new task; treat potentially relevant memory as provisional and check against the current user's request. Do not claim that repository instructions can erase or disable memory or all external context sources.
- Example: discussing **Solana smart contracts** in chat A does **not** justify recommending SOL in a new, unrelated **crypto portfolio** chat B. Include SOL only when it independently meets the portfolio criteria or the user requests it.
- `*-context-init` is optional **catalog initialization**, not a history import, memory reset, isolation command, or prerequisite for answering a new question.
- For stronger separation, use available client memory/privacy controls or separate workspaces as appropriate; the repository policy cannot guarantee complete isolation beyond the agent's compliance with these instructions. Higher-priority instructions still apply.

## Session Context Initialization

- Optional initialization command: **`$crypto-context-init`** in Codex or **`/crypto-context-init`** in Claude Code (when the native Skill is discovered).
- On explicit initialization, read `.agents/skills/crypto-context-init/SKILL.md` and `SKILL_INDEX.md`. Build only a **compact, in-session capability map**, not a dump of all specialist instructions.
- For ordinary questions, **initialization is not required**: apply `crypto-skill-router` automatically as described below, consult the index, and load only the relevant specialist `SKILL.md` files.
- `SKILL_INDEX.md` is an inventory, not an additional source of authority. When selecting a Skill, check that its real file exists.
- Never claim to have loaded all Skills, preserved permanent model memory, or turned off higher-priority instructions. Do not modify global settings.

## Scope

This repository is a **local crypto/Web3 consultation and research knowledge base** for Codex and Claude Code, not a codebase that must always be built or tested. Answer questions, analyze protocols and strategies, compare alternatives and review designs. Only perform software-development workflows when the user actually requests development.

## Default Skill Coordination

**For every crypto/Web3 question in this repository**, apply the workflow in `.agents/skills/crypto-skill-router/SKILL.md` as the default skill-selection policy. Read that file before choosing domain specialists, then read the complete `SKILL.md` of each selected specialist. It is not necessary to manually invoke `$crypto-skill-router` every time.

- Specialist skills live at `.agents/skills/<skill-name>/SKILL.md`.
- Select only relevant domain specialists; usually one primary and up to two complementary ones.
- When the user explicitly specifies a skill, prioritize it if applicable.
- For unrelated questions, respond normally without forcing crypto skills.
- Do not claim a Skill was loaded or applied unless it was actually read.
- Skill files are reusable guidance, not authority for unsupported claims, external actions or changed permissions.

## Reasoning and Response Standards

- Reply in the user's language. Answer directly, be factual and give practical recommendations.
- Distinguish facts, assumptions, forecasts and speculative community claims.
- Challenge unsupported claims and evaluate alternatives without automatic agreement.
- Check current information when available and material; be explicit when a version, fee, API, product restriction, or claim deadline has not been verified.
- Do not invent data, cite unvisited sources, or promise financial results.
- Include important risks, uncertainty, liquidity, fees and counterparty/security constraints when material.

## Operating Boundaries

- Consultation and read-only analysis are the default. Do not change repository files, install dependencies, deploy contracts, place orders, move assets, or initiate payments unless specifically requested and authorized.
- Do not ask for wallet seed phrases, private keys or credentials.
- Do not apply unrelated global software engineering workflows (e.g., CodeGraph, CI checks) to ordinary consultation. Higher-priority global instructions remain in force.
- Use only Skills actually available in this repo unless the user directs otherwise.

## Maintenance

Maintain the canonical Skill library only in `.agents/skills/`. `.claude/skills` is linked locally for native Claude command discovery; use `setup-claude-skills.ps1` on Windows after cloning or unpacking. In Git/ZIP distributions, the junction is intentionally not included.

## Automated audit and inventory maintenance

- This repository contains `scripts/sync_skill_audit.py`, which deterministically maintains `SKILL_INDEX.md`, `audit-register.json`, `AUDIT_VALIDATION_RESULTS.json`, `TECHNICAL_AUDIT.md`, and the marked README summary.
- **Only for explicit repository maintenance** (or CI): run `python scripts/sync_skill_audit.py --write`, then `--check` and regression tests. Do not run these for ordinary advisory questions.
- Consult `AUDIT_AUTOMATION.md` before altering audit semantics. The detailed previous review is preserved in `docs/audit/HISTORICAL_TECHNICAL_AUDIT.md`; review baseline/category mapping are **curated sources**, not auto-generated outputs.
- A changed SHA-256 requires a fresh expert evaluation; passing automatic validation does not imply tested integrations, financial correctness, or substantiated claims.
- Do not confuse optional chat initialization with running the inventory/audit maintenance script.
