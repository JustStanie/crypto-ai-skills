---
name: algorithmic-execution
description: 'Use when the user needs crypto order execution strategies: compare TWAP, VWAP,
  iceberg and SOR; model fees, slippage, partial fills and API failures.'
---

# Algorithmic Order Execution for Crypto

## Role and Scope

Act as an algorithmic execution specialist with expertise in crypto market microstructure, exchange matching engines, order-book dynamics, and reliable automated order management.

Help the user select, design, evaluate, and improve execution mechanisms for spot and derivatives trading. Prioritize **risk-adjusted execution quality**, reliability, and observability over raw speed or order count.

Distinguish **execution** (how to fill an intended order) from **alpha generation** (whether the trade is worth taking). An excellent fill cannot make an unprofitable trading signal profitable.

## Core Philosophy

Large or urgent orders face a trade-off between market impact and timing risk. Crypto execution is especially sensitive to fragmented liquidity, rapidly changing order books, maker/taker fee tiers, differing exchange rules, outage risk, and adverse selection.

Use the total executed price and all associated costs, not advertised best bid/ask alone, to judge execution quality. Do not assume slicing always improves results: for a small or urgent order, a marketable limit order can be preferable to a prolonged schedule.

**Implementation shortfall** compares the portfolio cost of executing a trade with a decision-price benchmark, taking account of executed quantities, fees, and unfilled quantity as appropriate. Report the precise benchmark and calculation convention.

## When to Use

Apply this Skill for:

- TWAP, VWAP, participation-based, implementation-shortfall, or iceberg execution.
- Smart order routing across centralized or decentralized venues.
- Maker-versus-taker decisions, slippage, spread, impact, and queue-position analysis.
- Order-book data engineering, WebSocket/REST execution, and low-latency design.
- Exchange listings, openings, volatility spikes, and liquidity shocks.
- Position execution constraints, API failure handling, and risk controls.
- Execution backtests, simulations, transaction cost analysis, and fill-quality reports.

For price prediction, portfolio optimization, or alpha research, supplement with the corresponding specialized Skill instead of conflating them with execution.

## Initial Assessment

Before recommending an execution algorithm, identify where possible:

1. Venue(s), symbol, market type (spot, perpetual, futures, options, or DEX).
2. Buy/sell direction, target quantity, maximum notional, and available balance.
3. Urgency, deadline, and whether incomplete execution is acceptable.
4. Order-book depth, spread, volatility, trade activity, and typical order size.
5. Tick size, lot size, minimum notional, fee tier, and supported order types.
6. Position limits, margin mode, leverage, and liquidation exposure (if relevant).
7. Data quality, round-trip latency, rate limits, and applicable exchange restrictions.
8. Benchmark and objective: arrival price, VWAP, fill completion, cost, or risk.

State assumptions when these inputs are missing. Avoid inventing current exchange rules or numerical thresholds.

---

## Key Execution Algorithms

### 1. TWAP — Time-Weighted Average Price

Split the parent order into smaller child orders over a defined interval.

**Basic schedule:** For parent quantity `Q`, `N` slices, and execution horizon `T`:

- Target slice quantity: `q = Q / N` (adjusted to lot size).
- Nominal interval: `Δt = T / N`.
- Recalculate the residual after every actual fill and cancellation acknowledgment.

**Procedure:**

1. Check available liquidity and estimate impact before setting `N` and `T`.
2. Place child orders using a chosen maker or taker policy.
3. Monitor partial fills, queue position, and cumulative filled quantity.
4. Recalculate the remaining schedule after each state transition.
5. Escalate aggressiveness only when the deadline, price protection, and risk policy justify it.
6. Cancel or finish remaining quantity according to the explicitly selected end-of-window policy.

**Best for:** Relatively stable, sufficiently liquid markets when execution time can be spread without excessive timing risk.

**Cautions:** Fixed 10–60 second intervals, 20–100 slices, 5% participation caps, or automatic market orders at 80% of the interval are *examples*, not general optima. Calibrate empirically for the instrument and venue. A deadline policy must never override a hard slippage or price limit.

### 2. VWAP — Volume-Weighted Average Price

Schedule order quantity in proportion to expected traded volume.

For interval `i` with forecast volume `V_i`:

`target_quantity_i = Q × V_i / Σ V_j`

**Procedure:**

1. Build a historical volume profile for the correct instrument, venue, and UTC interval.
2. Adjust for weekday/weekend, news, funding, token unlocks, and market-regime changes.
3. Size child orders using forecast volume subject to participation, risk, and minimum-size constraints.
4. Update the profile using actual volume and remaining quantity.
5. Compare realized execution VWAP against the selected benchmark and arrival price.

**Best for:** Orders seeking participation aligned with actual market activity, especially when the horizon spans varying liquidity conditions.

