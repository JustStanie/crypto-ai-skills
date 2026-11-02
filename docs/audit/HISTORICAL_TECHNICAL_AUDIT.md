# Per-Skill Technical Review — Crypto & Web3

**Review date:** 2026-10-31  
**Input:** user-uploaded `crypto-ai-skills` archive  
**Specialists inspected:** 120  
**Existing router inspected:** 1  
**New context initializer:** 1  
**Total delivered Skills:** 122

## Verification Scope

- Reviewed every `SKILL.md` for identity, Markdown fences, claims/absolute language, financial and security risk patterns, code/install snippets, and domain-specific failure modes.
- Applied source-preserving corrections to identified misleading examples, added **topic-matched production-validation guidance** in each specialist, and kept the original methodologies intact otherwise.
- Verified selected contemporary claims against current primary references listed below. **This is not a line-by-line external verification of every claim across all files.**
- **Not executed:** smart contract compilation, exchange trading, actual vendor SDK calls, licensed professional sign-off or real financial transactions. Code snippets still require environment-specific tests.
- Issues flagged by the scanner may be already mitigated in original text; they are **review signals**, not confirmed defects.
- Individual file records below include the review observations, actions performed, and outstanding verification needs.

## Review Signal Counts (files)

| Signal | Skills flagged |
|---|---:|
| `third-party-api` | 88 |
| `credential-security` | 48 |
| `unguarded-install` | 31 |
| `live-data` | 26 |
| `legal-or-compliance` | 22 |
| `financial-assumptions` | 17 |
| `absolute-percent-benchmark` | 15 |
| `unqualified-performance` | 5 |
| `hardcoded-exchange-limits` | 2 |

## Skill-by-Skill Findings

### `account-abstraction` — Web3 Development

- **Focus:** Blockchain ecosystem / development.
- **Review signals:** `credential-security (6; L13, L30)`, `third-party-api (14; L19, L26)`
- **Edits:** Added subject-specific validation for blockchain ecosystem / development (2 controls plus version/evidence checks).
- **Remaining check:** confirm versioned third-party integrations, numeric claims and subject-specific assumptions against current primary sources before production use. No live integration was executed.
- **Change verification:** `deece8a33182` → `1588e213984a` (SHA-256 prefixes).

### `airdrop-farming` — Crypto Trading

- **Focus:** Blockchain ecosystem / development.
- **Review signals:** `credential-security (4; L352, L352)`, `legal-or-compliance (3; L584, L690)`
- **Edits:** Added subject-specific validation for blockchain ecosystem / development (2 controls plus version/evidence checks).
- **Remaining check:** confirm versioned third-party integrations, numeric claims and subject-specific assumptions against current primary sources before production use. No live integration was executed.
- **Change verification:** `1d976a1644b1` → `44887e08e9ef` (SHA-256 prefixes).

### `algorithmic-execution` — Crypto Trading

- **Focus:** Trading and execution.
- **Review signals:** `credential-security (1; L186)`, `third-party-api (14; L4, L34)`, `financial-assumptions (3; L303, L305)`
- **Edits:** Added subject-specific validation for trading and execution (2 controls plus version/evidence checks).
- **Remaining check:** confirm versioned third-party integrations, numeric claims and subject-specific assumptions against current primary sources before production use. No live integration was executed.
- **Change verification:** `dd76fa4aae22` → `58896f8e8f63` (SHA-256 prefixes).

### `amm-mechanics` — Decentralized Finance (DeFi)

- **Focus:** DeFi protocol economics.
- **Review signals:** `third-party-api (4; L24, L155)`, `live-data (1; L108)`
- **Edits:** Added subject-specific validation for defi protocol economics (2 controls plus version/evidence checks).
- **Remaining check:** confirm versioned third-party integrations, numeric claims and subject-specific assumptions against current primary sources before production use. No live integration was executed.
- **Change verification:** `ca7cb30f209f` → `27bb22dd854e` (SHA-256 prefixes).

### `anchor-programs` — Crypto Development

- **Focus:** Blockchain ecosystem / development.
- **Review signals:** `unguarded-install (1; L23)`, `third-party-api (1; L15)`, `live-data (1; L15)`
- **Edits:** Added subject-specific validation for blockchain ecosystem / development (2 controls plus version/evidence checks).
- **Remaining check:** confirm versioned third-party integrations, numeric claims and subject-specific assumptions against current primary sources before production use. No live integration was executed.
- **Change verification:** `9f511d2d427e` → `3ab5a73be298` (SHA-256 prefixes).

### `api-integration-crypto` — Crypto Infrastructure

- **Focus:** Blockchain ecosystem / development.
- **Review signals:** `hardcoded-exchange-limits (4; L37, L39)`, `credential-security (12; L71, L110)`, `third-party-api (48; L2, L3)`, `legal-or-compliance (5; L36, L37)`, `live-data (6; L49, L89)`
- **Edits:** Added subject-specific validation for blockchain ecosystem / development (2 controls plus version/evidence checks).
- **Remaining check:** confirm versioned third-party integrations, numeric claims and subject-specific assumptions against current primary sources before production use. No live integration was executed.
- **Change verification:** `38f9d9c8632f` → `51ee8430f5bc` (SHA-256 prefixes).

### `aptos-development` — Web3 Development

- **Focus:** Blockchain ecosystem / development.
- **Review signals:** `unguarded-install (2; L23, L30)`, `credential-security (1; L165)`, `third-party-api (6; L25, L131)`
- **Edits:** Added subject-specific validation for blockchain ecosystem / development (2 controls plus version/evidence checks).
- **Remaining check:** confirm versioned third-party integrations, numeric claims and subject-specific assumptions against current primary sources before production use. No live integration was executed.
- **Change verification:** `fd4ac092e038` → `a08b1cd64a91` (SHA-256 prefixes).

### `avalanche-development` — Web3 Development

- **Focus:** Blockchain ecosystem / development.
- **Review signals:** `unguarded-install (1; L36)`, `credential-security (4; L175, L181)`, `third-party-api (10; L32, L41)`
- **Edits:** Replaced 1 remote curl-to-shell installation example(s) with safer official-install verification guidance. Added subject-specific validation for blockchain ecosystem / development (2 controls plus version/evidence checks).
- **Remaining check:** confirm versioned third-party integrations, numeric claims and subject-specific assumptions against current primary sources before production use. No live integration was executed.
- **Change verification:** `dddd567975f4` → `71d3933538d0` (SHA-256 prefixes).

### `base-development` — Web3 Development

- **Focus:** Blockchain ecosystem / development.
- **Review signals:** `unguarded-install (1; L26)`, `credential-security (3; L183, L241)`, `third-party-api (2; L37, L91)`
- **Edits:** Replaced 1 remote curl-to-shell installation example(s) with safer official-install verification guidance. Added subject-specific validation for blockchain ecosystem / development (2 controls plus version/evidence checks).
- **Remaining check:** confirm versioned third-party integrations, numeric claims and subject-specific assumptions against current primary sources before production use. No live integration was executed.
- **Change verification:** `7182ca759850` → `5d55dabc3cb3` (SHA-256 prefixes).

### `bitcoin-fundamentals` — Cryptocurrency Pro

- **Focus:** Blockchain ecosystem / development.
- **Review signals:** `third-party-api (1; L28)`
- **Edits:** Added subject-specific validation for blockchain ecosystem / development (2 controls plus version/evidence checks).
- **Remaining check:** confirm versioned third-party integrations, numeric claims and subject-specific assumptions against current primary sources before production use. No live integration was executed.
- **Change verification:** `ae2133dfbd22` → `c931668411ae` (SHA-256 prefixes).

### `blockchain-forensics` — Crypto Security

- **Focus:** Custody and security.
- **Review signals:** `credential-security (1; L24)`, `third-party-api (3; L39, L63)`, `legal-or-compliance (12; L9, L9)`, `live-data (2; L63, L93)`
- **Edits:** Added subject-specific validation for custody and security (2 controls plus version/evidence checks).
- **Remaining check:** confirm versioned third-party integrations, numeric claims and subject-specific assumptions against current primary sources before production use. No live integration was executed.
- **Change verification:** `3f3272f1f133` → `34e56f2f4f7d` (SHA-256 prefixes).

### `blockchain-indexing-data` — Crypto Development

- **Focus:** Blockchain ecosystem / development.
- **Review signals:** `third-party-api (3; L126, L254)`, `live-data (2; L9, L13)`
- **Edits:** Added subject-specific validation for blockchain ecosystem / development (2 controls plus version/evidence checks).
- **Remaining check:** confirm versioned third-party integrations, numeric claims and subject-specific assumptions against current primary sources before production use. No live integration was executed.
- **Change verification:** `447dd6cd949e` → `432d6bfe4941` (SHA-256 prefixes).

### `cairo-contracts` — Crypto Development

