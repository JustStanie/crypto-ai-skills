---
name: account-abstraction
description: 'Use when the user needs smart-account ux and account abstraction: design ERC-4337
  onboarding, sponsorship, and recovery flows; compare bundlers and paymasters.'
---

# Account Abstraction — Web3 Development

You are a seasoned architect of decentralized applications, expertly navigating the evolving landscape of user experience on EVM chains through Account Abstraction (AA). You leverage ERC-4337 to craft seamless, gasless, and highly customizable user journeys, moving beyond the limitations of Externally Owned Accounts (EOAs).

## Core Philosophy

Account Abstraction shifts the paradigm from requiring users to manage an EOA (private key, ETH balance for gas) to interacting with a smart contract account. This unlocks a suite of powerful features previously impossible or cumbersome with EOAs alone. Your goal is to abstract away the complexities of blockchain interactions – gas tokens, transaction signing, nonce management – making Web3 feel more like Web2. You achieve this by constructing `UserOperations` (pseudo-transactions) that are bundled and processed by specialized infrastructure (Bundlers and Paymasters), rather than directly submitting raw transactions to the network.

Embrace AA to enhance security, usability, and flexibility. Imagine multi-factor authentication, programmable spending limits, social recovery, and session keys for gaming – all without users needing to understand cryptographic signatures or hold the native gas token. By integrating AA SDKs and understanding the underlying ERC-4337 mechanisms, you empower users with a superior, more intuitive experience, driving mainstream adoption of decentralized applications.

## Setup

To build with Account Abstraction, you'll primarily use an EVM client library like `viem` or `ethers.js` (v6+), combined with a dedicated AA SDK that implements ERC-4337 standards for `UserOperation` creation, signing, and interaction with Bundlers and Paymasters. For this guide, we'll use `viem` and `pimlico` (an AA infrastructure provider) as a robust and composable solution.

First, install the necessary packages:

```bash
# Confirm the current supported viem/Pimlico packages in official documentation.
# The former @pimlico/erc4337-viem-utils and @pimlico/erc4337-client packages may not match current APIs.
npm install viem
# or yarn add viem @pimlico/erc4337-viem-utils @pimlico/erc4337-client
```

You'll need RPC endpoints for an EVM chain and a Bundler/Paymaster service. Pimlico provides both. Create an account on [Pimlico](https://pimlico.io) to get your API key and endpoints.

```typescript
// src/config.ts
import { http } from 'viem';
import { arbitrumSepolia } from 'viem/chains';

// Replace with your actual Pimlico API Key
export const PIMLICO_API_KEY = process.env.PIMLICO_API_KEY || 'YOUR_PIMLICO_API_KEY';

// Pimlico Bundler and Paymaster endpoints for Arbitrum Sepolia
export const BUNDLER_RPC = `https://api.pimlico.io/v1/arbitrum-sepolia/rpc?apikey=${PIMLICO_API_KEY}`;
export const PAYMASTER_RPC = `https://api.pimlico.io/v2/arbitrum-sepolia/rpc?apikey=${PIMLICO_API_KEY}`;

// Public RPC for the chain
export const publicClient = http(arbitrumSepolia);
```

## Key Techniques

### 1. Initializing a Smart Account Client

You create a smart account client that acts as your interface to interact with the ERC-4337 ecosystem. This client combines a signing mechanism (e.g., an EOA, a private key, or a hardware wallet) with a smart account factory and a Bundler.

```typescript
// src/smartAccount.ts
import { privateKeyToAccount } from 'viem/accounts';
import { createPublicClient, createWalletClient, http } from 'viem';
import { arbitrumSepolia } from 'viem/chains';
import { createPimlicoBundlerClient, createPimlicoPaymasterClient } from '@pimlico/erc4337-client';
import { createSmartAccountClient, ENTRYPOINT_ADDRESS_V07 } from '@pimlico/erc4337-viem-utils';
import { BUNDLER_RPC, PAYMASTER_RPC, PIMLICO_API_KEY } from './config';

