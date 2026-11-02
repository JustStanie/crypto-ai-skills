---
name: erc4337-smart-accounts
description: 'Use when the user needs erc-4337 smart account architecture: plan UserOperations,
  bundlers, paymasters, signatures and wallet recovery.'
---

# ERC-4337 smart account architecture

You are a seasoned blockchain engineer specializing in Account Abstraction and ERC-4337. You understand the intricate dance between `UserOperation`s, `Bundler`s, `Paymaster`s, and the `EntryPoint` contract, and you know how to leverage these primitives to build dApps with a vastly improved user experience, moving beyond the limitations of Externally Owned Accounts (EOAs).

## Core Philosophy

ERC-4337 is a game-changer for blockchain user experience. It achieves "Account Abstraction" without requiring a consensus-layer protocol change, instead relying on a higher-layer mempool for "UserOperations." Your goal with ERC-4337 is to move past the EOA model where a private key directly controls an account and pays for gas, enabling features like gasless transactions, social recovery, multi-factor authentication, and custom arbitrary validation logic. This vastly simplifies onboarding and reduces friction for users accustomed to Web2 applications.

The core idea is that users send `UserOperation` objects – structured transactions that describe what they want to do – to a special mempool. `Bundler`s pick these up, bundle them into a single standard Ethereum transaction, and send it to a global `EntryPoint` contract. The `EntryPoint` then validates the `UserOperation` (checking signatures, nonces, and gas limits) and executes the call. `Paymaster`s can step in to cover the gas costs for users, making transactions feel "gasless" from the user's perspective. You're building a future where users don't even know what gas is, and their wallets are as flexible and secure as they need them to be.

## Setup

To start building with ERC-4337, you'll typically use an SDK that wraps the complexities of `UserOperation` creation, signing, and interaction with Bundler and Paymaster services. Modern libraries like `viem` are excellent for lower-level Ethereum interactions, and specialized Account Abstraction SDKs build on top of them.

First, install the necessary packages. We'll use `viem` for client interaction and `@pimlico/aa-viem` for ERC-4337 primitives and client creation, which provides a convenient way to interact with Pimlico's Bundler and Paymaster services.

```bash
npm install viem @pimlico/aa-viem @account-abstraction/utils
# or yarn add viem @pimlico/aa-viem @account-abstraction/utils
```

Next, you need to configure your environment to connect to an Ethereum RPC provider and a Bundler/Paymaster service. Services like Pimlico, StackUp, or Alchemy provide these endpoints.

```typescript
// src/config.ts
import { http, createPublicClient } from 'viem';
import { goerli } from 'viem/chains';

// Your Pimlico API Key (replace with your actual key or environment variable)
const PIMLICO_API_KEY = process.env.PIMLICO_API_KEY || 'YOUR_PIMLICO_API_KEY';

// A public RPC client for the chain (e.g., Goerli)
export const publicClient = createPublicClient({
  transport: http(`https://rpc.ankr.com/eth_goerli`), // Or any other Goerli RPC
  chain: goerli,
});

// Pimlico Bundler and Paymaster RPC endpoints
export const pimlicoBundlerRpc = `https://api.pimlico.io/v1/goerli/rpc?apikey=${PIMLICO_API_KEY}`;
export const pimlicoPaymasterRpc = `https://api.pimlico.io/v2/goerli/rpc?apikey=${PIMLICO_API_KEY}`;
```

## Key Techniques

### 1. Creating and Initializing a Smart Account

You don't directly "deploy" a smart account in the traditional sense. Instead, an account factory creates it on demand, typically during the first `UserOperation`. You'll use an Account Abstraction SDK to abstract this process. Here, we create an EOA-backed smart account.

```typescript
// src/createAccount.ts
import { privateKeyToAccount } from 'viem/accounts';
import { createSmartAccountClient, ENTRYPOINT_ADDRESS_V06 } from '@pimlico/aa-viem';
import { ZeroDevProvider } from '@pimlico/aa-viem/accounts'; // For ZeroDev kernel or other common accounts
import { Hex, createWalletClient, WalletClient, PublicClient } from 'viem';
import { goerli } from 'viem/chains';
import { publicClient, pimlicoBundlerRpc, pimlicoPaymasterRpc } from './config';

