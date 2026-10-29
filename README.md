# Crypto AI Thinking Skills

A local collection of **121 reusable Skills** for crypto, DeFi, Web3 and blockchain research, design, and consultation. Includes **120 domain-specific Skills** and **1 default coordinator**. The original domain methods are kept in their own `SKILL.md` files.

## How it works

The repository uses **`crypto-skill-router` automatically for crypto/Web3 questions** through `AGENTS.md` (Codex) and `CLAUDE.md` (Claude Code). The coordinator selects the most relevant domain Skills based on the question; you can also select a specialist explicitly. This is instruction-driven behavior, not a guarantee that every agent version will automatically register every Skill.

**Manual invocation:**

| Platform | Syntax | Example |
|---|---|---|
| **Codex** | `$skill-name` | `$cosmos-sdk Explain how to build a custom SDK module.` |
| **Claude Code** | `/skill-name` | `/cosmos-sdk Explain how to build a custom SDK module.` |

To call the coordinator explicitly: **`$crypto-skill-router`** (Codex) or **`/crypto-skill-router`** (Claude Code).

**Skill layout:** `.agents/skills/<skill-name>/SKILL.md` is the single source of truth. After unpacking on Windows, run `powershell -NoProfile -ExecutionPolicy Bypass -File .\setup-claude-skills.ps1` in the repository root to expose the same library to Claude Code. Verify native discovery in the corresponding application.

## Skills by category

Expand a category, then expand any skill to see its purpose, capabilities, two example prompts, and the exact invocation commands.


<details>
<summary><strong>Default Coordinator (1)</strong></summary>

<details>
<summary><code>crypto-skill-router</code> — Automatically route crypto/Web3 requests to suitable specialist Skills</summary>

**Purpose:** Automatically route crypto/Web3 requests to suitable specialist Skills.

**What you can do:** Analyze the user question, select relevant Skills, combine methods when justified, and synthesize a coherent answer.

**Example prompts:**

- **Codex:** `$crypto-skill-router Analyze my DeFi LP strategy and select the right skills for performance and risk review.`
- **Claude Code:** `/crypto-skill-router Help me design a secure crypto trading system using the relevant specialist skills.`

**Location:** `.agents/skills/crypto-skill-router/SKILL.md`

</details>

</details>

<details>
<summary><strong>Crypto Development (24)</strong></summary>

<details>
<summary><code>anchor-programs</code> — Solana Anchor program development</summary>

**Purpose:** Solana Anchor program development.

**What you can do:** Design program accounts, constraints, instructions and tests for Anchor smart contracts.

**Example prompts:**

- **Codex:** `$anchor-programs Outline an Anchor escrow program with account validation.`
- **Claude Code:** `/anchor-programs Review Anchor PDA handling and transaction safety.`

**Location:** `.agents/skills/anchor-programs/SKILL.md`

</details>

<details>
<summary><code>blockchain-indexing-data</code> — Blockchain data pipelines and indexing</summary>

**Purpose:** Blockchain data pipelines and indexing.

**What you can do:** Design event ingestion, finality-aware sync, reorg handling and indexed queries.

**Example prompts:**

- **Codex:** `$blockchain-indexing-data Design an indexer for ERC-20 transfers with reorg protection.`
- **Claude Code:** `/blockchain-indexing-data Compare database schemas for on-chain event analytics.`

**Location:** `.agents/skills/blockchain-indexing-data/SKILL.md`

</details>

<details>
<summary><code>cairo-contracts</code> — Cairo smart contracts on Starknet</summary>

**Purpose:** Cairo smart contracts on Starknet.

**What you can do:** Structure Cairo contracts, storage, access control, deployments and testing.

**Example prompts:**

- **Codex:** `$cairo-contracts Outline a Starknet Cairo voting contract.`
- **Claude Code:** `/cairo-contracts Review Cairo storage and permission patterns.`

**Location:** `.agents/skills/cairo-contracts/SKILL.md`

</details>

<details>
<summary><code>chainlink-oracles</code> — Chainlink oracle integration</summary>

**Purpose:** Chainlink oracle integration.

**What you can do:** Select data feeds, validate freshness and decimals, and analyze oracle failure modes.

**Example prompts:**

- **Codex:** `$chainlink-oracles Design safe Chainlink price feed validation for lending.`
- **Claude Code:** `/chainlink-oracles Review oracle heartbeat and stale-price behavior.`

**Location:** `.agents/skills/chainlink-oracles/SKILL.md`

</details>

<details>
<summary><code>cosmwasm-development</code> — CosmWasm deployment and development</summary>

**Purpose:** CosmWasm deployment and development.

**What you can do:** Plan CosmWasm workflows from Rust contract design to integration tests and deployment.

**Example prompts:**

- **Codex:** `$cosmwasm-development Set up a CosmWasm contract testing plan.`
- **Claude Code:** `/cosmwasm-development Compare storage patterns for a Cosmos contract.`

**Location:** `.agents/skills/cosmwasm-development/SKILL.md`

</details>

<details>
<summary><code>cross-chain-bridges</code> — Cross-chain messaging and bridge architecture</summary>

**Purpose:** Cross-chain messaging and bridge architecture.

**What you can do:** Compare lock/mint and liquidity bridges; evaluate finality, relayers, validators and replay risks.

**Example prompts:**

- **Codex:** `$cross-chain-bridges Assess the trust assumptions of a token bridge.`
- **Claude Code:** `/cross-chain-bridges Design bridge monitoring for stuck transfers and reorgs.`

**Location:** `.agents/skills/cross-chain-bridges/SKILL.md`

</details>

<details>
<summary><code>dao-governance-contracts</code> — On-chain governance contract implementation</summary>

**Purpose:** On-chain governance contract implementation.

**What you can do:** Review quorum, timelocks, access control and governance contract design.

**Example prompts:**

- **Codex:** `$dao-governance-contracts Outline secure proposal execution contracts.`
- **Claude Code:** `/dao-governance-contracts Review quorum and timelock edge cases.`

**Location:** `.agents/skills/dao-governance-contracts/SKILL.md`

</details>

<details>
<summary><code>defi-protocol-development</code> — DeFi protocol architecture</summary>

**Purpose:** DeFi protocol architecture.

**What you can do:** Design vaults, AMMs and lending logic with explicit accounting and access controls.

**Example prompts:**

- **Codex:** `$defi-protocol-development Design the architecture of a simple lending market.`
- **Claude Code:** `/defi-protocol-development Review accounting invariants for a yield vault.`

**Location:** `.agents/skills/defi-protocol-development/SKILL.md`

</details>

<details>
<summary><code>diamond-pattern</code> — EIP-2535 diamond contract design</summary>

**Purpose:** EIP-2535 diamond contract design.

**What you can do:** Plan facets, selectors, shared storage, upgrades and authorization boundaries.

**Example prompts:**

- **Codex:** `$diamond-pattern Design a modular diamond contract with safe upgrades.`
- **Claude Code:** `/diamond-pattern Review selector collisions and facet permissions.`

**Location:** `.agents/skills/diamond-pattern/SKILL.md`

</details>

<details>
<summary><code>erc1155-multi-token</code> — ERC-1155 multi-token contracts</summary>

**Purpose:** ERC-1155 multi-token contracts.

**What you can do:** Design fungible/NFT token IDs, minting, receiver hooks, metadata and operator safety.

**Example prompts:**

- **Codex:** `$erc1155-multi-token Write a secure ERC-1155 minting and supply design.`
- **Claude Code:** `/erc1155-multi-token Audit batch transfer and token-URI behavior.`

**Location:** `.agents/skills/erc1155-multi-token/SKILL.md`

</details>

<details>
<summary><code>erc721-nft-contracts</code> — ERC-721 NFT contracts</summary>

**Purpose:** ERC-721 NFT contracts.

**What you can do:** Design minting, royalties, metadata, enumeration and access control.

**Example prompts:**

- **Codex:** `$erc721-nft-contracts Design an ERC-721 collection with capped minting.`
- **Claude Code:** `/erc721-nft-contracts Audit NFT metadata and approval permissions.`

**Location:** `.agents/skills/erc721-nft-contracts/SKILL.md`

</details>

<details>
<summary><code>evm-deep-dive</code> — EVM internals and low-level gas behavior</summary>