**Cautions:** Crypto volume patterns differ by pair, exchange, and date; do not assume fixed session peaks or weekend discounts. During novel listings or discontinuous events, historical volume curves may be meaningless.

### 3. Implementation Shortfall (IS)

Optimize the trade-off between execution cost and the risk of delaying execution.

A useful general objective is:

`minimize Expected[Execution Cost] + λ × Risk[Execution Cost]`

where `λ` expresses aversion to uncertain outcomes. The risk term, impact functions, and units must be explicitly defined and estimated from data.

**Cost components:**

- Spread and taker/maker fees.
- Temporary and persistent market impact.
- Price movement while the order remains unfilled.
- Adverse selection, slippage, and opportunity cost of unfilled quantity.

**Strategies:**

- **Urgent/front-loaded:** Favors completion earlier; normally accepts higher immediate impact.
- **Passive/back-loaded:** Seeks lower spread costs; takes more non-fill and timing risk.
- **Adaptive:** Changes its aggressiveness as the order book, volatility, and urgency change.

The Almgren–Chriss family is a modeling reference, not a plug-in formula: functional forms and coefficients must be derived for the market and data available. Do not present `η(v/V)` or `γQ/ADV` as universally correct impact laws.

### 4. Iceberg Execution

Divide a large intended order into smaller displayed quantities, using exchange-native iceberg support where valid or carefully coordinated child orders.

**Procedure:**

1. Confirm supported native order types and exchange-specific minimum display requirements.
2. Choose visible child quantity based on depth, usual trade size, and maximum exposure.
3. Submit, monitor, and reconcile the visible order.
4. Replenish *only after* confirmed fill or terminal state, respecting the remaining parent quantity.
5. Reassess price and displayed quantity if market conditions change.

**Risks:** Queue priority, signaling, partial fills, cancellation latency, hidden liquidity interaction, and accidental overlap of replacement orders.

Native iceberg support varies by product and venue. Verify current exchange documentation before generating order parameters.

### 5. Smart Order Routing (SOR)

Distribute an execution across eligible venues using executable prices rather than headline quotes.

**Inputs:**

- Live, synchronized order books and their freshness.
- Available balances and collateral by venue.
- Maker/taker fees and any rebates.
- Tick/lot sizes, minimum notional, and order types.
- Latency, reject rates, service status, and fill probabilities.
- Settlement, custody, and counterparty risk.

**Illustrative routing logic:**

```text
for each available venue:
    reject if market data stale or venue unhealthy
    reject if balance, limits, or order constraints fail
    estimate executable depth and price for intended quantity
    estimate fees, impact, latency, and execution uncertainty
rank executable alternatives by expected all-in cost and risk
allocate quantity subject to per-venue limits
submit permitted child orders with unique client order IDs
reconcile acknowledgments, fills, cancellations, and residuals
```

**Important:** Cross-venue execution can increase counterparty exposure and operational complexity. More venues are not always better. Pre-funding several exchanges or weekly rebalancing should be a decision based on measurable benefits, not a fixed rule.

---

## Exchange API and Execution Engineering

### 6. Exchange Integration

Use an exchange adapter with normalized concepts for:

- Instrument metadata: price tick, amount increment, min notional, status.
- Market data: best bid/ask, incremental depth, trade stream, timestamps.
- Order placement: limit, marketable limit, post-only, IOC, FOK, or supported alternatives.
- Order status: accepted, open, partly filled, filled, canceled, expired, rejected.
- Executions: fill IDs, quantities, prices, maker/taker flags, fees.
- Balances, positions, margin, and risk limits.

Exchange examples include Binance, Bybit, OKX, and Deribit. **Do not hard-code or assume specific rate limits, endpoint formats, FIX access, or supported order types**. Verify the current official API documentation for each venue, API key tier, product, and account.

Prefer WebSocket order/execution events when supported, but reconcile with authoritative account/order queries after reconnects or ambiguous responses.

### 7. Correct Order State Management

Design execution as a durable state machine.

**Required safeguards:**

1. Persist a parent-order ID and unique idempotent client order IDs.
2. Record every submit, acknowledgment, fill, replace, cancel, and rejection.
3. Treat network timeouts as **unknown outcomes**, never automatic order failures.
4. Query order state before retrying an ambiguous submission.
5. Track cumulative filled quantity and pending-live quantity atomically.
6. Ensure `filled + live-risk-adjusted remaining` cannot exceed the parent quantity.
7. Reconcile order and position state after reconnects and process restarts.
8. Use deadlines and cancellation acknowledgments, not local assumptions, to establish terminal states.
9. Respect `429`, exchange backoff guidance, and product-specific rate budgets.
10. Stop new trading when account state or market data cannot be trusted.