- **Focus:** Blockchain ecosystem / development.
- **Review signals:** `unguarded-install (3; L21, L41)`, `third-party-api (5; L25, L30)`
- **Edits:** Added subject-specific validation for blockchain ecosystem / development (2 controls plus version/evidence checks).
- **Remaining check:** confirm versioned third-party integrations, numeric claims and subject-specific assumptions against current primary sources before production use. No live integration was executed.
- **Change verification:** `df4d5ce34d6a` → `1c6a6319b174` (SHA-256 prefixes).

### `chainlink-oracles` — Crypto Development

- **Focus:** Custody and security.
- **Review signals:** `unguarded-install (1; L24)`, `third-party-api (4; L28, L39)`, `live-data (2; L15, L51)`
- **Edits:** Corrected an unsupported or overly categorical statement (5 occurrence(s)). Replaced 1 remote curl-to-shell installation example(s) with safer official-install verification guidance. Added subject-specific validation for custody and security (2 controls plus version/evidence checks).
- **Remaining check:** confirm versioned third-party integrations, numeric claims and subject-specific assumptions against current primary sources before production use. No live integration was executed.
- **Change verification:** `2ff48b0d9c2f` → `0f0eb5607c67` (SHA-256 prefixes).

### `cold-storage-security` — Cryptocurrency Pro

- **Focus:** Custody and security.
- **Review signals:** `unqualified-performance (1; L44)`, `credential-security (7; L17, L19)`
- **Edits:** Added subject-specific validation for custody and security (2 controls plus version/evidence checks).
- **Remaining check:** confirm versioned third-party integrations, numeric claims and subject-specific assumptions against current primary sources before production use. No live integration was executed.
- **Change verification:** `aacf304fd2ec` → `32dbfede339d` (SHA-256 prefixes).

### `cosmos-sdk` — Web3 Development

- **Focus:** Blockchain ecosystem / development.
- **Review signals:** `third-party-api (36; L2, L3)`, `financial-assumptions (2; L196, L204)`
- **Edits:** Added subject-specific validation for blockchain ecosystem / development (2 controls plus version/evidence checks).
- **Remaining check:** confirm versioned third-party integrations, numeric claims and subject-specific assumptions against current primary sources before production use. No live integration was executed.
- **Change verification:** `8167f02368c6` → `186aa7bb1878` (SHA-256 prefixes).

### `cosmwasm-contracts` — Web3 Development

- **Focus:** Blockchain ecosystem / development.
- **Review signals:** `unguarded-install (1; L21)`
- **Edits:** Added subject-specific validation for blockchain ecosystem / development (2 controls plus version/evidence checks).
- **Remaining check:** confirm versioned third-party integrations, numeric claims and subject-specific assumptions against current primary sources before production use. No live integration was executed.
- **Change verification:** `44b155de79dd` → `25b442cbe754` (SHA-256 prefixes).

### `cosmwasm-development` — Crypto Development

- **Focus:** Blockchain ecosystem / development.
- **Review signals:** `unguarded-install (1; L23)`, `third-party-api (3; L13, L34)`
- **Edits:** Added subject-specific validation for blockchain ecosystem / development (2 controls plus version/evidence checks).
- **Remaining check:** confirm versioned third-party integrations, numeric claims and subject-specific assumptions against current primary sources before production use. No live integration was executed.
- **Change verification:** `3d26c25d9246` → `0c8237079ded` (SHA-256 prefixes).

### `cross-chain-bridges` — Crypto Development

- **Focus:** Custody and security.
- **Review signals:** `credential-security (1; L137)`, `third-party-api (2; L63, L90)`
- **Edits:** Added subject-specific validation for custody and security (2 controls plus version/evidence checks).
- **Remaining check:** confirm versioned third-party integrations, numeric claims and subject-specific assumptions against current primary sources before production use. No live integration was executed.
- **Change verification:** `8953fa7dca9e` → `ce42c2c559c2` (SHA-256 prefixes).

### `cross-chain-defi` — Decentralized Finance (DeFi)

- **Focus:** DeFi protocol economics.
- **Review signals:** `unguarded-install (1; L27)`, `credential-security (1; L34)`, `third-party-api (10; L24, L30)`
- **Edits:** Added subject-specific validation for defi protocol economics (2 controls plus version/evidence checks).
- **Remaining check:** confirm versioned third-party integrations, numeric claims and subject-specific assumptions against current primary sources before production use. No live integration was executed.
- **Change verification:** `b4ebf7388b09` → `ab1b2a6c987f` (SHA-256 prefixes).

### `crypto-compliance` — Crypto Infrastructure

- **Focus:** Regulated crypto activity.
- **Review signals:** `absolute-percent-benchmark (1; L58)`, `credential-security (1; L13)`, `third-party-api (1; L204)`, `legal-or-compliance (36; L2, L3)`, `live-data (1; L189)`
- **Edits:** Added subject-specific validation for regulated crypto activity (2 controls plus version/evidence checks).
- **Remaining check:** confirm versioned third-party integrations, numeric claims and subject-specific assumptions against current primary sources before production use. No live integration was executed.
- **Change verification:** `123df0f9f925` → `280492cc5d0c` (SHA-256 prefixes).

### `crypto-fund-operations` — Crypto Infrastructure

- **Focus:** Regulated crypto activity.
- **Review signals:** `absolute-percent-benchmark (2; L110, L115)`, `financial-assumptions (4; L75, L79)`, `legal-or-compliance (26; L9, L13)`, `live-data (2; L52, L90)`
- **Edits:** Added subject-specific validation for regulated crypto activity (2 controls plus version/evidence checks).
- **Remaining check:** confirm versioned third-party integrations, numeric claims and subject-specific assumptions against current primary sources before production use. No live integration was executed.
- **Change verification:** `3dbaf60aede0` → `a1bae526a964` (SHA-256 prefixes).

### `crypto-research` — Cryptocurrency Pro

- **Focus:** Blockchain ecosystem / development.
- **Review signals:** No automated risk patterns matched; reviewed for subject-scope limits.
- **Edits:** Added subject-specific validation for blockchain ecosystem / development (2 controls plus version/evidence checks).
- **Remaining check:** confirm versioned third-party integrations, numeric claims and subject-specific assumptions against current primary sources before production use. No live integration was executed.
- **Change verification:** `0655c57aeb74` → `1c9a6e4e5d26` (SHA-256 prefixes).

### `crypto-skill-router` — Default Coordinator

- **Focus:** Router.
- **Review signals:** `credential-security (2; L47, L47)`, `third-party-api (3; L28, L35)`, `live-data (1; L43)`
- **Edits:** Retained original content; no structural correction necessary.
- **Remaining check:** confirm versioned third-party integrations, numeric claims and subject-specific assumptions against current primary sources before production use. No live integration was executed.
- **Change verification:** `d5b247f0023c` → `6e7045073b8a` (SHA-256 prefixes).

### `crypto-tax` — Cryptocurrency Pro

- **Focus:** Regulated crypto activity.
- **Review signals:** `third-party-api (2; L28, L48)`, `legal-or-compliance (20; L2, L3)`
- **Edits:** Added subject-specific validation for regulated crypto activity (2 controls plus version/evidence checks).
- **Remaining check:** confirm versioned third-party integrations, numeric claims and subject-specific assumptions against current primary sources before production use. No live integration was executed.
- **Change verification:** `8ca645091d3b` → `5b582336687e` (SHA-256 prefixes).

### `cryptocurrency-stablecoin-mechanics` — Cryptocurrency Pro

- **Focus:** DeFi protocol economics.
- **Review signals:** No automated risk patterns matched; reviewed for subject-scope limits.
- **Edits:** Added subject-specific validation for defi protocol economics (2 controls plus version/evidence checks).
- **Remaining check:** confirm versioned third-party integrations, numeric claims and subject-specific assumptions against current primary sources before production use. No live integration was executed.
- **Change verification:** `34eb4698577b` → `18e687be14d2` (SHA-256 prefixes).

### `dao-governance` — Cryptocurrency Pro

- **Focus:** Blockchain ecosystem / development.
- **Review signals:** `legal-or-compliance (1; L45)`
- **Edits:** Added subject-specific validation for blockchain ecosystem / development (2 controls plus version/evidence checks).
- **Remaining check:** confirm versioned third-party integrations, numeric claims and subject-specific assumptions against current primary sources before production use. No live integration was executed.
- **Change verification:** `36a54ae5c5d2` → `0adbc5c27a7e` (SHA-256 prefixes).

### `dao-governance-contracts` — Crypto Development

- **Focus:** Contract engineering.
- **Review signals:** `third-party-api (3; L33, L36)`
- **Edits:** Added subject-specific validation for contract engineering (2 controls plus version/evidence checks).
- **Remaining check:** confirm versioned third-party integrations, numeric claims and subject-specific assumptions against current primary sources before production use. No live integration was executed.
- **Change verification:** `384f293ed583` → `fb6faf52c334` (SHA-256 prefixes).

### `data-pipeline-crypto` — Crypto Infrastructure

