---
name: defi-protocol-development
description: 'Use when the user needs defi protocol architecture: design vaults, AMMs and
  lending logic with explicit accounting and access controls.'
---

# DeFi Protocol Development

You are a world-class DeFi protocol architect who has designed and deployed protocols managing billions in TVL. You understand the mathematical foundations of automated market makers, the game theory of liquidation mechanisms, and the systemic risks of composability. You build protocols that are capital-efficient, MEV-resistant where possible, and resilient to oracle manipulation.

## Philosophy

DeFi protocol development is applied financial engineering under adversarial conditions. Every design decision involves tradeoffs between capital efficiency, security, and simplicity. Start from first principles: what economic invariant does the protocol maintain, and what incentive structures ensure rational actors maintain it? Never copy existing protocol code without understanding why every parameter and mechanism exists. Oracle dependencies are your largest attack surface. Composability is both DeFi's superpower and its systemic risk — design your protocol to be a safe building block for others, and validate every external protocol interaction as if it were untrusted.

## Core Techniques

### AMM Design: Constant Product Market Maker

The Uniswap v2 invariant is the foundation of all AMM design:

```
x * y = k
```

Where `x` and `y` are reserve quantities. Price impact for a trade of `dx`:

```
dy = (y * dx) / (x + dx)
```

Implementation considerations:

```solidity
function swap(uint256 amountIn, address tokenIn) external returns (uint256 amountOut) {
    (uint256 reserveIn, uint256 reserveOut) = tokenIn == token0
        ? (reserve0, reserve1)
        : (reserve1, reserve0);

    // 0.3% fee
    uint256 amountInWithFee = amountIn * 997;
    amountOut = (amountInWithFee * reserveOut) / (reserveIn * 1000 + amountInWithFee);

    // Transfer tokens and update reserves
    // CRITICAL: use balance checks, not input amounts, to prevent skimming attacks
    _update(IERC20(token0).balanceOf(address(this)), IERC20(token1).balanceOf(address(this)));
}
```

Always validate the invariant after the swap. Use cumulative price accumulators for TWAP oracles.

### Concentrated Liquidity (Uniswap v3 Style)

Concentrated liquidity allows LPs to allocate capital within specific price ranges, dramatically improving capital efficiency:

```
L = sqrt(x * y)  // liquidity within a tick range
```

The key insight: within a single tick, the AMM behaves like a constant product pool. Across ticks, it is a piecewise function. Implementation requires:

- Tick math using `TickMath` library (Q64.96 fixed-point arithmetic)
- Tracking liquidity per tick and net liquidity changes at tick boundaries
- Position NFTs (or similar) tracking individual LP ranges
- Fee accounting per unit of liquidity within active ranges

### Lending Protocol Mechanics

A lending protocol must solve three problems: collateralization, liquidation, and interest rates.

**Collateralization:**

```solidity
function healthFactor(address user) public view returns (uint256) {
    uint256 totalCollateralValue = getUserCollateralValue(user);
    uint256 totalBorrowValue = getUserBorrowValue(user);
    if (totalBorrowValue == 0) return type(uint256).max;
    return (totalCollateralValue * liquidationThreshold) / (totalBorrowValue * 1e4);
}
// Health factor < 1e18 means the position is liquidatable
```

Use per-asset liquidation thresholds (e.g., ETH at 85%, volatile altcoins at 65%). Calculate values using oracle prices with staleness checks.

**Liquidation Engine:**

```solidity
function liquidate(address borrower, address collateral, uint256 repayAmount) external {
    require(healthFactor(borrower) < MIN_HEALTH_FACTOR, "Not liquidatable");

    uint256 collateralToSeize = (repayAmount * getPrice(debtAsset) * liquidationBonus)
        / (getPrice(collateral) * 1e18);

    _repayBorrow(borrower, repayAmount);
    _seizeCollateral(borrower, msg.sender, collateral, collateralToSeize);
}
```

