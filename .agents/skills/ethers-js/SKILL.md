---
name: ethers-js
description: 'Use when the user needs ethers.js application integration: build signer, provider,
  contract and event workflows with ethers.js.'
---

# Ethers.js — Web3 Development

You are an expert in ethers.js for building decentralized applications that interact with Ethereum and EVM-compatible blockchains.

## Overview

Ethers.js is a compact, complete library for interacting with the Ethereum blockchain. It provides utilities for managing wallets, signing transactions, querying on-chain data, and interacting with smart contracts. Version 6.x is the current major release with significant API changes from v5.

## Core Philosophy

Ethers.js prioritizes security, correctness, and developer ergonomics for blockchain interaction. The library enforces a clear separation between read-only providers and signing-capable wallets, ensuring that transaction signing is always an explicit action. Version 6 embraced native JavaScript primitives (BigInt over custom BigNumber classes) to reduce abstraction overhead and improve interoperability with the broader JavaScript ecosystem. When building with ethers.js, always treat blockchain interactions as inherently asynchronous, fallible, and adversarial.

## Anti-Patterns

*   **Mixing Ethers v5 and v6 APIs.** Using `ethers.utils` (v5) in a v6 project or mixing BigNumber and BigInt causes silent failures. Commit fully to one version and follow its migration guide.

*   **Ignoring Nonce Management for Rapid Transactions.** Sending multiple transactions without explicit nonce tracking causes replacement errors and stuck transactions. Implement a nonce manager for any high-throughput application.

*   **Hardcoded Gas Prices.** Embedding fixed gas values instead of dynamically fetching fee data causes transactions to underpay during congestion or overpay during calm periods.

*   **Missing Transaction Receipt Validation.** Assuming a mined transaction succeeded without checking `receipt.status` leads to silent failures where reverted transactions are treated as successful.

*   **Number Type for Token Amounts.** Converting BigInt token amounts to JavaScript Number for arithmetic introduces precision loss above 2^53, causing incorrect balances and transfer amounts.

## Core Concepts

### Providers

Providers are read-only connections to the blockchain. They allow querying state without signing transactions.

```typescript
import { JsonRpcProvider, InfuraProvider, AlchemyProvider } from "ethers";

// Connect to a local node
const localProvider = new JsonRpcProvider("http://127.0.0.1:8545");

// Connect via Infura
const infuraProvider = new InfuraProvider("mainnet", "YOUR_API_KEY");

// Connect via Alchemy
const alchemyProvider = new AlchemyProvider("mainnet", "YOUR_API_KEY");

// Query blockchain state
const blockNumber = await provider.getBlockNumber();
const balance = await provider.getBalance("0xAddress...");
const network = await provider.getNetwork();
```

### Signers and Wallets

Signers represent an Ethereum account that can sign transactions and messages.

```typescript
import { Wallet, HDNodeWallet, parseEther } from "ethers";

// Create wallet from private key
const wallet = new Wallet("0xPrivateKey...", provider);

// Create random wallet
const randomWallet = Wallet.createRandom();

// Create from mnemonic
const mnemonicWallet = HDNodeWallet.fromPhrase("word1 word2 word3 ...");

// Connect wallet to provider
const connectedWallet = randomWallet.connect(provider);

// Sign a message
const signature = await wallet.signMessage("Hello, Ethereum!");

// Send a transaction
const tx = await wallet.sendTransaction({
  to: "0xRecipient...",
  value: parseEther("0.1"),
});
const receipt = await tx.wait(); // Wait for confirmation
```

### Contract Interaction

```typescript
import { Contract, Interface, parseEther, formatEther } from "ethers";

// ERC-20 ABI (subset)
const erc20Abi = [
  "function name() view returns (string)",
  "function symbol() view returns (string)",
  "function balanceOf(address owner) view returns (uint256)",
  "function transfer(address to, uint256 amount) returns (bool)",
  "event Transfer(address indexed from, address indexed to, uint256 value)",
];

// Read-only contract (uses provider)
const token = new Contract("0xTokenAddress...", erc20Abi, provider);
const name = await token.name();
const balance = await token.balanceOf("0xHolder...");

// Writable contract (uses signer)
const tokenWithSigner = new Contract("0xTokenAddress...", erc20Abi, signer);
const tx = await tokenWithSigner.transfer("0xRecipient...", parseEther("10"));
await tx.wait();
```

### Event Listening and Filtering

```typescript
// Listen for Transfer events
token.on("Transfer", (from, to, value, event) => {
  console.log(`${from} sent ${formatEther(value)} to ${to}`);
});

// Query past events
const filter = token.filters.Transfer(walletAddress, null);
const events = await token.queryFilter(filter, -1000); // Last 1000 blocks

// Remove listeners
token.removeAllListeners("Transfer");
```

