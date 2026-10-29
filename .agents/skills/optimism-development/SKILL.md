---
name: optimism-development
description: 'Use when the user needs op stack and optimism development: plan OP Stack integrations,
  bridges, messaging and L2 deployment.'
---

# OP Stack and Optimism development

You are a battle-tested Optimism developer, expertly navigating the nuances of L2 scalability, cross-chain communication, and the broader OP Stack ecosystem. You build robust, gas-efficient decentralized applications that leverage Optimism's EVM compatibility and secure bridging mechanisms.

## Core Philosophy

Optimism provides an EVM-equivalent environment that feels just like Ethereum, but with significantly lower transaction costs and higher throughput. Your core philosophy when building on Optimism should be to maximize this efficiency while maintaining the security guarantees of Ethereum. This means designing contracts and dApps that minimize L1 data serialization costs, which are the primary variable component of transaction fees on Optimism. Embrace the standard tooling you're familiar with from Ethereum development – Hardhat, Foundry, Ethers.js, Viem – as they largely work out of the box, but always keep the L2-specific gas mechanics and the asynchronous nature of cross-chain communication in mind.

Think of Optimism as a high-speed lane directly connected to Ethereum's main highway. You get the same security and finality, but your operations are processed much faster and cheaper. This enables new categories of applications that might be cost-prohibitive on L1. Your goal is to build dApps that are not just *possible* but *practical* for everyday users, leveraging Optimism's capabilities to deliver a superior user experience without compromising on decentralization or security.

## Setup

Getting started with Optimism development is straightforward, often requiring minimal changes to your existing Ethereum development setup.

1.  **Node.js & npm/yarn**: Ensure you have a recent version installed.
2.  **Hardhat/Foundry**: Choose your preferred development environment. For Hardhat:
    ```bash
    npm install --save-dev hardhat @nomicfoundation/hardhat-toolbox
    npx hardhat init
    ```
    For Foundry:
    ```bash
    curl -L https://foundry.paradigm.xyz | bash
    foundryup
    forge init my-optimism-project
    ```
3.  **Optimism SDKs**: For interacting with Optimism's specific features like bridging, you'll need the Optimism SDK (which wraps `ethers.js`) or use `viem` with its Optimism-specific chain configurations.
    ```bash
    npm install @openzeppelin/contracts-upgradeable # For upgradeable contracts
    npm install @eth-optimism/sdk ethers # If using ethers.js
    npm install viem # If using viem
    ```
4.  **Configure Network**: Add Optimism networks (e.g., Optimism Mainnet, Optimism Sepolia) to your Hardhat configuration (`hardhat.config.js`). You'll need an RPC URL, which you can get from providers like Alchemy, Infura, or Blast.

    ```javascript
    // hardhat.config.js
    require("@nomicfoundation/hardhat-toolbox");
    require("dotenv").config();

    const ALCHEMY_API_KEY = process.env.ALCHEMY_API_KEY;
    const PRIVATE_KEY = process.env.PRIVATE_KEY;

    module.exports = {
      solidity: "0.8.20",
      networks: {
        "optimism-sepolia": {
          url: `https://opt-sepolia.g.alchemy.com/v2/${ALCHEMY_API_KEY}`,
          accounts: [PRIVATE_KEY],
          gasPrice: 1000000000, // Example, adjust as needed or let provider estimate
        },
        optimism: {
          url: `https://opt-mainnet.g.alchemy.com/v2/${ALCHEMY_API_KEY}`,
          accounts: [PRIVATE_KEY],
          gasPrice: 1000000000,
        },
      },
    };
    ```
    Remember to set `ALCHEMY_API_KEY` and `PRIVATE_KEY` in a `.env` file.

## Key Techniques

### 1. Deploying Contracts to Optimism L2

Deploying contracts to Optimism is nearly identical to Ethereum L1. You use the same development tools and Solidity code. The primary difference is pointing your deployment script to an Optimism network.

```javascript
// scripts/deploy.js (Hardhat example)
const { ethers } = require("hardhat");

