---
name: avalanche-development
description: 'Use when the user needs avalanche development and subnets: compare Avalanche
  deployment options, EVM tooling and custom-chain trade-offs.'
---

# Avalanche development and subnets

You are a battle-hardened Avalanche developer, deeply familiar with its unique architecture, high-throughput EVM, and the power of its custom Subnets. You build resilient, scalable dApps that leverage Avalanche's speed and flexibility, navigating its C-Chain, X-Chain, and P-Chain with expert precision.

## Core Philosophy

Avalanche distinguishes itself with a unique architecture designed for scalability, security, and decentralization. Its primary innovation lies in the platform's ability to host multiple custom blockchains called "Subnets," each with its own virtual machine, rules, and tokenomics, secured by a dynamic set of validators. The foundational Avalanche network comprises three built-in blockchains: the C-Chain (EVM-compatible for smart contracts), the X-Chain (for asset creation and trading), and the P-Chain (for staking, Subnet creation, and validator coordination).

When building on Avalanche, your fundamental approach should embrace this multi-chain paradigm. For most dApps, you'll primarily interact with the C-Chain, leveraging familiar EVM tooling like Hardhat or Foundry. However, for advanced use cases involving custom token creation, peer-to-peer asset transfers, or specialized application environments, you'll need to understand and utilize the X-Chain, P-Chain, or even create your own Subnet. The goal is to maximize throughput and customization by choosing the right chain for the right task, ensuring seamless user experiences even across the distinct chains within the Avalanche ecosystem.

## Setup

To begin developing on Avalanche, you'll primarily use familiar EVM development tools for the C-Chain and the Avalanche SDKs for broader platform interactions.

1.  **Node.js & npm/yarn:** Essential for most JavaScript-based tooling.
    ```bash
    # Verify Node.js
    node -v
    npm -v
    ```

2.  **Hardhat or Foundry (for C-Chain Smart Contracts):**
    Choose your preferred EVM development environment.
    ```bash
    # Hardhat setup
    npm install --save-dev hardhat
    npx hardhat init # Choose 'Create a basic sample project'

    # Foundry setup (if preferred)
    curl -L https://foundry.paradigm.xyz | bash
    foundryup
    forge init my-foundry-project
    ```

3.  **Avalanche.js SDK:** For interacting with X, P, and C-Chains programmatically.
    ```bash
    npm install avalanchejs
    ```

4.  **Configure RPC Endpoints:**
    For Hardhat/Foundry, configure your `hardhat.config.js` or `foundry.toml` to point to Avalanche C-Chain testnet (Fuji) or mainnet RPCs.
    ```javascript
    // hardhat.config.js example for Fuji Testnet
    require("@nomicfoundation/hardhat-toolbox");

    module.exports = {
      solidity: "0.8.19",
      networks: {
        fuji: {
          url: "https://api.avax-test.network/ext/bc/C/rpc",
          accounts: [process.env.PRIVATE_KEY], // Ensure PRIVATE_KEY is set in your .env file
          chainId: 43113,
        },
        mainnet: {
          url: "https://api.avax.network/ext/bc/C/rpc",
          accounts: [process.env.PRIVATE_KEY],
          chainId: 43114,
        }
      },
    };
    ```

## Key Techniques

### 1. Deploying an EVM Smart Contract to Avalanche C-Chain

Leverage Hardhat or Foundry to deploy your Solidity contracts just like on Ethereum. The only difference is the network configuration.

```solidity
// contracts/MyToken.sol
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";

contract MyToken is ERC20 {
    constructor(uint256 initialSupply) ERC20("MyAvalancheToken", "MAT") {
        _mint(msg.sender, initialSupply);
    }
}
```

```javascript
// scripts/deploy.js (Hardhat)
const hre = require("hardhat");

async function main() {
  const [deployer] = await hre.ethers.getSigners();
  console.log("Deploying contracts with the account:", deployer.address);

  const initialSupply = hre.ethers.parseEther("1000000"); // 1 million tokens
  const MyToken = await hre.ethers.getContractFactory("MyToken");
  const myToken = await MyToken.deploy(initialSupply);

  await myToken.waitForDeployment();

  console.log("MyToken deployed to:", await myToken.getAddress());
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
```

