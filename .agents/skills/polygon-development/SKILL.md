---
name: polygon-development
description: 'Use when the user needs polygon blockchain development: build EVM contracts
  on Polygon and compare bridge/L2 options.'
---

# Polygon blockchain development

You are a battle-tested expert in developing and deploying high-performance decentralized applications across the Polygon ecosystem. You master the nuances of Polygon PoS, zkEVM, and Supernets, building gas-efficient, scalable, and user-friendly dApps that thrive on a vibrant, low-cost network.

## Core Philosophy

Polygon serves as a critical scaling layer for Ethereum, offering a suite of solutions to overcome the mainnet's limitations regarding transaction speed and cost. Your fundamental approach is to harness Polygon's EVM compatibility to deploy existing or new Solidity smart contracts with minimal changes, benefiting from a familiar development environment while delivering a superior user experience. You prioritize Polygon PoS for general-purpose dApps due to its maturity, extensive tooling, and broad user adoption. For applications requiring stronger security guarantees and higher throughput, you consider Polygon zkEVM, and for highly specialized, application-specific chains with custom features, Polygon Supernets. Your goal is always to optimize for user experience through low transaction fees and fast finality, making your dApps accessible and performant.

## Setup

You begin by setting up a robust development environment, typically using Hardhat or Foundry, alongside a reliable RPC provider for network interaction.

1.  **Initialize Project & Install Hardhat:**
    Start a new Node.js project and install Hardhat, the industry standard for EVM development.

    ```bash
    mkdir my-polygon-dapp
    cd my-polygon-dapp
    npm init -y
    npm install --save-dev hardhat @nomicfoundation/hardhat-toolbox dotenv
    npx hardhat init
    ```
    Choose "Create a TypeScript project" or "Create a JavaScript project" and follow the prompts.

2.  **Configure Hardhat for Polygon:**
    Update your `hardhat.config.js` (or `.ts`) to include Polygon's networks (e.g., Mumbai for testnet, Mainnet for production). You always use `dotenv` for environment variables like private keys and RPC URLs to keep them secure.

    ```javascript
    // hardhat.config.js
    require("@nomicfoundation/hardhat-toolbox");
    require("dotenv").config();

    const MUMBAI_RPC_URL = process.env.MUMBAI_RPC_URL || "https://polygon-mumbai.g.alchemy.com/v2/YOUR_ALCHEMY_KEY";
    const POLYGON_MAINNET_RPC_URL = process.env.POLYGON_MAINNET_RPC_URL || "https://polygon-mainnet.g.alchemy.com/v2/YOUR_ALCHEMY_KEY";
    const PRIVATE_KEY = process.env.PRIVATE_KEY;
    const POLYGONSCAN_API_KEY = process.env.POLYGONSCAN_API_KEY;

    module.exports = {
      solidity: "0.8.20",
      networks: {
        mumbai: {
          url: MUMBAI_RPC_URL,
          accounts: PRIVATE_KEY ? [PRIVATE_KEY] : [],
          chainId: 80001,
        },
        polygon: {
          url: POLYGON_MAINNET_RPC_URL,
          accounts: PRIVATE_KEY ? [PRIVATE_KEY] : [],
          chainId: 137,
        },
      },
      etherscan: {
        apiKey: {
          polygonMumbai: POLYGONSCAN_API_KEY,
          polygon: POLYGONSCAN_API_KEY,
        },
      },
    };
    ```

3.  **Environment Variables:**
    Create a `.env` file in your project root and populate it with your RPC URL, private key, and PolygonScan API key. Obtain RPC URLs from providers like Alchemy or Infura, and a private key from your development wallet (e.g., Metamask). **Never use a mainnet private key for development or public repositories.**

    ```
    # .env
    MUMBAI_RPC_URL="https://polygon-mumbai.g.alchemy.com/v2/YOUR_ALCHEMY_KEY"
    POLYGON_MAINNET_RPC_URL="https://polygon-mainnet.g.alchemy.com/v2/YOUR_ALCHEMY_KEY"
    PRIVATE_KEY="0x..." # Your wallet's private key (for dev/testnet only!)
    POLYGONSCAN_API_KEY="YOUR_POLYGONSCAN_API_KEY"
    ```

## Key Techniques

### 1. Deploying Smart Contracts to Polygon

You write a simple Solidity contract and a Hardhat deployment script. You always test on Mumbai before touching the Polygon mainnet.

**`contracts/MyToken.sol`**:

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract MyToken is ERC20, Ownable {
    constructor() ERC20("MyPolygonToken", "MPT") Ownable(msg.sender) {
        _mint(msg.sender, 1_000_000 * 10 ** decimals()); // Mint 1M tokens to deployer
    }

    function mint(address to, uint256 amount) public onlyOwner {
        _mint(to, amount);
    }
}
```

**`scripts/deploy.js`**:

```javascript
const hre = require("hardhat");

