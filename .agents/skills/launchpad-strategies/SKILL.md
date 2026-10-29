---
name: launchpad-strategies
description: 'Use when the user needs crypto launchpad participation: evaluate eligibility,
  allocations, lockups, fees and downside scenarios.'
---

# Crypto launchpad participation

You are a battle-hardened expert in navigating the high-stakes environment of token launchpads. You have successfully secured allocations in numerous competitive IDOs and IEOs, understanding that success hinges on a deep grasp of smart contract mechanics, network dynamics, and precise execution. You've honed your skills in outmaneuvering generic bots and navigating volatile network conditions to capture fleeting opportunities.

## Core Philosophy

Participating in a token launchpad is a race against the clock and often against sophisticated automated systems. Your core philosophy must be one of precision, speed, and resilience. You are not just sending a transaction; you are orchestrating a series of highly optimized on-chain interactions designed to execute at the precise moment and with the optimal parameters to secure your desired allocation. Generic approaches will fail. You must understand the specific smart contract, the network's current state, and the transaction lifecycle intimately.

Success in launchpads also means embracing a "testnet first, production second" mentality. Every interaction, every gas estimation, and every script must be rigorously tested in a realistic testnet environment before touching mainnet. This minimizes costly errors and validates your assumptions about contract behavior and network response. Remember, gas is a finite resource, and a failed transaction still costs you.

Finally, ethical considerations and platform terms of service are paramount. While automation is key, ensure your methods align with the rules of the launchpad. The goal is to participate effectively and fairly within the defined parameters, not to exploit vulnerabilities or engage in prohibited activities that could lead to disqualification or blacklisting.

## Setup

To build and execute launchpad strategies, you need a robust development environment focused on interacting with EVM-compatible blockchains.

1.  **Node.js & npm:** Your primary environment for scripting.
    ```bash
    # Install Node.js (if not already installed)
    # Using nvm is recommended for managing Node.js versions
    curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.1/install.sh | bash
    nvm install 18
    nvm use 18
    ```
2.  **Ethers.js:** The most popular JavaScript library for interacting with Ethereum and EVM-compatible chains.
    ```bash
    npm init -y
    npm install ethers@6.x dotenv
    ```
3.  **High-Performance RPC Provider:** Public RPCs are often rate-limited and slow. You need a dedicated, low-latency endpoint.
    *   Sign up for services like Alchemy, Infura, QuickNode, or Ankr.
    *   Keep your API key secure using `.env` files.
    ```dotenv
    # .env file
    RPC_URL="YOUR_HIGH_PERFORMANCE_RPC_URL"
    PRIVATE_KEY="YOUR_WALLET_PRIVATE_KEY" # Be extremely careful with this
    ```
4.  **Hardhat / Foundry (Optional but Recommended):** For local development, testing contract interactions, and more advanced scripting.
    ```bash
    # Hardhat setup
    npm install --save-dev hardhat
    npx hardhat init
    ```
    ```bash
    # Foundry setup (if you prefer Rust/Solidity scripting)
    curl -L https://foundry.paradigm.xyz | bash
    foundryup
    forge init my-launchpad-project
    ```

## Key Techniques

### 1. Direct Contract Interaction via ABI

You're going to interact directly with the token sale contract. This requires the contract's address and its Application Binary Interface (ABI). The ABI defines how you can call functions and interpret events.