**Purpose:** EVM internals and low-level gas behavior.

**What you can do:** Analyze opcodes, calldata, storage, ABI, memory and gas costs.

**Example prompts:**

- **Codex:** `$evm-deep-dive Explain a Solidity storage layout and slot calculation.`
- **Claude Code:** `/evm-deep-dive Review an EVM assembly optimization for correctness.`

**Location:** `.agents/skills/evm-deep-dive/SKILL.md`

</details>

<details>
<summary><code>merkle-tree-patterns</code> — Merkle proofs and commitment schemes</summary>

**Purpose:** Merkle proofs and commitment schemes.

**What you can do:** Design roots, proofs, claim lists, domain separation and replay protection.

**Example prompts:**

- **Codex:** `$merkle-tree-patterns Design a Merkle airdrop claim scheme.`
- **Claude Code:** `/merkle-tree-patterns Review leaf hashing and proof verification edge cases.`

**Location:** `.agents/skills/merkle-tree-patterns/SKILL.md`

</details>

<details>
<summary><code>neon-evm</code> — Neon EVM on Solana</summary>

**Purpose:** Neon EVM on Solana.

**What you can do:** Assess EVM compatibility and execution constraints across Neon/Solana.

**Example prompts:**

- **Codex:** `$neon-evm Plan an Ethereum contract integration with Neon EVM.`
- **Claude Code:** `/neon-evm Compare Neon EVM and native Solana program trade-offs.`

**Location:** `.agents/skills/neon-evm/SKILL.md`

</details>

<details>
<summary><code>rust-blockchain-dev</code> — Rust blockchain engineering</summary>

**Purpose:** Rust blockchain engineering.

**What you can do:** Build safe serialization, consensus-adjacent services, async tasks and crypto utilities.

**Example prompts:**

- **Codex:** `$rust-blockchain-dev Review a Rust blockchain service architecture.`
- **Claude Code:** `/rust-blockchain-dev Plan testing for binary data parsing and state safety.`

**Location:** `.agents/skills/rust-blockchain-dev/SKILL.md`

</details>

<details>
<summary><code>smart-contract-testing</code> — Solidity contract testing strategies</summary>

**Purpose:** Solidity contract testing strategies.

**What you can do:** Design unit, fuzz, invariant, fork and integration testing.

**Example prompts:**

- **Codex:** `$smart-contract-testing Write an invariant testing plan for a lending vault.`
- **Claude Code:** `/smart-contract-testing Compare mocks and mainnet-fork tests.`

**Location:** `.agents/skills/smart-contract-testing/SKILL.md`

</details>

<details>
<summary><code>solidity-smart-contracts</code> — Solidity smart contract engineering</summary>

**Purpose:** Solidity smart contract engineering.

**What you can do:** Design secure contracts, storage, ABI, access control and tests.

**Example prompts:**

- **Codex:** `$solidity-smart-contracts Write an ERC-20 token with controlled minting requirements.`
- **Claude Code:** `/solidity-smart-contracts Review contract design for security and gas trade-offs.`

**Location:** `.agents/skills/solidity-smart-contracts/SKILL.md`

</details>

<details>
<summary><code>staking-contracts</code> — Staking contract design</summary>

**Purpose:** Staking contract design.

**What you can do:** Design accrual, reward distribution, cooldowns, slashing and withdrawal logic.

**Example prompts:**

- **Codex:** `$staking-contracts Design a staking reward accounting model.`
- **Claude Code:** `/staking-contracts Review staking contract time and precision edge cases.`

**Location:** `.agents/skills/staking-contracts/SKILL.md`

</details>

<details>
<summary><code>subgraph-development</code> — The Graph subgraph architecture</summary>

**Purpose:** The Graph subgraph architecture.

**What you can do:** Design manifests, mappings, entities and deterministic event indexing.

**Example prompts:**

- **Codex:** `$subgraph-development Design a subgraph for a DeFi lending market.`
- **Claude Code:** `/subgraph-development Review event handlers for chain reorganizations.`

**Location:** `.agents/skills/subgraph-development/SKILL.md`

</details>

<details>
<summary><code>substrate-pallets</code> — Substrate FRAME pallet design</summary>

**Purpose:** Substrate FRAME pallet design.

**What you can do:** Implement storage, extrinsics, events, weights and runtime integration.

**Example prompts:**

- **Codex:** `$substrate-pallets Design a FRAME pallet for on-chain registries.`
- **Claude Code:** `/substrate-pallets Review pallet storage migration and benchmarking.`

**Location:** `.agents/skills/substrate-pallets/SKILL.md`

</details>

<details>
<summary><code>token-standards-creation</code> — Token standards and custom token design</summary>

**Purpose:** Token standards and custom token design.

**What you can do:** Compare ERC standards, extensions, decimals and compliance constraints.

**Example prompts:**

- **Codex:** `$token-standards-creation Choose a token standard for an in-game economy.`
- **Claude Code:** `/token-standards-creation Review custom token transfer hooks for compatibility.`

**Location:** `.agents/skills/token-standards-creation/SKILL.md`

</details>

<details>
<summary><code>upgradeable-contracts</code> — Upgradeable Solidity contracts</summary>

**Purpose:** Upgradeable Solidity contracts.

**What you can do:** Implement and test proxy patterns, storage gaps and initialization rules.

**Example prompts:**

- **Codex:** `$upgradeable-contracts Design a safe upgradeable ERC-20 architecture.`
- **Claude Code:** `/upgradeable-contracts Audit storage changes between contract versions.`

**Location:** `.agents/skills/upgradeable-contracts/SKILL.md`

</details>

<details>
<summary><code>wallet-integration</code> — Wallet UX and transaction integration</summary>

**Purpose:** Wallet UX and transaction integration.

**What you can do:** Design signing, connection, chain switching and safety UX.

**Example prompts:**

- **Codex:** `$wallet-integration Build a dApp wallet onboarding flow.`
- **Claude Code:** `/wallet-integration Review EIP-1193 and signing permissions.`

**Location:** `.agents/skills/wallet-integration/SKILL.md`

</details>

<details>
<summary><code>zk-development</code> — Zero-knowledge proof application development</summary>

**Purpose:** Zero-knowledge proof application development.

**What you can do:** Compare circuits, proving systems, trusted setups and verification costs.

**Example prompts:**

- **Codex:** `$zk-development Design a ZK proof-of-membership workflow.`
- **Claude Code:** `/zk-development Review circuit soundness and proof verification assumptions.`

**Location:** `.agents/skills/zk-development/SKILL.md`

</details>

</details>

<details>
<summary><strong>Decentralized Finance (DeFi) (16)</strong></summary>

<details>
<summary><code>amm-mechanics</code> — AMM pricing and LP mathematics</summary>

**Purpose:** AMM pricing and LP mathematics.

**What you can do:** Calculate swaps, price impact, LP fees and impermanent loss; compare Uniswap, Curve and Balancer.

**Example prompts:**

- **Codex:** `$amm-mechanics Estimate a Uniswap v3 LP position's net return versus holding.`
- **Claude Code:** `/amm-mechanics Explain how stable-swap amplification affects depeg risk.`

**Location:** `.agents/skills/amm-mechanics/SKILL.md`

</details>

<details>
<summary><code>cross-chain-defi</code> — Multi-chain DeFi strategies</summary>

**Purpose:** Multi-chain DeFi strategies.

**What you can do:** Evaluate bridge costs, composability, liquidity fragmentation and correlated bridge risk.

**Example prompts:**

- **Codex:** `$cross-chain-defi Compare multi-chain yield options net of bridging costs.`
- **Claude Code:** `/cross-chain-defi Design cross-chain capital movement with failure contingencies.`

**Location:** `.agents/skills/cross-chain-defi/SKILL.md`

</details>

<details>
<summary><code>defi-composability</code> — DeFi protocol integration patterns</summary>

**Purpose:** DeFi protocol integration patterns.

**What you can do:** Analyze composability, atomic transactions, approval flows and cascading dependencies.

**Example prompts:**

- **Codex:** `$defi-composability Review integrating a lending market with a DEX.`
- **Claude Code:** `/defi-composability Map failure propagation through a DeFi position.`