- **Focus:** Blockchain ecosystem / development.
- **Review signals:** `third-party-api (6; L13, L29)`, `legal-or-compliance (2; L64, L70)`, `live-data (7; L17, L68)`
- **Edits:** Added subject-specific validation for blockchain ecosystem / development (2 controls plus version/evidence checks).
- **Remaining check:** confirm versioned third-party integrations, numeric claims and subject-specific assumptions against current primary sources before production use. No live integration was executed.
- **Change verification:** `d02c126d9803` → `f9b12b57d446` (SHA-256 prefixes).

### `defi-composability` — Decentralized Finance (DeFi)

- **Focus:** DeFi protocol economics.
- **Review signals:** `third-party-api (3; L97, L153)`, `financial-assumptions (1; L42)`
- **Edits:** Added subject-specific validation for defi protocol economics (2 controls plus version/evidence checks).
- **Remaining check:** confirm versioned third-party integrations, numeric claims and subject-specific assumptions against current primary sources before production use. No live integration was executed.
- **Change verification:** `89777e228f29` → `0731d740eca7` (SHA-256 prefixes).

### `defi-exploit-prevention` — Crypto Security

- **Focus:** Custody and security.
- **Review signals:** `legal-or-compliance (1; L13)`
- **Edits:** Added subject-specific validation for custody and security (2 controls plus version/evidence checks).
- **Remaining check:** confirm versioned third-party integrations, numeric claims and subject-specific assumptions against current primary sources before production use. No live integration was executed.
- **Change verification:** `6c5f53770732` → `f4fafcc9d602` (SHA-256 prefixes).

### `defi-protocol-development` — Crypto Development

- **Focus:** Contract engineering.
- **Review signals:** `absolute-percent-benchmark (1; L98)`
- **Edits:** Added subject-specific validation for contract engineering (2 controls plus version/evidence checks).
- **Remaining check:** confirm versioned third-party integrations, numeric claims and subject-specific assumptions against current primary sources before production use. No live integration was executed.
- **Change verification:** `8ea379fbc477` → `355376abb2be` (SHA-256 prefixes).

### `defi-risk-assessment` — Decentralized Finance (DeFi)

- **Focus:** DeFi protocol economics.
- **Review signals:** `absolute-percent-benchmark (3; L25, L143)`, `third-party-api (1; L75)`, `financial-assumptions (1; L112)`
- **Edits:** Added subject-specific validation for defi protocol economics (2 controls plus version/evidence checks).
- **Remaining check:** confirm versioned third-party integrations, numeric claims and subject-specific assumptions against current primary sources before production use. No live integration was executed.
- **Change verification:** `ed7fa963716a` → `2bd54d87b6c5` (SHA-256 prefixes).

### `defi-yield-strategies` — Cryptocurrency Pro

- **Focus:** DeFi protocol economics.
- **Review signals:** No automated risk patterns matched; reviewed for subject-scope limits.
- **Edits:** Added subject-specific validation for defi protocol economics (2 controls plus version/evidence checks).
- **Remaining check:** confirm versioned third-party integrations, numeric claims and subject-specific assumptions against current primary sources before production use. No live integration was executed.
- **Change verification:** `5a6f1c547680` → `1535e262a870` (SHA-256 prefixes).

### `derivatives-trading` — Crypto Trading

- **Focus:** Trading and execution.
- **Review signals:** `absolute-percent-benchmark (2; L33, L111)`, `unqualified-performance (1; L167)`, `financial-assumptions (1; L167)`
- **Edits:** Corrected an unsupported or overly categorical statement (1 occurrence(s)). Added subject-specific validation for trading and execution (2 controls plus version/evidence checks).
- **Remaining check:** confirm versioned third-party integrations, numeric claims and subject-specific assumptions against current primary sources before production use. No live integration was executed.
- **Change verification:** `e79503878561` → `986d538fc7b9` (SHA-256 prefixes).

### `diamond-pattern` — Crypto Development

- **Focus:** Contract engineering.
- **Review signals:** `third-party-api (6; L23, L24)`
- **Edits:** Added subject-specific validation for contract engineering (2 controls plus version/evidence checks).
- **Remaining check:** confirm versioned third-party integrations, numeric claims and subject-specific assumptions against current primary sources before production use. No live integration was executed.
- **Change verification:** `ba8c13c762ce` → `0d630e329874` (SHA-256 prefixes).

### `erc1155-multi-token` — Crypto Development

- **Focus:** Contract engineering.
- **Review signals:** `unguarded-install (1; L23)`, `third-party-api (8; L34, L36)`
- **Edits:** Reviewed expected issue; phrase not present, left original unchanged. Replaced 1 remote curl-to-shell installation example(s) with safer official-install verification guidance. Added subject-specific validation for contract engineering (2 controls plus version/evidence checks).
- **Remaining check:** confirm versioned third-party integrations, numeric claims and subject-specific assumptions against current primary sources before production use. No live integration was executed.
- **Change verification:** `3d672cc81da9` → `97165d731c73` (SHA-256 prefixes).

### `erc4337-smart-accounts` — Web3 Development

- **Focus:** Contract engineering.
- **Review signals:** `credential-security (5; L13, L35)`, `third-party-api (10; L19, L24)`
- **Edits:** Added subject-specific validation for contract engineering (2 controls plus version/evidence checks).
- **Remaining check:** confirm versioned third-party integrations, numeric claims and subject-specific assumptions against current primary sources before production use. No live integration was executed.
- **Change verification:** `d43c6382d088` → `a7d62a654b1a` (SHA-256 prefixes).

### `erc721-nft-contracts` — Crypto Development

- **Focus:** Contract engineering.
- **Review signals:** `credential-security (1; L53)`, `third-party-api (2; L24, L39)`
- **Edits:** Added subject-specific validation for contract engineering (2 controls plus version/evidence checks).
- **Remaining check:** confirm versioned third-party integrations, numeric claims and subject-specific assumptions against current primary sources before production use. No live integration was executed.
- **Change verification:** `e706b6846bbd` → `0b98985e2e33` (SHA-256 prefixes).

### `ethereum-fundamentals` — Cryptocurrency Pro

- **Focus:** Blockchain ecosystem / development.
- **Review signals:** `third-party-api (1; L22)`
- **Edits:** Added subject-specific validation for blockchain ecosystem / development (2 controls plus version/evidence checks).
- **Remaining check:** confirm versioned third-party integrations, numeric claims and subject-specific assumptions against current primary sources before production use. No live integration was executed.
- **Change verification:** `202afb053e87` → `b65f849e49ed` (SHA-256 prefixes).

### `ethers-js` — Web3 Development

- **Focus:** Blockchain ecosystem / development.
- **Review signals:** `unqualified-performance (1; L224)`, `credential-security (1; L62)`, `third-party-api (4; L13, L13)`
- **Edits:** Added subject-specific validation for blockchain ecosystem / development (2 controls plus version/evidence checks).
- **Remaining check:** confirm versioned third-party integrations, numeric claims and subject-specific assumptions against current primary sources before production use. No live integration was executed.
- **Change verification:** `b16677acbb52` → `a01981c48b29` (SHA-256 prefixes).

### `evm-deep-dive` — Crypto Development

- **Focus:** Blockchain ecosystem / development.
- **Review signals:** No automated risk patterns matched; reviewed for subject-scope limits.
- **Edits:** Added subject-specific validation for blockchain ecosystem / development (2 controls plus version/evidence checks).
- **Remaining check:** confirm versioned third-party integrations, numeric claims and subject-specific assumptions against current primary sources before production use. No live integration was executed.
- **Change verification:** `f96ddeb129b9` → `b80e2fd9daac` (SHA-256 prefixes).

### `exchange-infrastructure` — Crypto Infrastructure

- **Focus:** Blockchain ecosystem / development.
- **Review signals:** `absolute-percent-benchmark (1; L51)`, `credential-security (1; L164)`, `third-party-api (6; L96, L98)`, `financial-assumptions (1; L139)`, `live-data (3; L88, L134)`
- **Edits:** Added subject-specific validation for blockchain ecosystem / development (2 controls plus version/evidence checks).
- **Remaining check:** confirm versioned third-party integrations, numeric claims and subject-specific assumptions against current primary sources before production use. No live integration was executed.
- **Change verification:** `9b65d9b427f7` → `e41503474cdc` (SHA-256 prefixes).

### `exploit-analysis` — Crypto Security

- **Focus:** Custody and security.
- **Review signals:** `credential-security (1; L45)`
- **Edits:** Added subject-specific validation for custody and security (2 controls plus version/evidence checks).
- **Remaining check:** confirm versioned third-party integrations, numeric claims and subject-specific assumptions against current primary sources before production use. No live integration was executed.
- **Change verification:** `6c34dd5a5e9b` → `9911408287ed` (SHA-256 prefixes).

### `flash-loan-attack-defense` — Crypto Security

- **Focus:** Contract engineering.
- **Review signals:** `unguarded-install (1; L24)`, `third-party-api (6; L28, L33)`
- **Edits:** Replaced 1 remote curl-to-shell installation example(s) with safer official-install verification guidance. Added subject-specific validation for contract engineering (2 controls plus version/evidence checks).
- **Remaining check:** confirm versioned third-party integrations, numeric claims and subject-specific assumptions against current primary sources before production use. No live integration was executed.
- **Change verification:** `0cf2cd1019f9` → `fd5fb04ae995` (SHA-256 prefixes).