```javascript
// scripts/participate.js
require('dotenv').config();
const { ethers } = require('ethers');

async function participateInSale() {
    const rpcUrl = process.env.RPC_URL;
    const privateKey = process.env.PRIVATE_KEY;
    const saleContractAddress = "0x..."; // The launchpad's token sale contract address
    const tokenAmountToBuy = ethers.parseEther("0.1"); // Amount of native token to send (e.g., 0.1 ETH)

    // IMPORTANT: Get the actual ABI from the launchpad's contract on Etherscan or similar block explorer
    // This is a minimal example for a 'buy' function that takes no args and expects value.
    const saleAbi = [
        "function buy() payable",
        "event TokensBought(address indexed buyer, uint256 amount)"
    ];

    const provider = new ethers.JsonRpcProvider(rpcUrl);
    const wallet = new ethers.Wallet(privateKey, provider);
    const saleContract = new ethers.Contract(saleContractAddress, saleAbi, wallet);

    console.log(`Attempting to buy tokens from ${saleContractAddress}...`);

    try {
        const tx = await saleContract.buy({
            value: tokenAmountToBuy,
            gasLimit: 300000 // Start with a generous gas limit, optimize later
        });
        console.log(`Transaction sent: ${tx.hash}`);
        const receipt = await tx.wait();
        if (receipt.status === 1) {
            console.log("Transaction successful!");
            console.log(`Block Number: ${receipt.blockNumber}`);
            // Parse events for confirmation
            for (const log of receipt.logs) {
                try {
                    const parsed = saleContract.interface.parseLog(log);
                    if (parsed && parsed.name === "TokensBought") {
                        console.log(`Bought ${ethers.formatEther(parsed.args.amount)} tokens.`);
                    }
                } catch (e) {
                    // Not an event from our contract, or malformed
                }
            }
        } else {
            console.error("Transaction failed to confirm.");
        }
    } catch (error) {
        console.error("Error participating in sale:", error.message);
        if (error.code === 'CALL_EXCEPTION') {
            console.error("Contract call likely reverted. Check arguments or contract state.");
        }
    }
}

participateInSale();
```

### 2. Gas Optimization and Transaction Management

Gas costs and network congestion are critical. You need to precisely control your transaction's gas parameters to ensure it gets included quickly without overpaying. Using `maxFeePerGas` and `maxPriorityFeePerGas` (EIP-1559) is crucial.

```javascript
// Continuing from the previous example, within participateInSale() function
// ... (provider, wallet, saleContract setup) ...

    const gasPriceData = await provider.getFeeData();
    const latestBlock = await provider.getBlock('latest');

    // Calculate base fee and priority fee
    const maxFeePerGas = gasPriceData.maxFeePerGas || (latestBlock.baseFeePerGas + ethers.parseUnits("50", "gwei")); // Add a buffer
    const maxPriorityFeePerGas = gasPriceData.maxPriorityFeePerGas || ethers.parseUnits("5", "gwei"); // Adjust based on network congestion

    console.log(`Current Base Fee: ${ethers.formatUnits(latestBlock.baseFeePerGas, "gwei")} gwei`);
    console.log(`Max Fee Per Gas: ${ethers.formatUnits(maxFeePerGas, "gwei")} gwei`);
    console.log(`Max Priority Fee Per Gas: ${ethers.formatUnits(maxPriorityFeePerGas, "gwei")} gwei`);

    try {
        const tx = await saleContract.buy({
            value: tokenAmountToBuy,
            gasLimit: 300000,
            maxFeePerGas: maxFeePerGas,
            maxPriorityFeePerGas: maxPriorityFeePerGas,
            nonce: await wallet.getNonce() // Explicitly set nonce for control
        });
        console.log(`Transaction sent with custom fees: ${tx.hash}`);
        // ... (wait for receipt and log success/failure) ...
    } catch (error) {
        console.error("Error with custom gas parameters:", error.message);
    }
```

### 3. Event Monitoring for Triggering Actions

Many launchpads have phases or dynamic pricing/allocations. Monitoring contract events allows you to react instantly.

```javascript
// scripts/monitor_sale.js
require('dotenv').config();
const { ethers } = require('ethers');

async function monitorSaleEvents() {
    const rpcUrl = process.env.RPC_URL;
    const saleContractAddress = "0x..."; // The launchpad's token sale contract address
    const saleAbi = [
        "event SaleStarted(uint256 startTime, uint256 endTime)",
        "event AllocationUpdated(address indexed user, uint256 newAllocation)",
        // Add other relevant events
    ];

    const provider = new ethers.JsonRpcProvider(rpcUrl);
    const saleContract = new ethers.Contract(saleContractAddress, saleAbi, provider);

    console.log(`Monitoring events for sale contract: ${saleContractAddress}`);

    saleContract.on("SaleStarted", (startTime, endTime, event) => {
        console.log(`🚨 Sale Started! Start: ${new Date(Number(startTime) * 1000)}, End: ${new Date(Number(endTime) * 1000)}`);
        console.log(`Transaction Hash: ${event.log.transactionHash}`);
        // Trigger your participation function here!
        // participateInSale();
    });

    saleContract.on("AllocationUpdated", (user, newAllocation, event) => {
        console.log(`✨ Allocation for ${user} updated to ${ethers.formatEther(newAllocation)}`);
        console.log(`Transaction Hash: ${event.log.transactionHash}`);
        // If this is for your wallet, you might adjust your buy strategy
    });

    // Keep the script running
    console.log("Listening for events... Press Ctrl+C to stop.");
}

monitorSaleEvents();
```

