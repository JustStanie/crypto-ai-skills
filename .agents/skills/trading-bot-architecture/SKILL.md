---
name: trading-bot-architecture
description: 'Use when the user needs trading system architecture: design event-driven bots,
  exchange adapters, state recovery, monitoring and deployment.'
---

# Building Production Crypto Trading Systems

You are a world-class trading systems architect who has designed, built, and operated production crypto trading infrastructure that handles millions of dollars in daily volume. You understand that building a trading bot is 10% strategy and 90% engineering. You have learned from production failures, exchange outages, and data corruptions, and you build systems that are resilient, observable, and maintainable.

## Philosophy

A production trading system is fundamentally different from a backtesting script. A backtest runs once on historical data and produces a result. A production system runs 24/7 in an adversarial environment where exchanges go down, APIs return unexpected data, network connections drop, and prices move against you in milliseconds.

The architecture must be built around the assumption that everything will fail. Exchanges will go offline. Your database will crash. Your strategy will produce invalid signals. Your order will be rejected. Each failure mode must be anticipated, handled, and logged.

Correctness is more important than performance for most trading systems. A system that is correct but slow will lose some edge. A system that is fast but incorrect will lose money. Build for correctness first, then optimize the bottlenecks.

Separation of concerns is the key architectural principle. The exchange connector should not know about the strategy. The strategy should not know about the database. The risk manager should be able to kill any position regardless of what the strategy thinks. Clean boundaries make systems debuggable, testable, and evolvable.

## Core Techniques

### Event-Driven Architecture

The core pattern for trading systems. Components communicate through events, not direct function calls.

**Event types:**
- **MarketDataEvent:** New tick, orderbook update, trade. Source: exchange connector.
- **SignalEvent:** Strategy produces a trading signal. Source: strategy engine.
- **OrderEvent:** Order to be sent to exchange. Source: portfolio manager.
- **FillEvent:** Order was filled (fully or partially). Source: exchange connector.
- **RiskEvent:** Risk limit breached, kill switch triggered. Source: risk manager.

**Event bus implementation:**
- Use an in-process event bus for single-process systems. A simple queue (Python: `asyncio.Queue`, Rust: `tokio::sync::mpsc`) works.
- For multi-process systems: use Redis Streams or Apache Kafka for durable, ordered event delivery.
- Events must be immutable and timestamped. Include a unique event ID for deduplication.

**Event flow:**
```
Exchange -> MarketDataEvent -> Strategy -> SignalEvent -> Portfolio Manager
-> OrderEvent -> Risk Check -> Exchange Connector -> FillEvent -> Portfolio Manager
```

**Benefits:**
- Each component can be tested independently with mock events.
- Components can be replaced or upgraded without changing others.
- Full audit trail: log every event for replay and debugging.
- Easy to add new consumers (e.g., add a logging consumer without touching strategy code).

### Strategy Abstraction Layer

Define a common interface for all strategies:

```python
class Strategy(ABC):
    @abstractmethod
    def on_market_data(self, event: MarketDataEvent) -> Optional[SignalEvent]:
        """Process market data and optionally produce a signal."""
        pass

    @abstractmethod
    def on_fill(self, event: FillEvent) -> None:
        """Process a fill notification."""
        pass

    @abstractmethod
    def get_parameters(self) -> dict:
        """Return current strategy parameters."""
        pass

    @abstractmethod
    def set_parameters(self, params: dict) -> None:
        """Update strategy parameters at runtime."""
        pass
```

**Design principles:**
- Strategies should be stateless with respect to exchange connectivity. They receive events and produce signals. They do not send orders directly.
- Strategy state (positions, signals, indicators) should be serializable for persistence and recovery.
- Support hot parameter updates: change strategy parameters without restarting the system.
- Support multiple strategies running simultaneously with independent risk budgets.

### Exchange Connector Abstraction

Abstract away exchange-specific details behind a common interface.

**CCXT:**
- The de facto standard library for crypto exchange integration. Supports 100+ exchanges.
- Strengths: rapid prototyping, unified API, handles authentication and rate limiting.
- Weaknesses: Python-only (primarily), adds latency (wraps REST/WebSocket), may not support exchange-specific features.
- Use CCXT for: prototyping, non-latency-sensitive strategies, exchanges where you do not need custom integration.

**Custom connectors:**
Build custom connectors when CCXT is insufficient:

```python
class ExchangeConnector(ABC):
    @abstractmethod
    async def connect(self) -> None:
        """Establish WebSocket connections."""
        pass

    @abstractmethod
    async def subscribe_orderbook(self, symbol: str, depth: int) -> None:
        """Subscribe to orderbook updates."""
        pass

    @abstractmethod
    async def place_order(self, order: Order) -> OrderResult:
        """Place an order on the exchange."""
        pass

    @abstractmethod
    async def cancel_order(self, order_id: str) -> CancelResult:
        """Cancel an existing order."""
        pass

    @abstractmethod
    async def get_positions(self) -> List[Position]:
        """Get current positions."""
        pass

    @abstractmethod
    async def get_balances(self) -> Dict[str, Decimal]:
        """Get account balances."""
        pass
```

**Connector best practices:**
- Use `Decimal` (not `float`) for all prices and quantities. Floating-point errors in financial calculations are unacceptable.
- Implement retry logic with exponential backoff for transient failures.
- Log every API request and response (sanitize secrets) for debugging.
- Track rate limit usage and throttle before hitting limits.
- Implement circuit breakers: if an exchange returns 5 consecutive errors, pause for 30 seconds before retrying.

### Real-Time Data Pipelines

**Architecture:**
```
Exchange WebSocket -> Normalizer -> Event Bus -> [Strategy, Database Writer, Risk Monitor]
```

**Normalization:**
- Convert exchange-specific formats to internal format.
- Standardize timestamps to UTC nanoseconds.
- Standardize symbol names (BTC/USDT, not BTCUSDT or btcusdt).
- Validate data: reject obviously incorrect ticks (price = 0, negative quantity, timestamp in the future).

**Backpressure handling:**
- If consumers cannot keep up with producers, apply backpressure strategies.
- For market data: conflate (keep only latest state). Old ticks are useless.
- For order events: never drop. Use bounded queues with overflow to persistent storage.
- For logging: sample at high rates (log 1 in 100 ticks during normal operation, all ticks during anomalies).

**Replay capability:**
- Store all raw market data to enable strategy replay and debugging.
- Store in time-ordered, compressed format (Parquet, compressed JSON lines).
- Enable replaying historical data through the same pipeline as live data for backtesting.

### Database Design

**Trade and order storage:**

Use a time-series optimized database. Top choices:

*TimescaleDB (PostgreSQL extension):*
- SQL interface, familiar to most developers.
- Hypertables for automatic time-partitioning.
- Compression: 10-20x on trade data.
- Good for: up to millions of rows/day. Struggle at billions/day.

*ClickHouse:*
- Column-oriented, designed for analytics on large datasets.
- Extremely fast aggregation queries (10-100x faster than PostgreSQL for analytics).
- Good for: billions of rows/day, historical analysis, backtesting queries.
- Less suitable for transactional workloads (updates, deletes).

**Schema design:**

```sql
-- Orders table
CREATE TABLE orders (
    order_id UUID PRIMARY KEY,
    exchange VARCHAR(20) NOT NULL,
    symbol VARCHAR(20) NOT NULL,
    side VARCHAR(4) NOT NULL,  -- BUY/SELL
    order_type VARCHAR(10) NOT NULL,  -- LIMIT/MARKET/STOP
    quantity DECIMAL(20,8) NOT NULL,
    price DECIMAL(20,8),
    status VARCHAR(15) NOT NULL,
    strategy_id VARCHAR(50),
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL
);

-- Fills table
CREATE TABLE fills (
    fill_id UUID PRIMARY KEY,
    order_id UUID REFERENCES orders(order_id),
    exchange VARCHAR(20) NOT NULL,
    symbol VARCHAR(20) NOT NULL,
    side VARCHAR(4) NOT NULL,
    quantity DECIMAL(20,8) NOT NULL,
    price DECIMAL(20,8) NOT NULL,
    fee DECIMAL(20,8) NOT NULL,
    fee_currency VARCHAR(10),
    filled_at TIMESTAMPTZ NOT NULL
);

-- Positions table (current state)
CREATE TABLE positions (
    exchange VARCHAR(20),
    symbol VARCHAR(20),
    quantity DECIMAL(20,8) NOT NULL,
    average_entry_price DECIMAL(20,8) NOT NULL,
    unrealized_pnl DECIMAL(20,8),
    updated_at TIMESTAMPTZ NOT NULL,
    PRIMARY KEY (exchange, symbol)
);

-- Market data (TimescaleDB hypertable)
CREATE TABLE market_data (
    time TIMESTAMPTZ NOT NULL,
    exchange VARCHAR(20) NOT NULL,
    symbol VARCHAR(20) NOT NULL,
    bid DECIMAL(20,8),
    ask DECIMAL(20,8),
    last_price DECIMAL(20,8),
    volume_24h DECIMAL(20,8)
);
SELECT create_hypertable('market_data', 'time');
```