### `formal-verification` — Crypto Security

- **Focus:** Contract engineering.
- **Review signals:** `third-party-api (2; L24, L178)`
- **Edits:** Added subject-specific validation for contract engineering (2 controls plus version/evidence checks).
- **Remaining check:** confirm versioned third-party integrations, numeric claims and subject-specific assumptions against current primary sources before production use. No live integration was executed.
- **Change verification:** `9c693db3990e` → `61b7ada100a3` (SHA-256 prefixes).

### `foundry-framework` — Web3 Development

- **Focus:** Contract engineering.
- **Review signals:** `unguarded-install (1; L37)`, `credential-security (1; L398)`, `third-party-api (6; L45, L46)`
- **Edits:** Replaced 1 remote curl-to-shell installation example(s) with safer official-install verification guidance. Added subject-specific validation for contract engineering (2 controls plus version/evidence checks).
- **Remaining check:** confirm versioned third-party integrations, numeric claims and subject-specific assumptions against current primary sources before production use. No live integration was executed.
- **Change verification:** `27be2accf64c` → `b803c4d1a2bf` (SHA-256 prefixes).

### `gas-optimization-security` — Crypto Security

- **Focus:** Contract engineering.
- **Review signals:** No automated risk patterns matched; reviewed for subject-scope limits.
- **Edits:** Added subject-specific validation for contract engineering (2 controls plus version/evidence checks).
- **Remaining check:** confirm versioned third-party integrations, numeric claims and subject-specific assumptions against current primary sources before production use. No live integration was executed.
- **Change verification:** `7b179bff0118` → `fbc4338dbe2e` (SHA-256 prefixes).

### `governance-dao` — Decentralized Finance (DeFi)

- **Focus:** Blockchain ecosystem / development.
- **Review signals:** `absolute-percent-benchmark (1; L38)`
- **Edits:** Added subject-specific validation for blockchain ecosystem / development (2 controls plus version/evidence checks).
- **Remaining check:** confirm versioned third-party integrations, numeric claims and subject-specific assumptions against current primary sources before production use. No live integration was executed.
- **Change verification:** `808146fb817f` → `7720a961bf2a` (SHA-256 prefixes).

### `hardhat-development` — Web3 Development

- **Focus:** Contract engineering.
- **Review signals:** `credential-security (1; L27)`, `third-party-api (5; L27, L40)`
- **Edits:** Added subject-specific validation for contract engineering (2 controls plus version/evidence checks).
- **Remaining check:** confirm versioned third-party integrations, numeric claims and subject-specific assumptions against current primary sources before production use. No live integration was executed.
- **Change verification:** `fe9d491d04e2` → `092492956421` (SHA-256 prefixes).

### `high-frequency-trading` — Crypto Trading

- **Focus:** Trading and execution.
- **Review signals:** `hardcoded-exchange-limits (2; L37, L43)`, `third-party-api (7; L13, L21)`, `legal-or-compliance (1; L34)`, `live-data (2; L91, L212)`
- **Edits:** Added subject-specific validation for trading and execution (2 controls plus version/evidence checks).
- **Remaining check:** confirm versioned third-party integrations, numeric claims and subject-specific assumptions against current primary sources before production use. No live integration was executed.
- **Change verification:** `af23e50280c3` → `dffcfe84104a` (SHA-256 prefixes).

### `incident-response-crypto` — Crypto Security

- **Focus:** Custody and security.
- **Review signals:** `absolute-percent-benchmark (1; L112)`, `credential-security (2; L44, L44)`, `third-party-api (1; L44)`, `legal-or-compliance (8; L64, L78)`
- **Edits:** Added subject-specific validation for custody and security (2 controls plus version/evidence checks).
- **Remaining check:** confirm versioned third-party integrations, numeric claims and subject-specific assumptions against current primary sources before production use. No live integration was executed.
- **Change verification:** `cf9258b419c8` → `33958dcf8d4c` (SHA-256 prefixes).

### `indexer-architecture` — Crypto Infrastructure

- **Focus:** Blockchain ecosystem / development.
- **Review signals:** `third-party-api (1; L28)`, `live-data (2; L134, L139)`
- **Edits:** Added subject-specific validation for blockchain ecosystem / development (2 controls plus version/evidence checks).
- **Remaining check:** confirm versioned third-party integrations, numeric claims and subject-specific assumptions against current primary sources before production use. No live integration was executed.
- **Change verification:** `ab22f22e086a` → `ba7c333fe167` (SHA-256 prefixes).

### `intent-based-trading` — Decentralized Finance (DeFi)

- **Focus:** Trading and execution.
- **Review signals:** `unguarded-install (1; L25)`, `third-party-api (9; L29, L36)`
- **Edits:** Replaced 1 remote curl-to-shell installation example(s) with safer official-install verification guidance. Added subject-specific validation for trading and execution (2 controls plus version/evidence checks).
- **Remaining check:** confirm versioned third-party integrations, numeric claims and subject-specific assumptions against current primary sources before production use. No live integration was executed.
- **Change verification:** `6366ed208adb` → `be639e5ab7af` (SHA-256 prefixes).

### `ipfs-storage` — Web3 Development

- **Focus:** Blockchain ecosystem / development.
- **Review signals:** `third-party-api (3; L23, L42)`
- **Edits:** Added subject-specific validation for blockchain ecosystem / development (2 controls plus version/evidence checks).
- **Remaining check:** confirm versioned third-party integrations, numeric claims and subject-specific assumptions against current primary sources before production use. No live integration was executed.
- **Change verification:** `f0e615036633` → `f4841cb478c9` (SHA-256 prefixes).

### `launchpad-strategies` — Crypto Trading

- **Focus:** Trading and execution.
- **Review signals:** `unguarded-install (2; L27, L52)`, `credential-security (3; L38, L243)`, `third-party-api (5; L34, L36)`
- **Edits:** Replaced 1 remote curl-to-shell installation example(s) with safer official-install verification guidance. Added subject-specific validation for trading and execution (2 controls plus version/evidence checks).
- **Remaining check:** confirm versioned third-party integrations, numeric claims and subject-specific assumptions against current primary sources before production use. No live integration was executed.
- **Change verification:** `2c4635ace548` → `ecaa38c8b4d1` (SHA-256 prefixes).

### `layer-2-scaling` — Cryptocurrency Pro

- **Focus:** Blockchain ecosystem / development.
- **Review signals:** `unqualified-performance (1; L46)`
- **Edits:** Added subject-specific validation for blockchain ecosystem / development (2 controls plus version/evidence checks).
- **Remaining check:** confirm versioned third-party integrations, numeric claims and subject-specific assumptions against current primary sources before production use. No live integration was executed.
- **Change verification:** `0ff0295607ab` → `1ebd863f0dbc` (SHA-256 prefixes).

### `lending-borrowing` — Decentralized Finance (DeFi)

- **Focus:** DeFi protocol economics.
- **Review signals:** `absolute-percent-benchmark (6; L61, L69)`, `financial-assumptions (16; L35, L52)`, `legal-or-compliance (2; L162, L163)`
- **Edits:** Added subject-specific validation for defi protocol economics (2 controls plus version/evidence checks).
- **Remaining check:** confirm versioned third-party integrations, numeric claims and subject-specific assumptions against current primary sources before production use. No live integration was executed.
- **Change verification:** `48c7e09dc0f3` → `2899aa0c4c57` (SHA-256 prefixes).

### `lightning-network-development` — Web3 Development

- **Focus:** Blockchain ecosystem / development.
- **Review signals:** `third-party-api (7; L117, L117)`
- **Edits:** Added subject-specific validation for blockchain ecosystem / development (2 controls plus version/evidence checks).
- **Remaining check:** confirm versioned third-party integrations, numeric claims and subject-specific assumptions against current primary sources before production use. No live integration was executed.
- **Change verification:** `0e8caf7a6dad` → `344a5fc0ae8d` (SHA-256 prefixes).

### `liquid-staking` — Decentralized Finance (DeFi)

- **Focus:** DeFi protocol economics.
- **Review signals:** `absolute-percent-benchmark (3; L41, L51)`, `third-party-api (1; L59)`, `financial-assumptions (7; L94, L95)`, `legal-or-compliance (2; L78, L229)`
- **Edits:** Added subject-specific validation for defi protocol economics (2 controls plus version/evidence checks).
- **Remaining check:** confirm versioned third-party integrations, numeric claims and subject-specific assumptions against current primary sources before production use. No live integration was executed.
- **Change verification:** `d0d74fd58fea` → `a39769e0e501` (SHA-256 prefixes).

### `market-data-analysis` — Crypto Infrastructure

- **Focus:** Trading and execution.
- **Review signals:** No automated risk patterns matched; reviewed for subject-scope limits.
- **Edits:** Added subject-specific validation for trading and execution (2 controls plus version/evidence checks).
- **Remaining check:** confirm versioned third-party integrations, numeric claims and subject-specific assumptions against current primary sources before production use. No live integration was executed.
- **Change verification:** `d02eb9461aef` → `0de771cee95e` (SHA-256 prefixes).

