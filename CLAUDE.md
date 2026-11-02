# Claude Code — Crypto AI Thinking Skills

@AGENTS.md

Use the shared repository policy above. For crypto/Web3 requests, follow the default coordinator at `.agents/skills/crypto-skill-router/SKILL.md` and load only relevant specialist Skills.

Native project Skills are exposed through `.claude/skills/` (a Windows junction to the canonical `.agents/skills/`). If this directory is unavailable, read the canonical Skill files directly; do **not** claim that `/skill-name` was registered without checking.

To set up local discovery on Windows after extracting or cloning, run `./setup-claude-skills.ps1` once in PowerShell. Do not install Skills globally. Do not modify repository files unless asked.

## Context initialization

- Optional: `/crypto-context-init` reads `SKILL_INDEX.md` and the coordinator for a lightweight map of capabilities in **this chat**. This is not persistent memory.
- Do not load every `SKILL.md` during initialization; read relevant specialist instructions when questions arise.
- Normal questions still use `crypto-skill-router` automatically through the repository policy.
- If the native slash command is not registered, ask: `Read .agents/skills/crypto-context-init/SKILL.md and initialize the repository skill catalog.`

## Conversations and initialization

When a user creates a new Claude Code conversation in `crypto-ai-skills`, apply the shared repository policy and `crypto-skill-router` without requiring `/crypto-context-init`. The initializer is an optional, explicit catalog overview, **not** an obligatory command before each question. Reuse a chat when its history matters; start a new chat for unrelated subjects. Skills remain local to this repository. Never claim that prior chat history, a previous initialization, or other repositories' Skills are automatically available.

## Thread Context Isolation

- Follow the **Thread Context Isolation** section of `AGENTS.md` for every new independent Claude Code conversation.
- Do not favor a chain, asset, product, tool, technique, or decision merely because it appeared in another chat in this repository. Pick specialists based on the **current** request and evidence.
- Do not import automatic memories, summaries, or prior-session notes as implicit requirements. Reuse earlier work **only on an explicit continuity request**; confirm unavailable assumptions instead of guessing.
- `/crypto-context-init` only reads the Skill catalog; it neither restores earlier chats nor disables client-level memory. Repository instructions are behavioral guidance, **not a technical guarantee of memory isolation**.

## Automated repository maintenance (only when requested)

The deterministic local index and audit generator is `python scripts/sync_skill_audit.py --write`, with `--check` for a read-only CI test. See `AUDIT_AUTOMATION.md`. Do **not** run it to initialize a chat. `*-context-init` remains an optional **read-only** catalog overview. Existing expert review evidence is historical and never automatically renewed after a Skill changes.