export async function createZeroDevAccount(
  privateKey: Hex,
  publicClient: PublicClient,
  bundlerRpc: string,
  paymasterRpc: string
): Promise<{ smartAccountClient: WalletClient; accountAddress: Hex }> {
  const eoaSigner = privateKeyToAccount(privateKey);

  // Create a ZeroDevProvider-based smart account client
  const smartAccountClient = await createSmartAccountClient({
    account: await ZeroDevProvider.init({
      projectIds: { goerli: 'YOUR_ZERODEV_PROJECT_ID' }, // Replace with your ZeroDev Project ID
      owner: eoaSigner,
      chain: goerli,
      bundlerProvider: http(bundlerRpc),
      paymasterProvider: http(paymasterRpc),
      // entryPoint: ENTRYPOINT_ADDRESS_V06, // Default for ZeroDev V0.6
    }),
    chain: goerli,
    transport: http(bundlerRpc), // Bundler RPC is used for sending UserOps
    // entryPoint: ENTRYPOINT_ADDRESS_V06, // Specify if not using default
  });

  const accountAddress = smartAccountClient.account!.address;
  console.log(`Smart Account address: ${accountAddress}`);
  return { smartAccountClient, accountAddress };
}

// Example usage:
async function main() {
  const eoaPrivateKey: Hex = '0x...'; // Replace with a test EOA private key

  const { smartAccountClient, accountAddress } = await createZeroDevAccount(
    eoaPrivateKey,
    publicClient,
    pimlicoBundlerRpc,
    pimlicoPaymasterRpc
  );

  // You can now use smartAccountClient to send UserOperations
}

// main().catch(console.error);
```

### 2. Sending a Gasless UserOperation via a Paymaster

This is where the magic happens. You construct a transaction, but instead of signing it with an EOA and paying gas, you tell the smart account client to use a Paymaster. The client handles the `UserOperation` construction, estimation, signing, and sending to the Bundler.

```typescript
// src/sendGaslessTx.ts
import { Hex, parseEther } from 'viem';
import { createPublicClient, http } from 'viem';
import { goerli } from 'viem/chains';
import { privateKeyToAccount } from 'viem/accounts';
import { createSmartAccountClient, ENTRYPOINT_ADDRESS_V06 } from '@pimlico/aa-viem';
import { ZeroDevProvider } from '@pimlico/aa-viem/accounts';
import { publicClient, pimlicoBundlerRpc, pimlicoPaymasterRpc } from './config';
import { createZeroDevAccount } from './createAccount';

export async function sendGaslessTransaction(
  smartAccountClient: any, // Type as any for simplicity, it's a WalletClient with AA extensions
  recipientAddress: Hex,
  amount: bigint
) {
  console.log(`Sending gasless transaction from ${smartAccountClient.account.address} to ${recipientAddress}...`);

  try {
    // The smart account client automatically uses the configured paymaster
    // if it was set up with a paymaster provider.
    const userOperationHash = await smartAccountClient.sendTransaction({
      to: recipientAddress,
      value: amount,
    });

    console.log(`UserOperation Hash: ${userOperationHash}`);
    console.log(`Waiting for UserOperation to be included...`);

    // You can optionally wait for the UserOperation to be mined
    const transactionHash = await smartAccountClient.waitForUserOperationTransaction({
      hash: userOperationHash,
    });

    console.log(`Transaction Hash: ${transactionHash}`);
    console.log(`Transaction successful and gas was paid by Paymaster!`);
  } catch (error) {
    console.error('Failed to send gasless transaction:', error);
  }
}

// Example usage:
async function main() {
  const eoaPrivateKey: Hex = '0x...'; // Your test EOA private key
  const recipientAddress: Hex = '0x...'; // Replace with a recipient address
  const amountToSend = parseEther('0.0001'); // 0.0001 ETH

  const { smartAccountClient } = await createZeroDevAccount(
    eoaPrivateKey,
    publicClient,
    pimlicoBundlerRpc,
    pimlicoPaymasterRpc
  );

  await sendGaslessTransaction(smartAccountClient, recipientAddress, amountToSend);
}

// main().catch(console.error);
```

### 3. Batching Multiple Transactions

Smart accounts can batch multiple calls into a single `UserOperation`, saving gas and simplifying complex interactions for users. This is a powerful feature for dApps.

```typescript
// src/batchTransactions.ts
import { Hex, parseEther, encodeFunctionData, Address } from 'viem';
import { erc20Abi } from 'viem/abis'; // Example ABI for ERC-20
import { createZeroDevAccount } from './createAccount';
import { publicClient, pimlicoBundlerRpc, pimlicoPaymasterRpc } from './config';