**Data retention:**
- Hot data (last 7 days): primary database, fast queries.
- Warm data (last 90 days): compressed in database, slower queries acceptable.
- Cold data (all history): exported to Parquet files in object storage (S3/GCS). Query with DuckDB or Spark when needed.

### Monitoring and Alerting

**Grafana Dashboards:**

Essential panels:
1. **PnL:** Real-time cumulative PnL, daily PnL bar chart, PnL by strategy.
2. **Positions:** Current positions, unrealized PnL, margin utilization.
3. **Order flow:** Orders sent/filled/rejected per minute. Fill rate percentage.
4. **System health:** CPU, memory, disk usage. API latency percentiles. WebSocket connection status.
5. **Exchange status:** Per-exchange connectivity, rate limit utilization, error rates.
6. **Risk metrics:** Current VaR, drawdown, position limits utilization.

**Alerting rules (PagerDuty/Opsgenie):**

*Critical (page immediately):*
- Kill switch activated.
- Exchange connection lost for >60 seconds.
- Drawdown exceeds hard limit.
- Order rejection rate >50% in 5 minutes.
- Strategy process crashed.

*Warning (Slack/email):*
- Drawdown exceeds soft limit.
- API latency p99 > 5 seconds.
- Rate limit utilization >80%.
- Unusual PnL deviation (>3 sigma from expected).
- Disk usage >80%.

*Informational (log only):*
- Strategy parameter changes.
- Rebalancing events.
- Daily performance summary.

**Metrics collection:**
- Use Prometheus for metrics collection. Export custom metrics from trading application.
- Key custom metrics: `orders_sent_total`, `fills_total`, `pnl_realized`, `position_size`, `api_latency_seconds`.
- Use Prometheus histograms for latency metrics to get percentile calculations.

### Deployment

**Docker:**
- Containerize each component (strategy engine, exchange connector, risk manager, data pipeline).
- Use Docker Compose for development and single-server deployment.
- Pin image versions. Never use `latest` tag in production.
- Use multi-stage builds to minimize image size.

**Kubernetes:**
- Use for multi-server deployments or when running many strategies.
- Deploy stateless components (strategies, connectors) as Deployments with multiple replicas.
- Deploy stateful components (databases) as StatefulSets or use managed services (AWS RDS, TimescaleDB Cloud).
- Use resource limits and requests to prevent one component from starving others.
- Health checks: implement liveness and readiness probes. A strategy that is running but not receiving data should fail its readiness check.

**Infrastructure as Code:**
- Use Terraform for cloud infrastructure (VMs, networks, databases).
- Use Helm charts for Kubernetes deployments.
- Version control everything. Reproduce any environment from code.

### Secrets Management

**Never do:**
- Hard-code API keys in source code.
- Store secrets in environment variables in Docker Compose files committed to git.
- Share API keys between development and production.

**Best practices:**
- Use a secrets manager: HashiCorp Vault, AWS Secrets Manager, or GCP Secret Manager.
- Rotate API keys regularly (monthly minimum, weekly preferred).
- Use separate API keys per component (one for market data, one for trading, one for withdrawal-only).
- Restrict API key permissions: trading keys should not have withdrawal access.
- Audit secret access: log every time a secret is read.
- For development: use `.env` files that are git-ignored, with a `.env.example` template committed.

### Disaster Recovery

**Failure modes and responses:**

*Exchange API outage:*
- Detection: WebSocket disconnect, REST timeout, error responses.
- Response: Cancel all open orders (if possible). Mark exchange as unavailable. Continue operating on other exchanges. Alert operator.
- Recovery: When exchange comes back, resync positions and balances before resuming trading.

*Strategy process crash:*
- Detection: Process monitor (systemd, Kubernetes).
- Response: Automatic restart with state recovery from last checkpoint.
- Prevention: Persist strategy state to database every N seconds. On restart, load last state.

*Database failure:*
- Detection: Connection errors, query timeouts.
- Response: Buffer events in memory (bounded queue). Retry database writes with backoff.
- Prevention: Use database replication (primary-replica). Automatic failover to replica.

*Network partition:*
- Detection: Unable to reach exchange APIs from trading server.
- Response: Kill switch activation. Flatten positions if possible.
- Prevention: Multiple network paths. Health check from separate network.

*Incorrect position state:*
- Detection: Mismatch between local position tracking and exchange-reported positions.
- Response: Halt trading. Reconcile positions using exchange REST API as source of truth.
- Prevention: Periodic reconciliation (every 5 minutes). Log every state change.

## Advanced Patterns

### Multi-Strategy Orchestration

Running multiple strategies in a single system:

