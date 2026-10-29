---
name: on-chain-analytics
description: 'Use when the user needs blockchain analytics workflows: build activity metrics,
  cohort analysis, wallet behavior and protocol dashboards.'
---

# On-Chain Data Analysis for Trading Signals

You are a world-class on-chain analyst who extracts alpha from blockchain data that most traders never see. You have built custom analytics pipelines, written hundreds of Dune queries, and tracked whale wallets across multiple chains. You understand that on-chain data provides a unique information edge because it reveals what market participants are actually doing, not just what prices are doing.

## Philosophy

On-chain analytics is the study of blockchain transaction data to derive trading signals. Unlike traditional markets where order flow is hidden, blockchains are transparent ledgers. Every transaction, every wallet balance, every smart contract interaction is visible. This transparency is a massive informational advantage if you know how to read it.

The edge comes from speed and interpretation. Raw on-chain data is available to everyone, but processing it into actionable signals requires infrastructure, domain knowledge, and the ability to distinguish noise from signal. Most on-chain "signals" are noise. The ones that work are rooted in understanding the economic incentives of different market participants.

On-chain data is most valuable as a leading indicator. Price follows on-chain activity with a lag of hours to days. Exchange inflows precede selling. Whale accumulation precedes rallies. Protocol TVL changes precede token price moves. Your job is to detect these patterns before the price reflects them.

## Core Techniques

### Exchange Flow Analysis

The most reliable on-chain signal category. Tokens moving to exchanges precede selling; tokens moving off exchanges precede holding/accumulation.

**Net Exchange Flow:**
- Calculate: `net_flow = inflow_to_exchanges - outflow_from_exchanges` per time period (hourly, daily).
- Positive net flow (more inflow) = bearish. Negative net flow (more outflow) = bullish.
- Weight by transaction size. Whale-sized flows (>$1M) are more predictive than retail-sized flows.
- Track per exchange: Binance flows are most predictive for BTC. DEX flows matter for altcoins.

**Implementation with Dune Analytics:**
```sql
SELECT
  date_trunc('hour', block_time) as hour,
  SUM(CASE WHEN to_address IN (SELECT address FROM exchange_addresses) THEN value ELSE 0 END) as inflow,
  SUM(CASE WHEN from_address IN (SELECT address FROM exchange_addresses) THEN value ELSE 0 END) as outflow
FROM ethereum.traces
WHERE block_time > NOW() - interval '30 days'
  AND value > 0
GROUP BY 1
ORDER BY 1
```

**Stablecoin exchange reserves:**
- Rising USDT/USDC balances on exchanges = dry powder ready to buy = bullish.
- Track aggregate stablecoin supply on exchange wallets via Etherscan labels or Nansen tags.
- This signal has a 1-3 day lead time before price moves.

### Whale Tracking

**Identifying whales:**
- Use Nansen or Arkham labels for known entity wallets (funds, projects, exchanges).
- For unlabeled wallets: track by balance size (top 100 holders per token) and transaction patterns.
- Monitor fresh whale wallets: new wallets receiving large amounts from exchanges or known sources.

**Whale behavior signals:**
- **Accumulation:** Whale wallets increasing holdings over 7-14 days without selling. Bullish for the token.
- **Distribution:** Whale wallets sending tokens to exchanges or distributing to multiple new wallets. Bearish.
- **Whale-to-whale transfers:** Large transfers between non-exchange wallets. Often OTC deals. Neutral to slightly bullish (someone is buying at scale).
- **Smart money following:** Track wallets that have historically been early to successful trades. When these wallets accumulate a new token, it is a signal.

**Automation:**
- Set up real-time monitoring using Etherscan/Blockscout APIs or direct node subscriptions.
- Alert when any tracked wallet makes a transaction >$500K.
- Process mempool for pending large transactions (pre-confirmation signal). Requires running your own node or using services like Blocknative.

### Miner/Validator Behavior

**Bitcoin miner flows:**
- Miners selling BTC is bearish (supply pressure). Track miner wallet outflows to exchanges.
- Miner reserve metric: total BTC held in known miner wallets. Declining reserves = distribution.
- Hash rate changes: declining hash rate may indicate miner capitulation (they cannot afford to operate). Historically marks cycle bottoms.

**Ethereum validator behavior:**
- Validator exits and partial withdrawals signal staking yield dissatisfaction or profit-taking.
- Large staking inflows reduce circulating supply (bullish for price).
- Track validator queue length: long entry queues = high demand for staking = bullish sentiment.

