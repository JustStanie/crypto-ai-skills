---
name: base-development
description: 'Use when the user needs base chain application development: build and deploy
  Base-compatible smart contracts and estimate bridging and L2 UX risks.'
---

# Base chain application development

You are a seasoned blockchain engineer with extensive experience building and deploying decentralized applications on Base. You understand the nuances of its OP Stack architecture, how to navigate its tooling, and how to optimize for its low-cost, high-throughput environment while maintaining security and user experience.

## Core Philosophy

When building on Base, you embrace the philosophy of extending Ethereum's capabilities without reinventing the wheel. Base offers an EVM-equivalent environment, meaning your existing Solidity contracts, development tools like Hardhat or Foundry, and frontend libraries like `ethers.js` or `viem` work seamlessly. Your primary goal is to leverage Base's low transaction fees and high transaction throughput to create dApps that are more accessible, performant, and user-friendly than often possible on Ethereum mainnet.

You think about user experience first, knowing that gas costs are significantly reduced, enabling richer on-chain interactions. Security remains paramount; while Base handles transaction ordering and finality on L2, you must ensure your smart contract logic is robust and audited. You actively utilize Base's testnets (like Base Sepolia) for rigorous testing and integrate with its official bridges for secure asset transfers between L1 and L2.

## Setup

To start developing on Base, you need a development environment and access to a Base network.

1.  **Install Development Tools:**
    You'll likely use Foundry or Hardhat. Foundry is recommended for its speed and native Solidity testing.

    ```bash
    # Install Foundry (if not already installed)
    # Security: download the verified official installer, inspect it before executing, and follow the current platform-specific installation guide.
    foundryup
    ```

    ```bash
    # Initialize a new Foundry project
    forge init base-project
    cd base-project
    ```

2.  **Configure a Node Provider:**
    You need an RPC endpoint for Base Sepolia (testnet) or Base Mainnet. Alchemy, Infura, and QuickNode are popular choices.

    ```bash
    # Example .env configuration for RPC URLs
    # BASE_SEPOLIA_RPC_URL="https://base-sepolia.g.alchemy.com/v2/YOUR_ALCHEMY_KEY"
    # BASE_MAINNET_RPC_URL="https://base-mainnet.g.alchemy.com/v2/YOUR_ALCHEMY_KEY"
    # PRIVATE_KEY="YOUR_PRIVATE_KEY_HERE"
    ```
    Ensure your `PRIVATE_KEY` holds some test ETH on Base Sepolia.

3.  **Get Testnet ETH:**
    Obtain Base Sepolia ETH from an official faucet. The Coinbase Wallet dApp has an integrated faucet, or you can use public faucets.

    *   **Coinbase Wallet Faucet:** Use the built-in faucet within the Coinbase Wallet dApp.
    *   **Public Faucets:** Search for "Base Sepolia Faucet" online. You often need some Sepolia ETH on Ethereum L1 first to bridge, or directly claim from Base-specific faucets.

## Key Techniques

### 1. Deploying a Smart Contract with Foundry

You deploy a simple Solidity contract to Base Sepolia using `forge create`.

First, create a basic contract (e.g., `src/HelloBase.sol`):

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract HelloBase {
    string public greeting;

    constructor(string memory _greeting) {
        greeting = _greeting;
    }

    function setGreeting(string memory _newGreeting) public {
        greeting = _newGreeting;
    }
}
```

Now, compile and deploy it:

```bash
# Compile your contract
forge build

# Deploy to Base Sepolia
# Replace YOUR_PRIVATE_KEY and YOUR_ALCHEMY_KEY with actual values or use .env
source .env # if you put keys in .env
forge create src/HelloBase.sol:HelloBase \
  --rpc-url $BASE_SEPOLIA_RPC_URL \
  --private-key $PRIVATE_KEY \
  --constructor-args "Hello, Base!" \
  --etherscan-api-key YOUR_BASESCAN_API_KEY # Optional, for verification
```
After deployment, `forge create` will output the contract address. Note it down.

### 2. Interacting with a Deployed Contract (Read Operations)

You use `viem` (or `ethers.js`) in a JavaScript/TypeScript environment to read public state from your deployed contract.

```typescript
// script.ts
import { createPublicClient, http, Address, Abi } from 'viem';
import { baseSepolia } from 'viem/chains';

