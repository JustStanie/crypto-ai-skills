# Claude Code — Crypto AI Thinking Skills

@AGENTS.md

Use the shared repository policy above. For crypto/Web3 requests, follow the default coordinator at `.agents/skills/crypto-skill-router/SKILL.md` and load only relevant specialist Skills.

Native project Skills are exposed through `.claude/skills/` (a Windows junction to the canonical `.agents/skills/`). If this directory is unavailable, read the canonical Skill files directly; do **not** claim that `/skill-name` was registered without checking.

To set up local discovery on Windows after extracting or cloning, run `./setup-claude-skills.ps1` once in PowerShell. Do not install Skills globally. Do not modify repository files unless asked.
