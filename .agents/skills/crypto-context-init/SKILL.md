---
name: crypto-context-init
description: >-
  Initialize the local crypto & web3 skill catalog for the current chat. Read the compact skill index and routing instructions without loading all specialists. Use when the user explicitly requests a skill catalog initialization or refresh; do not require this for new chats.
---

# Crypto & Web3 — Context Initialization

## Purpose

Initialize **this conversation**, not the model's long-term memory. Read the compact repository inventory, establish where the domain methods live, and prepare for task-specific routing without loading every specialist into the context window.

## Procedure

1. Confirm the working repository is `crypto-ai-skills`. Do not access other repositories unless explicitly required.
2. Read `SKILL_INDEX.md` in the repository root. It is generated from the existing `SKILL.md` frontmatter. Treat it as a discovery index, **not** as proof of a specialist's content or current correctness.
3. Read `.agents/skills/crypto-skill-router/SKILL.md` to understand routing policy (skip re-reading if already loaded this turn).
4. Identify the relevant capability areas using concise category names. **Do not read all specialist `SKILL.md` files** during initialization.
5. State the total number of specialists and categories as reported by the actual index, plus the coordinator and initializer, and explain how a specialist will be selected when the user asks a real question.
6. Do not write a persistent `CONTEXT.md`, modify the repository, run builds, install packages, or fetch external data during initialization unless explicitly requested.
7. For the next user question, use the coordinator to select **one primary Skill and at most two supporting Skills** by default; open their full `SKILL.md` instructions only when needed.

## Output

Briefly acknowledge initialization, summarize domains in one compact paragraph, give an invocation example, and mention that no bulk content was loaded. Do not dump the full index unless requested.

## Limitations

- Initialization only applies to the current chat/session and context window; it does not retrain the model or install any global Skills.
- The index may become stale if folders change: verify actual `SKILL.md` files for the selected Skill when answering.
- Availability of native `$...` or `/...` command discovery depends on the actual desktop/CLI version and local Skills link.

## When to run this initializer

Run **only on explicit user request**, such as a request to initialize, refresh, or display available Skills. Do **not** make this a mandatory first step for every new chat: repository instructions already provide default Skill routing. Initialization reads a brief catalog for the **current** chat, never all specialist bodies, and does not transfer previous chat decisions or create long-term model memory.

## Isolation of new conversations

- This command **only** reads the local repository's Skill catalog and routing instructions. Never treat it as restoring previous sessions, carrying over a user's earlier preferences or decisions, or clearing client-level memory.
- During initialization, do not fetch prior chat transcripts, memory summaries, previous task notes or other repositories' histories, unless the user explicitly requests continuation of that prior work.
- Once initialized, route each question by **its own stated task**. A new portfolio question must not inherit an unrelated earlier blockchain-development preference; shared Skills are methodologies, not user positions.
- Product-specific memory or cross-session features may still exist. These repository instructions reduce inappropriate carry-over but cannot technically disable those features.