### Encoding and Decoding

```typescript
import { AbiCoder, Interface, keccak256, toUtf8Bytes, solidityPacked } from "ethers";

const abiCoder = AbiCoder.defaultAbiCoder();

// Encode parameters
const encoded = abiCoder.encode(
  ["address", "uint256"],
  ["0xAddress...", 1000n]
);

// Decode parameters
const decoded = abiCoder.decode(["address", "uint256"], encoded);

// Hash data
const hash = keccak256(toUtf8Bytes("Hello"));

// Solidity-compatible packed encoding
const packed = solidityPacked(
  ["address", "uint256"],
  ["0xAddress...", 1000n]
);
```

## Implementation Patterns

### Multicall Pattern for Batch Reads

```typescript
import { Contract } from "ethers";

const multicallAbi = [
  "function aggregate(tuple(address target, bytes callData)[] calls) view returns (uint256 blockNumber, bytes[] returnData)",
];

const multicall = new Contract("0xcA11bde05977b3631167028862bE2a173976CA11", multicallAbi, provider);

const tokenInterface = new Interface(erc20Abi);

const calls = tokenAddresses.map((addr) => ({
  target: addr,
  callData: tokenInterface.encodeFunctionData("balanceOf", [walletAddress]),
}));

const [, returnData] = await multicall.aggregate(calls);

const balances = returnData.map((data) =>
  tokenInterface.decodeFunctionResult("balanceOf", data)[0]
);
```

### Gas Estimation and EIP-1559 Transactions

```typescript
// Estimate gas
const gasEstimate = await tokenWithSigner.transfer.estimateGas(
  "0xRecipient...",
  parseEther("10")
);

// Get fee data (EIP-1559)
const feeData = await provider.getFeeData();

// Send with explicit gas parameters
const tx = await tokenWithSigner.transfer("0xRecipient...", parseEther("10"), {
  gasLimit: gasEstimate * 120n / 100n, // 20% buffer
  maxFeePerGas: feeData.maxFeePerGas,
  maxPriorityFeePerGas: feeData.maxPriorityFeePerGas,
});
```

### Transaction Receipt Parsing

```typescript
const receipt = await tx.wait();

// Parse logs from receipt
const transferEvents = receipt.logs
  .map((log) => {
    try {
      return token.interface.parseLog({ topics: log.topics, data: log.data });
    } catch {
      return null;
    }
  })
  .filter(Boolean);

for (const event of transferEvents) {
  console.log(`Transfer: ${event.args.from} -> ${event.args.to}: ${formatEther(event.args.value)}`);
}
```

## Best Practices

1. **Always use BigInt for numeric values.** Ethers v6 uses native BigInt instead of BigNumber. Never convert to Number for arithmetic on token amounts.
2. **Use human-readable ABI fragments** instead of full JSON ABIs when you only need a subset of functions. This reduces bundle size and improves readability.
3. **Always call `tx.wait()`** and check the receipt status. A transaction being mined does not guarantee success.
4. **Set reasonable gas limits** by estimating first and adding a buffer, rather than using hardcoded values.
5. **Use `parseEther` / `formatEther` and `parseUnits` / `formatUnits`** for conversions instead of manual BigInt math.
6. **Handle provider disconnections** by implementing reconnection logic and monitoring `provider.on("error", ...)`.
7. **Use `Contract.connect(signer)`** to switch between read-only and writable contract instances rather than creating new Contract objects.

## Common Pitfalls

- **Mixing v5 and v6 APIs.** `ethers.utils` no longer exists in v6; utilities are top-level exports. `BigNumber` is replaced by native `BigInt`.
- **Forgetting `await` on contract calls.** All contract reads and writes are async. Missing `await` gives you a Promise, not the result.
- **Not handling reverted transactions.** `tx.wait()` can throw if the transaction reverts. Always wrap in try/catch.
- **Using the wrong chain ID.** When switching networks, the provider and signer must both target the same chain.
- **Ignoring nonce management.** When sending multiple transactions rapidly, manually manage nonces to avoid replacement or stuck transactions.
- **Hardcoding gas prices.** Gas markets are dynamic; always fetch current fee data or use the provider defaults.

## Review & Production Validation (2026-10-31)

- **Domain control (Blockchain ecosystem / development):** Confirm active network, chain ID, toolchain/API version and protocol-specific conventions.
- **Independent validation:** Use primary documentation and reproducible tests for implementation instructions.
- **Time-sensitive details:** Treat fixed rates, thresholds, package versions, protocols and jurisdiction-specific rules in the examples above as illustrative unless reconfirmed against primary documentation.
- **Before relying on the result:** State inputs and assumptions; verify calculations and edge cases, and identify what has not been executed or tested.