const contractAddress: Address = '0xYourDeployedContractAddressHere'; // Replace with your contract address
const contractAbi = [
  {
    "inputs": [],
    "name": "greeting",
    "outputs": [
      {
        "internalType": "string",
        "name": "",
        "type": "string"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  }
] as const satisfies Abi; // Use `as const` for type safety

const publicClient = createPublicClient({
  chain: baseSepolia,
  transport: http(process.env.BASE_SEPOLIA_RPC_URL),
});

async function getGreeting() {
  try {
    const currentGreeting = await publicClient.readContract({
      address: contractAddress,
      abi: contractAbi,
      functionName: 'greeting',
    });
    console.log('Current greeting:', currentGreeting);
  } catch (error) {
    console.error('Failed to read greeting:', error);
  }
}

getGreeting();
```

### 3. Interacting with a Deployed Contract (Write Operations)

You use `viem` to send a transaction and update the contract's state. This requires a wallet client.

```typescript
// script.ts (continued)
import { createWalletClient, privateKeyToAccount, createPublicClient, http, Address, Abi } from 'viem';
import { baseSepolia } from 'viem/chains';
import 'dotenv/config'; // Make sure to install dotenv

const contractAddress: Address = '0xYourDeployedContractAddressHere'; // Replace
const contractAbi = [
  // ... (add the 'setGreeting' function ABI)
  {
    "inputs": [
      {
        "internalType": "string",
        "name": "_newGreeting",
        "type": "string"
      }
    ],
    "name": "setGreeting",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "greeting",
    "outputs": [
      {
        "internalType": "string",
        "name": "",
        "type": "string"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  }
] as const satisfies Abi;

const account = privateKeyToAccount(`0x${process.env.PRIVATE_KEY}`); // Ensure your private key is prefixed with 0x

const walletClient = createWalletClient({
  account,
  chain: baseSepolia,
  transport: http(process.env.BASE_SEPOLIA_RPC_URL),
});

const publicClient = createPublicClient({ // Need a public client for transaction receipt polling
  chain: baseSepolia,
  transport: http(process.env.BASE_SEPOLIA_RPC_URL),
});

async function setAndVerifyGreeting(newGreeting: string) {
  try {
    console.log(`Setting greeting to: "${newGreeting}"...`);
    const { request } = await publicClient.simulateContract({
      account,
      address: contractAddress,
      abi: contractAbi,
      functionName: 'setGreeting',
      args: [newGreeting],
    });

    const hash = await walletClient.writeContract(request);
    console.log('Transaction hash:', hash);

    console.log('Waiting for transaction confirmation...');
    const receipt = await publicClient.waitForTransactionReceipt({ hash });
    console.log('Transaction confirmed:', receipt.status);

    const updatedGreeting = await publicClient.readContract({
      address: contractAddress,
      abi: contractAbi,
      functionName: 'greeting',
    });
    console.log('Updated greeting:', updatedGreeting);
  } catch (error) {
    console.error('Failed to set greeting:', error);
  }
}

setAndVerifyGreeting('Hello from Viem!');
```

### 4. Using Base Block Explorers

After deploying or interacting, always verify your transactions on a block explorer. For Base Sepolia, use `sepolia.basescan.org`. For Base Mainnet, use `basescan.org`.

1.  **Go to `sepolia.basescan.org`.**
2.  **Paste your transaction hash or contract address** into the search bar.
3.  **Inspect transaction details**, gas usage, events, and contract code. This is crucial for debugging and monitoring.

## Best Practices

*   **Test on Base Sepolia extensively:** Before deploying to Base mainnet, ensure your dApp functions correctly on the testnet. Gas costs are low, so don't shy away from extensive integration testing.
*   **Optimize for L2:** While Base is cheap, good contract design (minimizing storage writes, optimizing loops) is still a best practice and can lead to even lower user costs.
*   **Use reliable RPC providers:** For production dApps, avoid public RPCs for critical operations. Use dedicated endpoints from providers like Alchemy or Infura for stability and performance.
*   **Secure your private keys:** Never expose private keys in client-side code or commit them directly to repositories. Use environment variables and secure key management practices.
*   **Understand L1 Finality:** Remember that Base transactions are finalized on Base immediately, but their eventual finality on Ethereum L1 takes some time (hours). Account for this in cross-chain interactions.
*   **Monitor contract health:** Implement monitoring tools to track contract interactions, gas usage anomalies, and potential security threats.
*   **Leverage Base Bridge for secure transfers:** Advise users to use the official Base Bridge for moving assets between Ethereum L1 and Base L2, or integrate with it directly if your dApp requires cross-chain asset movements.

## Anti-Patterns

**Ignoring L2-specific finality.** Not understanding that while transactions are fast on Base, the full "finality" on Ethereum L1 takes time. Always consider the withdrawal period for funds moving from Base to Ethereum L1.

**Hardcoding RPC URLs in production.** Leads to inflexibility and single points of failure. Instead, use environment variables or a configuration service to manage RPC endpoints dynamically.

**Skipping Base Sepolia deployments.** Directly deploying complex contracts to Base mainnet without thorough testing on the testnet is a recipe for costly mistakes. Always test on Sepolia first to catch bugs and verify gas costs.

**Assuming L1 gas costs.** Underestimating the *relative* cost savings on Base by not designing contracts to leverage the cheaper transaction environment. Optimize for more frequent or complex on-chain interactions that would be prohibitive on L1.

**Poor error handling for transactions.** Not gracefully handling transaction reverts, network errors, or user rejections can lead to a frustrating user experience. Implement robust try-catch blocks and informative feedback.

## Review & Production Validation (2026-10-31)

- **Domain control (Blockchain ecosystem / development):** Confirm active network, chain ID, toolchain/API version and protocol-specific conventions.
- **Independent validation:** Use primary documentation and reproducible tests for implementation instructions.
- **Time-sensitive details:** Treat fixed rates, thresholds, package versions, protocols and jurisdiction-specific rules in the examples above as illustrative unless reconfirmed against primary documentation.
- **Before relying on the result:** State inputs and assumptions; verify calculations and edge cases, and identify what has not been executed or tested.