async function main() {
  const MyContract = await ethers.getContractFactory("MyContract");
  console.log("Deploying MyContract...");
  const myContract = await MyContract.deploy();
  await myContract.waitForDeployment();
  console.log(`MyContract deployed to: ${myContract.target}`);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
```
To deploy:
```bash
npx hardhat run scripts/deploy.js --network optimism-sepolia
```

### 2. Standard L1-L2 ETH Deposit

To move ETH from Ethereum L1 to Optimism L2, you interact with the `StandardBridge` contract on L1. The Optimism SDK simplifies this.

```javascript
// depositEth.js (Using @eth-optimism/sdk)
const { ethers } = require("ethers");
const { getL2Provider, getL1Provider, getL1Wallet, getL2Wallet, L1_CHAIN_ID, L2_CHAIN_ID } = require('./utils/providers'); // Assume these are defined

const { CrossChainMessenger } = require("@eth-optimism/sdk");

async function depositEth() {
  const l1Wallet = getL1Wallet();
  const l2Wallet = getL2Wallet();

  const crossChainMessenger = new CrossChainMessenger({
    l1ChainId: L1_CHAIN_ID, // E.g., 11155111 for Sepolia
    l2ChainId: L2_CHAIN_ID, // E.g., 11155420 for Optimism Sepolia
    l1SignerOrProvider: l1Wallet,
    l2SignerOrProvider: l2Wallet,
  });

  const amountToDeposit = ethers.parseEther("0.01"); // 0.01 ETH

  console.log(`Depositing ${ethers.formatEther(amountToDeposit)} ETH from L1 to L2...`);
  const tx = await crossChainMessenger.depositETH(amountToDeposit);
  console.log(`L1 Deposit TX hash: ${tx.hash}`);

  await tx.wait(); // Wait for the L1 transaction to be mined

  console.log("L1 deposit confirmed. Waiting for L2 finalization (can take a few minutes)...");
  await crossChainMessenger.waitForMessageReceipt(tx); // Wait for the message to be relayed to L2

  console.log("ETH deposited to L2 successfully!");
}

depositEth().catch(console.error);
```
*Note*: `getL1Provider`, `getL2Provider`, etc., would involve setting up `ethers.JsonRpcProvider` instances with appropriate RPC URLs and `Wallet` instances with your private key.

### 3. Standard L2-L1 ETH Withdrawal

Withdrawing ETH from Optimism L2 back to Ethereum L1 is a two-step process due to Optimism's fraud proof window (typically 7 days on Mainnet, a few minutes on testnets).

```javascript
// withdrawEth.js (Using @eth-optimism/sdk)
const { ethers } = require("ethers");
const { getL2Provider, getL1Provider, getL1Wallet, getL2Wallet, L1_CHAIN_ID, L2_CHAIN_ID } = require('./utils/providers');

const { CrossChainMessenger } = require("@eth-optimism/sdk");

async function withdrawEth() {
  const l1Wallet = getL1Wallet();
  const l2Wallet = getL2Wallet();

  const crossChainMessenger = new CrossChainMessenger({
    l1ChainId: L1_CHAIN_ID,
    l2ChainId: L2_CHAIN_ID,
    l1SignerOrProvider: l1Wallet,
    l2SignerOrProvider: l2Wallet,
  });

  const amountToWithdraw = ethers.parseEther("0.005"); // 0.005 ETH

  console.log(`Initiating withdrawal of ${ethers.formatEther(amountToWithdraw)} ETH from L2 to L1...`);
  const tx = await crossChainMessenger.withdrawETH(amountToWithdraw);
  console.log(`L2 Withdrawal TX hash: ${tx.hash}`);

  await tx.wait(); // Wait for the L2 transaction to be mined

  console.log("L2 withdrawal initiated. Waiting for challenge period to pass and then finalizing on L1...");

  // This step waits for the challenge period to expire and for the message to be ready for finalization.
  // On mainnet, this is 7 days. On testnets, it's often a few minutes.
  await crossChainMessenger.waitForMessageStatus(tx.hash, await crossChainMessenger.getMessageStatus(tx.hash));

  // Now, finalize the withdrawal on L1
  console.log("Finalizing withdrawal on L1...");
  const finalizeTx = await crossChainMessenger.finalizeMessage(tx);
  console.log(`L1 Finalization TX hash: ${finalizeTx.hash}`);

  await finalizeTx.wait();
  console.log("ETH withdrawn to L1 successfully!");
}

withdrawEth().catch(console.error);
```

### 4. Estimating Gas and L1 Data Fees

Optimism transactions have two main gas components: L2 execution gas and L1 data gas. You can estimate total gas costs using the `optimism-ethers` or `viem` libraries.

```javascript
// gasEstimation.js (Using @eth-optimism/sdk and ethers.js)
const { ethers } = require("ethers");
const { getL2Provider, getL2Wallet } = require('./utils/providers'); // Assume defined

async function estimateGasCost() {
  const l2Provider = getL2Provider();
  const l2Wallet = getL2Wallet();

  const toAddress = "0x...some_recipient_address..."; // Replace with a real address
  const amountToSend = ethers.parseEther("0.0001");

  const tx = {
    to: toAddress,
    value: amountToSend,
    data: "0x", // For a simple ETH transfer
  };

  try {
    // Estimate L2 execution gas
    const l2GasEstimate = await l2Provider.estimateGas(tx);
    console.log(`L2 Execution Gas Estimate: ${l2GasEstimate.toString()} units`);

    // Get current L2 gas price
    const l2GasPrice = await l2Provider.getGasPrice();
    console.log(`L2 Gas Price: ${ethers.formatUnits(l2GasPrice, "gwei")} gwei`);

    // Calculate L2 execution cost
    const l2ExecutionCost = l2GasEstimate * l2GasPrice;
    console.log(`L2 Execution Cost: ${ethers.formatEther(l2ExecutionCost)} ETH`);

    // Estimate L1 data cost (using the Optimism SDK's provider extension)
    // Note: This requires an Optimism-aware provider, which `ethers-optimism` provides
    // If you're using a standard ethers.js provider, you might need to manually call a specific RPC method or use cross-chain messenger to simulate
    const opStackProvider = new ethers.OptimismProvider(l2Provider.connection.url); // Wrap for Optimism specific methods
    const l1GasFee = await opStackProvider.get  GasCost(tx); // Or getL1Fee(tx.data)
    console.log(`L1 Data Fee Estimate: ${ethers.formatEther(l1GasFee)} ETH`);

    const totalCost = l2ExecutionCost + l1GasFee;
    console.log(`Total Estimated Transaction Cost: ${ethers.formatEther(totalCost)} ETH`);

  } catch (error) {
    console.error("Error estimating gas:", error);
  }
}

estimateGasCost().catch(console.error);
```

## Best Practices

*   **Prioritize L1 Data Efficiency**: The largest variable cost on Optimism is the L1 data fee. Design your contracts to minimize calldata and storage writes, as these are compressed and posted to L1. Avoid storing large data blobs directly on-chain if possible.
*   **Use Standard Tooling**: Leverage Hardhat, Foundry, Ethers.js, and Viem. They integrate seamlessly with Optimism, requiring only network configuration.
*   **Test Bridging Thoroughly**: Cross-chain messaging is critical. Always test deposits and withdrawals extensively on testnets to understand the multi-step process and challenge periods.
*   **Monitor L1 Congestion**: L1 data fees are dynamic and tied to Ethereum Mainnet's gas prices. Keep an eye on L1 congestion, as it directly impacts your L2 transaction costs.
*   **Consider Upgradeable Contracts**: For critical dApps, deploy upgradeable contracts using OpenZeppelin UUPS or Transparent Proxy patterns. This allows you to fix bugs or add features without redeploying and migrating state, which is particularly valuable on an L2.
*   **Batch Transactions**: For operations involving multiple contract calls from the same EOA, consider batching them into a single transaction if logic allows. This amortizes the L1 data fee over several L2 operations.
*   **Use a Reliable RPC Provider**: For production dApps, use dedicated RPC services like Alchemy, Infura, or Blast for stable and fast access to Optimism nodes.

## Anti-Patterns

*   **Ignoring the Challenge Period.** Expecting L2-to-L1 withdrawals to be instant. You *must* wait for the fraud proof window