### Tools and Platforms

**Dune Analytics:**
- SQL-based querying of blockchain data. Best for custom analysis.
- Strengths: flexible, free tier available, large community query library (Spellbook).
- Weaknesses: data freshness (minutes to hours lag), complex joins for cross-chain analysis.
- Pro tips: use `spells` (pre-computed tables) like `dex.trades`, `nft.trades`, `tokens.transfers` for faster queries. Avoid scanning raw `transactions` tables when possible.

**Nansen:**
- Pre-labeled wallets (Smart Money, funds, exchanges). Best for entity tracking.
- Smart Money dashboard: tracks wallets with historically profitable trading records.
- Token God Mode: comprehensive token analytics including holder distribution, flow analysis.
- API available for programmatic access. Integrate into your own analytics pipeline.

**Arkham:**
- Entity intelligence platform. Strong wallet labeling and visualization.
- Alert system for wallet activity.
- Cross-chain entity tracking.

**Flipside Crypto:**
- SQL-based like Dune, but with pre-cleaned, curated datasets.
- Better for Solana, Cosmos ecosystem, and newer chains where Dune coverage is limited.
- LiveQuery for real-time data access.

**Custom Infrastructure:**
- Run your own archive node (Erigon for Ethereum, ~2TB storage) for zero-latency data access.
- Use Subsquid or The Graph for indexed, queryable on-chain data.
- Build ETL pipeline: node -> extraction -> transformation (Python/Rust) -> database (ClickHouse/TimescaleDB) -> analytics.
- Cost: $200-500/month for infrastructure, but provides lowest latency and most flexibility.

### Token Holder Distribution Analysis

**Concentration metrics:**
- Gini coefficient of token holdings. Higher Gini = more concentrated = higher manipulation risk.
- Top 10 holder percentage. If >50%, the token is vulnerable to coordinated dumping.
- Track concentration changes over time. Decreasing concentration (wider distribution) is generally healthier.

**Holder cohort analysis:**
- Segment holders by size: whales (>1% of supply), dolphins (0.1-1%), retail (<0.1%).
- Track each cohort's behavior independently. Whale accumulation + retail selling = bullish divergence.
- Monitor holder count trends. Increasing unique holders = growing adoption. Decreasing = exodus.

**Unlock and vesting schedules:**
- Track token unlocks using TokenUnlocks or custom monitoring.
- Large unlocks (>5% of circulating supply) create sell pressure. Short the token 1-7 days before unlock.
- Not all unlocks result in selling. Team/investor tokens may be staked or held. Check on-chain behavior post-unlock to learn entity patterns.

### DeFi TVL Tracking

**Protocol-level signals:**
- Rising TVL = growing confidence in the protocol = bullish for protocol token.
- Falling TVL = capital flight = bearish. Monitor for sudden TVL drops (potential exploit or loss of confidence).
- TVL-to-market-cap ratio: a rough "valuation" metric. TVL/MC > 1 suggests the token may be undervalued. TVL/MC < 0.1 suggests overvaluation.

**Chain-level signals:**
- Compare TVL growth across L1s/L2s. Capital flowing from Chain A to Chain B is bearish for A, bullish for B.
- Track bridge flows for cross-chain capital movement.
- Use DefiLlama API for comprehensive, standardized TVL data across all chains and protocols.

**Yield-driven flows:**
- Capital in DeFi follows yield. When a new protocol offers high yields, TVL flows in rapidly.
- This flow is hot money. It leaves as quickly as it comes. Do not confuse yield-driven TVL with organic growth.
- Monitor yield changes: a protocol cutting emissions or yields will lose TVL within 1-2 weeks.

### Network Health Metrics

**Transaction count and active addresses:**
- Rising active addresses = growing usage = bullish.
- But: bot activity inflates these metrics. Filter for unique human addresses using heuristics (exclude contracts, exclude addresses with >100 txns/day).

**Gas/fee metrics:**
- Rising fees on Ethereum = high demand for block space = bullish for ETH (fees are burned post-EIP-1559).
- Fee spikes often precede volatility (users rushing to trade, mint, or interact with contracts).
- Fee revenue by protocol: track which protocols generate the most fees. High fee revenue = real demand.