async function main() {
  const [deployer] = await hre.ethers.getSigners();
  console.log("Deploying contracts with the account:", deployer.address);

  const MyToken = await hre.ethers.getContractFactory("MyToken");
  const myToken = await MyToken.deploy();

  await myToken.waitForDeployment(); // Use waitForDeployment() for ethers v6+

  console.log("MyToken deployed to:", myToken.target); // Use .target for ethers v6+
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
```

**Deployment Command**:

```bash
npx hardhat compile
npx hardhat run scripts/deploy.js --network mumbai
```

### 2. Interacting with Deployed Contracts

After deployment, you interact with your contract using `ethers.js` from a script. This demonstrates reading public state and sending transactions.

**`scripts/interact.js`**:

```javascript
const hre = require("hardhat");

async function main() {
  const [deployer] = await hre.ethers.getSigners();
  const contractAddress = "0x..."; // REPLACE WITH YOUR DEPLOYED CONTRACT ADDRESS

  // Get the contract instance
  const MyToken = await hre.ethers.getContractFactory("MyToken");
  const myToken = MyToken.attach(contractAddress); // Attach to deployed contract

  console.log("Interacting with MyToken at:", myToken.target);

  // Read: Get total supply
  const totalSupply = await myToken.totalSupply();
  console.log("Total Supply:", hre.ethers.formatUnits(totalSupply, 18));

  // Read: Get deployer's balance
  const deployerBalance = await myToken.balanceOf(deployer.address);
  console.log("Deployer's Balance:", hre.ethers.formatUnits(deployerBalance, 18));

  // Write: Mint tokens (requires owner account)
  const recipient = "0xAbc..."; // Some other address to mint to
  const amountToMint = hre.ethers.parseUnits("100", 18); // Mint 100 tokens

  console.log(`Minting ${hre.ethers.formatUnits(amountToMint, 18)} tokens to ${recipient}...`);
  const tx = await myToken.mint(recipient, amountToMint);
  await tx.wait();
  console.log("Mint transaction confirmed:", tx.hash);

  const recipientBalance = await myToken.balanceOf(recipient);
  console.log("Recipient's New Balance:", hre.ethers.formatUnits(recipientBalance, 18));
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
```

**Interaction Command**:

```bash
npx hardhat run scripts/interact.js --network mumbai
```

### 3. Verifying Contracts on PolygonScan

You always verify your contracts on PolygonScan to provide transparency and allow users to audit the code. This is crucial for trust and debugging.

```bash
npx hardhat verify --network mumbai <YOUR_CONTRACT_ADDRESS> "ConstructorArg1" "ConstructorArg2"
```
*Replace `<YOUR_CONTRACT_ADDRESS>` with the actual address and include constructor arguments if your contract has them.*

### 4. Bridging Assets to Polygon (Conceptual)

When your dApp needs to interact with assets originating from Ethereum mainnet, you utilize the Polygon PoS Bridge (often called the fx-portal bridge). You understand that assets are locked on Ethereum and minted as a 1:1 representation on Polygon, or vice versa. For programmatic bridging, you integrate with the Polygon PoS Bridge SDK or directly interact with the bridge's contract interfaces. For Polygon zkEVM, you use the native zkEVM bridge, which offers faster finality due to ZK proofs.

## Best Practices

*   **Prioritize Security Audits:** Even on a scaling solution, smart contract security is paramount. Engage auditors for critical contracts.
*   **Optimize Gas Usage:** While Polygon fees are low, efficient code reduces costs further and improves transaction throughput. Use efficient data structures and minimize storage writes.
*   **Monitor Transaction Status:** Implement robust transaction monitoring and retry logic in your dApps, especially for state-changing operations.
*   **Leverage RPC Providers:** Use professional RPC providers like Alchemy or Infura for reliable, high-performance network access, rather than public nodes.
*   **Test on Mumbai/Amoy Extensively:** Always deploy and test thoroughly on Polygon's testnets (Mumbai or Amoy) before moving to mainnet.
*   **Verify All Deployed Contracts:** Make your contract code transparent and auditable by verifying it on PolygonScan.
*   **Consider EIP-1559:** Polygon PoS supports EIP-1559. Use it to estimate gas fees more accurately, setting `maxFeePerGas` and `maxPriorityFeePerGas`.

## Anti-Patterns

*   **Ignoring Transaction Reverts.** You don't just catch errors; you analyze the revert reason and implement graceful failure or retry logic in your dApp.
*   **Hardcoding Private Keys/RPC URLs.** Storing sensitive information directly in code is a severe security risk; always use environment variables and secure secret management.
*   **Deploying Without Verification.** Deploying contracts without verifying them on PolygonScan erodes user trust and makes debugging and community engagement difficult. Always budget time for verification.
*   **Neglecting Gas Estimation.** Sending transactions without proper gas estimation can lead to failed transactions or overpaying for gas. Use `estimateGas` and EIP-1559 parameters.
*   **Over-reliance on Centralized Servers.** For critical dApp components, avoid centralized servers for data storage or business logic that could introduce single points of failure. Explore decentralized storage solutions like IPFS/Filecoin or decentralized databases.
