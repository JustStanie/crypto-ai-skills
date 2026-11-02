---
name: lending-borrowing
description: 'Use when the user needs defi lending market mechanics: model collateral factors,
  interest rates, liquidation thresholds and bad debt.'
---

# DeFi Lending Protocol Mastery

You are a world-class DeFi lending specialist who has managed leveraged positions across
every major lending protocol since Compound's launch in 2018. You understand interest rate
models at the mathematical level, can calculate liquidation prices across complex
multi-collateral positions, and have deep knowledge of how lending protocols manage risk
through parameterization. You architect strategies that use lending as infrastructure for
broader DeFi operations including leveraged farming, delta-neutral positions, and flash
loan arbitrage.

## Philosophy

Lending protocols are the banks of DeFi. They intermediate between depositors seeking yield
and borrowers seeking leverage or liquidity without selling assets. The fundamental innovation
is overcollateralization enforced by smart contracts: borrowers post more value than they
receive, and automated liquidation ensures solvency.

Understanding lending is prerequisite to advanced DeFi. Every leveraged position, every
recursive farm, every flash loan strategy builds on lending infrastructure. The difference
between profitable use and liquidation is understanding the precise mechanics: how health
factors are calculated, when liquidation triggers, what interest rate spikes look like, and
where the protocol's risk parameters create opportunities or traps.

## Core Techniques

### Protocol Architecture Comparison

**Aave V3**: The market leader with multi-chain deployment. Features include E-Mode
(efficiency mode for correlated assets with up to 97% LTV), isolation mode for new assets,
portal (cross-chain liquidity), and GHO stablecoin integration. Governance-controlled risk
parameters per asset.

**Compound V3 (Comet)**: Simplified architecture with a single borrowable asset per market
(typically USDC). Multiple collateral types per market but no borrowing of collateral assets.
This reduces risk surface but limits composability compared to Aave's pooled model.

**Morpho**: Peer-to-peer matching layer that can sit on top of Aave/Compound, matching
lenders and borrowers directly at midpoint rates. Morpho Blue introduces permissionless
isolated markets with immutable parameters. Curators create vaults that allocate across
Morpho Blue markets.

**Spark Protocol**: MakerDAO's lending frontend, forked from Aave V3. Primarily for DAI
borrowing against crypto collateral. Benefits from Maker's DSR (DAI Savings Rate) for
supply-side yield and D3M (Direct Deposit Module) for liquidity.

### Collateral Factors and LTV

Each asset has parameters controlling how much can be borrowed against it:

- **LTV (Loan-to-Value)**: Maximum borrow amount as percentage of collateral value. ETH
  at 80% LTV means $10,000 ETH collateral allows $8,000 borrowing.
- **Liquidation Threshold**: The LTV at which liquidation becomes possible. Typically
  5-10% above max LTV. ETH might have 80% LTV, 82.5% liquidation threshold.
- **Liquidation Bonus/Penalty**: Discount given to liquidators (premium paid by borrower).
  Typically 5-10%. At 5% bonus, a liquidator repays $1,000 of debt and receives $1,050
  of collateral.

Health Factor = (Collateral * Liquidation Threshold) / Debt. Liquidation triggers at
HF < 1.0. Safe positions maintain HF > 1.5 for volatile assets, HF > 1.2 for stable pairs.

### Interest Rate Models

Lending protocols use kinked utilization curves. Below optimal utilization (typically 80%),
rates increase gradually. Above optimal, rates spike steeply to incentivize repayment and
new deposits.

Aave's model: below U_optimal, rate = base_rate + (U / U_optimal) * slope1.
Above U_optimal: rate = base_rate + slope1 + ((U - U_optimal) / (1 - U_optimal)) * slope2.

Typical parameters for stablecoins: base = 0%, slope1 = 4%, slope2 = 60-75%,
U_optimal = 80%. This means at 90% utilization, borrow rate jumps to approximately
37-41%. At 100%: 64-79%.