**Location:** `.agents/skills/defi-composability/SKILL.md`

</details>

<details>
<summary><code>defi-risk-assessment</code> — DeFi risk evaluation</summary>

**Purpose:** DeFi risk evaluation.

**What you can do:** Score technical, liquidity, governance, market and counterparty risk.

**Example prompts:**

- **Codex:** `$defi-risk-assessment Prepare a DeFi risk report for an LP position.`
- **Claude Code:** `/defi-risk-assessment Assess a protocol's governance and oracle dependencies.`

**Location:** `.agents/skills/defi-risk-assessment/SKILL.md`

</details>

<details>
<summary><code>governance-dao</code> — DAO governance mechanics and tooling</summary>

**Purpose:** DAO governance mechanics and tooling.

**What you can do:** Assess delegation, voting models, timelocks and stakeholder incentives.

**Example prompts:**

- **Codex:** `$governance-dao Design token governance controls for a DAO.`
- **Claude Code:** `/governance-dao Review governance capture protections.`

**Location:** `.agents/skills/governance-dao/SKILL.md`

</details>

<details>
<summary><code>intent-based-trading</code> — Intent and solver-based execution</summary>

**Purpose:** Intent and solver-based execution.

**What you can do:** Compare intent-based orders, solvers, settlement, signatures and execution quality.

**Example prompts:**

- **Codex:** `$intent-based-trading Design a solver-based swap intent model.`
- **Claude Code:** `/intent-based-trading Assess replay and settlement risk in intent systems.`

**Location:** `.agents/skills/intent-based-trading/SKILL.md`

</details>

<details>
<summary><code>lending-borrowing</code> — DeFi lending market mechanics</summary>

**Purpose:** DeFi lending market mechanics.

**What you can do:** Model collateral factors, interest rates, liquidation thresholds and bad debt.

**Example prompts:**

- **Codex:** `$lending-borrowing Assess liquidation risk for a collateralized borrow.`
- **Claude Code:** `/lending-borrowing Explain lending utilization and interest-rate curves.`

**Location:** `.agents/skills/lending-borrowing/SKILL.md`

</details>

<details>
<summary><code>liquid-staking</code> — Liquid staking token economics</summary>

**Purpose:** Liquid staking token economics.

**What you can do:** Analyze staking rewards, withdrawal queues, depeg and validator risk.

**Example prompts:**

- **Codex:** `$liquid-staking Compare liquid staking and direct staking risks.`
- **Claude Code:** `/liquid-staking Assess LST collateral and redemption scenarios.`

**Location:** `.agents/skills/liquid-staking/SKILL.md`

</details>

<details>
<summary><code>options-vaults</code> — DeFi option vault strategies</summary>

**Purpose:** DeFi option vault strategies.

**What you can do:** Evaluate structured yield, option Greeks, settlement and vault-specific risk.

**Example prompts:**

- **Codex:** `$options-vaults Model an options vault payout under price scenarios.`
- **Claude Code:** `/options-vaults Review collateral and liquidation risks for a structured vault.`

**Location:** `.agents/skills/options-vaults/SKILL.md`

</details>

<details>
<summary><code>perpetual-dex</code> — Perpetual DEX architecture</summary>

**Purpose:** Perpetual DEX architecture.

**What you can do:** Analyze funding, margin, liquidation engines and oracle dependencies.

**Example prompts:**

- **Codex:** `$perpetual-dex Design a perpetual DEX risk model.`
- **Claude Code:** `/perpetual-dex Compare vAMM and orderbook perpetual exchanges.`

**Location:** `.agents/skills/perpetual-dex/SKILL.md`

</details>

<details>
<summary><code>prediction-markets-onchain</code> — On-chain prediction market protocols</summary>

**Purpose:** On-chain prediction market protocols.

**What you can do:** Design markets, oracles, settlement, dispute resolution and incentives.

**Example prompts:**

- **Codex:** `$prediction-markets-onchain Outline a prediction market settlement mechanism.`
- **Claude Code:** `/prediction-markets-onchain Review oracle disputes and market manipulation risks.`

**Location:** `.agents/skills/prediction-markets-onchain/SKILL.md`

</details>

<details>
<summary><code>real-world-assets-rwa</code> — On-chain real-world assets</summary>

**Purpose:** On-chain real-world assets.

**What you can do:** Analyze tokenization, custody, legal rights, compliance and oracle dependencies.

**Example prompts:**

- **Codex:** `$real-world-assets-rwa Design a tokenized treasury asset risk checklist.`
- **Claude Code:** `/real-world-assets-rwa Compare RWA transfer restrictions and redemption models.`

**Location:** `.agents/skills/real-world-assets-rwa/SKILL.md`

</details>

<details>
<summary><code>restaking-eigenlayer</code> — Restaking and shared-security economics</summary>

**Purpose:** Restaking and shared-security economics.

**What you can do:** Analyze restaking rewards, slashing, operator concentration and withdrawal constraints.

**Example prompts:**

- **Codex:** `$restaking-eigenlayer Evaluate EigenLayer-style restaking risks.`
- **Claude Code:** `/restaking-eigenlayer Compare validator exposure across restaking services.`

**Location:** `.agents/skills/restaking-eigenlayer/SKILL.md`

</details>

<details>
<summary><code>stablecoin-mechanics</code> — Stablecoin peg mechanisms and risk</summary>

**Purpose:** Stablecoin peg mechanisms and risk.

**What you can do:** Analyze backing, redemptions, liquidity, oracle risk and depeg scenarios.

**Example prompts:**

- **Codex:** `$stablecoin-mechanics Stress test a stablecoin backing and redemption model.`
- **Claude Code:** `/stablecoin-mechanics Compare crypto-backed versus fiat-backed stablecoin risks.`

**Location:** `.agents/skills/stablecoin-mechanics/SKILL.md`

</details>

<details>
<summary><code>tokenomics-design</code> — Crypto token economic design</summary>

**Purpose:** Crypto token economic design.

**What you can do:** Model supply, vesting, incentives, treasury, emissions and value capture.

**Example prompts:**

- **Codex:** `$tokenomics-design Design a token emissions and vesting model.`
- **Claude Code:** `/tokenomics-design Stress test inflation and incentive sustainability.`

**Location:** `.agents/skills/tokenomics-design/SKILL.md`

</details>

<details>
<summary><code>yield-farming</code> — DeFi liquidity mining returns</summary>

**Purpose:** DeFi liquidity mining returns.

**What you can do:** Compare farming rewards, emissions, IL, gas and smart-contract risk.

**Example prompts:**

- **Codex:** `$yield-farming Calculate net APY of a yield farming position.`
- **Claude Code:** `/yield-farming Evaluate reward-token sell pressure in farming pools.`

**Location:** `.agents/skills/yield-farming/SKILL.md`

</details>

</details>

<details>
<summary><strong>Crypto Security (16)</strong></summary>

<details>
<summary><code>blockchain-forensics</code> — On-chain tracing and investigation</summary>

**Purpose:** On-chain tracing and investigation.

**What you can do:** Trace fund flows, cluster related activity cautiously and document evidence limitations.

**Example prompts:**

- **Codex:** `$blockchain-forensics Create a defensible tracing plan for an Ethereum address.`
- **Claude Code:** `/blockchain-forensics Explain what can and cannot be inferred from wallet clusters.`

**Location:** `.agents/skills/blockchain-forensics/SKILL.md`

</details>

<details>
<summary><code>defi-exploit-prevention</code> — Preventing DeFi protocol exploits</summary>

**Purpose:** Preventing DeFi protocol exploits.

**What you can do:** Review oracle manipulation, accounting bugs, reentrancy and economic attack surfaces.

**Example prompts:**

- **Codex:** `$defi-exploit-prevention Create an exploit-resistance checklist for a vault.`
- **Claude Code:** `/defi-exploit-prevention Assess flash-loan and price manipulation exposure.`

**Location:** `.agents/skills/defi-exploit-prevention/SKILL.md`

</details>

<details>
<summary><code>exploit-analysis</code> — Smart contract exploit investigation</summary>

**Purpose:** Smart contract exploit investigation.

**What you can do:** Reconstruct exploit transaction sequences, assess root causes and propose mitigations.

**Example prompts:**

