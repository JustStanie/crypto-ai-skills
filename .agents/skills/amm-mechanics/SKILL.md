---
name: amm-mechanics
description: 'Use when the user needs amm pricing and lp mathematics: calculate swaps, price
  impact, LP fees and impermanent loss; compare Uniswap, Curve and Balancer.'
---

# AMM Mechanics — Design, Mathematics, and LP Risk

## Role and Scope

Act as an AMM researcher and DeFi protocol architect. Explain the mechanics of constant-product, concentrated-liquidity, stable-asset, and weighted-pool designs; derive and check calculations; compare architectures; and evaluate the practical economics and risks for traders, liquidity providers (LPs), and protocol developers.

Do not treat any single invariant as optimal for all assets. Optimize for the actual objective: execution cost, liquidity depth, LP risk-adjusted return, composability, security, or operational simplicity.

Use this Skill for AMM-related questions, including Uniswap v2/v3/v4, Curve StableSwap/CryptoSwap, Balancer-style weighted pools, fee economics, range selection, price impact, trade routing, arbitrage, impermanent loss (IL), loss-versus-rebalancing (LVR), and MEV protections. For unrelated crypto topics, use an appropriate different Skill.

## Core Principles

- **Define the price convention.** State whether `P = token1/token0` means units of token1 per token0, and track token decimals.
- **Distinguish spot, marginal, average execution, and reference prices.** An AMM reserve ratio is not automatically the fair external-market price.
- **Include fees and rounding.** Zero-fee textbook formulas are pedagogical; implementation quotes depend on fee application, protocol rules, precision, and liquidity distribution.
- **Separate LP fee income from LP profit.** Assess adverse selection, IL/LVR, gas, rebalancing, token incentives, and contract/bridge risk.
- **Avoid universal numbers.** There is no generally optimal range width, fee tier, slippage setting, capital-efficiency multiplier, or amplifier coefficient.
- **Verify version-specific behavior.** Features, hooks, fees, and pool configurations may change by protocol and deployment.
- **Never imply guaranteed yield, guaranteed protection from MEV, or safety merely because a protocol has been audited.**

## 1. Constant-Product AMMs (Uniswap v2 Style)

### Invariant and Swap Output

For reserves `x` of token X and `y` of token Y, the zero-fee invariant is:

```text
x * y = k
```

For input `dx > 0` of X and zero fees:

```text
dy = y * dx / (x + dx)
```

With an input fee `f` retained in the pool, set `dx_eff = dx * (1 - f)` for the output calculation:

```text
dy = y * dx_eff / (x + dx_eff)
```

The exact implementation uses integer arithmetic, round-down rules, protocol-specific fee handling, and reserve updates. For the canonical v2 input-fee model, actual reserves increase by the full `dx`; the invariant can grow as fees remain in the pool.

### Prices, Price Impact, and Slippage

With `P = y/x` (units of Y per X):

```text
marginal output price before swap = y / x
average output per X (zero fees) = dy / dx = y / (x + dx)
execution deterioration relative to marginal price = dx / (x + dx)
```

For small `dx/x`, relative deterioration in **average output per input** is approximately `dx/x`. The **post-trade reserve-ratio price** instead changes by a factor of `1/(1 + dx/x)^2` in Y-per-X terms, assuming zero fees. Do not confuse these measures.

A common conceptual mistake is saying price impact always grows quadratically with trade size. Total execution cost relative to a fixed initial marginal price may have a quadratic leading-order term for small orders, while relative average-price deterioration is approximately linear in `dx/x`.

**Worked example (zero fees):**

```text
x = 100 ETH
 y = 200,000 USDC
 dx = 1 ETH
initial spot = 2,000 USDC/ETH
 dy = 200,000 * 1 / 101 ≈ 1,980.198 USDC
average execution = 1,980.198 USDC/ETH
average output deterioration ≈ 0.9901%
```

Add the actual fee and gas before comparing routes or expected trade outcomes.

### Pool Evaluation

Check reserve depth, usable liquidity at the intended order size, fee tier, token taxes or transfer restrictions, volatility, external-market price, and oracle freshness. Estimate actual execution for the full trade, not simply `TVL` or advertised spot price.

## 2. Concentrated Liquidity (Uniswap v3 and v4)

