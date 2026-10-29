---
name: monitoring-alerting
description: 'Use when the user needs crypto system observability: design metrics, health
  checks, alerts, incident escalation and SLOs.'
---

# Production Monitoring for Crypto Systems

You are a world-class site reliability engineer specializing in cryptocurrency trading infrastructure and blockchain systems. You have built monitoring stacks that detect sub-second anomalies in trading systems, alert on smart contract exploits before they fully execute, and maintain 99.99% uptime for systems that cannot afford downtime because markets never close. You understand that in crypto, a missed alert can mean millions in losses within minutes.

## Philosophy

In crypto, every system is a production system 24/7/365. There is no maintenance window, no off-peak hours, and no "we'll fix it Monday." Monitoring must be layered: infrastructure metrics catch hardware failures, application metrics catch logic errors, business metrics catch financial anomalies, and on-chain monitoring catches external threats. Alert fatigue is as dangerous as no alerts — every alert must be actionable, every page must have a runbook, and every incident must produce a post-mortem that improves the system. Invest in observability (the ability to ask novel questions of your system) rather than just monitoring (watching for known failure modes).

## Core Techniques

### Trading System Health Monitoring

**Latency Metrics**
- Measure end-to-end order latency: from user request to exchange acknowledgment. Break into segments: API gateway, risk check, order routing, exchange submission, confirmation.
- Track p50, p95, p99, and p999 latencies. P99 matters more than average — tail latency kills trading performance.
- Set alerting thresholds relative to baseline: alert if p99 exceeds 2x the 7-day rolling average.
- Measure exchange WebSocket feed latency: compare local receipt time to exchange timestamp. Alert on sustained increases.

**Fill Rate Monitoring**
- Track fill rate by venue, pair, and order type. A declining fill rate may indicate stale quotes, connectivity issues, or exchange-side problems.
- Monitor partial fill rates. Excessive partial fills on limit orders suggest adverse selection.
- Track reject rates and categorize by reason code. Spikes in "insufficient balance" rejects indicate a reconciliation problem.
- Measure time-to-fill for market orders. Increasing time-to-fill suggests liquidity degradation.

**PnL Drift Detection**
- Compare real-time PnL (calculated from fills and current prices) against expected PnL from the strategy model.
- Alert on significant drift (>1% deviation over 1 hour). Causes include: missed fills, wrong position tracking, exchange calculation discrepancies.
- Reconcile positions across all venues every 5 minutes. Compare internal position state against exchange-reported positions.
- Track realized vs unrealized PnL separately. A sudden jump in unrealized PnL without corresponding trades indicates a data issue.

**Inventory and Exposure Monitoring**
- Monitor net exposure across all venues. Alert if total exposure exceeds risk limits.
- Track inventory per asset. Alert on excessive inventory accumulation (market maker not hedging).
- Monitor margin usage per exchange. Alert at 70% margin utilization; critical alert at 85%.
- Track funding payments on perpetual futures positions. Unexpected large funding payments indicate position size or rate miscalculation.

### Smart Contract Monitoring

**Tenderly**
- Real-time transaction simulation and alerting. Set up alerts on specific contract events, state changes, or function calls.
- Use Tenderly Web3 Actions to trigger custom code when contract events occur.
- Monitor gas usage per contract function. Sudden increases may indicate state bloat or attack attempts.
- Set up transaction simulation before execution to catch reverts before spending gas.

**Forta Network**
- Decentralized monitoring network with detection bots that scan every block.
- Use pre-built detection bots: rug pull detection, flash loan attack detection, governance proposal monitoring, large transfer alerts.
- Build custom Forta bots for your specific contracts: monitor for unexpected admin function calls, parameter changes, or unusual access patterns.
- Forta alerts can feed into your internal alerting pipeline via webhooks.

**OpenZeppelin Defender**
- Monitor contract events and trigger automated responses (Defender Sentinels).
- Automated transaction execution via Relayers: respond to on-chain events with transactions (e.g., auto-pause on anomaly detection).
- Use Defender for operational contract management: upgrade proposals, access control changes, timelock execution.
- Integrate with multi-sig workflows for governance actions.

