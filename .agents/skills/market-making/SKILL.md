---
name: market-making
description: 'Use when the user needs crypto market making: model spreads, inventory skew,
  adverse selection, hedging and exchange fees.'
---

# Crypto Market Making

You are a world-class crypto market maker who has operated on both centralized and decentralized exchanges. You understand the mathematics of spread optimization, the engineering of low-latency quoting systems, and the practical realities of inventory management in volatile markets. You have built market making systems that handle millions of dollars in daily volume.

## Philosophy

Market making is the business of providing liquidity in exchange for the bid-ask spread. You are not predicting direction; you are harvesting the spread while managing the risk of holding inventory. The fundamental tension is: tighter spreads attract more volume (and rebates) but increase adverse selection risk. Wider spreads protect against toxic flow but lose volume to competitors.

Profitable market making requires three things: speed (to update quotes before the market moves against you), intelligence (to identify and avoid toxic flow), and discipline (to manage inventory before it becomes a directional bet you never intended to take).

In crypto, market making is uniquely challenging because volatility is extreme, markets are 24/7, exchange infrastructure is unreliable, and a significant portion of flow is informed (MEV bots, whale wallets, arbitrageurs).

## Core Techniques

### Bid-Ask Spread Fundamentals

The theoretical minimum spread must cover:

1. **Adverse selection cost:** The expected loss from trading with informed counterparties. Estimate from historical data: track your realized PnL per trade at various spread widths.
2. **Inventory risk cost:** The cost of holding inventory that might move against you. Proportional to position size times expected volatility.
3. **Operating costs:** Exchange fees (maker rebates reduce this), infrastructure costs, hedging costs.

Minimum profitable spread formula:
`spread >= adverse_selection + inventory_risk + fees - rebates`

In practice, on major pairs (BTC/USDT), competitive spreads are 1-3 bps. On altcoins, 10-50+ bps depending on volatility and volume.

### The Avellaneda-Stoikov Model

The foundational model for optimal market making. Key equations:

**Reservation price:**
`r = s - q * gamma * sigma^2 * (T - t)`

Where:
- `s` = mid price
- `q` = current inventory (positive = long, negative = short)
- `gamma` = risk aversion parameter
- `sigma` = volatility
- `T - t` = time horizon

**Optimal spread:**
`delta = gamma * sigma^2 * (T - t) + (2/gamma) * ln(1 + gamma/k)`

Where `k` is the order arrival intensity parameter.

**Practical implementation:**
- Set `gamma` based on your risk tolerance. Higher gamma = wider spreads, less inventory risk.
- Estimate `sigma` using rolling realized volatility (5-minute returns over the last hour).
- Estimate `k` from historical fill rates at various spread levels.
- Update `T - t` continuously. Use a rolling horizon of 1-4 hours.
- Skew quotes: when long inventory, lower ask more than raise bid (incentivize sells).

### Inventory Management

Inventory is the market maker's primary risk. Strategies:

- **Skewing:** Shift quotes away from mid based on inventory. If long 10 BTC, lower ask by 1-2 bps and raise bid by 1-2 bps. Linear skew is simplest; exponential skew (increasing urgency) works better at extreme inventory.
- **Hard limits:** Define max inventory (e.g., 50 BTC equivalent). Pull quotes entirely when limit is reached on one side.
- **Hedging:** When inventory exceeds soft limits, hedge on a correlated market (e.g., hedge altcoin inventory with BTC futures if correlation > 0.7).
- **Passive rebalancing:** Place larger size on the side that reduces inventory. If long, offer 2x size on the ask vs bid.
- **Active rebalancing:** If inventory exceeds threshold and passive skewing is too slow, send aggressive orders (market or limit IOC) to flatten.

### CEX Market Making

**API integration essentials:**
- Use WebSocket for market data (orderbook, trades) and order updates.
- REST API for order placement if WebSocket order entry is not supported.
- Maintain local orderbook from WebSocket deltas. Validate periodically against REST snapshots.
- Handle reconnection gracefully: cancel all open orders on disconnect, re-sync state on reconnect.

**Colocation and latency:**
- Major exchanges (Binance, OKX, Bybit) have servers in AWS Tokyo, Singapore, or custom data centers.
- Colocate in the same region. Expect 1-5ms round-trip to exchange.
- Every millisecond matters for adverse selection. Faster quote updates = less toxic fills.

**Exchange-specific considerations:**
- **Binance:** Maker rebate tiers reward volume. Use self-trade prevention. Check the current venue- and endpoint-specific order-rate limits; they can change and vary by account tier.
- **Bybit:** Good API, competitive fee structure. Unified margin account simplifies hedging across spot and perps.
- **OKX:** Supports FIX protocol for lower latency. Maker rebate programs for high-volume MMs.
- **Deribit:** Primary options venue. Market makers get preferential fees and priority fills.

### DEX Market Making

**Concentrated Liquidity (Uniswap V3, etc.):**
- Provide liquidity in tight ranges around current price for capital efficiency.
- Narrower range = higher fee income per dollar deployed but more impermanent loss and more frequent rebalancing.
- Optimal range width: `price * (1 +/- 2 * daily_vol)`. For BTC with 3% daily vol, that is roughly +/- 6% around current price.
- Rebalance when price exits your range. Automate this with on-chain keepers or off-chain bots.
- Account for gas costs in rebalancing frequency calculation.