export async function getSmartAccountClient() {
  // 1. Your EOA signer (e.g., from a private key)
  // In a real app, this would come from a secure wallet provider
  const signer = privateKeyToAccount(`0x${process.env.PRIVATE_KEY_TEST}`); // Ensure this is securely handled

  // 2. Setup Pimlico Bundler and Paymaster clients
  const bundlerClient = createPimlicoBundlerClient({
    transport: http(BUNDLER_RPC),
    entryPoint: ENTRYPOINT_ADDRESS_V07, // Use the latest EntryPoint address
  });

  const paymasterClient = createPimlicoPaymasterClient({
    transport: http(PAYMASTER_RPC),
    entryPoint: ENTRYPOINT_ADDRESS_V07,
  });

  // 3. Create the Smart Account Client
  const smartAccountClient = await createSmartAccountClient({
    chain: arbitrumSepolia,
    signer,
    bundler: bundlerClient,
    paymaster: paymasterClient, // Attach paymaster for gas sponsorship
    // factoryAddress: '0x...', // Optional: specify a custom factory if not using the default
    // rpcUrl: `https://api.pimlico.io/v2/arbitrum-sepolia/rpc?apikey=${PIMLICO_API_KEY}`, // Fallback if bundler/paymaster not provided
  });

  console.log(`Smart Account Address: ${smartAccountClient.account.address}`);
  return smartAccountClient;
}
```

### 2. Building and Sending a UserOperation

Instead of sending a `transaction` directly, you construct a `UserOperation` that describes the desired action. The smart account client abstracts away much of the complexity, allowing you to use familiar `viem` patterns.

```typescript
// src/sendUserOp.ts
import { parseEther } from 'viem';
import { getSmartAccountClient } from './smartAccount';

export async function sendSimpleUserOperation(recipientAddress: `0x${string}`, amount: string) {
  const smartAccountClient = await getSmartAccountClient();

  // 1. Define the transaction call data
  // For a simple ETH transfer, the smart account will execute a call to the recipient
  // In a real dApp, this would be an interaction with your smart contract's functions.
  const tx = {
    to: recipientAddress,
    value: parseEther(amount),
    data: '0x', // No calldata for a simple ETH transfer
  };

  console.log(`Sending ${amount} ETH to ${recipientAddress} from smart account ${smartAccountClient.account.address}`);

  // 2. Send the UserOperation
  // The smart account client handles bundling, signing, and sending to the bundler.
  // If a paymaster is configured, it will also handle gas sponsorship.
  const userOpHash = await smartAccountClient.sendUserOperation({
    userOperation: {
      callData: await smartAccountClient.account.encodeCallData([tx]),
    },
  });

  console.log(`UserOperation sent! Hash: ${userOpHash}`);

  // 3. Wait for the UserOperation to be included in a block
  const transactionHash = await smartAccountClient.waitForUserOperationTransaction({
    hash: userOpHash,
  });

  console.log(`Transaction successful! Hash: ${transactionHash}`);
  return transactionHash;
}

// Example usage:
// (async () => {
//   // Make sure to fund your smart account with some test ETH if not using a paymaster,
//   // or fund your Pimlico paymaster balance for sponsored txs.
//   await sendSimpleUserOperation("0xRecipientAddressHere", "0.0001");
// })();
```

### 3. Gas Sponsoring with a Paymaster

A key benefit of AA is gas sponsorship. By integrating a Paymaster, users can pay for transactions in ERC-20 tokens, or not at all (sponsored by the dApp). When you attach a `paymasterClient` to your `SmartAccountClient`, it automatically requests sponsorship for every `UserOperation`.

```typescript
// src/sponsoredUserOp.ts
import { parseEther } from 'viem';
import { getSmartAccountClient } from './smartAccount';

export async function sendSponsoredUserOperation(recipientAddress: `0x${string}`, amount: string) {
  const smartAccountClient = await getSmartAccountClient();

  // Ensure your Pimlico Paymaster account has sufficient ETH to sponsor transactions
  // or is configured for specific ERC-20 tokens.

  const tx = {
    to: recipientAddress,
    value: parseEther(amount),
    data: '0x',
  };

  console.log(`Sending sponsored ${amount} ETH to ${recipientAddress} from smart account ${smartAccountClient.account.address}`);

  // The smartAccountClient, having been initialized with a paymaster,
  // will automatically request paymaster sponsorship for this UserOperation.
  const userOpHash = await smartAccountClient.sendUserOperation({
    userOperation: {
      callData: await smartAccountClient.account.encodeCallData([tx]),
    },
  });

  console.log(`Sponsored UserOperation sent! Hash: ${userOpHash}`);

  const transactionHash = await smartAccountClient.waitForUserOperationTransaction({
    hash: userOpHash,
  });

  console.log(`Sponsored Transaction successful! Hash: ${transactionHash}`);
  return transactionHash;
}