To deploy on Fuji:
```bash
npx hardhat run scripts/deploy.js --network fuji
```

### 2. Interacting with C-Chain Smart Contracts via `ethers.js`

Once deployed, interact with your contract from a frontend or backend application using `ethers.js` (or `web3.js`), configuring it for Avalanche's C-Chain.

```javascript
// Example: Interact with MyToken contract on Fuji
const { ethers } = require("ethers");
require('dotenv').config();

async function interactWithToken() {
  const rpcUrl = "https://api.avax-test.network/ext/bc/C/rpc";
  const provider = new ethers.JsonRpcProvider(rpcUrl);
  const wallet = new ethers.Wallet(process.env.PRIVATE_KEY, provider);

  const contractAddress = "0xYourDeployedMyTokenAddress"; // Replace with your deployed contract address
  const abi = [ // Minimal ABI for transfer and balanceOf
    "function name() view returns (string)",
    "function symbol() view returns (string)",
    "function balanceOf(address account) view returns (uint256)",
    "function transfer(address recipient, uint256 amount) returns (bool)"
  ];
  const tokenContract = new ethers.Contract(contractAddress, abi, wallet);

  console.log("Token Name:", await tokenContract.name());
  console.log("Token Symbol:", await tokenContract.symbol());

  const recipientAddress = "0xAnotherAddressHere"; // Replace with recipient address
  const amountToSend = ethers.parseEther("10"); // Send 10 tokens

  console.log(`Sending ${amountToSend} tokens to ${recipientAddress}...`);
  const tx = await tokenContract.transfer(recipientAddress, amountToSend);
  await tx.wait();
  console.log("Transaction successful:", tx.hash);

  const deployerBalance = await tokenContract.balanceOf(wallet.address);
  console.log("Deployer balance after transfer:", ethers.formatEther(deployerBalance));
}

interactWithToken().catch(console.error);
```

### 3. Performing Cross-Chain Asset Transfers (C-Chain to X-Chain)

Avalanche's `avalanchejs` SDK is crucial for handling transfers between its native chains. This example shows moving AVAX from the C-Chain to the X-Chain.

```javascript
const { Avalanche, BinTools, BN, Buffer } = require('avalanche');
require('dotenv').config();

const networkID = 43113; // Fuji Testnet
const AVAX_ASSET_ID = "FvwYkXthgZAKfWPpVEGqJrfw4FqEwJd2t7JvRk45KgpvE4Dk5"; // AVAX asset ID on Fuji

async function cToXTransfer() {
  const avalanche = new Avalanche("api.avax-test.network", 443, "https", networkID);
  const cchain = avalanche.CChain();
  const xchain = avalanche.XChain();
  const bintools = BinTools.getInstance();

  const privateKey = process.env.PRIVATE_KEY; // C-chain private key (0x prefix)
  const cchainWallet = cchain.newKeypair();
  cchainWallet.importKey(privateKey);
  const cchainAddress = cchainWallet.getAddressString();

  const xchainWallet = xchain.newKeypair();
  xchainWallet.importKey(privateKey); // Use the same private key for simplicity, though separate keys are common
  const xchainAddress = xchainWallet.getAddressString();

  console.log(`C-Chain Address: ${cchainAddress}`);
  console.log(`X-Chain Address: ${xchainAddress}`);

  const amountToSend = new BN(1000000000); // 1 AVAX (10^9 nanoAVAX)

  // 1. Get C-chain balance
  const cChainBalance = await cchain.getBalance(cchainAddress);
  console.log(`C-Chain AVAX Balance: ${cChainBalance.balance / Math.pow(10, 9)} AVAX`);

  // 2. Export AVAX from C-Chain to X-Chain
  console.log(`Exporting ${amountToSend.div(new BN(Math.pow(10,9)))} AVAX from C-Chain to X-Chain...`);
  const exportTxId = await cchain.exportAVAX(
    amountToSend,
    xchainAddress,
    cchainAddress,
    cchainWallet
  );
  console.log(`C-Chain Export Tx ID: ${exportTxId}`);
  await cchain.get
  // Wait for the C-chain transaction to be finalized
  // In a real app, you'd poll for transaction receipt
  await new Promise(resolve => setTimeout(resolve, 5000)); // Simulate wait

  // 3. Get UTXOs on X-Chain for the import
  const utxos = await xchain.getUTXOs(xchainAddress);
  const assetID = bintools.cb58Decode(AVAX_ASSET_ID);

  // 4. Import AVAX from C-Chain into X-Chain
  console.log(`Importing AVAX to X-Chain...`);
  const importTxId = await xchain.importAVAX(
    utxos,
    xchainAddress,
    xchainAddress,
    [xchainWallet],
    assetID
  );
  console.log(`X-Chain Import Tx ID: ${importTxId}`);
  await new Promise(resolve => setTimeout(resolve, 5000)); // Simulate wait

  // 5. Verify X-Chain balance
  const xChainBalance = await xchain.getBalance(xchainAddress, AVAX_ASSET_ID);
  console.log(`X-Chain AVAX Balance: ${xChainBalance.balance / Math.pow(10, 9)} AVAX`);
}

cToXTransfer().catch(console.error);
```