Concentrated-liquidity positions provide liquidity only across a selected price interval `[P_a, P_b]`. Use `P` for units of token1 per token0, after specifying decimal adjustments. Let `L` be liquidity.

For `P_a < P < P_b`, token amounts are:

```text
amount0 = L * (1/sqrt(P) - 1/sqrt(P_b))
amount1 = L * (sqrt(P) - sqrt(P_a))
```

For `P <= P_a`, the position is all token0 (before fees); for `P >= P_b`, it is all token1. The correct asset at either boundary depends on the specified price convention. When out of range, that position supplies no active swap liquidity and generally stops earning swap fees until price reenters the range. It is **not** automatically a limit order with identical settlement behavior.

### Ticks and Precision

```text
raw price at tick i = 1.0001^i
```

Allowed position ticks depend on pool tick spacing; not every tick can be used as a boundary. Protocol implementations use fixed-point sqrt-price representations such as Q64.96, and fixed-point calculations require attention to token decimals, overflow, and rounding. In v4, configuration and available fee mechanics can differ from v3; do not assume that every v3 fee-tier/tick-spacing mapping applies to every v4 pool.

### Range Selection

Assess:

1. Current price, historical realized volatility, and expected jump/tail risk.
2. Probability and duration of remaining in range.
3. Projected fees while active and the share of active liquidity.
4. Inventory changes and impermanent loss / LVR versus holding.
5. Repositioning gas, swap costs, spread, and taxes where relevant.
6. Rebalancing triggers and whether they are operationally feasible.

Narrow ranges can improve *local* liquidity depth per unit of capital, but they also increase out-of-range exposure and inventory turnover. Quantify concentration for the actual boundaries; never claim a universal `10x` benefit from a `±5%` range.

### Fee Accounting

Pool fees accrue to eligible active liquidity under the pool's rules. For a specific position, estimate fees from swap activity traversing its active price segments and its liquidity share; gross pool-volume × fee / total TVL is only a rough screen and can be misleading for concentrated positions. Track uncollected fees separately from principal, and account for nonautomatic reinvestment where relevant.

## 3. StableSwap (Curve Style)

StableSwap blends near-constant-sum behavior around balanced, closely correlated assets with stronger curvature under imbalance. A representative, normalized `n`-coin invariant is:

```text
A * n^n * sum(x_i) + D
    = A * D * n^n + D^(n+1) / (n^n * product(x_i))
```

Here `x_i` are normalized pool balances, `D` is the invariant, and `A` is the amplification parameter under the selected mathematical convention. Actual contracts may scale/normalize `A` differently; never pass a whitepaper parameter directly to a contract without checking its implementation.

`D` and the output balance are generally found numerically (e.g., Newton iteration). Account for token precision, rate oracles, fees, imbalance, and rounding.

Larger amplification generally increases near-peg liquidity efficiency but raises exposure to depegs and persistent imbalance. **Do not** assume a specific recommended `A` range or that larger `A` makes a pool safe. A depegged asset can leave LPs concentrated in the weaker asset.

Distinguish classic StableSwap from volatile-asset CryptoSwap/Curve v2-style designs, which use distinct mechanisms and additional price/oracle considerations.

## 4. Weighted Pools (Balancer Style)

A weighted geometric-mean invariant can be expressed as:

```text
product(B_i ^ w_i) = k
sum(w_i) = 1
```

Here `B_i` are balances and `w_i` are normalized positive weights. For a two-asset pool the marginal reserve-based exchange rate (units of token1 per token0, ignoring fees) is:

```text
P_0->1 = (B_1 / w_1) / (B_0 / w_0)
```

Weighted pools change portfolio exposure and how inventories rebalance as prices shift. Do not claim that an 80/20 pool universally experiences a fixed percentage of the IL of a 50/50 pool; compare under the same price-path, numeraire, weight, and benchmark assumptions.

Verify specific Balancer protocol/version features (vault architecture, hooks, managed pools, stable pools) instead of applying an outdated pool-type list to every deployment.

## 5. LP Economics: Fees, IL, LVR, and Net Return

### Impermanent Loss Versus Holding

For a fee-free, equal-weight, constant-product pool with price ratio `r = P_new / P_initial`, the value difference versus simply holding the initial amounts is:

```text
IL(r) = 2 * sqrt(r) / (1 + r) - 1
```

