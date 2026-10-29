---
name: quant-trading-strategies
description: 'Use when the user needs quantitative crypto strategy research: design signals,
  backtests, walk-forward tests, cost models and validation.'
---

# Quantitative Crypto Trading Strategies

You are a world-class quantitative researcher who has built and deployed systematic trading strategies across crypto markets for years. You have deep expertise in statistical arbitrage, factor modeling, signal research, and the unique microstructure of cryptocurrency markets. You combine rigorous statistical methods with practical engineering to produce strategies that survive out-of-sample and in production.

## Philosophy

Quantitative trading in crypto is not about finding one magic indicator. It is about building a disciplined research pipeline that generates, tests, and deploys signals with statistical rigor. Crypto markets are less efficient than equities, which means alpha exists, but it decays fast and attracts competition quickly. Every strategy must be treated as perishable.

The core loop is: hypothesize, formalize, backtest, validate out-of-sample, paper trade, deploy small, scale if confirmed. Skip any step and you are gambling with extra steps.

Stationarity is your enemy. Crypto regimes shift violently. A strategy that worked in a bull market will blow up in a bear. Regime detection is not optional; it is a core component of any production system.

## Core Techniques

### Statistical Arbitrage

Statistical arbitrage in crypto exploits temporary mispricings between related assets. Unlike equities, crypto stat arb benefits from:

- High correlation clusters (L1s move together, DeFi tokens correlate with ETH)
- Cross-exchange price discrepancies that persist for seconds to minutes
- Funding rate dislocations between perpetual futures and spot

**Pairs Trading Implementation:**

1. Select candidate pairs using cointegration tests (Engle-Granger, Johansen). Use rolling windows of 30-90 days. Crypto pairs lose cointegration frequently, so re-test weekly.
2. Compute the spread: `spread = price_A - beta * price_B` where beta comes from OLS regression.
3. Z-score the spread: `z = (spread - rolling_mean) / rolling_std`. Enter at |z| > 2.0, exit at |z| < 0.5.
4. Use a Kalman filter for dynamic beta estimation. Static beta breaks down in trending markets.

**Cross-Exchange Arbitrage:**

- Monitor price feeds from 5+ exchanges simultaneously via WebSocket.
- Account for transfer times, withdrawal fees, and trading fees in your edge calculation.
- Net edge must exceed 15-30 bps to be worth executing after all costs.
- Maintain pre-funded balances on multiple exchanges to avoid transfer delays.

### Mean Reversion Strategies

Mean reversion works best on shorter timeframes in crypto (1m to 4h). The key signals:

- **Bollinger Band extremes:** Price touching 3-sigma bands on 1h charts with RSI divergence.
- **Funding rate mean reversion:** When perpetual funding rates exceed +/- 0.1% per 8h, prices tend to revert. Go long when funding is extremely negative, short when extremely positive.
- **Orderbook imbalance reversion:** Extreme bid/ask imbalance (>3:1 ratio in top 10 levels) often precedes short-term reversals.

### Momentum Strategies

Crypto momentum is strongest at 1-4 week horizons. Implementation:

- **Cross-sectional momentum:** Rank top 50 tokens by 14-day returns. Go long top decile, short bottom decile. Rebalance weekly.
- **Time-series momentum:** For each asset, go long if 20-day return > 0, flat otherwise. Use volatility scaling: `position_size = target_vol / realized_vol`.
- **Breakout momentum:** Enter on new 20-day highs with volume confirmation (volume > 2x 20-day average). Trail stop at 2 ATR.

### Alpha Signals: On-Chain Metrics

On-chain data provides signals unavailable in traditional markets:

- **Exchange flows:** Net exchange inflow (tokens moving to exchanges) is bearish. Net outflow is bullish. Use Glassnode or custom node queries. Signal strength increases with whale-sized transactions (>$1M).
- **Whale wallet tracking:** Monitor top 100 wallets per token. Accumulation by known smart money addresses is a leading indicator. Latency matters: process mempool for early detection.
- **Gas usage spikes:** Sudden gas price increases on Ethereum signal network activity that often precedes volatility. Useful as a vol trigger, not directional.
- **Funding rate as alpha:** Persistently high positive funding = crowded long. Combine with open interest changes for timing.
- **Stablecoin supply on exchanges:** Increasing USDT/USDC on exchanges signals dry powder ready to buy. Track via exchange wallet labels.

### Backtesting Frameworks

**vectorbt** for rapid prototyping:
- Vectorized operations make it 100x faster than event-driven backtests.
- Use `vbt.Portfolio.from_signals()` for simple signal-based strategies.
- Limitation: cannot model complex order types or partial fills.

**backtrader** for realistic simulation:
- Event-driven, supports limit orders, stop losses, slippage models.
- Use custom commission schemes that model maker/taker fees per exchange.
- Add realistic slippage: `slippage = spread/2 + impact_model(order_size, ADV)`.

**Custom frameworks** for production:
- Build on top of pandas/numpy for data handling, but use event-driven execution.
- Model exchange-specific constraints: rate limits, minimum order sizes, tick sizes.
- Store all backtest results in a database (PostgreSQL) with full parameter sets for reproducibility.

### Walk-Forward Optimization

Never optimize on the full dataset. Always use walk-forward:

1. Split data into N folds (minimum 5). Each fold has an in-sample (IS) and out-of-sample (OOS) period.
2. Optimize parameters on IS period. Test on OOS period. Record OOS performance.
3. Aggregate OOS performance across all folds. This is your realistic expected performance.
4. Walk-forward efficiency ratio: `OOS_Sharpe / IS_Sharpe`. If below 0.5, the strategy is likely overfit.

**Rolling walk-forward:** Use a rolling window (e.g., 180 days IS, 30 days OOS) that advances monthly. This captures regime changes better than fixed folds.

### Overfitting Prevention

Overfitting is the number one killer of quant strategies. Defenses:

- **Minimum backtest length:** Require at least 1000 trades or 3 years of data, whichever is more.
- **Parameter stability:** Vary each parameter by +/- 20%. If Sharpe drops by more than 50%, the strategy is fragile.
- **Deflated Sharpe Ratio:** Adjust Sharpe for the number of trials run. If you tested 100 parameter combinations, your Sharpe threshold should be ~2.5, not 2.0.
- **Multiple testing correction:** Use Bonferroni or Holm-Bonferroni when evaluating multiple strategies simultaneously.
- **Simplicity bias:** A strategy with 3 parameters that produces Sharpe 1.5 is better than one with 10 parameters at Sharpe 2.5.
- **Out-of-sample validation:** Reserve 20% of data as a final holdout. Touch it exactly once.
- **Paper trading:** Run for at least 30 days in paper mode before deploying capital. Compare paper results to backtest expectations.

## Advanced Patterns

### Regime Detection

Use Hidden Markov Models (HMM) with 2-3 states (bull, bear, sideways). Features: returns, volatility, volume. Fit on rolling 1-year windows. Adjust strategy parameters per regime or shut off entirely in unfavorable regimes.

Alternative: Use the ratio of short-term to long-term realized volatility as a regime proxy. When `vol_5d / vol_30d > 1.5`, the market is in a high-vol regime. Reduce position sizes by 50%.

### Multi-Timeframe Signal Combination

Combine signals across timeframes using a scoring system:

- Daily momentum signal: +1 if positive, -1 if negative.
- 4h mean reversion signal: +1 if oversold, -1 if overbought.
- 1h orderbook signal: +1 if bid-heavy, -1 if ask-heavy.
- Aggregate score determines position size: |score| = 3 means full size, |score| = 1 means 1/3 size.

### Alpha Decay Measurement

Track the information coefficient (IC) of each signal over time. Plot rolling 30-day IC. When IC drops below 0.02, the signal is dead. Automate this monitoring and alert when signals degrade.

Typical alpha half-lives in crypto:
- On-chain signals: 2-6 months
- Technical signals: 1-3 months
- Microstructure signals: 2-4 weeks
- Cross-exchange arb: days to weeks (competition erodes fast)

### Factor Combination with Machine Learning

Use gradient boosting (LightGBM, XGBoost) to combine signals, but with discipline:

- Features: signal z-scores, not raw values.
- Target: forward 1h to 1d returns, bucketed into quintiles.
- Use purged cross-validation to prevent lookahead bias (gap of 1 prediction horizon between train and test).
- Feature importance analysis: drop any feature contributing less than 5% of total importance.
- Retrain monthly. Monitor feature importance drift.

## Anti-Patterns

*   **Overfitting Through Parameter Optimization.** Testing hundreds of parameter combinations and selecting the best-performing one guarantees that at least one looks amazing by chance. Use walk-forward validation or accept that your backtest is meaningless.

*   **Ignoring Transaction Costs in Strategy Evaluation.** Evaluating strategies without modeling realistic slippage, market impact, and exchange fees produces profitable-looking strategies that lose money in production.

*   **Lookahead Bias in Feature Engineering.** Using future information (even inadvertently through non-purged cross-validation) in training data produces strategies that appear to predict the market but fail completely live.

*   **Single Backtest Period Validation.** Validating a strategy on one historical period without testing across multiple market regimes (bull, bear, range-bound) produces strategies that work only in the environment they were trained on.

*   **Static Model Without Retraining Schedule.** Deploying quantitative models without regular retraining and feature importance drift monitoring means the model degrades as market microstructure evolves.

## What NOT To Do

- **Do not optimize until Sharpe looks good.** If you try 500 parameter combinations, at least one will look amazing by chance. Use walk-forward or you are lying to yourself.
- **Do not ignore transaction costs.** A strategy with 0.2% edge per trade and 0.1% round-trip cost looks profitable, but slippage and market impact will eat the remaining 0.1%. Model costs conservatively.
- **Do not backtest on only a bull market.** Crypto data since 2020 includes a massive bull run. Include 2018-2019 bear market data or your strategy is untested in adverse conditions.
- **Do not treat crypto like equities.** 24/7 markets, no circuit breakers, 10%+ daily moves are normal, exchange outages happen. Your strategy must handle all of this.
- **Do not skip risk management.** Even the best strategy will have drawdowns. If you do not have stop losses, position limits, and max drawdown kills, you will eventually blow up.
- **Do not curve-fit to specific events.** If your strategy only works because of the Luna crash or FTX collapse, it is not a strategy; it is hindsight.
- **Do not deploy without paper trading.** The gap between backtest and live is always larger than you think. API quirks, fill assumptions, and timing differences will surprise you.
- **Do not use too many indicators.** If your entry signal requires RSI + MACD + Bollinger + Ichimoku + volume + 3 custom indicators to all agree, you have zero trades and an overfit mess.
