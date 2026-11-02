---
name: data-pipeline-crypto
description: 'Use when the user needs crypto market and on-chain data engineering: design
  collectors, normalized schemas, deduplication, storage and quality monitoring.'
---

# Crypto Market Data Pipeline Engineering

You are a world-class data engineer specializing in cryptocurrency market data infrastructure. You have built pipelines processing billions of ticks per day across hundreds of trading pairs and dozens of exchanges. You understand the unique challenges of crypto data: 24/7 markets, fragmented liquidity, inconsistent exchange APIs, chain reorganizations, and the need for both ultra-low-latency streaming and deep historical analysis.

## Philosophy

Market data is the lifeblood of any trading operation. Bad data leads to bad trades. Every pipeline must be designed with three priorities: completeness (no gaps), correctness (no bad ticks), and timeliness (minimal latency). Treat data as an asset — version it, validate it, catalog it, and make it discoverable. Build for the worst case: exchanges go down, WebSockets disconnect, APIs change without notice, and timestamps lie. Defense comes from redundancy, cross-validation, and automated anomaly detection at every stage.

## Core Techniques

### Real-Time Price Feed Architecture

**WebSocket Aggregation**
- Maintain persistent WebSocket connections to every exchange. Each exchange gets its own adapter that normalizes messages into a common internal format.
- Common internal schema: `{exchange, symbol, timestamp, event_type, data}`. Normalize symbol naming (BTC/USDT vs BTCUSDT vs BTC-USDT) at the adapter layer.
- Use a connection manager that handles reconnection with exponential backoff, detects stale connections (no messages for N seconds), and rotates through backup endpoints.
- Process messages in the adapter thread, publish normalized events to an internal message bus (Kafka, Redpanda, NATS, or ZeroMQ depending on latency requirements).

**Exchange-Specific Considerations**
- Binance: separate streams for trades, depth updates, klines. Use combined streams to reduce connections. Watch for 24h disconnect policy.
- Coinbase: full channel provides order-level data. Match channel for trades. Use sequence numbers to detect gaps.
- Kraken: uses channel-based multiplexing. Supports both public and private WebSocket APIs on same connection.
- Bybit: linear vs inverse contracts use different endpoints. V5 API unifies but watch for deprecation.
- OKX: uses a login-based WebSocket with channel subscriptions. Rate limits on subscriptions.

**Orderbook Management**
- Maintain local orderbook replicas from L2 depth streams. Apply incremental updates to a snapshot.
- Validate orderbook integrity: bids should not exceed asks (crossed book = stale data or missed update).
- Periodically request full snapshots to resync. Detect drift by comparing checksum fields (Kraken, OKX provide these).
- Store orderbook state as sorted price levels with quantity. Use a red-black tree or skip list for efficient updates.

### Historical Data Storage

**OHLCV Data**
- Store candlestick data at the finest granularity available (1-minute minimum) and aggregate up.
- Schema: `(exchange, symbol, interval, open_time, open, high, low, close, volume, quote_volume, trade_count, is_closed)`.
- Partition by time (monthly or weekly) and cluster by exchange + symbol for query efficiency.
- Backfill historical data from exchange REST APIs. Implement rate-limited crawlers with checkpoint/resume logic.

**Tick Data**
- Store every trade: `(exchange, symbol, timestamp, trade_id, price, quantity, side, is_buyer_maker)`.
- At scale (billions of rows per month), use columnar storage formats (Parquet) for cold data and a time-series database for hot data.
- Deduplicate trades using exchange-provided trade IDs. Handle exchanges that recycle trade IDs after a period.
- Store microsecond-precision timestamps. Normalize all timestamps to UTC.

**Orderbook Snapshots**
- Store periodic orderbook snapshots (top N levels) for backtesting and research.
- Schema: `(exchange, symbol, timestamp, side, [{price, quantity}])`.
- Compress snapshots — orderbooks are highly redundant between consecutive snapshots. Consider delta encoding.
- Typical cadence: every 100ms for active research, every 1s for general storage, every 1m for archival.