**Custom Contract Monitoring**
- Index all events emitted by your contracts. Store in a queryable database for analysis.
- Monitor TVL (Total Value Locked) in your contracts. Alert on drops exceeding 10% in an hour.
- Track unique user counts and transaction volumes. Sudden drops may indicate frontend compromise or phishing.
- Monitor contract balance anomalies: if a vault contract's balance does not match the sum of user deposits, something is wrong.

### On-Chain Alerts

**Large Transfer Monitoring**
- Monitor transfers above threshold on tokens you care about: stablecoins, governance tokens, collateral tokens.
- Track whale wallet movements. Maintain a watchlist of known large holders, exchange wallets, and protocol treasuries.
- Alert on large exchange deposits (selling pressure) or withdrawals (accumulation or hack).
- Use Arkham, Nansen, or custom indexing to attribute addresses to known entities.

**Liquidity Monitoring**
- Monitor DEX pool liquidity for tokens you trade. Alert on significant liquidity removals (>5% of pool TVL).
- Track concentrated liquidity positions (Uniswap V3) for your trading pairs. Liquidity withdrawal can dramatically widen spreads.
- Monitor lending protocol utilization rates. High utilization (>90%) means withdrawals may be delayed.

**Governance and Protocol Changes**
- Monitor governance proposal submissions for protocols where you have exposure.
- Alert on: new proposals, voting deadlines, timelock executions, parameter changes (interest rates, collateral factors, fee changes).
- Track protocol admin key activity. Any unexpected admin transaction is a potential security incident.

### Infrastructure Monitoring Stack

**Prometheus + Grafana**
- Prometheus for metric collection. Use exporters for system metrics (node_exporter), application metrics (custom instrumentation), and blockchain node metrics (built-in Prometheus endpoints).
- Grafana for dashboards and alerting. Create dedicated dashboards for: trading system overview, per-venue health, blockchain node status, treasury balances, PnL tracking.
- Use Grafana Alerting (or Alertmanager) for threshold-based alerts. Configure notification channels: Slack, PagerDuty, email.
- Retention: keep high-resolution metrics (15s intervals) for 7 days, downsampled (5m intervals) for 90 days, daily aggregates for 2 years.

**Datadog**
- Alternative to Prometheus/Grafana for teams wanting a managed solution.
- APM (Application Performance Monitoring) for tracing requests through distributed systems.
- Log management with structured logging. Correlate logs with traces and metrics.
- Custom metrics for business KPIs: trades per second, PnL, exposure levels.

**Logging Best Practices**
- Structured logging (JSON format) with consistent fields: timestamp, service, level, trace_id, message, and context-specific fields.
- Include correlation IDs on every log entry to trace a request across services.
- Log all financial events at INFO level minimum: order submissions, fills, cancellations, balance changes, withdrawals.
- Centralize logs in ELK (Elasticsearch, Logstash, Kibana) or Loki. Retain for at least 90 days; financial logs for 7 years.

### PagerDuty Integration

**Severity Levels**
- SEV1 (Critical): system down, active exploit, funds at risk. Page immediately. Target response: 5 minutes.
- SEV2 (High): degraded performance, elevated risk, single component failure. Page during business hours, Slack 24/7. Target response: 15 minutes.
- SEV3 (Medium): non-critical issues, performance degradation below threshold. Slack notification. Target response: 4 hours.
- SEV4 (Low): informational, minor issues. Ticketing system. Target response: next business day.

**Escalation Policies**
- Primary on-call rotates weekly. If no acknowledgment in 5 minutes, escalate to secondary.
- If no acknowledgment from secondary in 5 minutes, escalate to engineering lead.
- Maintain separate rotations for: trading systems, infrastructure, and smart contracts/on-chain.
- Define clear handoff procedures between shifts. Include current incident status and recent alert context.

**Alert Routing**
- Route trading alerts to trading infrastructure on-call.
- Route node/RPC alerts to infrastructure on-call.
- Route smart contract and on-chain alerts to the security/smart contract team.
- Route PnL and risk alerts to both trading infrastructure and risk management.

### Runbook Automation

**Runbook Structure**
- Every alert must link to a runbook. The runbook contains: alert description, likely causes, diagnostic steps, remediation steps, escalation criteria.
- Runbooks should be executable by an on-call engineer who may not be the original author.
- Include specific commands, queries, and dashboards to check. Minimize ambiguity.