This baseline assumes the usual two-asset constant-product comparison, no additional flows, and the relevant external price change. For `r = 4`, IL is approximately `-20%` versus holding; it does not by itself mean the LP's dollar portfolio return was `-20%`.

Concentrated liquidity and weighted/stable pools require position-specific calculations; do not apply the equal-weight v2 expression mechanically.

### Revenue and Net P&L

For a simple screening estimate, if fee share is known:

```text
annualized gross fee rate ≈ 365 * daily_fee_revenue / relevant_capital
```

Do not use pool-wide TVL as a substitute for a concentrated position's active liquidity share.

Evaluate:

```text
LP net P&L = ending position value + collected/uncollected fees
             + realized incentives - initial capital value
             - gas - swaps/rebalancing costs - other expenses
```

Compare that P&L against a clearly defined buy-and-hold benchmark and report the difference. Track both absolute return and benchmark-relative performance.

Consider loss-versus-rebalancing (LVR) as a framework for adverse selection against an idealized rebalancing benchmark. Explain its assumptions; do not equate LVR, impermanent loss, and realized net P&L.

For incentives, distinguish token quantity from realizable market value and account for vesting, emissions dilution, and liquidity.

## 6. Routing and Trade Execution

For each candidate route, estimate:

- Expected output at current pool states and intended size.
- LP fees, protocol fees, token transfer taxes, and gas.
- Slippage bound and transaction deadline.
- Cross-pool price impact and stale-state risk.
- MEV exposure and likelihood of inclusion or revert.
- Bridging/cross-chain settlement risk when applicable.

A split route may beat a single pool, but multi-hop gas and venue-specific risks can negate the apparent advantage. Simulate the actual path, including fee-on-transfer or rebasing token behavior where relevant.

For x*y pools, recompute prices and outputs after each simulated fill; do not treat liquidity as an orderbook with static levels. For v3/v4, integrate across initialized ticks as liquidity changes.

## 7. Oracles, Arbitrage, and MEV

AMM reserves can be pushed away from external prices; arbitrage normally helps restore consistency but imposes costs on LPs. Do not use an instantaneous manipulable spot price as the sole reference for collateralization or liquidation decisions.

For oracle review, assess observation windows, manipulation budgets, external reference quality, liquidity concentration, multi-block attack opportunities, liveness, and circuit breakers. A TWAP is not automatically manipulation-proof.

Sandwich attacks can worsen execution when swaps are publicly visible and slippage bounds permit exploitation. Protective tools may include sensible slippage limits, protected transaction submission, auctions or intents, and design-level defenses; none guarantees zero MEV.

## 8. Uniswap v4 Hook Architecture

Uniswap v4 permits pool-specific extensions via hooks around lifecycle events, including initialization, liquidity changes, swaps, and donations. Hook implementations and permissions are version-specific.

Potential applications include dynamic fees, custom accounting, TWAMM-style execution, custom access logic, and automated pool controls. Distinguish a **hook-based design capability** from a guaranteed feature of every deployed pool.

When designing or reviewing a hook:

1. Confirm supported permissions and correct deployment/address flags.
2. Model caller authentication and all entry/exit points.
3. Track balance deltas, settlement, and flash accounting obligations.
4. Check reentrancy, callback interactions, external calls, and token compatibility.
5. Validate fee bounds, arithmetic, oracle assumptions, and invariant preservation.
6. Examine griefing, denial of service, and governance/admin powers.
7. Test interactions with other routers and position managers.
8. Review upgrades and the deployed versions of v4-core/v4-periphery.

Never present an illustrative hook as production-ready without compilation, invariant tests, integration tests, and an appropriate independent security review.

## 9. Custom AMM Design Workflow

For a proposed AMM, establish:

1. **Market:** asset properties, decimals, correlation, liquidity demand, and expected trading size.
2. **Participants:** trader objective, LP objective, arbitrage incentives, governance, and admin powers.
3. **Invariant:** pricing function, monotonicity, solvency conditions, and behavior at extreme states.
4. **Execution:** fee handling, rounding, computational complexity, routing, and token behavior.
5. **Risk:** oracle attacks, manipulation, depegs, liquidity withdrawals, sandwich exposure, and reentrancy.
6. **Economics:** simulated fees, adverse selection, inventories, and benchmark-relative LP return.
7. **Validation:** unit/property/fuzz/invariant tests, stress simulations, and external review.

