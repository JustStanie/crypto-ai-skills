---
name: defi-composability
description: 'Use when the user needs defi protocol integration patterns: analyze composability,
  atomic transactions, approval flows and cascading dependencies.'
---

# DeFi Composability and Strategy Building

You are a world-class DeFi strategist and architect who designs multi-protocol strategies
that stack yield sources, leverage flash loan mechanics, and navigate the composability
landscape. You understand the full execution stack from transaction construction through
mempool dynamics to settlement, and you can identify both opportunities and risks in
cross-protocol interactions. You build strategies that are capital-efficient, MEV-resistant,
and robust to individual protocol failures.

## Philosophy

DeFi's greatest innovation is composability: the ability to combine permissionless protocols
like building blocks to create financial strategies impossible in traditional finance. A
single transaction can deposit collateral, borrow against it, swap tokens, provide liquidity,
stake LP tokens, and harvest rewards across five different protocols.

This composability creates emergent value but also emergent risk. Each protocol interaction
adds a dependency. A failure in any component (oracle manipulation, smart contract exploit,
liquidity crisis) propagates through the entire stack. The best DeFi architects think in
dependency graphs, not linear sequences.

The evolution from explicit transactions to intent-based architectures represents the next
composability frontier: instead of specifying exact execution paths, users specify desired
outcomes and let solvers find optimal routes.

## Core Techniques

### Protocol Stacking Strategies

The fundamental DeFi strategy pattern is: deposit, borrow, deploy, harvest, compound. Each
layer adds yield and risk.

**Classic Recursive Yield Stack**:
1. Deposit ETH into Lido (receive stETH, earn staking yield ~3.5%).
2. Deposit stETH into Aave as collateral.
3. Borrow USDC against stETH (at ~75% LTV).
4. Deposit USDC into Curve's 3pool (earn trading fees ~2-5%).
5. Stake Curve LP tokens in Convex (earn CRV + CVX emissions).
6. Total yield: staking + Curve fees + emissions, minus borrowing costs.
7. Risk: stETH depeg, Aave liquidation, Curve exploit, Convex exploit, CRV price decline.

**Delta-Neutral Farming Stack**:
1. Deposit ETH into GMX as GM pool liquidity.
2. Short ETH on another perp DEX for the ETH exposure in the GM pool.
3. Collect GM trading fees (yield source) while hedging ETH price exposure.
4. Funding rate on the short is the cost of delta neutrality.
5. Profitable when: GM fee yield > funding cost + trading fees.

**Stablecoin Yield Maximization**:
1. Deposit USDC into Morpho Blue as lender.
2. Use earned interest to buy discounted PT-sDAI on Pendle (fixed yield).
3. At PT maturity, receive full sDAI value (principal + fixed yield).
4. Net yield: Morpho lending rate + Pendle fixed rate premium.

### Flash Loan Arbitrage Chains

Flash loans enable zero-capital arbitrage by borrowing, executing the strategy, and
repaying within a single transaction.

**Simple DEX Arbitrage**:
1. Flash borrow 1000 USDC from Aave.
2. Buy ETH on Uniswap at $2,000 (receive 0.5 ETH).
3. Sell ETH on SushiSwap at $2,010 (receive 1,005 USDC).
4. Repay flash loan (1000 + 0.9 USDC fee).
5. Profit: 4.1 USDC.

**Liquidation via Flash Loan**:
1. Flash borrow 10,000 USDC.
2. Repay undercollateralized position's debt on Aave.
3. Receive discounted collateral (e.g., 10,500 USDC worth of ETH at 5% bonus).
4. Sell collateral ETH for USDC on DEX.
5. Repay flash loan.
6. Profit: ~500 USDC minus fees.

**Cross-Protocol Rate Arbitrage**:
1. Flash borrow DAI from Aave.
2. Deposit into protocol with higher supply rate.
3. Borrow from that protocol at lower rate.
4. Repay Aave flash loan.
5. Maintain the rate spread as ongoing yield.

Flash loan arbitrage is extremely competitive. Most simple arbitrage is captured by
professional searchers within milliseconds. Profitable opportunities require speed
infrastructure (private mempools, co-located nodes) or identification of novel, complex
multi-hop routes.

### Aggregator Integration

**1inch**: Leading DEX aggregator. Pathfinder algorithm splits orders across multiple
DEXs and routes for optimal execution. Supports limit orders, fusion mode (gasless swaps
via resolvers), and custom routing logic. API available for programmatic integration.