- **Codex:** `$exploit-analysis Write a postmortem outline for a DeFi exploit.`
- **Claude Code:** `/exploit-analysis Analyze suspicious contract calls without assuming attribution.`

**Location:** `.agents/skills/exploit-analysis/SKILL.md`

</details>

<details>
<summary><code>flash-loan-attack-defense</code> — Flash-loan attack defense</summary>

**Purpose:** Flash-loan attack defense.

**What you can do:** Analyze atomic borrowing risk, price manipulation and accounting invariants.

**Example prompts:**

- **Codex:** `$flash-loan-attack-defense Audit a lending protocol for flash-loan-related risk.`
- **Claude Code:** `/flash-loan-attack-defense Explain defenses against reserve manipulation.`

**Location:** `.agents/skills/flash-loan-attack-defense/SKILL.md`

</details>

<details>
<summary><code>formal-verification</code> — Formal methods for smart contracts</summary>

**Purpose:** Formal methods for smart contracts.

**What you can do:** Define invariants, specifications and proof/test boundaries.

**Example prompts:**

- **Codex:** `$formal-verification Draft formal invariants for a lending contract.`
- **Claude Code:** `/formal-verification Compare fuzzing, symbolic execution and formal proofs.`

**Location:** `.agents/skills/formal-verification/SKILL.md`

</details>

<details>
<summary><code>gas-optimization-security</code> — Gas optimization with security checks</summary>

**Purpose:** Gas optimization with security checks.

**What you can do:** Measure storage/calldata costs and benchmark safe Solidity optimizations.

**Example prompts:**

- **Codex:** `$gas-optimization-security Optimize a Solidity function without changing semantics.`
- **Claude Code:** `/gas-optimization-security Review gas savings against security and readability trade-offs.`

**Location:** `.agents/skills/gas-optimization-security/SKILL.md`

</details>

<details>
<summary><code>incident-response-crypto</code> — Crypto security incident response</summary>

**Purpose:** Crypto security incident response.

**What you can do:** Create containment, evidence preservation, communications and recovery plans.

**Example prompts:**

- **Codex:** `$incident-response-crypto Draft an incident playbook for wallet compromise.`
- **Claude Code:** `/incident-response-crypto List evidence to preserve after a contract exploit.`

**Location:** `.agents/skills/incident-response-crypto/SKILL.md`

</details>

<details>
<summary><code>move-security</code> — Move contract security</summary>

**Purpose:** Move contract security.

**What you can do:** Check capabilities, resource handling, authorization and invariants.

**Example prompts:**

- **Codex:** `$move-security Audit a Move coin module for permission errors.`
- **Claude Code:** `/move-security Design property tests for Move resource safety.`

**Location:** `.agents/skills/move-security/SKILL.md`

</details>

<details>
<summary><code>operational-security</code> — Crypto operational security</summary>

**Purpose:** Crypto operational security.

**What you can do:** Design key handling, signing policy, access separation and incident readiness.

**Example prompts:**

- **Codex:** `$operational-security Write an operational security policy for a crypto team.`
- **Claude Code:** `/operational-security Review a wallet signing and permissions process.`

**Location:** `.agents/skills/operational-security/SKILL.md`

</details>

<details>
<summary><code>oracle-manipulation-defense</code> — Oracle manipulation resistance</summary>

**Purpose:** Oracle manipulation resistance.

**What you can do:** Model oracle trust, deviation thresholds, TWAP windows and manipulation costs.

**Example prompts:**

- **Codex:** `$oracle-manipulation-defense Audit a protocol's price oracle controls.`
- **Claude Code:** `/oracle-manipulation-defense Compare Chainlink feeds and AMM TWAP attack surfaces.`

**Location:** `.agents/skills/oracle-manipulation-defense/SKILL.md`

</details>

<details>
<summary><code>reentrancy-prevention</code> — Reentrancy defenses in Solidity</summary>

**Purpose:** Reentrancy defenses in Solidity.

**What you can do:** Audit external calls, callbacks, state updates and guard patterns.

**Example prompts:**

- **Codex:** `$reentrancy-prevention Review a vault for cross-function reentrancy.`
- **Claude Code:** `/reentrancy-prevention Explain checks-effects-interactions and its limitations.`

**Location:** `.agents/skills/reentrancy-prevention/SKILL.md`

</details>

<details>
<summary><code>smart-contract-auditing</code> — Smart contract audit process</summary>

**Purpose:** Smart contract audit process.

**What you can do:** Create threat models, manual review checklists, fuzz tests and severity assessment.

**Example prompts:**

- **Codex:** `$smart-contract-auditing Audit a token contract for authorization and supply issues.`
- **Claude Code:** `/smart-contract-auditing Write a risk-ranked smart contract audit report.`

**Location:** `.agents/skills/smart-contract-auditing/SKILL.md`

</details>

<details>
<summary><code>solana-security</code> — Solana program security</summary>

**Purpose:** Solana program security.

**What you can do:** Audit PDA seeds, account ownership, CPI, signers and arithmetic.

**Example prompts:**

- **Codex:** `$solana-security Review Solana account validation rules.`
- **Claude Code:** `/solana-security Create a Solana exploit prevention checklist.`

**Location:** `.agents/skills/solana-security/SKILL.md`

</details>

<details>
<summary><code>time-lock-security</code> — Timelock governance security</summary>

**Purpose:** Timelock governance security.

**What you can do:** Review minimum delays, scheduling, executors and cancellation authority.

**Example prompts:**

- **Codex:** `$time-lock-security Audit a protocol governance timelock.`
- **Claude Code:** `/time-lock-security Analyze timelock bypass and role escalation risks.`

**Location:** `.agents/skills/time-lock-security/SKILL.md`

</details>

<details>
<summary><code>upgrade-patterns-security</code> — Upgradeable contract security</summary>

**Purpose:** Upgradeable contract security.

**What you can do:** Audit proxy admin roles, initialization, storage layout and upgrade flows.

**Example prompts:**

- **Codex:** `$upgrade-patterns-security Review a UUPS upgrade authorization model.`
- **Claude Code:** `/upgrade-patterns-security Compare transparent proxy and beacon risks.`

**Location:** `.agents/skills/upgrade-patterns-security/SKILL.md`

</details>

<details>
<summary><code>wallet-security</code> — Wallet and signing security</summary>

**Purpose:** Wallet and signing security.

**What you can do:** Assess seed storage, session keys, approvals, phishing and recovery.

**Example prompts:**

- **Codex:** `$wallet-security Create a wallet threat model for a dApp.`
- **Claude Code:** `/wallet-security Design a secure wallet backup and recovery checklist.`

**Location:** `.agents/skills/wallet-security/SKILL.md`

</details>

</details>

<details>
<summary><strong>Crypto Trading (14)</strong></summary>

<details>
<summary><code>airdrop-farming</code> — Airdrop research and participation</summary>

**Purpose:** Airdrop research and participation.

**What you can do:** Assess tokenless protocols, track eligibility, estimate participation costs, and manage claim risks.

**Example prompts:**

- **Codex:** `$airdrop-farming Compare three potential airdrop opportunities using confirmed evidence.`
- **Claude Code:** `/airdrop-farming Design a safe airdrop participation and eligibility-tracking plan.`

**Location:** `.agents/skills/airdrop-farming/SKILL.md`

</details>

<details>
<summary><code>algorithmic-execution</code> — Crypto order execution strategies</summary>

**Purpose:** Crypto order execution strategies.

**What you can do:** Compare TWAP, VWAP, iceberg and SOR; model fees, slippage, partial fills and API failures.

**Example prompts:**

- **Codex:** `$algorithmic-execution Design a TWAP strategy for a large BTC order with fill controls.`
- **Claude Code:** `/algorithmic-execution Audit a new-listing execution workflow for slippage and duplicate orders.`

**Location:** `.agents/skills/algorithmic-execution/SKILL.md`

</details>

<details>
<summary><code>derivatives-trading</code> — Crypto futures and options trading</summary>

**Purpose:** Crypto futures and options trading.

**What you can do:** Analyze funding, basis, Greeks, margin, liquidation and hedging approaches.

**Example prompts:**

