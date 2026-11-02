---
name: options-vaults
description: 'Use when the user needs defi option vault strategies: evaluate structured
  yield, option Greeks, settlement and vault-specific risk.'
---

# DeFi option vault strategies

You are a seasoned architect of sophisticated DeFi yield protocols, deeply entrenched in the mechanics of on-chain derivatives and automated strategy execution. You've engineered and deployed decentralized options vaults (DOVs) that empower users to passively earn yield by managing complex options positions. Your expertise spans the entire lifecycle, from smart contract design and risk parameterization to oracle integration and keeper automation, ensuring robust, capital-efficient, and user-friendly structured products.

## Core Philosophy

Options vaults abstract away the complexities of on-chain options trading, offering users a passive way to earn yield by participating in defined strategies. At its core, an options vault pools user capital and programmatically executes a specific options strategy, such as selling covered calls or cash-secured puts, over regular intervals (epochs). Users simply deposit their assets, and the vault handles everything from strike selection and option selling to premium collection and yield distribution.

The fundamental value proposition lies in democratizing access to sophisticated options strategies, which traditionally require deep market knowledge and active management. By automating these strategies, vaults reduce gas costs, minimize user cognitive load, and provide consistent, programmatic access to volatility-based yield. This approach requires meticulous smart contract design, robust oracle dependencies for pricing and implied volatility, and reliable off-chain keeper infrastructure to ensure timely execution and rebalancing, all while carefully managing the inherent risks associated with derivatives.

## Setup

Building and interacting with options vaults primarily involves smart contract development (Solidity) and off-chain automation (TypeScript/JavaScript with Ethers.js or Web3.js).

1.  **Development Environment:**
    You'll need a robust Solidity development framework. Foundry is often preferred for its speed and developer experience.

    ```bash
    # Install Foundry (if you haven't already)
    # Security: download the verified official installer, inspect it before executing, and follow the current platform-specific installation guide.
    foundryup

    # Create a new Foundry project
    forge init options-vault-project
    cd options-vault-project
    ```

2.  **Client-side Interaction:**
    Use `ethers.js` or `web3.js` for interacting with deployed vaults, fetching data, and building keeper bots.

    ```bash
    # Install ethers.js
    npm install ethers
    # or
    yarn add ethers
    ```

3.  **Oracle Integration:**
    For price feeds, you'll typically use Chainlink Data Feeds. For implied volatility (IV) or custom market data, you might integrate with protocols like Pyth Network or build custom oracle solutions.

    ```solidity
    // Example Chainlink import in Solidity
    import "@chainlink/contracts/src/v0.8/interfaces/AggregatorV3Interface.sol";
    ```

## Key Techniques

### 1. Vault Core Contract Architecture

Design your vault to manage deposits, withdrawals, and strategy execution. A common pattern involves an `initialize` function, `deposit` for users to add collateral, `withdraw` for users to reclaim their share, and an `executeStrategy` function called by keepers.

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.18;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";

interface IOptionsProtocol {
    function sellOption(address quoteAsset, uint256 quoteAmount, /* ... other params */) external returns (uint256 premiumReceived);
    // ... other options protocol specific functions
}

contract CoveredCallVault is Ownable {
    using SafeERC20 for IERC20;

    IERC20 public immutable collateralToken;
    IERC20 public immutable quoteToken; // e.g., USDC for premium
    IOptionsProtocol public immutable optionsProtocol;

    uint256 public totalVaultShares;
    mapping(address => uint256) public shares;

    constructor(address _collateralToken, address _quoteToken, address _optionsProtocol) {
        collateralToken = IERC20(_collateralToken);
        quoteToken = IERC20(_quoteToken);
        optionsProtocol = IOptionsProtocol(_optionsProtocol);
    }

    function deposit(uint256 amount) external returns (uint256 mintedShares) {
        require(amount > 0, "Deposit amount must be positive");
        collateralToken.safeTransferFrom(msg.sender, address(this), amount);

        if (totalVaultShares == 0) {
            mintedShares = amount; // First depositor sets the initial share price
        } else {
            mintedShares = (amount * totalVaultShares) / collateralToken.balanceOf(address(this));
        }

        shares[msg.sender] += mintedShares;
        totalVaultShares += mintedShares;
        // Emit Deposit event
    }

    // ... withdraw, executeStrategy, etc.
}
```

### 2. Strategy Execution and Option Selling

Within the `executeStrategy` function, the vault will interact with an underlying options protocol (e.g., Lyra, Dopex, Premia) to sell options. This involves calculating the amount of collateral to use, determining the strike price and expiry based on current market conditions (often via oracles or protocol-specific logic), and calling the `sellOption` function.

```solidity
// Inside CoveredCallVault contract
// This function would typically be callable only by a designated keeper or role
function executeStrategy(uint256 strikePrice, uint256 expiry, uint256 amountToSell) external onlyOwner {
    require(amountToSell > 0, "Amount to sell must be positive");
    require(collateralToken.balanceOf(address(this)) >= amountToSell, "Insufficient collateral in vault");

    // Approve the options protocol to spend collateral
    collateralToken.safeApprove(address(optionsProtocol), amountToSell);

    // Call the underlying options protocol to sell the call option
    // Parameters like `strikePrice` and `expiry` would come from off-chain analysis or an oracle
    uint256 premiumReceived = optionsProtocol.sellOption(
        address(collateralToken), // Underlying asset
        amountToSell,             // Amount of underlying to collateralize
        strikePrice,              // Strike price for the call option
        expiry,                   // Expiry timestamp
        /* ... other protocol-specific parameters like option type, minimum premium, etc. */
    );

    // Store premium, update accounting, etc.
    // Premiums are usually in a stablecoin or the quoteToken
    quoteToken.safeTransferFrom(address(optionsProtocol), address(this), premiumReceived);

    // Emit StrategyExecuted event
}
```

### 3. Keeper Automation for Rebalancing

Off-chain keeper bots monitor market conditions, vault states, and epoch timings. They are responsible for calling the `executeStrategy` function at appropriate times, potentially with calculated strike prices and expiries.

```typescript
// keeper.ts using ethers.js
import { ethers } from "ethers";
import { ABI as CoveredCallVaultABI } from './abis/CoveredCallVault.json'; // Your vault's ABI
import { VAULT_ADDRESS, PRIVATE_KEY, RPC_URL, CHAINLINK_PRICE_FEED } from './config';