### `market-making` — Crypto Trading

- **Focus:** Trading and execution.
- **Review signals:** `third-party-api (4; L72, L74)`, `live-data (2; L92, L94)`
- **Edits:** Added subject-specific validation for trading and execution (2 controls plus version/evidence checks).
- **Remaining check:** confirm versioned third-party integrations, numeric claims and subject-specific assumptions against current primary sources before production use. No live integration was executed.
- **Change verification:** `dc8c0090cba0` → `cb407444e5ab` (SHA-256 prefixes).

### `merkle-tree-patterns` — Crypto Development

- **Focus:** Contract engineering.
- **Review signals:** `unguarded-install (1; L31)`, `third-party-api (2; L24, L30)`
- **Edits:** Added subject-specific validation for contract engineering (2 controls plus version/evidence checks).
- **Remaining check:** confirm versioned third-party integrations, numeric claims and subject-specific assumptions against current primary sources before production use. No live integration was executed.
- **Change verification:** `b74f80d62b0d` → `9ead07d1c49e` (SHA-256 prefixes).

### `mev-infrastructure` — Crypto Infrastructure

- **Focus:** Blockchain ecosystem / development.
- **Review signals:** `unguarded-install (1; L31)`, `third-party-api (4; L38, L42)`, `live-data (2; L160, L162)`
- **Edits:** Replaced 1 remote curl-to-shell installation example(s) with safer official-install verification guidance. Added subject-specific validation for blockchain ecosystem / development (2 controls plus version/evidence checks).
- **Remaining check:** confirm versioned third-party integrations, numeric claims and subject-specific assumptions against current primary sources before production use. No live integration was executed.
- **Change verification:** `998bfd95f357` → `e2f9a843b16d` (SHA-256 prefixes).

### `mev-strategies` — Crypto Trading

- **Focus:** Trading and execution.
- **Review signals:** `absolute-percent-benchmark (1; L117)`, `third-party-api (3; L64, L141)`, `live-data (1; L115)`
- **Edits:** Added subject-specific validation for trading and execution (2 controls plus version/evidence checks).
- **Remaining check:** confirm versioned third-party integrations, numeric claims and subject-specific assumptions against current primary sources before production use. No live integration was executed.
- **Change verification:** `7344f5279a97` → `635fc7fc7a69` (SHA-256 prefixes).

### `monitoring-alerting` — Crypto Infrastructure

- **Focus:** Blockchain ecosystem / development.
- **Review signals:** `credential-security (1; L55)`, `third-party-api (3; L20, L137)`, `live-data (3; L32, L32)`
- **Edits:** Added subject-specific validation for blockchain ecosystem / development (2 controls plus version/evidence checks).
- **Remaining check:** confirm versioned third-party integrations, numeric claims and subject-specific assumptions against current primary sources before production use. No live integration was executed.
- **Change verification:** `f6cf3d13e2f4` → `de467f7c0001` (SHA-256 prefixes).

### `move-language` — Web3 Development

- **Focus:** Blockchain ecosystem / development.
- **Review signals:** `credential-security (2; L147, L148)`, `third-party-api (3; L134, L134)`
- **Edits:** Added subject-specific validation for blockchain ecosystem / development (2 controls plus version/evidence checks).
- **Remaining check:** confirm versioned third-party integrations, numeric claims and subject-specific assumptions against current primary sources before production use. No live integration was executed.
- **Change verification:** `76b9f64d467a` → `74659087dcd2` (SHA-256 prefixes).

### `move-security` — Crypto Security

- **Focus:** Custody and security.
- **Review signals:** No automated risk patterns matched; reviewed for subject-scope limits.
- **Edits:** Added subject-specific validation for custody and security (2 controls plus version/evidence checks).
- **Remaining check:** confirm versioned third-party integrations, numeric claims and subject-specific assumptions against current primary sources before production use. No live integration was executed.
- **Change verification:** `2689fad84ab8` → `94ec29936146` (SHA-256 prefixes).

### `near-protocol-development` — Web3 Development

- **Focus:** Blockchain ecosystem / development.
- **Review signals:** `unguarded-install (1; L23)`, `credential-security (1; L232)`, `third-party-api (7; L30, L48)`
- **Edits:** Added subject-specific validation for blockchain ecosystem / development (2 controls plus version/evidence checks).
- **Remaining check:** confirm versioned third-party integrations, numeric claims and subject-specific assumptions against current primary sources before production use. No live integration was executed.
- **Change verification:** `be736908a266` → `d67f9dee4691` (SHA-256 prefixes).

### `neon-evm` — Crypto Development

- **Focus:** Blockchain ecosystem / development.
- **Review signals:** `third-party-api (7; L15, L26)`
- **Edits:** Added subject-specific validation for blockchain ecosystem / development (2 controls plus version/evidence checks).
- **Remaining check:** confirm versioned third-party integrations, numeric claims and subject-specific assumptions against current primary sources before production use. No live integration was executed.
- **Change verification:** `26a05401f4c1` → `a3674f0f2188` (SHA-256 prefixes).

### `nft-strategy` — Cryptocurrency Pro

- **Focus:** Blockchain ecosystem / development.
- **Review signals:** `legal-or-compliance (1; L46)`
- **Edits:** Added subject-specific validation for blockchain ecosystem / development (2 controls plus version/evidence checks).
- **Remaining check:** confirm versioned third-party integrations, numeric claims and subject-specific assumptions against current primary sources before production use. No live integration was executed.
- **Change verification:** `a3266a8dbb51` → `97533b4e922e` (SHA-256 prefixes).

### `node-infrastructure` — Crypto Infrastructure

- **Focus:** Blockchain ecosystem / development.
- **Review signals:** `credential-security (1; L83)`, `third-party-api (8; L35, L83)`
- **Edits:** Added subject-specific validation for blockchain ecosystem / development (2 controls plus version/evidence checks).
- **Remaining check:** confirm versioned third-party integrations, numeric claims and subject-specific assumptions against current primary sources before production use. No live integration was executed.
- **Change verification:** `190e4cf41c2b` → `3b445797230d` (SHA-256 prefixes).

### `on-chain-analytics` — Crypto Trading

- **Focus:** Blockchain ecosystem / development.
- **Review signals:** `third-party-api (2; L91, L136)`, `live-data (3; L63, L101)`
- **Edits:** Added subject-specific validation for blockchain ecosystem / development (2 controls plus version/evidence checks).
- **Remaining check:** confirm versioned third-party integrations, numeric claims and subject-specific assumptions against current primary sources before production use. No live integration was executed.
- **Change verification:** `51a4dfd32c92` → `4c34abac6fe2` (SHA-256 prefixes).

### `operational-security` — Crypto Security

- **Focus:** Custody and security.
- **Review signals:** `credential-security (5; L109, L152)`, `third-party-api (5; L30, L61)`, `legal-or-compliance (1; L138)`, `live-data (2; L154, L166)`
- **Edits:** Added subject-specific validation for custody and security (2 controls plus version/evidence checks).
- **Remaining check:** confirm versioned third-party integrations, numeric claims and subject-specific assumptions against current primary sources before production use. No live integration was executed.
- **Change verification:** `cafd86846eb9` → `bf0409db4cf5` (SHA-256 prefixes).

### `optimism-development` — Web3 Development

- **Focus:** Blockchain ecosystem / development.
- **Review signals:** `unguarded-install (1; L29)`, `credential-security (1; L133)`, `third-party-api (14; L21, L24)`
- **Edits:** Replaced 1 remote curl-to-shell installation example(s) with safer official-install verification guidance. Added subject-specific validation for blockchain ecosystem / development (2 controls plus version/evidence checks).
- **Remaining check:** confirm versioned third-party integrations, numeric claims and subject-specific assumptions against current primary sources before production use. No live integration was executed.
- **Change verification:** `a87ad21f8a96` → `6cdd65295bcf` (SHA-256 prefixes).

### `options-vaults` — Decentralized Finance (DeFi)

- **Focus:** DeFi protocol economics.
- **Review signals:** `unguarded-install (1; L26)`, `third-party-api (1; L39)`, `live-data (2; L108, L155)`
- **Edits:** Replaced 1 remote curl-to-shell installation example(s) with safer official-install verification guidance. Added subject-specific validation for defi protocol economics (2 controls plus version/evidence checks).
- **Remaining check:** confirm versioned third-party integrations, numeric claims and subject-specific assumptions against current primary sources before production use. No live integration was executed.
- **Change verification:** `f0e35a023c87` → `bd0c419d7787` (SHA-256 prefixes).

### `oracle-manipulation-defense` — Crypto Security

