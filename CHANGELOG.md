# Change Log / Review Summary

## Inventory
- Input domain Skills: **120**
- Output domain Skills: **120**
- New coordinator: **1 (`crypto-skill-router` )**
- Missing YAML frontmatter fixed: **26**
- All frontmatter `name` values match their skill directory.
- Updated short, accurate skill-routing `description` fields on all 120 original skills.
- Original specialized skill bodies retained except narrowly documented corrections below.
- `README.md` rebuilt in English with expandable categories and individual skill details, practical capabilities and prompts.
- `AGENTS.md` and `CLAUDE.md` updated for local default routing.

## Targeted technical corrections
- `account-abstraction`: avoid brittle outdated AA integration packages; added subject-specific verification guidance.
- `algorithmic-execution`: added subject-specific verification guidance.
- `blockchain-forensics`: added subject-specific verification guidance.
- `chainlink-oracles`: clarify oracle freshness validation; added subject-specific verification guidance.
- `cosmos-sdk`: updated outdated Go/Ignite version and remote installer assumptions; added subject-specific verification guidance.
- `crypto-compliance`: added subject-specific verification guidance.
- `crypto-tax`: added subject-specific verification guidance.
- `erc1155-multi-token`: clarify metadata placeholders; added subject-specific verification guidance.
- `erc4337-smart-accounts`: added subject-specific verification guidance.
- `foundry-framework`: added subject-specific verification guidance.
- `hardhat-development`: avoid incompatible hardhat package prescription; added subject-specific verification guidance.
- `market-making`: remove hardcoded rate limit.
- `mev-strategies`: correct bundle inclusion guarantee; remove misleading speed claim; added subject-specific verification guidance.
- `prediction-markets-onchain`: added subject-specific verification guidance.
- `risk-management-crypto`: remove unsupported fixed correlation estimates; qualify stop execution risk; added subject-specific verification guidance.
- `smart-contract-deployment`: added subject-specific verification guidance.
- `solana-anchor-framework`: remove obsolete pinned Solana installer; added subject-specific verification guidance.
- `solana-trading-bots`: added subject-specific verification guidance.
- `the-graph-development`: added subject-specific verification guidance.
- `tokenomics-design`: qualify scarcity claim.
- `wallet-connect`: added subject-specific verification guidance.

## Validation scope and limitations

- Automated validation covers file completeness, YAML parsing, folder-name parity, unique names, documentation coverage, and basic Markdown structure.
- Focused manual editorial corrections address identifiable stale or risky assumptions; **this is not an exhaustive factual verification of all technology details in 120 documents**.
- Solidity, Rust, Move, and API examples were not compiled or executed, and no production performance or profitability was validated.
- Toolchain versions, exchange APIs, prices, tax rules and protocol parameters still require verification at use time.
- Claude Code native skill discovery through Windows Junction requires testing on the target machine; the ZIP does not preserve Junctions.

## Files

- `.agents/skills/`: 120 original specialists and 1 coordinator.
- `AGENTS.md`, `CLAUDE.md`: default selection policy.
- `README.md`: categorized user documentation.
- `setup-claude-skills.ps1`: optional local Windows junction setup.