async function runKeeper() {
    const provider = new ethers.JsonRpcProvider(RPC_URL);
    const wallet = new ethers.Wallet(PRIVATE_KEY, provider);
    const vault = new ethers.Contract(VAULT_ADDRESS, CoveredCallVaultABI, wallet);

    console.log("Keeper running...");

    // In a real scenario, you'd fetch current market data, IV, etc.
    // For simplicity, let's assume a dummy strike and expiry
    const currentPriceFeed = new ethers.Contract(CHAINLINK_PRICE_FEED, ["function latestRoundData() external view returns (uint80 roundId, int256 answer, uint256 startedAt, uint256 updatedAt, uint80 answeredInRound)"], provider);
    const [, currentUnderlyingPrice,,,] = await currentPriceFeed.latestRoundData();
    const strikePrice = (BigInt(currentUnderlyingPrice) * 105n) / 100n; // Example: 5% OTM
    const expiry = Math.floor(Date.now() / 1000) + (7 * 24 * 60 * 60); // Example: 1 week from now
    const amountToSell = await vault.collateralToken().balanceOf(VAULT_ADDRESS); // Sell all available collateral

    try {
        // Check if strategy needs execution (e.g., new epoch, options expired)
        // This logic would be more complex in a real vault.
        const tx = await vault.executeStrategy(strikePrice, expiry, amountToSell);
        await tx.wait();
        console.log(`Strategy executed. Tx hash: ${tx.hash}`);
    } catch (error) {
        console.error("Error executing strategy:", error);
    }
}

// Execute every X hours/days using a cron job or similar
setInterval(runKeeper, 4 * 60 * 60 * 1000); // Run every 4 hours for example
```

### 4. Premium Distribution and Yield Calculation

Premiums collected from selling options are usually accumulated in the vault and then distributed to depositors. This often happens at the end of an epoch or upon withdrawal. The yield is typically calculated as the increase in the value of a user's shares relative to their initial deposit value.

```solidity
// Inside CoveredCallVault contract
function withdraw(uint256 _shares) external returns (uint256 withdrawnAmount) {
    require(_shares > 0, "Withdraw amount must be positive");
    require(shares[msg.sender] >= _shares, "Insufficient shares");

    // Calculate current share value: (total vault collateral + total premiums) / total shares
    // This needs careful accounting if premiums are in a different token than collateral
    uint256 currentVaultValue = collateralToken.balanceOf(address(this)) + quoteToken.balanceOf(address(this)); // Simplified
    withdrawnAmount = (_shares * currentVaultValue) / totalVaultShares;

    shares[msg.sender] -= _shares;
    totalVaultShares -= _shares;

    collateralToken.safeTransfer(msg.sender, withdrawnAmount); // Assuming collateral is primary asset for withdrawal
    // Also transfer a proportional amount of accumulated premiums if not auto-compounded.

    // Emit Withdraw event
}

// A more sophisticated vault would have a `harvest` function to claim profits
// and potentially compound them or distribute them directly.
```

## Best Practices

*   **Robust Risk Management:** Clearly define and parameterize the strategy's risk profile (e.g., maximum percentage out-of-the-money for calls, maximum capital at risk).
*   **Thorough Audits & Testing:** Options vaults are complex; rigorous unit, integration, and fuzz testing, combined with multiple independent audits, are non-negotiable.
*   **Decentralized Keeper Network:** Avoid single points of failure by using decentralized keeper networks (e.g., Chainlink Keepers, Gelato Network) or incentivizing multiple independent keepers.
*   **Transparent Fees & Performance:** Clearly communicate all fees (management, performance) and provide accessible historical performance data to users.
*   **Emergency Shutdown Mechanisms:** Include a multisig-controlled emergency stop function to pause deposits, withdrawals, or strategy execution in case of exploits or market black swans.
*   **Impermanent Loss Mitigation:** For covered call vaults, be aware that if the underlying asset appreciates significantly past the strike, the vault might underperform a simple HODL strategy. Communicate this risk.
*   **Oracle Redundancy:** Use multiple, reputable oracle sources or a weighted average to prevent reliance on a single point of failure for price and implied volatility data.

## Anti-Patterns

*   **Single Point of Failure Keeper.** Relying on a single, centrally controlled bot to execute the strategy introduces a critical vulnerability. Implement decentralized keeper solutions or require multiple independent keepers to sign off on executions.
*   **Stale or Manipulated Oracles.** Using outdated or easily manipulable price feeds for strike selection or collateral valuation can lead to significant losses.

## Review & Production Validation (2026-10-31)

- **Domain control (DeFi protocol economics):** Verify collateral parameters, oracle freshness, fees, liquidation and withdrawal constraints.
- **Independent validation:** Distinguish net yield from nominal rewards; model depeg, hack and liquidity stress.
- **Time-sensitive details:** Treat fixed rates, thresholds, package versions, protocols and jurisdiction-specific rules in the examples above as illustrative unless reconfirmed against primary documentation.
- **Before relying on the result:** State inputs and assumptions; verify calculations and edge cases, and identify what has not been executed or tested.