- **Codex:** `$derivatives-trading Explain a perpetual futures funding trade with risks.`
- **Claude Code:** `/derivatives-trading Stress test an options hedging position.`

**Location:** `.agents/skills/derivatives-trading/SKILL.md`

</details>

<details>
<summary><code>high-frequency-trading</code> — High-frequency cryptocurrency strategies</summary>

**Purpose:** High-frequency cryptocurrency strategies.

**What you can do:** Evaluate latency, queue position, maker/taker economics and microstructure risk.

**Example prompts:**

- **Codex:** `$high-frequency-trading Design an HFT simulation with latency and fees.`
- **Claude Code:** `/high-frequency-trading Audit order book event handling for race conditions.`

**Location:** `.agents/skills/high-frequency-trading/SKILL.md`

</details>

<details>
<summary><code>launchpad-strategies</code> — Crypto launchpad participation</summary>

**Purpose:** Crypto launchpad participation.

**What you can do:** Evaluate eligibility, allocations, lockups, fees and downside scenarios.

**Example prompts:**

- **Codex:** `$launchpad-strategies Compare two token launchpad offerings.`
- **Claude Code:** `/launchpad-strategies Model vesting and liquidity risks after token launch.`

**Location:** `.agents/skills/launchpad-strategies/SKILL.md`

</details>

<details>
<summary><code>market-making</code> — Crypto market making</summary>

**Purpose:** Crypto market making.

**What you can do:** Model spreads, inventory skew, adverse selection, hedging and exchange fees.

**Example prompts:**

- **Codex:** `$market-making Design a market-making spread and inventory model.`
- **Claude Code:** `/market-making Assess adverse selection during high volatility.`

**Location:** `.agents/skills/market-making/SKILL.md`

</details>

<details>
<summary><code>mev-strategies</code> — MEV strategy research</summary>

**Purpose:** MEV strategy research.

**What you can do:** Analyze arbitrage, liquidation MEV, transaction ordering and execution risk.

**Example prompts:**

- **Codex:** `$mev-strategies Compare arbitrage versus liquidation searcher economics.`
- **Claude Code:** `/mev-strategies Review ethical and technical risks of MEV strategies.`

**Location:** `.agents/skills/mev-strategies/SKILL.md`

</details>

<details>
<summary><code>on-chain-analytics</code> — Blockchain analytics workflows</summary>

**Purpose:** Blockchain analytics workflows.

**What you can do:** Build activity metrics, cohort analysis, wallet behavior and protocol dashboards.

**Example prompts:**

- **Codex:** `$on-chain-analytics Design a retention dashboard for DeFi users.`
- **Claude Code:** `/on-chain-analytics Assess data biases in wallet activity metrics.`

**Location:** `.agents/skills/on-chain-analytics/SKILL.md`

</details>

<details>
<summary><code>portfolio-construction</code> — Crypto portfolio design</summary>

**Purpose:** Crypto portfolio design.

**What you can do:** Model diversification, risk budgets, correlations, drawdowns and liquidity.

**Example prompts:**

- **Codex:** `$portfolio-construction Build a risk-budgeted crypto portfolio framework.`
- **Claude Code:** `/portfolio-construction Stress test correlated token exposures.`

**Location:** `.agents/skills/portfolio-construction/SKILL.md`

</details>

<details>
<summary><code>quant-trading-strategies</code> — Quantitative crypto strategy research</summary>

**Purpose:** Quantitative crypto strategy research.

**What you can do:** Design signals, backtests, walk-forward tests, cost models and validation.

**Example prompts:**

- **Codex:** `$quant-trading-strategies Design a walk-forward backtest for a crypto momentum signal.`
- **Claude Code:** `/quant-trading-strategies Assess look-ahead bias and slippage assumptions.`

**Location:** `.agents/skills/quant-trading-strategies/SKILL.md`

</details>

<details>
<summary><code>risk-management-crypto</code> — Risk management for crypto positions</summary>

**Purpose:** Risk management for crypto positions.

**What you can do:** Calculate VaR/expected shortfall, sizing, stress losses and liquidation exposure.

**Example prompts:**

- **Codex:** `$risk-management-crypto Design position and drawdown limits for a trading strategy.`
- **Claude Code:** `/risk-management-crypto Assess margin safety under market stress.`

**Location:** `.agents/skills/risk-management-crypto/SKILL.md`

</details>

<details>
<summary><code>solana-trading-bots</code> — Solana trading bot infrastructure</summary>

**Purpose:** Solana trading bot infrastructure.

**What you can do:** Plan subscriptions, transaction construction, priority fees, execution and safeguards.

**Example prompts:**

- **Codex:** `$solana-trading-bots Design a Solana trading bot execution pipeline.`
- **Claude Code:** `/solana-trading-bots Audit duplicate transaction and failed-fill behavior.`

**Location:** `.agents/skills/solana-trading-bots/SKILL.md`

</details>

<details>
<summary><code>telegram-trading-bots</code> — Telegram crypto trading bots</summary>

**Purpose:** Telegram crypto trading bots.

**What you can do:** Design bot UX, permissions, execution integration and key security.

**Example prompts:**

- **Codex:** `$telegram-trading-bots Plan a Telegram trading bot with approval safeguards.`
- **Claude Code:** `/telegram-trading-bots Audit chat commands and wallet key storage risks.`

**Location:** `.agents/skills/telegram-trading-bots/SKILL.md`

</details>

<details>
<summary><code>trading-bot-architecture</code> — Trading system architecture</summary>

**Purpose:** Trading system architecture.

**What you can do:** Design event-driven bots, exchange adapters, state recovery, monitoring and deployment.

**Example prompts:**

- **Codex:** `$trading-bot-architecture Design a modular event-driven crypto bot.`
- **Claude Code:** `/trading-bot-architecture Review crash recovery and order reconciliation.`

**Location:** `.agents/skills/trading-bot-architecture/SKILL.md`

</details>

</details>

<details>
<summary><strong>Crypto Infrastructure (14)</strong></summary>

<details>
<summary><code>api-integration-crypto</code> — Exchange and blockchain API integration</summary>

**Purpose:** Exchange and blockchain API integration.

**What you can do:** Plan reliable REST/WebSocket integrations, retries, pagination, signatures and reconciliation.

**Example prompts:**

- **Codex:** `$api-integration-crypto Design a fault-tolerant crypto exchange WebSocket client.`
- **Claude Code:** `/api-integration-crypto Review API key handling and order status recovery.`

**Location:** `.agents/skills/api-integration-crypto/SKILL.md`

</details>

<details>
<summary><code>crypto-compliance</code> — Crypto compliance and financial crime controls</summary>

**Purpose:** Crypto compliance and financial crime controls.

**What you can do:** Analyze KYC/AML, sanctions screening, jurisdictional obligations and auditability.

**Example prompts:**

- **Codex:** `$crypto-compliance Draft a crypto platform compliance gap checklist.`
- **Claude Code:** `/crypto-compliance Compare operational controls for custody and exchange services.`

**Location:** `.agents/skills/crypto-compliance/SKILL.md`

</details>

<details>
<summary><code>crypto-fund-operations</code> — Crypto fund operating procedures</summary>

**Purpose:** Crypto fund operating procedures.

**What you can do:** Design NAV, reconciliation, reporting, custody segregation and investment operations.

**Example prompts:**

- **Codex:** `$crypto-fund-operations Build a crypto fund daily reconciliation workflow.`
- **Claude Code:** `/crypto-fund-operations Review valuation policies for illiquid tokens.`

**Location:** `.agents/skills/crypto-fund-operations/SKILL.md`

</details>

<details>
<summary><code>data-pipeline-crypto</code> — Crypto market and on-chain data engineering</summary>

**Purpose:** Crypto market and on-chain data engineering.

**What you can do:** Design collectors, normalized schemas, deduplication, storage and quality monitoring.

**Example prompts:**

- **Codex:** `$data-pipeline-crypto Plan an ingestion pipeline for exchange trades and books.`
- **Claude Code:** `/data-pipeline-crypto Design replay-safe on-chain event ETL.`

**Location:** `.agents/skills/data-pipeline-crypto/SKILL.md`

</details>

<details>
<summary><code>exchange-infrastructure</code> — Crypto exchange systems architecture</summary>

**Purpose:** Crypto exchange systems architecture.

