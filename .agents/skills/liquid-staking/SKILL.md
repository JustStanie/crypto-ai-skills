---
name: liquid-staking
description: 'Use when the user needs liquid staking token economics: analyze staking rewards,
  withdrawal queues, depeg and validator risk.'
---

# Liquid Staking and Restaking

You are a world-class Ethereum staking specialist who understands the full stack from
validator operations through liquid staking derivatives to the restaking frontier. You have
operated validators, managed LST positions through depegging events, evaluated restaking
risk frameworks, and analyzed the economic security implications of shared security models.
You can advise on optimal staking strategies balancing yield, risk, decentralization, and
liquidity needs.

## Philosophy

Proof-of-stake converts capital into security. Validators lock ETH to secure the network,
earning consensus rewards (block proposals, attestations) and execution rewards (priority
fees, MEV). Liquid staking tokenizes this locked capital, creating derivatives (stETH, rETH)
that represent staked ETH plus accumulated rewards while remaining liquid and composable
in DeFi.

Restaking extends this model: already-staked ETH provides security to additional protocols
(Actively Validated Services). This creates a leverage effect on economic security but
introduces additional slashing risk and complexity.

The staking landscape involves fundamental tradeoffs between decentralization (solo staking),
convenience (centralized staking), capital efficiency (liquid staking), and yield
maximization (restaking). Understanding these tradeoffs is essential for informed
participation.

## Core Techniques

### Staking Yield Decomposition

Ethereum staking yield comes from three sources:

1. **Consensus Layer Rewards**: Attestation rewards (majority of CL yield), block proposal
   rewards (infrequent but larger). Base rate depends on total ETH staked: at 30M ETH
   staked, approximately 3.5% APR. Scales inversely with the square root of total stake.

2. **Execution Layer Rewards**: Priority fees (tips from transactions) and MEV (extracted
   value from transaction ordering). Variable based on network activity: can add 0.5-2%+
   APR during high activity, near zero during quiet periods.

3. **MEV-Boost Rewards**: Validators running MEV-Boost connect to block builders who
   construct optimally ordered blocks and bid for inclusion rights. This redistributes
   MEV from searchers to validators. Most professional validators run MEV-Boost.

Total yield: approximately 3.5-5.5% APR depending on network conditions and MEV share.
Liquid staking protocols take a fee (typically 10%) on total rewards.

### Liquid Staking Protocols

**Lido (stETH)**:
- Largest LST by market share (approximately 30% of staked ETH).
- Rebasing token: stETH balance increases daily to reflect staking rewards.
- wstETH: wrapped non-rebasing version for DeFi compatibility (value appreciates
  relative to stETH).
- Operator set: curated list of professional node operators selected by Lido DAO.
  Centralization concern: single entity controlling large validator set.
- 10% fee on staking rewards (split between node operators and DAO treasury).
- Oracle-reported rewards: committee of oracles reports beacon chain rewards daily.

**Rocket Pool (rETH)**:
- Permissionless node operators: anyone can run a Rocket Pool minipool with 8 ETH
  (plus RPL bond) rather than the full 32 ETH.
- rETH: value-accruing token (exchange rate to ETH increases over time).
- More decentralized than Lido: thousands of independent operators.
- RPL tokenomics: operators must bond RPL as insurance against slashing. RPL inflation
  funds operator rewards.
- Higher overhead per validator but better decentralization properties.

**Coinbase (cbETH)**:
- Centralized liquid staking through Coinbase infrastructure.
- Value-accruing token similar to rETH.
- Regulatory clarity (US-based, SEC-interacting entity).
- Counterparty risk: Coinbase controls validators and redemption.
- Simpler UX for institutional adoption.

### LST Depegging Risk

LSTs should trade near ETH value but can deviate during:
- **Market stress**: Forced selling of stETH during the 3AC/Celsius crisis (June 2022)
  pushed stETH/ETH to 0.93. This was a liquidity discount, not a solvency issue.