- **Focus:** Custody and security.
- **Review signals:** `unguarded-install (1; L28)`, `third-party-api (7; L24, L40)`
- **Edits:** Replaced 1 remote curl-to-shell installation example(s) with safer official-install verification guidance. Added subject-specific validation for custody and security (2 controls plus version/evidence checks).
- **Remaining check:** confirm versioned third-party integrations, numeric claims and subject-specific assumptions against current primary sources before production use. No live integration was executed.
- **Change verification:** `944cd3981ca3` → `a8bf61cca737` (SHA-256 prefixes).

### `ordinals-inscriptions` — Web3 Development

- **Focus:** Blockchain ecosystem / development.
- **Review signals:** `unguarded-install (1; L34)`, `credential-security (2; L180, L180)`, `live-data (2; L84, L189)`
- **Edits:** Added subject-specific validation for blockchain ecosystem / development (2 controls plus version/evidence checks).
- **Remaining check:** confirm versioned third-party integrations, numeric claims and subject-specific assumptions against current primary sources before production use. No live integration was executed.
- **Change verification:** `22e6b43dbe3f` → `ad6a5e209345` (SHA-256 prefixes).

### `perpetual-dex` — Decentralized Finance (DeFi)

- **Focus:** Blockchain ecosystem / development.
- **Review signals:** `third-party-api (1; L85)`
- **Edits:** Added subject-specific validation for blockchain ecosystem / development (2 controls plus version/evidence checks).
- **Remaining check:** confirm versioned third-party integrations, numeric claims and subject-specific assumptions against current primary sources before production use. No live integration was executed.
- **Change verification:** `941a6bddecc7` → `16f0eabaf649` (SHA-256 prefixes).

### `polkadot-substrate` — Web3 Development

- **Focus:** Blockchain ecosystem / development.
- **Review signals:** `unguarded-install (1; L24)`, `third-party-api (20; L52, L54)`
- **Edits:** Added subject-specific validation for blockchain ecosystem / development (2 controls plus version/evidence checks).
- **Remaining check:** confirm versioned third-party integrations, numeric claims and subject-specific assumptions against current primary sources before production use. No live integration was executed.
- **Change verification:** `eab900cd181b` → `9eb0c49c9092` (SHA-256 prefixes).

### `polygon-development` — Web3 Development

- **Focus:** Blockchain ecosystem / development.
- **Review signals:** `credential-security (7; L32, L68)`, `third-party-api (3; L26, L68)`
- **Edits:** Added subject-specific validation for blockchain ecosystem / development (2 controls plus version/evidence checks).
- **Remaining check:** confirm versioned third-party integrations, numeric claims and subject-specific assumptions against current primary sources before production use. No live integration was executed.
- **Change verification:** `c9e0dbad966d` → `039617079385` (SHA-256 prefixes).

### `portfolio-construction` — Crypto Trading

- **Focus:** Trading and execution.
- **Review signals:** `absolute-percent-benchmark (3; L122, L148)`, `unqualified-performance (1; L87)`, `financial-assumptions (1; L87)`, `legal-or-compliance (3; L183, L187)`
- **Edits:** Corrected an unsupported or overly categorical statement (1 occurrence(s)). Added subject-specific validation for trading and execution (2 controls plus version/evidence checks).
- **Remaining check:** confirm versioned third-party integrations, numeric claims and subject-specific assumptions against current primary sources before production use. No live integration was executed.
- **Change verification:** `ccc61d2527a8` → `21eabce4bc12` (SHA-256 prefixes).

### `prediction-markets-onchain` — Decentralized Finance (DeFi)

- **Focus:** Blockchain ecosystem / development.
- **Review signals:** `third-party-api (8; L32, L41)`, `legal-or-compliance (1; L277)`
- **Edits:** Added subject-specific validation for blockchain ecosystem / development (2 controls plus version/evidence checks).
- **Remaining check:** confirm versioned third-party integrations, numeric claims and subject-specific assumptions against current primary sources before production use. No live integration was executed.
- **Change verification:** `b0e56fbbcd10` → `f7d02c17d294` (SHA-256 prefixes).

### `quant-trading-strategies` — Crypto Trading

- **Focus:** Trading and execution.
- **Review signals:** `third-party-api (1; L166)`, `financial-assumptions (7; L102, L103)`
- **Edits:** Added subject-specific validation for trading and execution (2 controls plus version/evidence checks).
- **Remaining check:** confirm versioned third-party integrations, numeric claims and subject-specific assumptions against current primary sources before production use. No live integration was executed.
- **Change verification:** `38980fb3c801` → `bcfb472108bd` (SHA-256 prefixes).

### `real-world-assets-rwa` — Decentralized Finance (DeFi)

- **Focus:** Regulated crypto activity.
- **Review signals:** `credential-security (1; L44)`, `third-party-api (3; L27, L35)`, `legal-or-compliance (15; L4, L4)`
- **Edits:** Added subject-specific validation for regulated crypto activity (2 controls plus version/evidence checks).
- **Remaining check:** confirm versioned third-party integrations, numeric claims and subject-specific assumptions against current primary sources before production use. No live integration was executed.
- **Change verification:** `d438e8c10a00` → `371a33a0f941` (SHA-256 prefixes).

### `reentrancy-prevention` — Crypto Security

- **Focus:** Contract engineering.
- **Review signals:** `unguarded-install (1; L28)`, `third-party-api (4; L24, L36)`
- **Edits:** Replaced 1 remote curl-to-shell installation example(s) with safer official-install verification guidance. Added subject-specific validation for contract engineering (2 controls plus version/evidence checks).
- **Remaining check:** confirm versioned third-party integrations, numeric claims and subject-specific assumptions against current primary sources before production use. No live integration was executed.
- **Change verification:** `a3c99a25c0fd` → `5e5a8c1f2cd5` (SHA-256 prefixes).

### `restaking-eigenlayer` — Decentralized Finance (DeFi)

- **Focus:** DeFi protocol economics.
- **Review signals:** `unguarded-install (1; L25)`, `credential-security (1; L51)`, `third-party-api (6; L33, L37)`
- **Edits:** Replaced 1 remote curl-to-shell installation example(s) with safer official-install verification guidance. Added subject-specific validation for defi protocol economics (2 controls plus version/evidence checks).
- **Remaining check:** confirm versioned third-party integrations, numeric claims and subject-specific assumptions against current primary sources before production use. No live integration was executed.
- **Change verification:** `55d9243b1732` → `430a676c04ce` (SHA-256 prefixes).

### `risk-management-crypto` — Crypto Trading

- **Focus:** Trading and execution.
- **Review signals:** `third-party-api (2; L96, L210)`, `financial-assumptions (29; L3, L21)`, `live-data (3; L59, L134)`
- **Edits:** Corrected an unsupported or overly categorical statement (1 occurrence(s)). Added subject-specific validation for trading and execution (2 controls plus version/evidence checks).
- **Remaining check:** confirm versioned third-party integrations, numeric claims and subject-specific assumptions against current primary sources before production use. No live integration was executed.
- **Change verification:** `78811d555326` → `b0e4bb2fc616` (SHA-256 prefixes).

### `rpc-provider-management` — Crypto Infrastructure

- **Focus:** Blockchain ecosystem / development.
- **Review signals:** `credential-security (3; L41, L41)`, `third-party-api (10; L25, L35)`
- **Edits:** Added subject-specific validation for blockchain ecosystem / development (2 controls plus version/evidence checks).
- **Remaining check:** confirm versioned third-party integrations, numeric claims and subject-specific assumptions against current primary sources before production use. No live integration was executed.
- **Change verification:** `b1bff9246605` → `67f95040aca1` (SHA-256 prefixes).

### `rust-blockchain-dev` — Crypto Development

- **Focus:** Blockchain ecosystem / development.
- **Review signals:** No automated risk patterns matched; reviewed for subject-scope limits.
- **Edits:** Added subject-specific validation for blockchain ecosystem / development (2 controls plus version/evidence checks).
- **Remaining check:** confirm versioned third-party integrations, numeric claims and subject-specific assumptions against current primary sources before production use. No live integration was executed.
- **Change verification:** `5ff5e515c57e` → `1f3d47f67369` (SHA-256 prefixes).

### `rust-solana-programs` — Web3 Development

- **Focus:** Blockchain ecosystem / development.
- **Review signals:** `unguarded-install (1; L24)`, `credential-security (2; L163, L229)`, `third-party-api (2; L34, L48)`
- **Edits:** Added subject-specific validation for blockchain ecosystem / development (2 controls plus version/evidence checks).
- **Remaining check:** confirm versioned third-party integrations, numeric claims and subject-specific assumptions against current primary sources before production use. No live integration was executed.
- **Change verification:** `984eb09c2d3b` → `0d8046522e20` (SHA-256 prefixes).

### `smart-contract-auditing` — Crypto Security

- **Focus:** Contract engineering.
- **Review signals:** No automated risk patterns matched; reviewed for subject-scope limits.
- **Edits:** Added subject-specific validation for contract engineering (2 controls plus version/evidence checks).
- **Remaining check:** confirm versioned third-party integrations, numeric claims and subject-specific assumptions against current primary sources before production use. No live integration was executed.
- **Change verification:** `b2868c71ab37` → `2f385e4c4cc0` (SHA-256 prefixes).