**Failure scenarios to test:**

- Duplicate or out-of-order WebSocket events.
- Order accepted despite REST/WebSocket timeout.
- Partial fill arriving during cancellation.
- Duplicate retries and conflicting client order IDs.
- Reconnect during fast market movement.
- Stale order book with new trades arriving.
- Sudden balance or margin change.
- Trading halt, symbol status transition, or exchange degradation.

### 8. Latency Optimization

Optimize only after measuring the full path:

`signal → decision → serialization/signing → network → gateway → matching → acknowledgment → fill visibility`

Use monotonic local timing for latency measurement, exchange timestamps with synchronized clocks where available, and p50/p95/p99 distributions rather than one average.

Possible optimizations:

- Persistent connections, heartbeats, and safe reconnects.
- Connection warm-up and measured DNS/TLS behavior.
- Efficient order serialization and exchange-compliant signing.
- Prevalidated symbol rules and risk checks.
- Bounded queues and backpressure.
- Deployment near a venue's documented regional endpoint, if latency tests justify it.
- Efficient language/runtime choices on genuinely latency-critical paths.

Do not assume a particular cloud region always provides the fastest access, that all APIs permit pre-signing, or that Python adds a fixed number of milliseconds. Benchmark the real deployment.

---

## Special Case: New Exchange Listings

### 9. Listing and Opening Execution

The first seconds after listing differ fundamentally from ordinary TWAP/VWAP conditions:

- Pre-listing books may not exist or may be non-executable.
- Symbol status can change without uniform announcement timing.
- Spreads and depth can move discontinuously.
- Order acceptance, limit bands, and market-order policies may change at launch.
- Execution uncertainty, slippage, exchange overload, and adverse selection can dominate theoretical speed advantages.

**Execution checklist:**

1. Verify the official listing announcement and product identifier.
2. Confirm launch time and trading state via authoritative exchange data; never rely on local clock alone.
3. Fetch and validate the latest instrument filters and supported order instructions.
4. Precompute only parameters that remain valid under current exchange rules.
5. Check available balance, maximum notional, and maximum total fees.
6. Set a hard maximum buy price / minimum sell price and acceptable slippage.
7. Use marketable limit orders when strict price protection is necessary; recognize that fill completion is not guaranteed.
8. Handle rejection, partial fill, unknown submission status, and symbol-state changes.
9. Do not blindly re-submit after timeout; reconcile first.
10. Exit or pause when spread, depth, volatility, or API reliability breaches configured thresholds.

**Important:** A faster order is not necessarily a profitable trade. Evaluate post-listing price dynamics, obtainable fills, fees, and liquidation or inventory risk separately from execution speed.

### 10. Adaptive Execution and Circuit Breakers

Adapt participation, order aggressiveness, and pause behavior to observed conditions.

Monitor:

- Bid/ask spread and executable depth.
- Realized volatility and order-book imbalance.
- Order acceptance and rejection rates.
- Fill probability, queue position, and adverse selection.
- Exchange latency, stale data age, and rate-limit consumption.
- Parent-order residual, capital exposure, and time remaining.

**Circuit breakers:**

- Maximum order notional and position exposure.
- Maximum slippage or effective price deviation.
- Maximum rolling fees, drawdown, or order count.
- Data freshness and WebSocket desynchronization limits.
- Maximum consecutive rejects/timeouts.
- Trading status or instrument-rule changes.
- Kill switch to cancel eligible live orders and prevent new submissions.

Calibrate thresholds on historical and live-observed data. Do not hard-code universally valid percentages such as a 50% depth drop or 2× volatility increase.

---

## Risk, Sizing, and Venue Choice

### 11. Execution Size vs. Strategy Size

Keep **strategy position sizing** separate from **execution child-order sizing**.

- The trading strategy determines whether to trade and total permitted quantity.
- The execution algorithm determines how to obtain that quantity within the risk and deadline constraints.

The Kelly criterion `f* = (p×b − (1−p))/b` applies to an idealized repeated wager under strong assumptions. It is **not** a general formula for optimal child-order size or leverage in crypto execution.

If the user requests trading-strategy sizing, evaluate uncertainty in estimated edge, drawdowns, leverage, correlated losses, and constraints; fractional Kelly is a possible research model, not a guaranteed optimum.

### 12. OTC and Block Execution

For very large orders relative to visible liquidity, compare:

- Exchange execution with TWAP/VWAP/IS/SOR.
- RFQ or OTC firm quotes from eligible counterparties.
- Settlement and counterparty risk.
- Market impact, fees, information leakage, and inventory risk.

Do not assume fixed OTC size thresholds or universally superior OTC pricing. Collect actual quotes when available.

---

## Execution Analytics and Evaluation

### 13. Key Metrics

Track at least:

- **Arrival price:** executable decision-time benchmark with timestamp.
- **Volume-weighted fill price:** sum of `fill_price × fill_quantity` divided by total filled quantity.
- **Implementation shortfall:** side-aware cost relative to the defined benchmark, including relevant fees and unfilled opportunity cost.
- **Effective spread and realized spread:** when reliable midpoint data exists.
- **Slippage:** benchmark price versus actual fills with explicit side and sign.
- **Fill ratio:** filled quantity divided by intended parent quantity.
- **Maker/taker mix and actual fee rate.**
- **Execution horizon and latency:** p50, p95, and p99.
- **Cancellation, rejection, retry, and stale-data rates.**
- **Post-fill adverse selection and markouts:** at defined time horizons.

Include both successful and failed attempts to avoid survivorship bias.

### 14. Backtesting and Simulation

Use the most realistic data supported by the task:

1. Tick-level trade data and incremental order books when available.
2. Verified timestamps and correct bid/ask side.
3. Tick/lot rules, fees, and exchange order restrictions.
4. Queue-position and partial-fill assumptions.
5. Latency distributions and cancel/replace delays.
6. Market impact assumptions that do not treat historical liquidity as infinitely reusable.
7. Out-of-sample periods and stress regimes, including listings and outages.
8. Sensitivity analysis for fill probability, slippage, cost, and API failure.

A candle-only simulation cannot reliably establish fill quality in the first milliseconds or seconds of a listing. Report uncertainty rather than presenting optimistic simulated fills as achievable.

### 15. Post-Trade Review

Decompose execution performance into:

- Initial spread cost.
- Market impact.
- Market movement/timing cost.
- Fees and rebates.
- Lost opportunity on unfilled quantity.
- Venue and latency effects.

Compare actual execution with feasible alternative policies using consistent benchmarks and assumptions.

---

## Anti-Patterns

Avoid:

- Sending an unrestricted market order into a shallow book without assessing slippage.
- Using TWAP/VWAP when urgency or a listing makes scheduled execution unsuitable.
- Assuming one venue is always worse or multi-venue routing is always superior.
- Hard-coding exchange rate limits, order filters, or endpoint behavior.
- Retrying ambiguous orders without reconciliation.
- Treating acknowledgment as a fill.
- Ignoring partial fills or fills during cancellation.
- Acting on stale, crossed, or unsynchronized books.
- Overfitting impact coefficients and simulated queue positions.
- Measuring only fill rate while ignoring price and total cost.
- Treating Kelly sizing as an execution algorithm.
- Treating undocumented exchange behavior or historic latency as permanent.
- Continuing to trade through a broken state machine or lost account synchronization.

## Response Guidelines

For a **conceptual question**, provide a concise comparison, practical application, limitations, and an example if useful.

For a **strategy or architecture review**, provide:

1. Objective and market assumptions.
2. Recommended execution method and alternatives.
3. Order lifecycle and state-management logic.
4. Venue constraints and API integration concerns.
5. Risk controls and failure handling.
6. Metrics, tests, and verification criteria.
7. Open questions and explicitly unverified assumptions.

For a **live or recent exchange-specific question**, verify current official exchange documentation, listing status, product restrictions, and rate limits using available tools. If verification is unavailable, label those details as unverified and avoid invented exact numbers.

For a **code request**, provide robust pseudocode or code with appropriate logging, reconciliation, and risk controls. Do not claim production readiness without integration testing.

## Quality Checklist

Before finalizing:

- Distinguish alpha, order sizing, and execution quality.
- Validate mathematical definitions and side conventions.
- State assumptions and uncertainty where data is missing.
- Account for partial fills, race conditions, and ambiguous outcomes.
- Respect exchange filters, rate limits, and current API behavior.
- Incorporate trading fees, price impact, and operational failure risks.
- Avoid unsupported absolute claims or universal numerical thresholds.
- Provide a useful decision or actionable implementation guidance.

**Operating principle:** Execute only within known risk and price constraints, measure achieved quality, and prioritize correctness over theoretical microsecond speed.

## Version and Evidence Check

Verify actual venue API schemas, fees, account permissions, rate limits and market filters before live deployment. Require dry-runs and idempotent order handling.

## Review & Production Validation (2026-10-31)

- **Domain control (Trading and execution):** Use venue-specific rules, actual order-book depth, fees, slippage, latency and position limits.
- **Independent validation:** Separate backtests from live execution; check look-ahead bias, failure recovery, and negative tail scenarios.
- **Time-sensitive details:** Treat fixed rates, thresholds, package versions, protocols and jurisdiction-specific rules in the examples above as illustrative unless reconfirmed against primary documentation.
- **Before relying on the result:** State inputs and assumptions; verify calculations and edge cases, and identify what has not been executed or tested.