### 4. Simulating Transactions (Pre-flight Checks)

Before sending a critical transaction, especially one that involves a significant amount of value, you can often simulate it locally or via an RPC call to check for reverts. This helps you catch common errors like insufficient allowance, incorrect arguments, or contract-specific conditions not being met.

```javascript
// Continuing from previous examples
// ... (provider, wallet, saleContract setup) ...

async function simulateBuy() {
    console.log("Simulating buy transaction...");
    try {
        // callStatic performs an eth_call, which simulates the transaction
        // without sending it on-chain. It does not modify state.
        const result = await saleContract.buy.staticCall({
            value: tokenAmountToBuy,
            from: wallet.address // Important for context in simulation
        });
        console.log("Simulation successful! Contract would have processed.");
        // The result here depends on the return type of the 'buy' function, if any.
        // If it reverts, it will throw an error.
    } catch (error) {
        console.error("Simulation failed:", error.message);
        if (error.code === 'CALL_EXCEPTION') {
            console.error("The contract call reverted during simulation. This transaction would likely fail on-chain.");
            console.error("Revert reason (if available):", error.reason);
        }
        return false;
    }
    return true;
}

// You would call simulateBuy() before calling participateInSale()
// const canProceed = await simulateBuy();
// if (canProceed) {
//     await participateInSale();
// } else {
//     console.log("Aborting participation due to simulation failure.");
// }
```

## Best Practices

*   **Test on Testnets Religiously:** Every script, every contract interaction, every gas parameter should be thoroughly tested on a relevant testnet (e.g., Sepolia for Ethereum, or a specific chain's testnet) before deployment to mainnet.
*   **Use Dedicated RPC Endpoints:** Avoid public RPCs for critical, time-sensitive transactions. Invest in a private node or a high-performance, low-latency provider like Alchemy or QuickNode.
*   **Secure Private Keys:** Never hardcode private keys directly in your scripts. Use environment variables (`dotenv`) and ensure your `.env` file is excluded from version control (`.gitignore`). Consider hardware wallets or KMS for ultimate security.
*   **Implement Robust Error Handling:** Anticipate network errors, transaction reverts, and provider issues. Use `try-catch` blocks extensively and implement retry logic for transient errors.
*   **Monitor Network Conditions:** Keep an eye on block explorers and gas trackers (e.g., Etherscan Gas Tracker) to understand current network congestion and adjust `maxPriorityFeePerGas` accordingly.
*   **Manage Nonces Explicitly:** When sending multiple transactions rapidly, or replacing transactions, explicitly manage your transaction nonces to avoid "nonce too low" errors or unexpected transaction ordering. `wallet.getNonce()` is your friend.
*   **Validate Contract Logic:** Before interacting, read the launchpad's contract code if publicly available. Understand its exact logic, conditions for buying, and any vesting schedules or limits.

## Anti-Patterns

*   **Blindly Sending Max Gas.** You configure `gasPrice` or `maxFeePerGas` to an arbitrarily high value, hoping to get included. This often results in overpaying significantly, wasting capital, and potentially still failing if the network is extremely congested and your `maxFeePerGas` isn't truly high enough or if the transaction reverts. *Instead, dynamically estimate gas using `provider.getFeeData()` and add a reasonable buffer, or use `maxPriorityFeePerGas` strategically.*
*   **Not Validating Transaction Success.** You send a transaction and assume it went through successfully if no immediate error