Rate spikes during high-demand events (market crashes causing liquidation cascades, yield
farming launches) can cause borrowing costs to exceed 100% annualized for hours or days.
Monitor utilization and have exit plans for high-utilization scenarios.

### Liquidation Mechanics

When a position's health factor drops below 1.0, liquidators can repay a portion of the
debt (close factor, typically 50%) and claim discounted collateral. The process:

1. Liquidator identifies undercollateralized position (via event monitoring or indexing).
2. Liquidator calls liquidation function, specifying debt to repay and collateral to seize.
3. Protocol transfers collateral (at discount) to liquidator.
4. Borrower's debt is reduced, improving health factor.

Liquidation is competitive. Professional liquidators run bots that monitor every position,
simulate price movements, and submit liquidation transactions within milliseconds. They
use flash loans to liquidate without capital: borrow funds, repay debt, receive collateral,
sell collateral, repay flash loan.

Partial liquidation prevents cascading failures. After a 50% close, the position's health
factor typically improves above 1.0, stopping further liquidation. However, in severe
crashes, sequential liquidations can fully close positions.

### Flash Loan Strategies

Flash loans provide uncollateralized borrowing within a single transaction. If the loan
is not repaid by transaction end, the entire transaction reverts. Fee: typically 0.05-0.09%.

Common flash loan use cases:
- **Collateral swaps**: Flash borrow, repay existing debt, withdraw collateral, deposit
  new collateral, borrow again, repay flash loan.
- **Self-liquidation**: Flash borrow, repay own debt, withdraw collateral, sell portion
  to repay flash loan. Avoids liquidation penalty.
- **Arbitrage**: Flash borrow, buy asset on DEX A, sell on DEX B at higher price, repay.
- **Leverage adjustment**: Flash borrow, deposit as collateral, borrow against it, repay
  flash loan. Achieves leverage in one transaction.

### Recursive Borrowing / Leverage Loops

Deposit collateral, borrow against it, deposit borrowed asset as more collateral, borrow
again. Each loop increases leverage. Maximum leverage = 1 / (1 - LTV). At 80% LTV:
max theoretical leverage = 5x.

Example at 75% LTV, 3 loops:
- Deposit 1 ETH ($3,000)
- Borrow $2,250 USDC, swap to 0.75 ETH, deposit
- Borrow $1,687, swap to 0.5625 ETH, deposit
- Borrow $1,265, swap to 0.42 ETH, deposit
- Total exposure: ~2.73 ETH on 1 ETH capital (2.73x leverage)

Liquidation price for this position: initial_price * (1 - 1/leverage) / LT, roughly
$1,200 for a $3,000 entry at 2.73x. Borrowing costs eat into returns and compound
with leverage.

## Advanced Patterns

### E-Mode and Correlated Asset Strategies

Aave V3's E-Mode allows up to 97% LTV for correlated asset pairs (stETH/ETH, USDC/DAI).
This enables extremely capital-efficient positions: deposit stETH, borrow ETH at 97% LTV,
stake the borrowed ETH for more stETH, repeat. The risk is stETH depeg, which has
historically reached 5-7% during stress events.

At 97% LTV, a 3.1% depeg triggers liquidation. Only use E-Mode leverage with clear
understanding of depegging risk and active monitoring.

### Isolated Lending Markets

Morpho Blue and newer Aave markets support isolation: each market has a single collateral
and single debt asset, with fixed parameters set at creation. Benefits include no risk
contagion between assets, permissionless market creation, and oracle-specific risk
containment.

The tradeoff is fragmented liquidity. Each isolated market has its own supply and
utilization, so rates can diverge significantly from pooled markets.

### Real-World Asset (RWA) Lending

Protocols like Centrifuge, Maple Finance, and MakerDAO's RWA vaults bring off-chain
assets (invoices, real estate, treasuries) as collateral for DeFi borrowing. MakerDAO
holds billions in US Treasury exposure through RWA vaults.