## Best Practices

*   **Understand the Three Chains:** Always know whether you're targeting the C-Chain (EVM), X-Chain (asset transfers), or P-Chain (staking/Subnets). Each has distinct APIs and use cases.
*   **Utilize the Fuji Testnet:** Before deploying to mainnet, thoroughly test your dApps on the Fuji testnet. It accurately mirrors mainnet behavior.
*   **Optimize C-Chain Gas:** While Avalanche has high throughput, gas optimization for your smart contracts remains crucial for cost-efficiency, especially for complex operations.
*   **Secure Private Keys:** Never expose private keys directly in your code. Use environment variables, KMS solutions, or hardware wallets.
*   **Handle Cross-Chain Transfers Carefully:** Cross-chain operations require multiple transactions and careful state management. Provide clear UI feedback and robust error handling for users.
*   **Choose Reliable RPC Providers:** For production dApps, rely on dedicated RPC providers (like Ankr, QuickNode, Chainstack) rather than public Avalanche Foundation endpoints for better stability and rate limits.
*   **Leverage Subnets for Specific Needs:** If your application requires custom gas fees, specific validators, or a custom VM, consider deploying a dedicated Subnet for unparalleled control and scalability.

## Anti-Patterns

**Ignoring Chain Context.** You try to send C-Chain transactions to an X-Chain endpoint or expect an ERC-20 token to exist on the P-Chain. Always ensure your SDK calls, contract deployments, and RPC connections are pointed to the correct Avalanche chain (C, X, or P) for the intended operation.

**Hardcoding Asset IDs.** You use a hardcoded Asset ID for AVAX or other tokens without considering that Asset IDs can differ between testnet and mainnet, or for custom tokens. Always fetch Asset IDs dynamically or use configuration files that are environment-aware.

**Inefficient Cross-Chain Logic.** You design a dApp that requires users to perform frequent, manual C-Chain to X-Chain (or vice-versa) transfers for basic operations. This creates a clunky user experience; instead, design your dApp to minimize these interactions or abstract them away where possible.

**Underestimating Subnet Complexity.** You decide to launch a custom Subnet without fully understanding the operational overhead, validator economics, or security implications. Subnets offer immense power but require careful planning, resource allocation, and ongoing maintenance to be successful.

**Blindly Trusting Public RPCs for Production.** You deploy a dApp relying solely on the public Avalanche Foundation RPC endpoints for all production traffic. These endpoints are rate-limited and not designed for high-traffic production use cases; always integrate with a dedicated, enterprise-grade RPC provider for reliability.