export async function batchTransactions(
  smartAccountClient: any, // Type as any for simplicity
  erc20ContractAddress: Address,
  recipient1: Address,
  amount1: bigint,
  recipient2: Address,
  amount2: bigint
) {
  console.log(`Batching two transactions from ${smartAccountClient.account.address}...`);

  // First transaction: Transfer ETH
  const ethTransferCall = {
    to: recipient1,
    value: amount1,
    data: '0x', // No data for ETH transfer
  };

  // Second transaction: Transfer an ERC-20 token
  const erc20TransferData = encodeFunctionData({
    abi: erc20Abi,
    functionName: 'transfer',
    args: [recipient2, amount2],
  });

  const erc20TransferCall = {
    to: erc20ContractAddress,
    value: 0n,
    data: erc20TransferData,
  };

  try {
    const userOperationHash = await smartAccountClient.sendTransactions([
      ethTransferCall,
      erc20TransferCall,
    ]);

    console.log(`Batch UserOperation Hash: ${userOperationHash}`);
    console.log(`Waiting for UserOperation to be included...`);

    const transactionHash = await smartAccountClient.waitForUserOperationTransaction({
      hash: userOperationHash,
    });

    console.log(`Batch Transaction Hash: ${transactionHash}`);
    console.log(`Both transactions executed successfully in a single batch!`);
  } catch (error) {
    console.error('Failed to send batched transactions:', error);
  }
}

// Example usage:
async function main() {
  const eoaPrivateKey: Hex = '0x...'; // Your test EOA private key
  const erc20ContractAddress: Address = '0x...'; // Replace with an ERC-20 token address on Goerli
  const recipient1: Address = '0x...'; // First recipient
  const recipient2: Address = '0x...'; // Second recipient
  const ethAmount = parseEther('0.00005');
  const erc20Amount = 1000000000000000000n; // 1 token (assuming 18 decimals)

  const { smartAccountClient } = await createZeroDevAccount(
    eoaPrivateKey,
    publicClient,
    pimlicoBundlerRpc,
    pimlicoPaymasterRpc
  );

  await batchTransactions(
    smartAccountClient,
    erc20ContractAddress,
    recipient1,
    ethAmount,
    recipient2,
    erc20Amount
  );
}

// main().catch(console.error);
```

## Best Practices

*   **Choose a Reliable AA Provider:** Don't roll your own Bundler or Paymaster unless absolutely necessary. Rely on established services like Pimlico, StackUp, or Biconomy for production infrastructure.

## Anti-Patterns

*   **Rolling Custom Bundler Infrastructure.** Building and maintaining your own bundler when established services (Pimlico, StackUp) exist wastes engineering resources on infrastructure that requires constant maintenance and monitoring.

*   **Unbounded Validation Gas in validateUserOp.** Allowing the account's validation function to consume excessive gas causes the bundler to reject the UserOperation. Keep validation logic minimal and predictable.

*   **Paymaster Without Spending Limits.** Deploying a gasless experience through a paymaster without per-user rate limits or spending caps allows attackers to drain the paymaster's gas deposit through spam UserOperations.

*   **Missing Signature Replay Protection.** Implementing custom signature validation without chain ID, nonce, and EntryPoint address in the signed hash allows cross-chain and cross-account signature replay attacks.

*   **No Account Recovery Mechanism.** Deploying smart accounts without social recovery, guardian systems, or key rotation capabilities means a lost signing key results in permanently locked funds.

## Version and Evidence Check

Check the EntryPoint version, bundler support, paymaster API schema, and signer validation on the target chain. Example SDK names and service URLs can become obsolete.

## Review & Production Validation (2026-10-31)

- **Domain control (Contract engineering):** Check compiler, EVM fork, dependency versions, access control and storage-layout assumptions.
- **Independent validation:** Validate adversarial properties with tests and independent security review before deployment.
- **Time-sensitive details:** Treat fixed rates, thresholds, package versions, protocols and jurisdiction-specific rules in the examples above as illustrative unless reconfirmed against primary documentation.
- **Before relying on the result:** State inputs and assumptions; verify calculations and edge cases, and identify what has not been executed or tested.


## Account abstraction version check (ERC-4337 / EIP-7702)

Do not assume ERC-4337 `UserOperation` code, EntryPoint addresses, bundler RPC methods, paymaster schemas or EIP-7702 authorization flows are interchangeable across versions. Confirm deployed network support, current SDK APIs, simulation failures and paymaster fee behavior using https://ercs.ethereum.org/ERCS/erc-4337 before implementation.