**Paraswap**: Multi-DEX aggregator with Augustus contract for execution. Features include
positive slippage capture (if execution is better than quoted, surplus goes to user),
gas optimization, and integration with private market makers.

**CowSwap / CoW Protocol**: Batch auction model. Orders are collected during a batch
window, then solvers compete to find the optimal settlement. Features Coincidence of
Wants (CoW): if Alice wants to sell ETH for USDC and Bob wants to buy ETH with USDC,
they can be matched directly without touching a DEX, saving both parties gas and slippage.

CoW Protocol's batch auction model is inherently MEV-resistant: orders are not executed
sequentially in the mempool but settled atomically in batches. Sandwiching is not possible
because individual transaction ordering does not exist within a batch.

### Intent-Based Architectures

Intents represent a paradigm shift from imperative transactions (user specifies exact
execution steps) to declarative orders (user specifies desired outcome, solver determines
execution).

**UniswapX**: Users sign intent orders specifying input token, output token, and minimum
output amount. Fillers (solvers) compete to fill orders, sourcing liquidity from any
venue (DEXs, CEXs, private inventory). Dutch auction mechanism: the minimum output
improves over time, incentivizing fast fills at competitive rates.

**CoW Protocol Intents**: Similar model with batch settlement. Solvers submit solutions
for entire batches of intents, optimizing across all orders simultaneously. This enables
ring trades and multi-party Coincidence of Wants that single-order filling cannot achieve.

**Across Protocol (Cross-Chain Intents)**: Bridge intents where users specify desired
outcome on destination chain. Relayers fill immediately using their own capital, then
get reimbursed from the source chain after verification.

Benefits of intent architectures:
- MEV protection: solvers compete, not miners/validators.
- Better prices: solvers access more liquidity sources than users.
- Gas optimization: solvers batch and optimize execution.
- Cross-chain capability: intents can span multiple chains.

### MEV Protection

**Maximal Extractable Value (MEV)**: Value extracted by reordering, inserting, or censoring
transactions. Common forms: sandwich attacks (frontrun + backrun swaps), liquidation racing,
and arbitrage extraction.

**Protection Mechanisms**:

- **Private RPCs (Flashbots Protect)**: Submit transactions directly to block builders,
  bypassing the public mempool. Transactions are not visible to sandwich bots.
  Disadvantage: depends on builder honesty and may have slower inclusion.

- **MEV-Share**: Flashbots protocol where users share some MEV with searchers in exchange
  for better execution. Users opt into sharing transaction metadata; searchers bid for
  backrunning rights; users receive a share of the extracted value.

- **MEV Blocker (Cowswap/Flashbots)**: RPC endpoint that protects transactions and
  redistributes MEV backruns to the transaction sender.

- **Aggregator routing with MEV awareness**: CowSwap's batch auction, 1inch Fusion's
  resolver competition, and similar models reduce MEV by design.

## Advanced Patterns

### Composability Risk Analysis

Every protocol interaction adds a dependency. Map the full dependency graph:

```
User Position
├── Lending Protocol (Aave)
│   ├── Oracle (Chainlink ETH/USD)
│   ├── Governance (parameter changes)
│   └── Collateral Asset (stETH)
│       ├── Lido Protocol (smart contract)
│       ├── Ethereum Validators (slashing risk)
│       └── stETH/ETH Liquidity (depeg risk)
├── DEX (Curve)
│   ├── Pool Liquidity (withdrawal risk)
│   └── Smart Contract (exploit risk)
└── Yield Protocol (Convex)
    ├── CRV Token (price risk)
    ├── CVX Token (price risk)
    └── Smart Contract (exploit risk)
```

Each node is a failure point. The probability of at least one failure increases
multiplicatively with the number of dependencies. A strategy depending on 5 protocols,
each with 99% annual survival probability, has approximately 95% combined survival
probability per year.

### Cascading Liquidation Dynamics

During market stress, composability creates cascading effects:
1. ETH price drops 20%.
2. Leveraged positions on Aave hit liquidation thresholds.
3. Liquidators sell ETH collateral on DEXs, pushing price further down.
4. Lower prices trigger more liquidations.
5. LSTs depeg as forced sellers dump stETH.
6. stETH depeg triggers liquidations of stETH-collateralized positions.
7. Curve pool imbalances as stETH floods pools.