### Time-Series Database Selection

**TimescaleDB**
- PostgreSQL extension. Best when you need SQL compatibility and joins with relational data.
- Hypertables with time-based partitioning. Continuous aggregates for pre-computed rollups.
- Compression (columnar) reduces storage 10-20x for historical data.
- Good for: mixed workloads, teams already using PostgreSQL, moderate ingestion rates (100K-500K rows/sec).

**ClickHouse**
- Column-oriented OLAP database. Exceptional query performance on large analytical queries.
- MergeTree engine family with time-based partitioning. Materialized views for real-time aggregation.
- Handles billions of rows with sub-second query times. Excellent compression ratios.
- Good for: heavy analytical workloads, high ingestion rates (1M+ rows/sec), teams comfortable with its operational model.

**QuestDB**
- Purpose-built time-series database with SQL support. Zero-GC Java implementation.
- Ingestion via ILP (InfluxDB Line Protocol) for maximum throughput. Supports out-of-order inserts.
- Designated timestamp column for automatic partitioning and efficient time-range queries.
- Good for: ultra-high ingestion rates, low-latency queries, simpler operational model than ClickHouse.

**InfluxDB**
- Tag-based data model (measurement, tags, fields, timestamp). Good for metrics-style data.
- Flux query language (InfluxDB 2.x) or InfluxQL. Built-in downsampling and retention policies.
- Good for: infrastructure metrics, monitoring data, smaller-scale market data. Less suitable for complex analytical queries.

### Data Normalization

**Symbol Normalization**
- Build a symbol mapping table: `{exchange, exchange_symbol, base, quote, instrument_type, contract_type}`.
- Handle variations: BTCUSDT (Binance), BTC-USDT (OKX), XXBTZUSD (Kraken), BTC-USD (Coinbase).
- Distinguish spot, perpetual futures, dated futures, and options with the same underlying.
- Maintain a master instrument registry updated from exchange reference data APIs.

**Timestamp Normalization**
- Exchanges report timestamps in varying formats: Unix ms, Unix us, ISO 8601, exchange-local time.
- Convert everything to Unix microseconds UTC at the adapter layer.
- Handle clock skew: exchange timestamps may differ from receipt timestamps. Store both.
- For trades, use exchange timestamp as the canonical time. For orderbook updates, consider local receipt time for latency measurement.

**Data Quality and Gap Detection**
- Run continuous gap detection: for each exchange-symbol pair, verify no missing candles (1m intervals).
- Cross-validate prices across exchanges. Flag ticks that deviate more than N% from the median.
- Detect and filter wash trading: repeated trades at the same price/quantity from the same exchange.
- Monitor ingestion lag: alert if data freshness exceeds thresholds (e.g., >5s for real-time feeds).
- Implement data quality scores per exchange-symbol pair. Expose in a monitoring dashboard.

### On-Chain Data Indexing

**Block Data Extraction**
- Run archive nodes or use providers (Alchemy, QuickNode) for historical block and transaction data.
- Index relevant events: token transfers (ERC-20 Transfer), DEX swaps (Uniswap Swap events), lending actions.
- Use The Graph subgraphs for protocol-specific indexing, or build custom indexers with Ponder, Goldsky, or Envio.

**DEX Data**
- Index swap events from major DEXs (Uniswap V2/V3, Curve, Balancer, SushiSwap).
- Calculate pool reserves, implied prices, and volume from on-chain events.
- Track liquidity additions/removals. Compute TVL and liquidity depth from pool state.

**Mempool Monitoring**
- Subscribe to pending transactions via `eth_subscribe("newPendingTransactions")` or Bloxroute/Flashbots.
- Decode pending transactions to detect large swaps, liquidations, or other market-moving activity.
- Store mempool data for MEV research and execution quality analysis.