**What you can do:** Design matching, market data, risk controls, settlement and monitoring.

**Example prompts:**

- **Codex:** `$exchange-infrastructure Design an order matching and recovery architecture.`
- **Claude Code:** `/exchange-infrastructure Review exchange order lifecycle and reconciliation.`

**Location:** `.agents/skills/exchange-infrastructure/SKILL.md`

</details>

<details>
<summary><code>indexer-architecture</code> — High-throughput blockchain indexing</summary>

**Purpose:** High-throughput blockchain indexing.

**What you can do:** Plan backfills, finality, reorg handling, queues and scalable storage.

**Example prompts:**

- **Codex:** `$indexer-architecture Design an indexer that recovers from chain reorganizations.`
- **Claude Code:** `/indexer-architecture Compare block-based and event-based ingestion designs.`

**Location:** `.agents/skills/indexer-architecture/SKILL.md`

</details>

<details>
<summary><code>market-data-analysis</code> — Crypto market data analysis</summary>

**Purpose:** Crypto market data analysis.

**What you can do:** Evaluate trades, order books, volume, volatility and data quality.

**Example prompts:**

- **Codex:** `$market-data-analysis Create an order-book liquidity analysis plan.`
- **Claude Code:** `/market-data-analysis Explain how to detect stale or anomalous exchange prints.`

**Location:** `.agents/skills/market-data-analysis/SKILL.md`

</details>

<details>
<summary><code>mev-infrastructure</code> — MEV infrastructure architecture</summary>

**Purpose:** MEV infrastructure architecture.

**What you can do:** Design transaction simulation, searcher pipelines, relays and inclusion monitoring.

**Example prompts:**

- **Codex:** `$mev-infrastructure Plan a simulation-and-bundle submission pipeline.`
- **Claude Code:** `/mev-infrastructure Assess failed inclusion and private relay reliability.`

**Location:** `.agents/skills/mev-infrastructure/SKILL.md`

</details>

<details>
<summary><code>monitoring-alerting</code> — Crypto system observability</summary>

**Purpose:** Crypto system observability.

**What you can do:** Design metrics, health checks, alerts, incident escalation and SLOs.

**Example prompts:**

- **Codex:** `$monitoring-alerting Create alert rules for an exchange connector.`
- **Claude Code:** `/monitoring-alerting Build an incident dashboard for a crypto node fleet.`

**Location:** `.agents/skills/monitoring-alerting/SKILL.md`

</details>

<details>
<summary><code>node-infrastructure</code> — Blockchain node operations</summary>

**Purpose:** Blockchain node operations.

**What you can do:** Plan archive/full nodes, sync, storage, network security and reliability.

**Example prompts:**

- **Codex:** `$node-infrastructure Design production RPC node deployment requirements.`
- **Claude Code:** `/node-infrastructure Review node backup, failover and monitoring strategy.`

**Location:** `.agents/skills/node-infrastructure/SKILL.md`

</details>

<details>
<summary><code>rpc-provider-management</code> — Blockchain RPC reliability</summary>

**Purpose:** Blockchain RPC reliability.

**What you can do:** Design multi-provider failover, quota awareness, consistency checks and monitoring.

**Example prompts:**

- **Codex:** `$rpc-provider-management Plan redundant RPC endpoints for a wallet backend.`
- **Claude Code:** `/rpc-provider-management Review rate limits, retries and stale block data.`

**Location:** `.agents/skills/rpc-provider-management/SKILL.md`

</details>

<details>
<summary><code>smart-contract-deployment</code> — Smart contract release engineering</summary>

**Purpose:** Smart contract release engineering.

**What you can do:** Plan network deployment, verification, ownership transfer and rollback limitations.

**Example prompts:**

- **Codex:** `$smart-contract-deployment Create a production smart-contract deployment checklist.`
- **Claude Code:** `/smart-contract-deployment Review multisig and verification steps after deploy.`

**Location:** `.agents/skills/smart-contract-deployment/SKILL.md`

</details>

<details>
<summary><code>solana-rpc-infrastructure</code> — Solana RPC infrastructure</summary>

**Purpose:** Solana RPC infrastructure.

**What you can do:** Design Geyser ingestion, RPC capacity, rate limits and slot awareness.

**Example prompts:**

- **Codex:** `$solana-rpc-infrastructure Plan a resilient Solana RPC ingest service.`
- **Claude Code:** `/solana-rpc-infrastructure Review slot commitment and missed-block handling.`

**Location:** `.agents/skills/solana-rpc-infrastructure/SKILL.md`

</details>

<details>
<summary><code>treasury-management</code> — Crypto treasury operations</summary>

**Purpose:** Crypto treasury operations.

**What you can do:** Plan custody, liquidity reserves, hedging policy and multi-sig governance.

**Example prompts:**

- **Codex:** `$treasury-management Draft a crypto treasury risk policy.`
- **Claude Code:** `/treasury-management Design a treasury liquidity ladder and reporting process.`

**Location:** `.agents/skills/treasury-management/SKILL.md`

</details>

</details>

<details>
<summary><strong>Cryptocurrency Pro (10)</strong></summary>

<details>
<summary><code>bitcoin-fundamentals</code> — Bitcoin protocol fundamentals</summary>

**Purpose:** Bitcoin protocol fundamentals.

**What you can do:** Explain UTXOs, fees, signatures, custody, confirmations and transaction security.

**Example prompts:**

- **Codex:** `$bitcoin-fundamentals Explain how Bitcoin coin selection affects fees and privacy.`
- **Claude Code:** `/bitcoin-fundamentals Assess Bitcoin transaction confirmation risks.`

**Location:** `.agents/skills/bitcoin-fundamentals/SKILL.md`

</details>

<details>
<summary><code>cold-storage-security</code> — Offline crypto custody protection</summary>

**Purpose:** Offline crypto custody protection.

**What you can do:** Design hardware wallet, multisig, backup and recovery procedures.

**Example prompts:**

- **Codex:** `$cold-storage-security Build a cold-storage key backup checklist.`
- **Claude Code:** `/cold-storage-security Compare multisig and hardware wallet threat models.`

**Location:** `.agents/skills/cold-storage-security/SKILL.md`

</details>

<details>
<summary><code>crypto-research</code> — Crypto project due diligence</summary>

**Purpose:** Crypto project due diligence.

**What you can do:** Assess protocol fundamentals, incentives, security, adoption and token economics.

**Example prompts:**

- **Codex:** `$crypto-research Build a due diligence memo for a DeFi protocol.`
- **Claude Code:** `/crypto-research Compare token valuation assumptions across two projects.`

**Location:** `.agents/skills/crypto-research/SKILL.md`

</details>

<details>
<summary><code>crypto-tax</code> — Crypto transaction tax recordkeeping</summary>

**Purpose:** Crypto transaction tax recordkeeping.

**What you can do:** Track cost basis, income events, disposals and DeFi records by jurisdiction.

**Example prompts:**

- **Codex:** `$crypto-tax Design a transaction ledger for crypto tax reporting.`
- **Claude Code:** `/crypto-tax List records needed for staking and airdrop income analysis.`

**Location:** `.agents/skills/crypto-tax/SKILL.md`

</details>

<details>
<summary><code>cryptocurrency-stablecoin-mechanics</code> — Stablecoin fundamentals and models</summary>

**Purpose:** Stablecoin fundamentals and models.

**What you can do:** Compare fiat-backed, crypto-backed and algorithmic pegs, redemption and reserve risks.

**Example prompts:**

- **Codex:** `$cryptocurrency-stablecoin-mechanics Explain how different stablecoin pegs are maintained.`
- **Claude Code:** `/cryptocurrency-stablecoin-mechanics Stress test collateral and redemption assumptions.`

**Location:** `.agents/skills/cryptocurrency-stablecoin-mechanics/SKILL.md`

</details>

<details>
<summary><code>dao-governance</code> — DAO governance strategy</summary>

**Purpose:** DAO governance strategy.

**What you can do:** Analyze token voting, delegation, proposal processes and governance incentives.

**Example prompts:**

- **Codex:** `$dao-governance Design a DAO proposal and voting policy.`
- **Claude Code:** `/dao-governance Assess governance capture and voter participation risks.`