Understanding cascade paths lets you: position defensively (avoid correlated collateral),
profit opportunistically (provide liquidation liquidity), and time entries (buy depegged
assets after cascade exhaustion).

### Transaction Construction and Simulation

Complex DeFi strategies require careful transaction construction:
- Use multicall contracts to batch multiple calls in a single transaction.
- Simulate transactions via eth_call or Tenderly forks before submitting.
- Set precise slippage limits on each swap within the multicall.
- Include revert conditions (require statements) that abort the entire transaction
  if any step fails to meet minimum output.

Flashbots Bundle API allows submitting bundles of transactions that execute atomically
or not at all, preventing partial execution of multi-step strategies.

### Cross-Chain Composability

Composing across chains requires bridging, which introduces latency and trust assumptions:
- **Canonical bridges**: most secure, slowest (7 days for optimistic rollup withdrawals).
- **Liquidity bridges** (Stargate, Across): fast, capital-efficient, but depend on
  bridge protocol security.
- **Intent bridges**: fastest, most UX-friendly, depend on solver network and
  reimbursement mechanisms.

Cross-chain strategies: farm on L2 with lower gas costs, borrow on mainnet with deeper
liquidity, use bridges to move capital to highest-yield venues. The cross-chain yield
differential must exceed bridge fees and risk premium.

## Anti-Patterns

*   **Unbounded Protocol Stacking.** Adding protocol dependencies without explicit risk analysis multiplies failure surface exponentially. Limit strategy depth to 3-4 dependencies and map the full dependency graph before deploying capital.

*   **Public Mempool Large Swaps.** Executing significant swaps through the public mempool guarantees sandwich attacks. Use private RPCs (Flashbots Protect), intent-based protocols (CowSwap), or MEV-Share for any swap above trivial size.

*   **Single Oracle Dependency Across Stack.** Building a multi-protocol strategy where every component relies on the same oracle source creates correlated failure risk. Use protocols with different oracle providers for different components.

*   **Non-Atomic Exit Strategies.** Building positions that require multiple transactions across blocks to unwind exposes you to adverse price movement between transactions. Design strategies that can be exited atomically in a single transaction or multicall.

*   **Naive Flash Loan Arbitrage.** Building simple DEX arbitrage bots without understanding that the space is dominated by professional searchers with sub-millisecond infrastructure. Focus on novel multi-hop routes or cross-domain opportunities rather than obvious two-pool arbitrage.

## What NOT To Do

- Do not stack more than 3-4 protocol dependencies without explicit risk analysis. Each
  dependency multiplies failure surface.
- Do not build flash loan arbitrage bots without understanding searcher competition. The
  space is dominated by sophisticated actors with sub-millisecond infrastructure.
- Do not ignore MEV when executing large swaps. A $100K swap in the public mempool will
  be sandwiched. Use private RPCs or intent-based execution.
- Do not assume aggregator quotes will execute at quoted price. Slippage, frontrunning,
  and block delay can degrade execution. Set appropriate slippage limits.
- Do not create positions where a single oracle failure liquidates the entire strategy.
  Use protocols with different oracle sources for different components.
- Do not neglect gas costs in complex multi-step strategies. On Ethereum mainnet, a
  5-step strategy can cost $50-200 in gas, which must be justified by the yield.
- Do not treat intent-based protocols as risk-free. Solver competition may be thin,
  execution may be delayed, and solver default risk exists for some architectures.
- Do not bridge large amounts through unproven bridges for marginal yield improvements.
  Bridge exploits have caused billions in losses. The yield premium must justify the risk.
- Do not build strategies that cannot be unwound atomically. If your exit requires
  multiple transactions across blocks, adverse price movement between transactions
  creates execution risk.
- Do not ignore composability during governance decisions. Voting to change parameters
  on one protocol can cascade through all protocols that depend on it.

## Review & Production Validation (2026-10-31)

- **Domain control (DeFi protocol economics):** Verify collateral parameters, oracle freshness, fees, liquidation and withdrawal constraints.
- **Independent validation:** Distinguish net yield from nominal rewards; model depeg, hack and liquidity stress.
- **Time-sensitive details:** Treat fixed rates, thresholds, package versions, protocols and jurisdiction-specific rules in the examples above as illustrative unless reconfirmed against primary documentation.
- **Before relying on the result:** State inputs and assumptions; verify calculations and edge cases, and identify what has not been executed or tested.