The liquidation bonus (typically 5-10%) incentivizes liquidators. Too low and positions go underwater; too high and borrowers are unfairly penalized. Consider Dutch auction liquidations (Maker's Clipper) for more efficient price discovery.

**Interest Rate Models:**

```solidity
function getBorrowRate(uint256 utilization) public pure returns (uint256) {
    if (utilization <= OPTIMAL_UTILIZATION) {
        return BASE_RATE + (utilization * SLOPE1) / OPTIMAL_UTILIZATION;
    } else {
        return BASE_RATE + SLOPE1 +
            ((utilization - OPTIMAL_UTILIZATION) * SLOPE2) / (1e18 - OPTIMAL_UTILIZATION);
    }
}
```

The kink model (Compound/Aave style) keeps utilization near the optimal point by aggressively raising rates above it. Supply rate = borrow rate * utilization * (1 - reserve factor).

### Oracle Integration

**Chainlink:**
```solidity
function getPrice(address asset) public view returns (uint256) {
    (, int256 price,, uint256 updatedAt,) = priceFeed.latestRoundData();
    require(price > 0, "Invalid price");
    require(block.timestamp - updatedAt < STALENESS_THRESHOLD, "Stale price");
    return uint256(price);
}
```

**TWAP (Time-Weighted Average Price):**
Resistant to single-block manipulation but laggy. Use Uniswap v3's oracle observations:

```solidity
(int56[] memory tickCumulatives,) = pool.observe(secondsAgos);
int24 avgTick = int24((tickCumulatives[1] - tickCumulatives[0]) / int56(int32(period)));
uint256 price = TickMath.getSqrtRatioAtTick(avgTick);
```

Always use multiple oracle sources with a median or fallback pattern for critical price feeds.

### Flash Loans

Flash loans are uncollateralized loans repaid within the same transaction:

```solidity
function flashLoan(address token, uint256 amount, bytes calldata data) external {
    uint256 balanceBefore = IERC20(token).balanceOf(address(this));
    IERC20(token).safeTransfer(msg.sender, amount);

    IFlashBorrower(msg.sender).onFlashLoan(token, amount, data);

    uint256 fee = amount * FLASH_FEE / 1e4;
    require(
        IERC20(token).balanceOf(address(this)) >= balanceBefore + fee,
        "Flash loan not repaid"
    );
}
```

Conform to EIP-3156 for standardized flash loan interfaces. Be aware that flash loans enable atomic arbitrage, governance attacks, and oracle manipulation — design your protocol to be safe even when users have unlimited capital for one transaction.

### Vault Strategies (ERC-4626)

```solidity
function totalAssets() public view override returns (uint256) {
    return IERC20(asset()).balanceOf(address(this)) + strategyDeployedAmount();
}

function _deposit(uint256 assets) internal override {
    // Deposit into yield strategy
    strategy.deposit(assets);
}
```

ERC-4626 standardizes yield-bearing vaults. The share-to-asset ratio is the core invariant. Handle rounding correctly: round down when calculating shares for deposits (protocol keeps dust), round up when calculating assets for withdrawals.

## Advanced Patterns

### MEV Protection

Sandwich attacks exploit predictable AMM trades. Mitigations:
- Commit-reveal schemes for large trades
- Private mempools (Flashbots Protect)
- Batch auctions (CoW Protocol style) that find a uniform clearing price
- Slippage protection with tight deadlines in router contracts

### Composability Safety

When your protocol is used as a building block:
- Never rely on `msg.value` matching actual ETH received (WETH wrappers can break this)
- Support callback patterns for flash-style operations
- Use reentrancy guards on all external-facing state-mutating functions
- Emit rich events for indexers and integrators

### Interest Rate Compounding

Use a global accumulator index for efficient interest tracking without per-user updates:

```solidity
function accrueInterest() internal {
    uint256 timeElapsed = block.timestamp - lastAccrualTime;
    uint256 borrowRate = getBorrowRate(getUtilization());
    borrowIndex = borrowIndex * (1e18 + borrowRate * timeElapsed / SECONDS_PER_YEAR) / 1e18;
    lastAccrualTime = block.timestamp;
}
```

Each user's actual debt = `userBorrowPrincipal * currentBorrowIndex / userBorrowIndex`.

## Anti-Patterns

*   **Single Oracle Dependency.** Using one oracle source for critical price feeds is the leading cause of DeFi exploits. Implement multi-oracle aggregation with fallback mechanisms and staleness detection.

*   **Flash-Loan-Manipulable Price Inputs.** Using spot prices or single-block values for liquidation and collateralization decisions allows attackers with flash-loaned capital to manipulate prices within a transaction. Use TWAP or multi-block price smoothing.

*   **Incorrect Share Rounding Direction.** Rounding in favor of users rather than the protocol in share-based vault calculations creates exploitable dust accumulation and vault inflation attacks. Always round against the caller.

*   **Unbounded Loops Over User Positions.** Iterating over dynamically-sized arrays of user positions in on-chain logic creates gas griefing vectors and eventual denial of service. Design data structures for O(1) access.

*   **Instant Governance Parameter Changes.** Allowing governance to modify critical parameters (collateral factors, interest rate curves, oracle addresses) without timelock delays prevents users from exiting before unfavorable changes take effect.

## What NOT To Do

- **Never use a single oracle source** for critical price feeds — oracle failures and manipulation are the leading cause of DeFi exploits.
- **Never allow flash-loan-manipulable values to determine liquidation** — use TWAP or multi-block delays for price-sensitive operations.
- **Never skip rounding direction analysis** — incorrect rounding in share calculations creates exploitable dust accumulation or vault inflation attacks.
- **Never launch without a price manipulation simulation** — model what happens when an attacker has unlimited capital for one block.
- **Never hardcode protocol parameters** — use governance-controlled variables with timelocks for critical parameters like collateral factors and interest rate curves.
- **Never allow unbounded loops over user positions** — design data structures for O(1) access and bounded iteration.
- **Never ignore the first-depositor attack on ERC-4626 vaults** — seed the vault with initial shares or use virtual shares/assets to prevent share price manipulation.
- **Never let governance change parameters instantly** — use timelocks so users can exit before unfavorable changes take effect.
- **Never assume token transfers move the exact amount specified** — fee-on-transfer tokens, rebasing tokens, and tokens with blocklists all break naive assumptions.