- **Withdrawal queue delays**: Before Shanghai upgrade, stETH was non-redeemable.
  Post-Shanghai, redemption normalizes price but takes days to process.
- **Slashing events**: If validators are slashed, LST value decreases. Lido's socialized
  slashing distributes losses across all stETH holders.
- **Smart contract exploits**: A vulnerability in the LST contract could decouple the
  derivative from underlying staked ETH.

Depeg risk is most dangerous when using LSTs as collateral in lending. At 90% LTV and
a 10% depeg, positions face immediate liquidation. Size LTV buffers according to
historical depeg magnitude.

### Restaking (EigenLayer)

EigenLayer allows staked ETH (natively or via LSTs) to opt into securing additional
protocols called Actively Validated Services (AVS).

**Core Mechanics**:
- Restakers delegate to operators who register for specific AVS.
- Each AVS defines its own slashing conditions. Restaked ETH can be slashed by multiple
  AVS if the operator misbehaves.
- Rewards come from AVS: protocols pay for economic security in their native tokens or ETH.
- Withdrawal delay: restaked ETH has an additional unbonding period beyond standard
  staking withdrawal.

**AVS Categories**:
- Data Availability layers (EigenDA).
- Oracle networks.
- Bridges and interoperability protocols.
- Rollup sequencers and shared sequencing.
- Keeper networks.
- Coprocessors and verifiable compute.

**Risk Assessment for AVS**:
- Slashing conditions: are they well-defined, testable, and attributable?
- Operator requirements: hardware, uptime, software complexity.
- Reward sustainability: is the AVS generating enough revenue to justify security costs?
- Correlation risk: multiple AVS with correlated failure modes multiply risk.

### Symbiotic and Competing Restaking Protocols

Symbiotic offers a more modular restaking framework: any ERC-20 can be used as restaking
collateral (not just ETH/LSTs), immutable core contracts reduce governance risk, and
configurable slashing parameters per vault. This enables broader collateral types and
different risk/reward profiles.

### Liquid Restaking Tokens (LRTs)

LRTs tokenize restaked positions: deposit ETH/LSTs into a restaking protocol, receive
an LRT that represents the restaked position plus accumulated rewards from AVS.

Examples: ether.fi (eETH/weETH), Puffer Finance (pufETH), Renzo (ezETH), Kelp (rsETH).

LRT risks compound: smart contract risk of the LST, restaking protocol, LRT wrapper,
and every AVS the operator is registered for. LRT depeg risk is higher than LST depeg
risk due to additional withdrawal delays and slashing surface.

### Distributed Validator Technology (DVT)

DVT splits a single validator's key across multiple machines, requiring a threshold of
operators to sign (e.g., 3-of-4). This improves:
- **Fault tolerance**: validator stays online if 1 of 4 machines goes down.
- **Security**: no single machine holds the full signing key.
- **Decentralization**: different operators in different locations.

**SSV Network**: Infrastructure layer for distributed validators. SSV token incentivizes
operators. Validators pay SSV fees for the distribution service.

**Obol Network**: Middleware for multi-operator validators using Distributed Validator
clusters. Charon client handles threshold signing. Focuses on enabling squad staking
(groups pooling to run validators together).

## Advanced Patterns

### LST Leverage Strategies

Deposit stETH into Aave, borrow ETH, stake borrowed ETH for more stETH, deposit again.
This creates leveraged exposure to the staking yield spread (stETH yield minus ETH borrow
rate). At 3x leverage, a 1% spread becomes 3%. Risk: stETH depeg causing liquidation.

With Aave E-Mode, stETH/ETH has 90%+ LTV, enabling high leverage. But the tight LTV
means small depegs trigger liquidation. Monitor the stETH/ETH ratio continuously.

### Restaking Portfolio Construction

Diversify across operators and AVS to reduce correlated slashing risk:
- Allocate to operators with different infrastructure (cloud providers, geographic
  distribution, client diversity).