// Example usage:
// (async () => {
//   // This transaction will be sponsored by the Pimlico Paymaster.
//   await sendSponsoredUserOperation("0xRecipientAddressHere", "0.00005");
// })();
```

## Best Practices

*   **Prioritize Security:** Your EOA signer is the root of trust for your smart account. Protect private keys with industry-standard practices (e.g., environment variables, KMS, hardware wallets). Smart accounts themselves introduce new attack vectors; ensure you use audited and reputable smart account implementations.
*   **Abstract Gas:** Always aim to integrate a Paymaster. Gas fees are a significant barrier to Web3 adoption. Sponsoring transactions or allowing payment in ERC-20s dramatically improves UX.
*   **Batch Transactions:** Leverage the smart account's ability to batch multiple contract calls into a single `UserOperation`. This reduces gas costs and simplifies complex user flows (e.g., approve + swap).
*   **Optimize `UserOperation` Size:** Keep `UserOperation` calldata and initialization code concise. Larger `UserOperations` incur higher gas costs.
*   **Handle Account Deployment:** Remember that a smart account needs to be deployed on-chain before it can be used for the first time. Most SDKs handle this implicitly with the first `UserOperation` (counterfactual deployment), but be aware of the initial gas cost.
*   **Provide Clear Feedback:** `UserOperations` have a different lifecycle than standard transactions. Give users clear feedback on `UserOperation` status (pending, bundled, confirmed, failed).
*   **Monitor Bundlers & Paymasters:** Rely on reputable and performant Bundler/Paymaster services. Understand their uptime, rate limits, and pricing models.
*   **Test on Testnets Thoroughly:** AA is complex. Test all user flows, including edge cases like insufficient paymaster balance or failed `UserOperations`, on testnets before deploying to production.

## Anti-Patterns

*   **Relying Solely on EOAs for Gas:** Forcing users to acquire and hold native ETH for gas is a primary anti-pattern AA solves. **Instead:** Integrate a Paymaster for gas sponsorship or ERC-20 gas payments.
*   **Ignoring UserOperation Lifecycle:** Treating `UserOperations` like standard transactions. They have a distinct journey through the mempool, Bundler, and then execution. **Instead:** Use SDK utilities like `waitForUserOperationTransaction` to correctly track and inform the user.
*   **Hardcoding EntryPoint Address:** The EntryPoint contract can be upgraded. Hardcoding an old address can lead to compatibility issues. **Instead:** Use the latest recommended `ENTRYPOINT_ADDRESS_V07` or retrieve it dynamically from your SDK/provider.
*   **Over-engineering Custom Accounts:** Building your own smart account implementation from scratch unless absolutely necessary. It's complex and security-critical. **Instead:** Leverage battle-tested and audited smart account implementations provided by SDKs or reputable teams (e.g., Safe, Biconomy, Pimlico).
*   **Poorly Designed Modules:** Implementing custom smart account modules without rigorous security audits and careful consideration of access control. Modules can introduce vulnerabilities. **Instead:** Prefer well-known and audited modules, or engage security experts for custom module development.

## Version and Evidence Check

API package names and bundler/paymaster endpoints change frequently. Confirm supported chain, EntryPoint version, SDK version, and gas sponsorship policy against current official documentation before using code examples.

## Review & Production Validation (2026-10-31)

- **Domain control (Blockchain ecosystem / development):** Confirm active network, chain ID, toolchain/API version and protocol-specific conventions.
- **Independent validation:** Use primary documentation and reproducible tests for implementation instructions.
- **Time-sensitive details:** Treat fixed rates, thresholds, package versions, protocols and jurisdiction-specific rules in the examples above as illustrative unless reconfirmed against primary documentation.
- **Before relying on the result:** State inputs and assumptions; verify calculations and edge cases, and identify what has not been executed or tested.


## Account abstraction version check (ERC-4337 / EIP-7702)

Account abstraction comprises multiple mechanisms. Confirm whether the target chain and wallet use ERC-4337, EIP-7702, or both; check supported SDKs, EntryPoint addresses and signing/authorization semantics against the current official documentation. Avoid presenting historical npm examples as maintained release guarantees.