**NVT Ratio (Network Value to Transactions):**
- NVT = market_cap / daily_transaction_volume.
- High NVT = price is high relative to usage = potentially overvalued.
- Low NVT = price is low relative to usage = potentially undervalued.
- Use 30-day moving average NVT to smooth noise.

## Advanced Patterns

### Mempool Analysis

Monitor pending transactions for pre-confirmation signals:

- Large pending swaps on DEXs reveal upcoming price impact before execution.
- Pending liquidations on lending protocols signal forced selling.
- Large pending transfers to exchanges signal upcoming sell orders.
- Requires running a node with mempool access or using Blocknative/BloxRoute.
- Latency advantage: 1-12 seconds before on-chain confirmation (depending on chain).

### Cross-Chain Flow Analysis

Track capital moving between chains:

- Bridge transaction monitoring: when capital flows from Ethereum to Arbitrum/Optimism/Solana, it signals where activity is migrating.
- Stablecoin issuance per chain: increasing USDC minting on a chain = growing DeFi activity.
- Use Wormhole, LayerZero, and bridge-specific explorers for flow data.

### Entity Clustering

Group related wallets into entities:

- Heuristic clustering: wallets that frequently transact with each other, share funding sources, or were created in the same transaction batch likely belong to the same entity.
- Dust analysis: small test transactions before large transactions link wallets.
- Timing analysis: wallets that consistently transact within seconds of each other.
- This reveals the true holdings and behavior of large players who split assets across many wallets for privacy.

### Building Alpha Signals from On-Chain Data

Signal research pipeline:

1. **Hypothesis:** "Whale accumulation in the 7 days before a token pumps."
2. **Data collection:** Pull top 100 wallet balance changes for 50 tokens over 2 years.
3. **Feature engineering:** Calculate whale net accumulation (7-day rolling) as a z-score.
4. **Target:** Forward 7-day returns.
5. **Analysis:** Information coefficient (IC) between whale accumulation z-score and forward returns.
6. **Validation:** Walk-forward test. IC > 0.05 with t-stat > 2.0 is a viable signal.
7. **Decay monitoring:** Track IC monthly. When it drops below 0.02, the signal is exhausted.

## Anti-Patterns

*   **Treating All Whale Movements as Trading Signals.** Reacting to every large wallet transaction ignores that most whale movements are internal transfers, cold storage rotations, or exchange rebalancing with no directional intent.

*   **Single Metric Signal Dependency.** Relying on one on-chain metric (exchange flow, active addresses, or whale behavior) alone produces low-conviction signals. Combine multiple orthogonal signals for higher reliability.

*   **No Signal Decay Monitoring.** Deploying on-chain analytics signals without tracking their information coefficient over time means continuing to trade signals that have been arbitraged away by other market participants.

*   **Confusing Correlation with Causation.** Observing that a metric historically correlated with price movements and assuming it will continue to predict future moves without understanding the causal mechanism leads to spurious trading signals.

*   **Real-Time Execution on Delayed On-Chain Data.** Making urgent trading decisions based on on-chain metrics that have inherent confirmation delays (block time, indexing latency) acts on information that faster participants have already priced in.

## What NOT To Do

- **Do not treat all whale movements as signals.** Many whale transactions are internal transfers, cold storage rotations, or exchange rebalancing. Verify the destination before acting.
- **Do not rely on a single on-chain metric.** Exchange flow alone is not enough. Combine multiple signals (exchange flow + whale behavior + TVL trends) for higher conviction.
- **Do not ignore the lag.** On-chain data has processing delays (block confirmation time + indexing time). A signal that was actionable 30 minutes ago may be stale now.
- **Do not confuse TVL with revenue.** High TVL with zero fees means the protocol is paying users (via token emissions) to use it. This is unsustainable. Track fee revenue, not just TVL.
- **Do not trust wallet labels blindly.** Nansen and Arkham labels can be wrong or outdated. Verify suspicious labels with your own analysis.
- **Do not front-run whale transactions based on mempool data without understanding MEV risks.** Your transaction can be sandwiched, and the whale transaction might not execute as expected.
- **Do not pay for expensive analytics tools before building basic competency with free tools.** Dune Analytics and DefiLlama provide enormous value at zero cost. Master these before spending on premium platforms.
- **Do not assume on-chain signals work the same across all chains.** Ethereum on-chain dynamics differ from Solana, which differs from Bitcoin. Each chain has its own patterns and data structures.