RWA lending introduces legal and counterparty risks absent from pure DeFi. Default
recovery requires legal proceedings, jurisdictional considerations, and trust in
off-chain custodians. The yield premium over T-bills reflects this additional risk.

### Interest Rate Arbitrage

When rates diverge across protocols (Aave borrow rate 3%, Compound supply rate 5%
for the same asset), arbitrage exists. Borrow on the cheaper platform, supply on the
more expensive one. This works best with stablecoins to avoid price risk.

Watch for: utilization shifts closing the spread, gas costs eating profits on small
positions, and smart contract risk doubling (exposed to both protocols).

### Liquidation Protection Strategies

- Maintain health factor buffers (HF > 2.0 in volatile markets).
- Use DeFi Saver or Instadapp automation to auto-repay or add collateral when HF drops.
- Deposit correlated collateral (e.g., borrow ETH against stETH) to reduce liquidation
  sensitivity.
- Set alerts at HF thresholds: warning at 1.5, critical at 1.2, emergency at 1.1.

## Anti-Patterns

*   **Maximum LTV Borrowing.** Borrowing at the protocol's maximum loan-to-value ratio leaves zero buffer for adverse price movements. One tick against you triggers liquidation with penalty. Always maintain a health factor buffer proportional to collateral volatility.

*   **Ignoring Interest Rate Spikes.** Maintaining leveraged positions without monitoring utilization rates risks exposure to spike events where borrowing costs exceed 100% APR for hours or days, rapidly degrading health factor.

*   **Recursive Leverage Without Liquidation Price Calculation.** Building leveraged loop positions without computing the exact liquidation price including accumulated interest creates positions where the liquidation threshold is unknown until it hits.

*   **Uncorrelated Collateral-Debt Pairs.** Borrowing volatile assets against uncorrelated volatile collateral (e.g., borrowing altcoin A against altcoin B) maximizes liquidation risk because both legs can move adversely independently.

*   **Treating Lending Yields as Risk-Free.** Depositing into lending protocols expecting guaranteed returns ignores smart contract risk, oracle risk, and governance risk that could result in total loss. Diversify across protocols and treat all DeFi yield as risk-bearing.

## What NOT To Do

- Do not borrow volatile assets against volatile collateral without understanding the
  correlation. Borrowing ETH against BTC is safer than borrowing ETH against an altcoin.
- Do not ignore interest rate spikes. Utilization above 90% can cause rates to exceed
  50-100% APR for hours or days, rapidly degrading health factor.
- Do not use maximum LTV. One adverse price tick and you face liquidation with penalty.
  Always leave a buffer proportional to the asset's volatility.
- Do not rely solely on dashboard health factor readings during market volatility. Oracle
  updates may lag, and the displayed HF can be stale.
- Do not flash loan without thorough testing on forked mainnet. A failed flash loan
  transaction reverts cleanly but still costs gas for the failed transaction.
- Do not assume lending protocol parameters are immutable. Governance can change LTV,
  liquidation thresholds, and interest rate curves. Monitor governance proposals for
  protocols where you have positions.
- Do not ignore the difference between variable and stable rates. Aave's stable rate is
  not truly fixed; it can be rebalanced if utilization changes significantly.
- Do not build recursive leverage positions without calculating the exact liquidation
  price including accumulated interest.
- Do not treat lending yields as risk-free. Smart contract risk, oracle risk, and
  governance risk are always present. Diversify across protocols.

## Review & Production Validation (2026-10-31)

- **Domain control (DeFi protocol economics):** Verify collateral parameters, oracle freshness, fees, liquidation and withdrawal constraints.
- **Independent validation:** Distinguish net yield from nominal rewards; model depeg, hack and liquidity stress.
- **Time-sensitive details:** Treat fixed rates, thresholds, package versions, protocols and jurisdiction-specific rules in the examples above as illustrative unless reconfirmed against primary documentation.
- **Before relying on the result:** State inputs and assumptions; verify calculations and edge cases, and identify what has not been executed or tested.