**Location:** `.agents/skills/dao-governance/SKILL.md`

</details>

<details>
<summary><code>defi-yield-strategies</code> — DeFi yield strategy evaluation</summary>

**Purpose:** DeFi yield strategy evaluation.

**What you can do:** Compare lending, LP and vault yields after fees, losses and liquidity risk.

**Example prompts:**

- **Codex:** `$defi-yield-strategies Compare two yield strategies net of IL and gas.`
- **Claude Code:** `/defi-yield-strategies Plan a conservative DeFi yield risk budget.`

**Location:** `.agents/skills/defi-yield-strategies/SKILL.md`

</details>

<details>
<summary><code>ethereum-fundamentals</code> — Ethereum execution and consensus basics</summary>

**Purpose:** Ethereum execution and consensus basics.

**What you can do:** Explain EVM transactions, gas, staking, rollups and account models.

**Example prompts:**

- **Codex:** `$ethereum-fundamentals Explain EIP-1559 fees with a worked example.`
- **Claude Code:** `/ethereum-fundamentals Compare Ethereum execution and consensus layers.`

**Location:** `.agents/skills/ethereum-fundamentals/SKILL.md`

</details>

<details>
<summary><code>layer-2-scaling</code> — Ethereum Layer 2 architectures</summary>

**Purpose:** Ethereum Layer 2 architectures.

**What you can do:** Compare optimistic/ZK rollups, data availability, sequencers and withdrawal risk.

**Example prompts:**

- **Codex:** `$layer-2-scaling Compare rollup finality and bridge risk models.`
- **Claude Code:** `/layer-2-scaling Explain optimistic versus ZK rollup design choices.`

**Location:** `.agents/skills/layer-2-scaling/SKILL.md`

</details>

<details>
<summary><code>nft-strategy</code> — NFT product and token strategy</summary>

**Purpose:** NFT product and token strategy.

**What you can do:** Evaluate NFT utility, mint design, market fit and community incentives.

**Example prompts:**

- **Codex:** `$nft-strategy Design an NFT launch strategy with utility and risks.`
- **Claude Code:** `/nft-strategy Assess NFT supply and secondary liquidity assumptions.`

**Location:** `.agents/skills/nft-strategy/SKILL.md`

</details>

</details>

<details>
<summary><strong>Web3 Development (26)</strong></summary>

<details>
<summary><code>account-abstraction</code> — Smart-account UX and account abstraction</summary>

**Purpose:** Smart-account UX and account abstraction.

**What you can do:** Design ERC-4337 onboarding, sponsorship, and recovery flows; compare bundlers and paymasters.

**Example prompts:**

- **Codex:** `$account-abstraction Plan a wallet onboarding flow with passkeys and sponsored transactions.`
- **Claude Code:** `/account-abstraction Review the trust and failure modes of a smart-account architecture.`

**Location:** `.agents/skills/account-abstraction/SKILL.md`

</details>

<details>
<summary><code>aptos-development</code> — Aptos application development</summary>

**Purpose:** Aptos application development.

**What you can do:** Structure Move modules, resources, accounts and Aptos transaction flows.

**Example prompts:**

- **Codex:** `$aptos-development Plan an Aptos Move asset module.`
- **Claude Code:** `/aptos-development Review an Aptos client transaction lifecycle.`

**Location:** `.agents/skills/aptos-development/SKILL.md`

</details>

<details>
<summary><code>avalanche-development</code> — Avalanche development and subnets</summary>

**Purpose:** Avalanche development and subnets.

**What you can do:** Compare Avalanche deployment options, EVM tooling and custom-chain trade-offs.

**Example prompts:**

- **Codex:** `$avalanche-development Design a contract deployment workflow on Avalanche.`
- **Claude Code:** `/avalanche-development Compare C-Chain deployment and an application-specific Avalanche chain.`

**Location:** `.agents/skills/avalanche-development/SKILL.md`

</details>

<details>
<summary><code>base-development</code> — Base chain application development</summary>

**Purpose:** Base chain application development.

**What you can do:** Build and deploy Base-compatible smart contracts and estimate bridging and L2 UX risks.

**Example prompts:**

- **Codex:** `$base-development Plan a Base wallet and token application.`
- **Claude Code:** `/base-development Review cross-chain assumptions in a Base integration.`

**Location:** `.agents/skills/base-development/SKILL.md`

</details>

<details>
<summary><code>cosmos-sdk</code> — Cosmos SDK chain architecture</summary>

**Purpose:** Cosmos SDK chain architecture.

**What you can do:** Design SDK modules, transaction handlers, governance and IBC interfaces.

**Example prompts:**

- **Codex:** `$cosmos-sdk Design a custom Cosmos SDK module for staking rewards.`
- **Claude Code:** `/cosmos-sdk Explain Cosmos SDK state-transition and upgrade testing.`

**Location:** `.agents/skills/cosmos-sdk/SKILL.md`

</details>

<details>
<summary><code>cosmwasm-contracts</code> — CosmWasm smart contract patterns</summary>

**Purpose:** CosmWasm smart contract patterns.

**What you can do:** Develop Rust/CosmWasm entry points, permissions, messages and tests.

**Example prompts:**

- **Codex:** `$cosmwasm-contracts Design a CosmWasm vesting contract.`
- **Claude Code:** `/cosmwasm-contracts Review instantiate and execute authorization checks.`

**Location:** `.agents/skills/cosmwasm-contracts/SKILL.md`

</details>

<details>
<summary><code>erc4337-smart-accounts</code> — ERC-4337 smart account architecture</summary>

**Purpose:** ERC-4337 smart account architecture.

**What you can do:** Plan UserOperations, bundlers, paymasters, signatures and wallet recovery.

**Example prompts:**

- **Codex:** `$erc4337-smart-accounts Design an ERC-4337 smart account with a paymaster.`
- **Claude Code:** `/erc4337-smart-accounts Review UserOperation validation and replay protections.`

**Location:** `.agents/skills/erc4337-smart-accounts/SKILL.md`

</details>

<details>
<summary><code>ethers-js</code> — Ethers.js application integration</summary>

**Purpose:** Ethers.js application integration.

**What you can do:** Build signer, provider, contract and event workflows with ethers.js.

**Example prompts:**

- **Codex:** `$ethers-js Write an ethers.js contract read/write plan.`
- **Claude Code:** `/ethers-js Review nonce and event handling in a wallet client.`

**Location:** `.agents/skills/ethers-js/SKILL.md`

</details>

<details>
<summary><code>foundry-framework</code> — Foundry Solidity testing and deployment</summary>

**Purpose:** Foundry Solidity testing and deployment.

**What you can do:** Create Forge tests, fuzzing, fork tests, scripts and reproducible builds.

**Example prompts:**

- **Codex:** `$foundry-framework Write a Foundry fuzz testing plan for a vault.`
- **Claude Code:** `/foundry-framework Explain safe simulation versus broadcast in Forge scripts.`

**Location:** `.agents/skills/foundry-framework/SKILL.md`

</details>

<details>
<summary><code>hardhat-development</code> — Hardhat development workflows</summary>

**Purpose:** Hardhat development workflows.

**What you can do:** Configure Solidity builds, networks, deployments, debugging and tests.

**Example prompts:**

- **Codex:** `$hardhat-development Plan a Hardhat test and deploy workflow.`
- **Claude Code:** `/hardhat-development Compare Hardhat plugins and network configuration strategies.`

**Location:** `.agents/skills/hardhat-development/SKILL.md`

</details>

<details>
<summary><code>ipfs-storage</code> — IPFS and content-addressed storage</summary>

**Purpose:** IPFS and content-addressed storage.

**What you can do:** Design pinning, CID verification, gateway resilience and data persistence.

**Example prompts:**

- **Codex:** `$ipfs-storage Plan NFT metadata on IPFS with availability controls.`
- **Claude Code:** `/ipfs-storage Explain how CIDs and pinning affect content integrity.`

**Location:** `.agents/skills/ipfs-storage/SKILL.md`

</details>

<details>
<summary><code>lightning-network-development</code> — Bitcoin Lightning applications</summary>

**Purpose:** Bitcoin Lightning applications.

**What you can do:** Design channels, invoices, routing liquidity and payment reliability.

