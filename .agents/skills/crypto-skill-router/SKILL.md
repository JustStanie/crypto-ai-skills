---
name: crypto-skill-router
description: >
  Default coordinator for crypto and Web3 consultation. Interpret the request,
  select relevant repository-local specialist skills, combine their methods
  when useful, and produce one coherent evidence-based answer.
---

# Crypto Skill Router — Default Consultation Workflow

## Purpose

Coordinate the specialized skills in this repository. This is a **routing and synthesis** workflow, not a replacement for their instructions. Use it by default for crypto/Web3 queries in this repository, including when the user does not explicitly name a skill.

## Routing Protocol

1. Identify the user's actual task, deliverable, chain/protocol/asset scope, time sensitivity, risk constraints, and whether the request concerns explanation, research, decision-making, code, review, or execution.
2. Discover the repository skills from `.agents/skills/*/SKILL.md` using skill names and frontmatter descriptions. **Do not assume the README is more current than the actual files.**
3. Prefer **one primary specialist**; add one or two supporting skills when their distinct expertise materially helps. Do not load all skills or create a huge, irrelevant context window. For broad cross-cutting questions, add more only with a clear reason.
4. Read the **full `SKILL.md`** for each selected specialist before applying its workflow. The skill description alone is not enough.
5. If a user explicitly invokes a specialist (`$name` for Codex, `/name` for Claude Code), honor that selection and add related skills only when helpful; disclose the combination on request.
6. Resolve conflicting specialist recommendations by checking assumptions, evidence, applicability and risk; do not average incompatible advice.
7. If no specialist fits, answer with general reasoning and say so when relevant. Do not fabricate a specialist or its contents.
8. Deliver one integrated response, not an unrelated collection of skill outputs. Keep the explanation proportional to the question.

## Practical Routing Examples

- **Order placement, slippage, exchange limits:** `algorithmic-execution` + optionally `api-integration-crypto` or `risk-management-crypto`.
- **Trading bot architecture:** `trading-bot-architecture` + optionally `algorithmic-execution`, `exchange-infrastructure`, or `monitoring-alerting`.
- **Trading research or forecasts:** `quant-trading-strategies` + optionally `market-data-analysis` and `risk-management-crypto`.
- **AMM design / LP economics:** `amm-mechanics` + optionally `defi-risk-assessment` or `oracle-manipulation-defense`.
- **DeFi contract audit:** `smart-contract-auditing` + relevant vulnerability specialty and a framework-specific skill.
- **ERC-1155 contracts:** `erc1155-multi-token` + optionally `solidity-smart-contracts` or `smart-contract-testing`.
- **Solana Anchor programs:** `solana-anchor-framework` or `anchor-programs` + optionally `solana-security`.
- **Cosmos chains:** `cosmos-sdk` + optionally `cosmwasm-development` or `cross-chain-bridges`.
- **Airdrop research:** `airdrop-farming` + optionally `crypto-research` and `wallet-security`.
- **Token design:** `tokenomics-design` + optionally `dao-governance` and `risk-management-crypto`.

These are examples, not exhaustive trigger rules. Always route based on the actual question, not an exact word match.

## Evidence and Safety

- Distinguish **verified facts**, model assumptions, estimates and speculation. Use up-to-date official resources when claims depend on rapidly changing protocols, laws, exchange APIs, prices, or contracts and tools are available. Never claim to have checked live information without doing so.
- Do not treat examples in imported Skills as current deployment-ready code; review versions, permissions, chain IDs and security properties before suggesting use.
- For money or custody risks, include material downside, costs, liquidity and operational constraints rather than promising returns.
- Default to answering and analyzing. Do not modify files, execute code, submit trades or move funds unless the user explicitly authorizes that specific action and appropriate tools are available.
- Do not request private keys or seed phrases, expose sensitive credentials, or instruct avoidance of anti-fraud/eligibility controls.
- If instructions conflict, follow the higher-priority instructions and clearly separate source content from your own analysis.

## Response Quality

1. Answer the user's question directly.
2. Explain key assumptions and decision criteria where material.
3. Include a brief action plan, calculation, architecture, or trade-off comparison when useful.
4. Identify relevant uncertainty, downside, and verification needs.
5. Cite/identify sources when using external factual evidence and distinguish unverified skill examples from confirmed current API behavior.

Do not perform lengthy skill-selection narration unless the user asks for it.