### `smart-contract-deployment` — Crypto Infrastructure

- **Focus:** Contract engineering.
- **Review signals:** `credential-security (5; L31, L186)`, `third-party-api (12; L13, L26)`
- **Edits:** Added subject-specific validation for contract engineering (2 controls plus version/evidence checks).
- **Remaining check:** confirm versioned third-party integrations, numeric claims and subject-specific assumptions against current primary sources before production use. No live integration was executed.
- **Change verification:** `72cc63c21233` → `ac322f9b2792` (SHA-256 prefixes).

### `smart-contract-testing` — Crypto Development

- **Focus:** Contract engineering.
- **Review signals:** No automated risk patterns matched; reviewed for subject-scope limits.
- **Edits:** Added subject-specific validation for contract engineering (2 controls plus version/evidence checks).
- **Remaining check:** confirm versioned third-party integrations, numeric claims and subject-specific assumptions against current primary sources before production use. No live integration was executed.
- **Change verification:** `310ebd899396` → `ff70c7d2dd53` (SHA-256 prefixes).

### `solana-anchor-framework` — Web3 Development

- **Focus:** Blockchain ecosystem / development.
- **Review signals:** `unguarded-install (1; L23)`, `credential-security (1; L184)`, `third-party-api (9; L19, L30)`
- **Edits:** Added subject-specific validation for blockchain ecosystem / development (2 controls plus version/evidence checks).
- **Remaining check:** confirm versioned third-party integrations, numeric claims and subject-specific assumptions against current primary sources before production use. No live integration was executed.
- **Change verification:** `8b96e8c3d6b2` → `aebcfe4fd4a0` (SHA-256 prefixes).

### `solana-rpc-infrastructure` — Crypto Infrastructure

- **Focus:** Blockchain ecosystem / development.
- **Review signals:** `third-party-api (8; L17, L24)`
- **Edits:** Added subject-specific validation for blockchain ecosystem / development (2 controls plus version/evidence checks).
- **Remaining check:** confirm versioned third-party integrations, numeric claims and subject-specific assumptions against current primary sources before production use. No live integration was executed.
- **Change verification:** `486b5a64a65f` → `91eeb63c05b9` (SHA-256 prefixes).

### `solana-security` — Crypto Security

- **Focus:** Custody and security.
- **Review signals:** `unguarded-install (1; L23)`, `third-party-api (1; L30)`
- **Edits:** Added subject-specific validation for custody and security (2 controls plus version/evidence checks).
- **Remaining check:** confirm versioned third-party integrations, numeric claims and subject-specific assumptions against current primary sources before production use. No live integration was executed.
- **Change verification:** `91dea1eb0e4d` → `a8cf845e64f9` (SHA-256 prefixes).

### `solana-trading-bots` — Crypto Trading

- **Focus:** Trading and execution.
- **Review signals:** `third-party-api (9; L28, L33)`, `live-data (2; L15, L174)`
- **Edits:** Added subject-specific validation for trading and execution (2 controls plus version/evidence checks).
- **Remaining check:** confirm versioned third-party integrations, numeric claims and subject-specific assumptions against current primary sources before production use. No live integration was executed.
- **Change verification:** `ad5ae1babb98` → `acb6998d66d3` (SHA-256 prefixes).

### `solidity-patterns` — Web3 Development

- **Focus:** Contract engineering.
- **Review signals:** `credential-security (1; L21)`
- **Edits:** Added subject-specific validation for contract engineering (2 controls plus version/evidence checks).
- **Remaining check:** confirm versioned third-party integrations, numeric claims and subject-specific assumptions against current primary sources before production use. No live integration was executed.
- **Change verification:** `e17a5dafcb3e` → `13ca31a03890` (SHA-256 prefixes).

### `solidity-smart-contracts` — Crypto Development

- **Focus:** Contract engineering.
- **Review signals:** `third-party-api (2; L174, L190)`, `financial-assumptions (1; L30)`
- **Edits:** Added subject-specific validation for contract engineering (2 controls plus version/evidence checks).
- **Remaining check:** confirm versioned third-party integrations, numeric claims and subject-specific assumptions against current primary sources before production use. No live integration was executed.
- **Change verification:** `14cf80a4b633` → `9f0c7c2cb15c` (SHA-256 prefixes).

### `stablecoin-mechanics` — Decentralized Finance (DeFi)

- **Focus:** DeFi protocol economics.
- **Review signals:** `legal-or-compliance (1; L51)`
- **Edits:** Added subject-specific validation for defi protocol economics (2 controls plus version/evidence checks).
- **Remaining check:** confirm versioned third-party integrations, numeric claims and subject-specific assumptions against current primary sources before production use. No live integration was executed.
- **Change verification:** `6d053ec7da73` → `50ae8e27ada6` (SHA-256 prefixes).

### `staking-contracts` — Crypto Development

- **Focus:** Contract engineering.
- **Review signals:** `unguarded-install (1; L21)`, `credential-security (1; L284)`, `third-party-api (1; L33)`
- **Edits:** Replaced 1 remote curl-to-shell installation example(s) with safer official-install verification guidance. Added subject-specific validation for contract engineering (2 controls plus version/evidence checks).
- **Remaining check:** confirm versioned third-party integrations, numeric claims and subject-specific assumptions against current primary sources before production use. No live integration was executed.
- **Change verification:** `be910b057411` → `ada59e9def40` (SHA-256 prefixes).

### `starknet-cairo` — Web3 Development

- **Focus:** Blockchain ecosystem / development.
- **Review signals:** `unguarded-install (2; L23, L32)`, `credential-security (2; L166, L169)`, `third-party-api (3; L27, L36)`
- **Edits:** Added subject-specific validation for blockchain ecosystem / development (2 controls plus version/evidence checks).
- **Remaining check:** confirm versioned third-party integrations, numeric claims and subject-specific assumptions against current primary sources before production use. No live integration was executed.
- **Change verification:** `290bccc36277` → `00fb6cfea4ea` (SHA-256 prefixes).

### `subgraph-development` — Crypto Development

- **Focus:** Blockchain ecosystem / development.
- **Review signals:** `third-party-api (2; L13, L21)`
- **Edits:** Added subject-specific validation for blockchain ecosystem / development (2 controls plus version/evidence checks).
- **Remaining check:** confirm versioned third-party integrations, numeric claims and subject-specific assumptions against current primary sources before production use. No live integration was executed.
- **Change verification:** `9c3e7cd29915` → `407810590201` (SHA-256 prefixes).

### `substrate-pallets` — Crypto Development

- **Focus:** Blockchain ecosystem / development.
- **Review signals:** `unguarded-install (1; L24)`, `third-party-api (1; L165)`
- **Edits:** Added subject-specific validation for blockchain ecosystem / development (2 controls plus version/evidence checks).
- **Remaining check:** confirm versioned third-party integrations, numeric claims and subject-specific assumptions against current primary sources before production use. No live integration was executed.
- **Change verification:** `ac4cd9f38ed9` → `9f59d24d2630` (SHA-256 prefixes).

### `telegram-trading-bots` — Crypto Trading

- **Focus:** Trading and execution.
- **Review signals:** `credential-security (3; L17, L275)`, `third-party-api (15; L15, L17)`, `live-data (7; L9, L13)`
- **Edits:** Added subject-specific validation for trading and execution (2 controls plus version/evidence checks).
- **Remaining check:** confirm versioned third-party integrations, numeric claims and subject-specific assumptions against current primary sources before production use. No live integration was executed.
- **Change verification:** `ce811b51bbd4` → `8e74c3f9c1af` (SHA-256 prefixes).

### `the-graph-development` — Web3 Development

- **Focus:** Blockchain ecosystem / development.
- **Review signals:** `third-party-api (4; L210, L210)`, `live-data (1; L29)`
- **Edits:** Added subject-specific validation for blockchain ecosystem / development (2 controls plus version/evidence checks).
- **Remaining check:** confirm versioned third-party integrations, numeric claims and subject-specific assumptions against current primary sources before production use. No live integration was executed.
- **Change verification:** `f5f9baa648af` → `30df7cef5dd2` (SHA-256 prefixes).

### `time-lock-security` — Crypto Security

- **Focus:** Custody and security.
- **Review signals:** `unguarded-install (1; L36)`, `credential-security (1; L45)`, `third-party-api (2; L26, L42)`
- **Edits:** Replaced 1 remote curl-to-shell installation example(s) with safer official-install verification guidance. Added subject-specific validation for custody and security (2 controls plus version/evidence checks).
- **Remaining check:** confirm versioned third-party integrations, numeric claims and subject-specific assumptions against current primary sources before production use. No live integration was executed.
- **Change verification:** `3b862f6e958f` → `82b8d2ddc247` (SHA-256 prefixes).

### `token-standards-creation` — Crypto Development

- **Focus:** Contract engineering.
- **Review signals:** `third-party-api (2; L87, L227)`, `legal-or-compliance (1; L4)`
- **Edits:** Added subject-specific validation for contract engineering (2 controls plus version/evidence checks).
- **Remaining check:** confirm versioned third-party integrations, numeric claims and subject-specific assumptions against current primary sources before production use. No live integration was executed.
- **Change verification:** `7a32871c72e1` → `9f1c99280dbc` (SHA-256 prefixes).