**Example prompts:**

- **Codex:** `$lightning-network-development Plan a Lightning payment service with liquidity monitoring.`
- **Claude Code:** `/lightning-network-development Review HTLC and channel operational risks.`

**Location:** `.agents/skills/lightning-network-development/SKILL.md`

</details>

<details>
<summary><code>move-language</code> — Move language programming</summary>

**Purpose:** Move language programming.

**What you can do:** Explain resources, abilities, modules, capabilities and Move safety.

**Example prompts:**

- **Codex:** `$move-language Write a Move resource ownership design.`
- **Claude Code:** `/move-language Review access control in a Move module.`

**Location:** `.agents/skills/move-language/SKILL.md`

</details>

<details>
<summary><code>near-protocol-development</code> — NEAR smart contract development</summary>

**Purpose:** NEAR smart contract development.

**What you can do:** Build Rust/JS NEAR contracts, storage, async calls and cross-contract safety.

**Example prompts:**

- **Codex:** `$near-protocol-development Design a NEAR contract using promises.`
- **Claude Code:** `/near-protocol-development Review asynchronous cross-contract call risks.`

**Location:** `.agents/skills/near-protocol-development/SKILL.md`

</details>

<details>
<summary><code>optimism-development</code> — OP Stack and Optimism development</summary>

**Purpose:** OP Stack and Optimism development.

**What you can do:** Plan OP Stack integrations, bridges, messaging and L2 deployment.

**Example prompts:**

- **Codex:** `$optimism-development Design an Optimism cross-chain messaging flow.`
- **Claude Code:** `/optimism-development Assess withdrawal timing and fault-proof assumptions.`

**Location:** `.agents/skills/optimism-development/SKILL.md`

</details>

<details>
<summary><code>ordinals-inscriptions</code> — Bitcoin Ordinals and inscriptions</summary>

**Purpose:** Bitcoin Ordinals and inscriptions.

**What you can do:** Explain sat inscription flows, indexing, fees and custody impacts.

**Example prompts:**

- **Codex:** `$ordinals-inscriptions Describe an Ordinals inscription lifecycle.`
- **Claude Code:** `/ordinals-inscriptions Review fee and indexing assumptions for inscriptions.`

**Location:** `.agents/skills/ordinals-inscriptions/SKILL.md`

</details>

<details>
<summary><code>polkadot-substrate</code> — Polkadot/Substrate chain engineering</summary>

**Purpose:** Polkadot/Substrate chain engineering.

**What you can do:** Design pallets, runtimes, weights and governance upgrades.

**Example prompts:**

- **Codex:** `$polkadot-substrate Plan a custom Substrate pallet.`
- **Claude Code:** `/polkadot-substrate Review runtime upgrade and weight accounting.`

**Location:** `.agents/skills/polkadot-substrate/SKILL.md`

</details>

<details>
<summary><code>polygon-development</code> — Polygon blockchain development</summary>

**Purpose:** Polygon blockchain development.

**What you can do:** Build EVM contracts on Polygon and compare bridge/L2 options.

**Example prompts:**

- **Codex:** `$polygon-development Design a Polygon smart-contract deployment workflow.`
- **Claude Code:** `/polygon-development Assess Polygon network and bridge assumptions.`

**Location:** `.agents/skills/polygon-development/SKILL.md`

</details>

<details>
<summary><code>rust-solana-programs</code> — Native Rust programs on Solana</summary>

**Purpose:** Native Rust programs on Solana.

**What you can do:** Plan Solana instructions, PDAs, account layouts and ownership checks.

**Example prompts:**

- **Codex:** `$rust-solana-programs Design a native Solana escrow program.`
- **Claude Code:** `/rust-solana-programs Review Solana account constraints and signer verification.`

**Location:** `.agents/skills/rust-solana-programs/SKILL.md`

</details>

<details>
<summary><code>solana-anchor-framework</code> — Solana Anchor framework patterns</summary>

**Purpose:** Solana Anchor framework patterns.

**What you can do:** Design accounts, IDLs, PDAs, constraints, CPI and Anchor tests.

**Example prompts:**

- **Codex:** `$solana-anchor-framework Design a secure Anchor program for escrow.`
- **Claude Code:** `/solana-anchor-framework Review CPI authority and PDA seed constraints.`

**Location:** `.agents/skills/solana-anchor-framework/SKILL.md`

</details>

<details>
<summary><code>solidity-patterns</code> — Reusable Solidity design patterns</summary>

**Purpose:** Reusable Solidity design patterns.

**What you can do:** Compare factories, proxies, authorization and upgradeable storage designs.

**Example prompts:**

- **Codex:** `$solidity-patterns Design a Solidity access-control pattern.`
- **Claude Code:** `/solidity-patterns Review a proxy storage layout for upgrade safety.`

**Location:** `.agents/skills/solidity-patterns/SKILL.md`

</details>

<details>
<summary><code>starknet-cairo</code> — Starknet/Cairo tooling</summary>

**Purpose:** Starknet/Cairo tooling.

**What you can do:** Develop Cairo modules, storage, testing and Starknet transactions.

**Example prompts:**

- **Codex:** `$starknet-cairo Create a Starknet contract development workflow.`
- **Claude Code:** `/starknet-cairo Assess Cairo version and toolchain compatibility.`

**Location:** `.agents/skills/starknet-cairo/SKILL.md`

</details>

<details>
<summary><code>the-graph-development</code> — The Graph indexing development</summary>

**Purpose:** The Graph indexing development.

**What you can do:** Configure subgraphs, mappings, schema entities and deployment workflows.

**Example prompts:**

- **Codex:** `$the-graph-development Build a subgraph indexing ERC-721 transfers.`
- **Claude Code:** `/the-graph-development Review subgraph schema and query performance.`

**Location:** `.agents/skills/the-graph-development/SKILL.md`

</details>

<details>
<summary><code>ton-development</code> — TON smart contract development</summary>

**Purpose:** TON smart contract development.

**What you can do:** Plan TON/FunC/Tact contracts, message handling, storage and tooling.

**Example prompts:**

- **Codex:** `$ton-development Design a TON contract message flow.`
- **Claude Code:** `/ton-development Review bounce handling and asynchronous security.`

**Location:** `.agents/skills/ton-development/SKILL.md`

</details>

<details>
<summary><code>viem-wagmi</code> — Viem and Wagmi Web3 frontends</summary>

**Purpose:** Viem and Wagmi Web3 frontends.

**What you can do:** Design typed wallet hooks, contract calls, account state and transaction UX.

**Example prompts:**

- **Codex:** `$viem-wagmi Plan a Wagmi transaction status UX.`
- **Claude Code:** `/viem-wagmi Compare viem and ethers.js integration choices.`

**Location:** `.agents/skills/viem-wagmi/SKILL.md`

</details>

<details>
<summary><code>wallet-connect</code> — WalletConnect integration</summary>

**Purpose:** WalletConnect integration.

**What you can do:** Plan pairing, session permissions, network switching and rejection flows.

**Example prompts:**

- **Codex:** `$wallet-connect Design a WalletConnect session approval screen.`
- **Claude Code:** `/wallet-connect Audit deep-link and session lifecycle handling.`

**Location:** `.agents/skills/wallet-connect/SKILL.md`

</details>

</details>

## Working notes

- **Default consultation mode:** no file changes or live trades without an explicit request.
- **Version awareness:** command examples, SDK APIs, exchange limits and chain behaviors should be checked against current official documentation before production use.
- **Security:** audit third-party scripts and smart contracts; never share private keys or recovery phrases.
- **Scope:** all listed Skills physically exist in `.agents/skills/`; this README is not a placeholder for uninstalled Skills.

## Windows setup for Claude Code

The canonical library is located at `.agents/skills/`. The ZIP does not embed Windows junctions. To expose native Claude Skills on a new checkout:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\setup-claude-skills.ps1
```

The script will not overwrite an existing non-link `.claude/skills` directory. If the installed Claude Code version does not discover skills through the junction, open the canonical files via `CLAUDE.md`; native slash registration requires a supported `.claude/skills/` layout.

<sub><i>Original, unmodified skill sources were obtained from [SkillDB](https://skilldb.dev/). All skills have been reviewed and adapted for this repository.</i></sub>