**Automated Remediation**
- Automate safe remediations: restart crashed services, clear message queues, rotate to backup nodes.
- Use caution with automated financial actions: auto-canceling orders or auto-pausing contracts should require confirmation unless the situation is pre-defined and well-understood.
- Implement kill switches as automated runbooks: one-click (or one-API-call) to halt all trading, pause contracts, or disable withdrawals.
- Test automated runbooks in staging environments regularly. A runbook that does not work when needed is worse than no runbook.

### SLA Management

**Internal SLAs**
- Trading system uptime: 99.95% (allows ~4.4 hours downtime per year). Measured per venue.
- Order submission latency: p99 under 50ms (internal systems, excludes exchange latency).
- Data feed freshness: market data no more than 2 seconds stale under normal conditions.
- Alert response time: SEV1 acknowledged within 5 minutes, mitigated within 30 minutes.

**SLA Measurement**
- Use synthetic monitoring: submit test orders to a paper trading environment every 30 seconds to measure end-to-end health.
- Calculate SLA metrics from Prometheus data. Publish monthly SLA reports to stakeholders.
- Track error budget: if you are consuming error budget faster than expected, prioritize reliability work.

## Advanced Patterns

### Anomaly Detection with ML
- Train models on baseline metric patterns (latency, volume, error rates). Alert on deviations that statistical thresholds would miss.
- Use seasonal decomposition: crypto markets have patterns (higher volume during US/Asia overlap, lower on weekends for some pairs).
- Implement change-point detection for regime shifts (e.g., volatility regime change that alters normal latency patterns).

### Chaos Engineering for Crypto Systems
- Simulate exchange API failures: inject timeouts, error responses, malformed data.
- Test WebSocket disconnection recovery: kill connections and verify automatic reconnection and state resync.
- Simulate chain reorganizations: verify that deposit tracking handles reorgs correctly.
- Run fire drills: simulate a hack scenario and measure response time and effectiveness.

### Correlation and Root Cause Analysis
- Build dependency maps: which services depend on which. When a node goes down, what trading pairs are affected?
- Implement automated correlation: group related alerts that fire within the same time window.
- Use distributed tracing (Jaeger, Zipkin) to pinpoint latency bottlenecks in the order submission path.

## Anti-Patterns

*   **Alerts Without Runbooks.** Creating alerts that page on-call engineers without documented response procedures wastes response time and leads to inconsistent incident handling.

*   **Alert Fatigue Through Over-Alerting.** Generating more than 5 actionable pages per on-call shift causes engineers to ignore or delay responses to genuine incidents. Tune thresholds and eliminate noisy alerts.

*   **No Dependency-Aware Alert Correlation.** Firing independent alerts for every downstream symptom of a single root cause (e.g., node down triggers 20 separate service alerts) overwhelms responders. Implement automated alert grouping.

*   **Monitoring Without Baseline Establishment.** Setting static alert thresholds without first establishing normal operational baselines produces either constant false positives or missed anomalies. Use statistical baselines with dynamic thresholds.

*   **Dashboard-Only Observability.** Relying on engineers to notice problems by watching dashboards instead of implementing proactive alerting means incidents are detected only after they impact users.

## What NOT To Do

- Never create alerts without runbooks. An alert that pages someone at 3 AM with no guidance on what to do is worse than useless.
- Never ignore alert fatigue. If on-call engineers are getting more than 5 actionable pages per shift, the alerting needs tuning.
- Never monitor only for known failure modes. Invest in observability tools that let you investigate novel issues.
- Never rely solely on cloud provider monitoring. If AWS goes down, your CloudWatch alerts go down with it. Use external monitoring.
- Never skip monitoring for the monitoring system itself. Who watches the watchmen? Use a separate monitoring path for your primary monitoring stack.
- Never set static thresholds without reviewing them quarterly. System baselines change as you scale.
- Never page on warnings. Pages are for issues requiring immediate human action. Everything else goes to a queue.
- Never treat on-chain monitoring as optional. Smart contract exploits can drain funds in a single block — minutes of delay in detection mean total loss.
- Never deploy changes without updating associated dashboards and alerts. Observability is part of the deployment checklist.
- Never operate without kill switches. The ability to halt everything within seconds is a safety requirement, not a luxury.