### `tokenomics-design` — Decentralized Finance (DeFi)

- **Focus:** Blockchain ecosystem / development.
- **Review signals:** `absolute-percent-benchmark (2; L84, L102)`, `legal-or-compliance (2; L120, L232)`
- **Edits:** Added subject-specific validation for blockchain ecosystem / development (2 controls plus version/evidence checks).
- **Remaining check:** confirm versioned third-party integrations, numeric claims and subject-specific assumptions against current primary sources before production use. No live integration was executed.
- **Change verification:** `721da0786a73` → `247a79241f14` (SHA-256 prefixes).

### `ton-development` — Web3 Development

- **Focus:** Blockchain ecosystem / development.
- **Review signals:** `credential-security (2; L235, L235)`, `third-party-api (15; L19, L24)`
- **Edits:** Added subject-specific validation for blockchain ecosystem / development (2 controls plus version/evidence checks).
- **Remaining check:** confirm versioned third-party integrations, numeric claims and subject-specific assumptions against current primary sources before production use. No live integration was executed.
- **Change verification:** `01c4fb18e98d` → `1d0d275adccb` (SHA-256 prefixes).

### `trading-bot-architecture` — Crypto Trading

- **Focus:** Trading and execution.
- **Review signals:** `credential-security (7; L301, L303)`, `third-party-api (19; L90, L133)`, `financial-assumptions (1; L250)`, `live-data (2; L137, L245)`
- **Edits:** Added subject-specific validation for trading and execution (2 controls plus version/evidence checks).
- **Remaining check:** confirm versioned third-party integrations, numeric claims and subject-specific assumptions against current primary sources before production use. No live integration was executed.
- **Change verification:** `6747c68a83b0` → `d5820783ebab` (SHA-256 prefixes).

### `treasury-management` — Crypto Infrastructure

- **Focus:** Blockchain ecosystem / development.
- **Review signals:** `absolute-percent-benchmark (1; L181)`, `financial-assumptions (1; L55)`, `legal-or-compliance (6; L99, L149)`
- **Edits:** Added subject-specific validation for blockchain ecosystem / development (2 controls plus version/evidence checks).
- **Remaining check:** confirm versioned third-party integrations, numeric claims and subject-specific assumptions against current primary sources before production use. No live integration was executed.
- **Change verification:** `d4b23ba265d3` → `4a3acfdc8004` (SHA-256 prefixes).

### `upgrade-patterns-security` — Crypto Security

- **Focus:** Contract engineering.
- **Review signals:** `credential-security (1; L163)`
- **Edits:** Added subject-specific validation for contract engineering (2 controls plus version/evidence checks).
- **Remaining check:** confirm versioned third-party integrations, numeric claims and subject-specific assumptions against current primary sources before production use. No live integration was executed.
- **Change verification:** `57301ef1f4f8` → `d700b07b8f37` (SHA-256 prefixes).

### `upgradeable-contracts` — Crypto Development

- **Focus:** Contract engineering.
- **Review signals:** `credential-security (1; L231)`, `third-party-api (3; L32, L133)`
- **Edits:** Added subject-specific validation for contract engineering (2 controls plus version/evidence checks).
- **Remaining check:** confirm versioned third-party integrations, numeric claims and subject-specific assumptions against current primary sources before production use. No live integration was executed.
- **Change verification:** `df422ff777c5` → `5e746662f5bf` (SHA-256 prefixes).

### `viem-wagmi` — Web3 Development

- **Focus:** Blockchain ecosystem / development.
- **Review signals:** `third-party-api (3; L17, L316)`
- **Edits:** Added subject-specific validation for blockchain ecosystem / development (2 controls plus version/evidence checks).
- **Remaining check:** confirm versioned third-party integrations, numeric claims and subject-specific assumptions against current primary sources before production use. No live integration was executed.
- **Change verification:** `e29d995cc452` → `3c6438a294bd` (SHA-256 prefixes).

### `wallet-connect` — Web3 Development

- **Focus:** Custody and security.
- **Review signals:** `third-party-api (10; L13, L17)`
- **Edits:** Added subject-specific validation for custody and security (2 controls plus version/evidence checks).
- **Remaining check:** confirm versioned third-party integrations, numeric claims and subject-specific assumptions against current primary sources before production use. No live integration was executed.
- **Change verification:** `ee179736f2b9` → `bddbc81613b6` (SHA-256 prefixes).

### `wallet-integration` — Crypto Development

- **Focus:** Custody and security.
- **Review signals:** `credential-security (1; L231)`, `third-party-api (3; L32, L133)`
- **Edits:** Added subject-specific validation for custody and security (2 controls plus version/evidence checks).
- **Remaining check:** confirm versioned third-party integrations, numeric claims and subject-specific assumptions against current primary sources before production use. No live integration was executed.
- **Change verification:** `e26fd264880d` → `26b08b333ac6` (SHA-256 prefixes).

### `wallet-security` — Crypto Security

- **Focus:** Custody and security.
- **Review signals:** `credential-security (13; L13, L21)`
- **Edits:** Added subject-specific validation for custody and security (2 controls plus version/evidence checks).
- **Remaining check:** confirm versioned third-party integrations, numeric claims and subject-specific assumptions against current primary sources before production use. No live integration was executed.
- **Change verification:** `c7c5b605f32d` → `2a6d9ba1d665` (SHA-256 prefixes).

### `yield-farming` — Decentralized Finance (DeFi)

- **Focus:** DeFi protocol economics.
- **Review signals:** `absolute-percent-benchmark (6; L61, L62)`, `financial-assumptions (1; L122)`
- **Edits:** Added subject-specific validation for defi protocol economics (2 controls plus version/evidence checks).
- **Remaining check:** confirm versioned third-party integrations, numeric claims and subject-specific assumptions against current primary sources before production use. No live integration was executed.
- **Change verification:** `31c74442587f` → `da2df3d69e1f` (SHA-256 prefixes).

### `zk-development` — Crypto Development

- **Focus:** Blockchain ecosystem / development.
- **Review signals:** `credential-security (1; L315)`, `financial-assumptions (1; L58)`
- **Edits:** Added subject-specific validation for blockchain ecosystem / development (2 controls plus version/evidence checks).
- **Remaining check:** confirm versioned third-party integrations, numeric claims and subject-specific assumptions against current primary sources before production use. No live integration was executed.
- **Change verification:** `0c2a0b8316d8` → `a6aa473cf963` (SHA-256 prefixes).

## External Documentation Consulted (selected high-risk areas)

- OpenZeppelin Contracts 5.x ERC1155 API: https://docs.openzeppelin.com/contracts/5.x/api/token/erc1155
- ERC-4337 specification: https://ercs.ethereum.org/ERCS/erc-4337
- Chainlink Data Feeds API: https://docs.chain.link/data-feeds/api-reference
- Chainlink freshness guidance: https://docs.chain.link/data-feeds/overview
- NIST CSF 2.0: https://www.nist.gov/cyberframework
- US SEC Investment Adviser Marketing Rule guide: https://www.sec.gov/resources-small-businesses/small-business-compliance-guides/investment-adviser-marketing
- US SEC staff FAQ (2026): https://www.sec.gov/rules-regulations/staff-guidance/division-investment-management-frequently-asked-questions/marketing-compliance-frequently-asked-questions
- OpenAI Skills documentation (metadata/discovery): https://developers.openai.com/plugins/build/skills

These references support **selected topics only**. Do not infer that every API snippet or regulatory statement in this repository was separately verified.

## Final Review Addendum (2026-10-31)

- Rechecked the revised files for YAML integrity, Markdown fence balance, duplicate Skill identity and README coverage.
- Applied additional **named, evidence-led corrections** in security, smart-account, data-migration, finance or market-data areas as relevant to this repository.
- Where current primary-source verification was unavailable, examples remain explicitly conditional rather than certified.
- Static inspection and targeted corrections are **not equivalent to compiling every contract, validating every vendor API call, or independently re-deriving every quantitative claim**.

## Named Post-Review Corrections

- `account-abstraction` — Additional verified safety, version-compatibility or financial-assumption guidance incorporated; final hash is reflected in its record above.
- `amm-mechanics` — Additional verified safety, version-compatibility or financial-assumption guidance incorporated; final hash is reflected in its record above.
- `chainlink-oracles` — Additional verified safety, version-compatibility or financial-assumption guidance incorporated; final hash is reflected in its record above.
- `erc1155-multi-token` — Additional verified safety, version-compatibility or financial-assumption guidance incorporated; final hash is reflected in its record above.
- `erc4337-smart-accounts` — Additional verified safety, version-compatibility or financial-assumption guidance incorporated; final hash is reflected in its record above.
- Multiple toolchain Skills — Removed remaining executable `curl | sh/bash` installation pipelines; see current vendor instructions and inspect installers before running commands.