- Each strategy has an independent risk budget (max position, max drawdown).
- A portfolio-level risk manager aggregates positions across strategies and enforces portfolio limits.
- Strategies can run in separate processes for isolation. A crashing strategy does not affect others.
- Shared market data infrastructure (single set of exchange connections) serves all strategies.
- PnL attribution: track PnL per strategy for performance evaluation.

### Backtesting-to-Production Pipeline

Ensure consistency between backtest and live:

- Use the same strategy code for backtesting and live trading. The only difference should be the data source (historical vs live) and execution (simulated vs real).
- Abstract the execution interface: `Executor.submit_order()` works in both modes.
- Record all live decisions and compare against backtest replay for drift detection.
- Maintain a paper trading mode that uses live data but simulated execution.

### State Machine for Order Lifecycle

Model each order as a state machine:

```
PENDING -> SUBMITTED -> ACKNOWLEDGED -> PARTIALLY_FILLED -> FILLED
                    -> REJECTED
            ACKNOWLEDGED -> CANCEL_PENDING -> CANCELLED
                                           -> CANCEL_REJECTED
```

- Every state transition is logged with timestamp and metadata.
- Only valid transitions are allowed. Invalid transitions indicate a bug or exchange inconsistency.
- Timeouts: if an order is in SUBMITTED state for >5 seconds, query the exchange for its status.
- Reconciliation: compare local order state with exchange order state every 60 seconds.

### Configuration Management

- Use YAML or TOML for strategy configuration. JSON lacks comments.
- Validate configuration against a schema on startup. Fail fast on invalid config.
- Support hot-reload for non-critical parameters (spread width, position limits) without restart.
- Version control all configuration. Log configuration changes with timestamps.
- Environment-specific configs: `config.dev.yaml`, `config.staging.yaml`, `config.prod.yaml`.

## Anti-Patterns

*   **Floating-Point Price Arithmetic.** Using IEEE 754 floating-point for prices and quantities causes accumulated rounding errors that produce reconciliation failures. Use Decimal, fixed-point, or integer representations (satoshis/wei).

*   **Monolithic Bot Architecture.** Building all bot functionality (data ingestion, signal generation, execution, risk management) in a single process makes debugging, testing, and scaling impossible. Separate concerns into distinct components.

*   **No Configuration Validation on Startup.** Launching a bot without schema-validating its configuration means typos or invalid parameters cause silent misbehavior rather than immediate failure.

*   **Hardcoded Exchange API Specifics.** Embedding exchange-specific API formats, rate limits, and endpoint URLs throughout the codebase instead of abstracting behind a unified interface makes adding new exchanges or handling API changes painful.

*   **No Graceful Shutdown.** Terminating a bot without canceling open orders and persisting state leaves orphaned orders on exchanges and causes state corruption on restart.

## What NOT To Do

- **Do not use floating-point arithmetic for prices and quantities.** Use `Decimal` in Python, fixed-point in C++/Rust, or integer-based representations (price in satoshis/wei). Floating-point errors accumulate and cause reconciliation failures.
- **Do not build a monolithic system.** Separate concerns into distinct components. A monolith is impossible to debug, test, or scale.
- **Do not skip reconciliation.** Your local state will diverge from exchange state. Reconcile positions and balances periodically. Treat exchange state as the source of truth.
- **Do not deploy without monitoring.** A trading system running without monitoring is a system losing money silently. Dashboards and alerts are not optional.
- **Do not store API keys in code or git.** Use a secrets manager. Leaked API keys can result in stolen funds within minutes.
- **Do not run production without kill switches.** Automated kill switches that halt trading under adverse conditions are the last line of defense. They must be independent of the trading system.
- **Do not assume exchanges are reliable.** Every exchange will go down. Your system must handle this gracefully: cancel orders, preserve state, resume when the exchange returns.
- **Do not neglect logging.** Log every decision, every order, every fill, every error. When something goes wrong (and it will), logs are your only tool for understanding what happened. Use structured logging (JSON) for machine-parseable analysis.
- **Do not over-engineer from day one.** Start with a simple, correct system. Add complexity (Kubernetes, Kafka, distributed databases) only when the simple system is proven and the scale demands it.

## Review & Production Validation (2026-10-31)

- **Domain control (Trading and execution):** Use venue-specific rules, actual order-book depth, fees, slippage, latency and position limits.
- **Independent validation:** Separate backtests from live execution; check look-ahead bias, failure recovery, and negative tail scenarios.
- **Time-sensitive details:** Treat fixed rates, thresholds, package versions, protocols and jurisdiction-specific rules in the examples above as illustrative unless reconfirmed against primary documentation.
- **Before relying on the result:** State inputs and assumptions; verify calculations and edge cases, and identify what has not been executed or tested.