**JIT (Just-In-Time) Liquidity:**
- Monitor the mempool for large swaps.
- Add concentrated liquidity in the tick range of the incoming swap.
- Capture fees from the swap, then immediately remove liquidity.
- Requires mempool access (MEV infrastructure) and fast transaction submission.
- Competitive: you are racing other JIT providers and sandwich bots.

**Fee Tier Selection:**
- 0.01% (1 bps): Only for stablecoin pairs (USDC/USDT). Minimal impermanent loss.
- 0.05% (5 bps): Major pairs (ETH/USDC). High volume compensates for tight spread.
- 0.30% (30 bps): Mid-cap tokens. Balance between volume and spread income.
- 1.00% (100 bps): Long-tail, volatile tokens. Wide spread protects against IL.

### Hedging Strategies

- **Delta hedging:** Hedge inventory risk by taking opposite positions in perpetual futures. If your spot market making has you long 10 ETH, short 10 ETH in perps. Cost: funding rate.
- **Cross-asset hedging:** Hedge altcoin exposure with BTC or ETH futures using beta-adjusted ratios. `hedge_size = position_size * beta_to_BTC`.
- **Options hedging:** Buy puts to protect against sharp downside during market making. Cost is the premium, but it caps tail risk. Worthwhile for large inventories.
- **Correlation-based portfolio hedging:** If making markets in multiple correlated tokens, hedge the net portfolio delta rather than each position individually. More capital efficient.

### PnL Attribution

Break down market making PnL into components:

1. **Spread capture:** Sum of (fill_price - mid_at_fill) for all fills. This should be positive.
2. **Inventory PnL:** Mark-to-market change in inventory value. This is the volatile component.
3. **Rebate income:** Exchange maker rebates earned.
4. **Hedging cost:** PnL from hedge positions, including funding rates.
5. **Total PnL:** Sum of all components.

Track daily. If spread capture is consistently positive but inventory PnL is negative and growing, your adverse selection is too high. Widen spreads or improve signal-based skewing.

## Advanced Patterns

### Signal-Enhanced Market Making

Pure market making ignores information. Signal-enhanced MM uses short-term predictions to improve quoting:

- **Orderbook imbalance signal:** If bid volume >> ask volume in top 5 levels, skew quotes upward (wider bid, tighter ask). Captures mean reversion toward the heavy side.
- **Trade flow toxicity (VPIN):** Calculate Volume-Synchronized Probability of Informed Trading. When VPIN is high, widen spreads or pull quotes entirely.
- **Cross-exchange lead:** Some exchanges lead price discovery (often Binance for major pairs). If Binance mid moves before your venue, adjust quotes pre-emptively.
- **Funding rate signal:** When funding is extremely positive, shorts are expensive and longs are crowded. Skew quotes bearishly.

### Multi-Venue Market Making

Make markets on 3-5 exchanges simultaneously:

- Centralize risk management: track aggregate inventory across all venues.
- Route hedging to the cheapest venue.
- Use one venue's orderbook as a signal for quoting on another.
- Rebalance across venues using internal transfers to avoid building up single-venue inventory.

### Options Market Making

Unique challenges:
- Quote multiple strikes and expiries simultaneously. Manage portfolio Greeks, not individual positions.
- Delta-hedge frequently (every 1-5 minutes for near-term options).
- Model vol surface: Use SVI (Stochastic Volatility Inspired) parameterization for smooth interpolation.
- Vega risk is the primary concern. Hedge by trading options at different strikes/expiries or by adjusting quotes to reduce net vega.

## Anti-Patterns

*   **No Inventory Limits.** Operating a market maker without position caps allows unconstrained accumulation during trending markets, resulting in massive directional losses that exceed all accumulated spread profits.

*   **Ignoring Adverse Selection Metrics.** Failing to track the percentage of fills that are immediately losing (fill price worse than mid within 1 second) means your spreads are too tight or your quoting is too slow without your knowledge.

*   **Static Spread Width.** Using fixed bid-ask spreads regardless of volatility regime charges too much during calm markets (losing volume to competitors) and too little during volatile markets (getting adversely selected).

*   **Single-Asset Market Making Without Portfolio Risk.** Quoting individual assets without managing aggregate portfolio Greeks means correlated moves across your quoted assets compound losses multiplicatively.

*   **No Kill Switch.** Operating without an automated kill switch that cancels all open orders when losses exceed a threshold allows a single adverse event to wipe out weeks or months of accumulated profits.

## What NOT To Do

- **Do not make markets without inventory limits.** An unconstrained market maker in a trending market will accumulate a massive losing position.
- **Do not ignore adverse selection.** If a significant fraction of your fills are immediately losing money (fill price worse than mid 1 second later), your spreads are too tight or your quoting is too slow.
- **Do not provide liquidity in illiquid altcoins without understanding the risks.** One whale dump can wipe out months of spread income.
- **Do not run DEX liquidity positions without monitoring.** Impermanent loss in concentrated positions can be severe during volatility spikes.
- **Do not treat maker rebates as guaranteed profit.** Rebates incentivize volume, but toxic flow costs more than rebates earn.
- **Do not use static spreads.** Volatility changes constantly. A spread that is profitable at 2% daily vol is suicidal at 10% daily vol.
- **Do not market make on exchanges with unreliable infrastructure.** If the exchange goes down and you cannot cancel orders, you will get picked off on stale quotes.
- **Do not overlook the carry cost of hedging.** Funding rates on perpetual futures can be 0.1-0.3% per day in extreme markets. This erodes hedge effectiveness.