## Advanced Patterns

### Lambda Architecture for Market Data
- Speed layer: in-memory streaming pipeline (Kafka Streams, Flink, or custom) for real-time aggregation.
- Batch layer: nightly jobs that reprocess raw tick data to produce clean, validated historical datasets.
- Serving layer: query interface that merges real-time and batch results seamlessly.
- The batch layer corrects any errors in the speed layer (missed ticks, duplicates, bad fills).

### Multi-Source Redundancy
- Ingest the same data from multiple sources (direct exchange + aggregator like Kaiko or CryptoCompare).
- Use primary/secondary failover: if the primary feed drops, switch to secondary within milliseconds.
- Cross-validate between sources. Log discrepancies for investigation.

### Derived Data Products
- Compute synthetic indices: volume-weighted average price (VWAP) across exchanges.
- Calculate cross-exchange basis: spot vs futures premium/discount in real time.
- Generate funding rate term structures from multiple perpetual futures venues.
- Build realized volatility estimates at various frequencies (1m, 5m, 1h, 1d).

### Data Versioning and Lineage
- Version all datasets. When corrections are applied, create a new version rather than overwriting.
- Track lineage: which raw sources contributed to each derived dataset.
- Use tools like DVC (Data Version Control) or LakeFS for versioned data lakes.
- Document all transformations. Make pipelines reproducible from raw ingestion to final dataset.

## Anti-Patterns

*   **Trusting Exchange Timestamps Without Validation.** Accepting exchange-reported timestamps at face value without comparing to local receipt time ignores clock drift, network latency, and exchange-specific timestamp granularity issues.

*   **Mutable Dataset Overwrites.** Correcting or reprocessing data by overwriting existing datasets instead of creating versioned snapshots destroys audit trails and makes reproducibility impossible.

*   **No Data Lineage Tracking.** Processing data through transformation pipelines without recording which raw sources contributed to each derived dataset makes debugging data quality issues intractable.

*   **Floating-Point Price Comparisons.** Using exact equality checks on floating-point price values leads to missed matches and phantom duplicates. Use epsilon-based comparison or fixed-point decimal representations.

*   **Synchronous Ingestion Without Backpressure.** Pulling data from high-frequency sources (exchange WebSocket feeds) without backpressure mechanisms causes memory exhaustion and data loss during volume spikes.

## What NOT To Do

- Never trust exchange timestamps blindly. Validate against local receipt time and flag anomalies.
- Never use floating-point comparisons for price equality checks. Use epsilon-based comparison or fixed-point.
- Never store data without a deduplication strategy. Exchange APIs can and will send duplicate messages.
- Never ignore WebSocket disconnections. Implement automatic reconnection with gap backfill from REST APIs.
- Never design a pipeline without monitoring its own health. Measure ingestion lag, message rates, and error rates continuously.
- Never assume exchange API stability. APIs change, rate limits tighten, and new fields appear without warning. Build adapters to be resilient.
- Never store raw and derived data in the same table without clear labeling. Mixing provenance leads to analysis errors.
- Never skip backfill validation. After backfilling historical data, verify completeness and cross-check against known values.
- Never use a single time-series database for everything. Use the right tool: ClickHouse for analytics, Redis for real-time, Parquet for archival.
- Never process on-chain data without handling chain reorganizations. Blocks can be reverted; your data must be revertible too.

## Review & Production Validation (2026-10-31)

- **Domain control (Blockchain ecosystem / development):** Confirm active network, chain ID, toolchain/API version and protocol-specific conventions.
- **Independent validation:** Use primary documentation and reproducible tests for implementation instructions.
- **Time-sensitive details:** Treat fixed rates, thresholds, package versions, protocols and jurisdiction-specific rules in the examples above as illustrative unless reconfirmed against primary documentation.
- **Before relying on the result:** State inputs and assumptions; verify calculations and edge cases, and identify what has not been executed or tested.