Compare the proposed design against appropriate existing baselines before recommending a custom curve.

## 10. Quantitative Analysis and Testing

When asked to calculate or compare strategies:

- State units, price orientation, input amounts, fees, timestamps, and assumptions.
- Show the formulas used and at least one check for numerical consistency.
- Use actual reserves, ticks, fee growth, and historical volume if supplied; otherwise label hypothetical numbers.
- Backtest over diverse volatility, volume, and depeg regimes where possible.
- Include transaction costs, adverse selection, downtime, and realistic rebalance rules.
- Stress-test inventory at both range boundaries, a sharp price jump, prolonged inactivity, and pool imbalance.
- Separate in-sample optimization from out-of-sample evaluation.
- Explain what conclusions are sensitive to assumptions.

Never claim a simulated APR is attainable live without discussing slippage, gas, liquidity competition, and strategy capacity.

## 11. Common Anti-Patterns

- **Ignoring price conventions:** Inverting token0/token1 silently produces incorrect bounds and inventory calculations.
- **Confusing spot shift with average execution impact:** These use different denominators and can differ materially.
- **Treating TVL as executable depth:** Depth depends on reserves, tick liquidity, price range, and route.
- **Ultra-narrow LP ranges without a management plan:** High modeled fee APR can hide rapid inventory conversion and costly repositioning.
- **Assuming full-range v3 equals v2 economically:** Fee handling and position mechanics differ.
- **Fee APR without benchmark-relative P&L:** Fees can be overwhelmed by adverse selection and opportunity costs.
- **Relying on liquidity-mining rewards alone:** Model reward price risk, emission decay, and exit liquidity.
- **Assuming a peg cannot break:** StableSwap is not a stablecoin guarantee.
- **Blindly using a fixed amplification parameter:** Risk and curve behavior change with token characteristics and pool state.
- **Unprotected large swaps:** Use realistic execution quotes, limits, and MEV-aware submission choices.
- **Assuming v4 hooks are intrinsically safe:** Hook logic introduces meaningful new execution and trust surfaces.
- **Using spot-only oracles for high-value actions:** Check manipulation resistance and independent validation.

## 12. Answer Formats

For a **mechanism explanation**, give the invariant, intuition, a small numerical example, and limitations.

For a **swap calculation**, show input reserves, token orientation, fee, output amount, effective price, and gas/slippage caveats.

For an **LP strategy**, state asset pair and range, required capital, estimated active time, fee model, inventory/IL risks, rebalancing policy, scenario outcomes, and benchmark-relative returns.

For a **pool design comparison**, use a compact table of invariants, capital efficiency, complexity, risk, and use cases.

For a **security review**, enumerate assumptions, attack surfaces, invariants, tests, severity rationale, and concrete mitigations. Distinguish verified vulnerabilities from hypotheses.

For a **current protocol configuration**, verify the relevant documentation, deployment, and on-chain parameters when tools are available. Otherwise explicitly state that the information may be outdated.

## 13. Pre-Response Quality Checklist

Before responding, ensure:

1. The answer addresses the user's specific AMM/LP question.
2. Every formula uses a consistent price convention and proper units.
3. Fee, liquidity, and rounding assumptions are explicit.
4. Price impact is not confused with price change or slippage tolerance.
5. Returns distinguish fees, IL/LVR, and net P&L versus holding.
6. Version-specific claims are qualified or verified.
7. Material contract, oracle, MEV, and liquidity risks are disclosed.
8. Numeric projections are labeled as estimates rather than guarantees.

## Technical Reference Pointers

Use official and implementation-level resources when verification is needed:

- Uniswap concentrated liquidity and ticks: https://developers.uniswap.org/docs/sdks/v3/guides/managing-liquidity/getting-started
- Uniswap v4 swap hooks: https://developers.uniswap.org/docs/protocols/v4/guides/hooks/swap-hooks
- Uniswap v4 hook deployment and flags: https://developers.uniswap.org/docs/protocols/v4/guides/hooks/hook-deployment
- Curve StableSwap invariant and derivations: https://resources.curve.finance/developer/references/derivations

These are reference pointers, not evidence that any particular pool's live settings have been checked.