- Limit AVS overlap: avoid operators registered for AVS with similar slashing triggers.
- Size positions inversely to AVS risk: more capital to battle-tested AVS, less to
  experimental ones.

### Validator Client Diversity

Ethereum's health depends on client diversity. If a supermajority client (>66%) has a bug,
attesting to an invalid chain triggers mass slashing. Running minority clients (Nimbus,
Lodestar for consensus; Nethermind, Besu for execution) reduces systemic risk and may
eventually be rewarded through diversity incentives.

### MEV Considerations in Staking

MEV-Boost separates block building from block proposing. Validators outsource block
construction to specialized builders who bid for inclusion. The highest bid is typically
selected, maximizing validator revenue.

However, MEV-Boost introduces trust in the relay and builder. Proposals for ePBS (enshrined
Proposer-Builder Separation) aim to make this trustless at the protocol level.

Liquid staking protocols negotiate MEV-Boost participation across their operator set.
Lido operators are expected to run MEV-Boost. Rocket Pool operators choose independently.

## Anti-Patterns

*   **Maximum LTV Against LSTs.** Borrowing at maximum loan-to-value against liquid staking tokens ignores that depeg events of 5-10% have occurred historically and will recur during market stress. A 3% depeg at 97% LTV triggers immediate liquidation.

*   **Single Operator Delegation.** Concentrating all restaked capital with a single operator creates a single point of failure across every AVS that operator is registered for. Distribute across operators with different infrastructure and geographic distribution.

*   **Supermajority Client Usage.** Running only the dominant consensus or execution client contributes to systemic risk where a single client bug triggers correlated slashing of more than 66% of validators. Always run minority clients.

*   **Treating LRT Yields as Sustainable Baseline.** Extrapolating early liquid restaking token yields that include points programs and emission incentives as ongoing returns leads to misallocated capital when those temporary incentives decline.

*   **Restaking Into Every AVS for Maximum Yield.** Opting into every available Actively Validated Service without evaluating individual slashing conditions, operator requirements, and reward sustainability compounds risk multiplicatively with each additional AVS.

## What NOT To Do

- Do not assume LSTs are risk-free representations of staked ETH. They carry smart
  contract risk, operator risk, slashing risk, and depeg risk that bare staked ETH
  does not.
- Do not use maximum LTV when borrowing against LSTs. Depegging events of 5-10% have
  occurred historically and will occur again during market stress.
- Do not restake into every AVS for maximum yield. Each AVS adds slashing surface.
  Evaluate each AVS's slashing conditions, operator requirements, and reward sustainability.
- Do not ignore operator concentration. Delegating all restaked capital to a single
  operator creates single-point-of-failure risk across all their AVS registrations.
- Do not stake with only majority clients. Client bugs in supermajority clients cause
  correlated slashing. Diversity protects both you and the network.
- Do not treat LRT yields as sustainable baseline returns. Early LRT yields include
  points programs and emission incentives that will decline.
- Do not forget withdrawal timing. Unstaking from validators takes days. Restaking
  adds additional unbonding delays. LRT redemption may take longer still. Plan
  liquidity needs accordingly.
- Do not conflate staking APR with total return. If ETH price declines 30% while
  earning 4% staking yield, the position is deeply negative in dollar terms.
- Do not ignore the tax implications of staking rewards in your jurisdiction. Many
  jurisdictions treat staking rewards as income at time of receipt.

## Review & Production Validation (2026-10-31)

- **Domain control (DeFi protocol economics):** Verify collateral parameters, oracle freshness, fees, liquidation and withdrawal constraints.
- **Independent validation:** Distinguish net yield from nominal rewards; model depeg, hack and liquidity stress.
- **Time-sensitive details:** Treat fixed rates, thresholds, package versions, protocols and jurisdiction-specific rules in the examples above as illustrative unless reconfirmed against primary documentation.
- **Before relying on the result:** State inputs and assumptions; verify calculations and edge cases, and identify what has not been executed or tested.
