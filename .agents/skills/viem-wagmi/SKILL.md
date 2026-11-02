---
name: viem-wagmi
description: 'Use when the user needs viem and wagmi web3 frontends: design typed wallet
  hooks, contract calls, account state and transaction UX.'
---

# Viem and Wagmi — Web3 Development

You are an expert in Viem and Wagmi for building type-safe, performant React decentralized applications.

## Overview

Viem is a lightweight, type-safe TypeScript interface for Ethereum that serves as an alternative to ethers.js. Wagmi is a collection of React hooks built on top of Viem and TanStack Query that simplifies wallet connection, contract interaction, and chain management in React applications.

## Core Philosophy

Viem and Wagmi bring TypeScript-first, type-safe blockchain interaction to React development. Viem replaces ethers.js with a tree-shakeable, strictly-typed core that catches ABI mismatches, wrong parameter types, and invalid chain configurations at compile time rather than runtime. Wagmi builds on this foundation with React hooks that integrate with TanStack Query for automatic caching, refetching, and loading state management, making blockchain data feel as natural as REST API data in React applications.

## Anti-Patterns

*   **Direct Viem Calls in React Components.** Bypassing Wagmi hooks to call Viem clients directly inside components loses caching, automatic refetching, and loading state management. Use Wagmi hooks for all blockchain reads in React.

*   **Missing Chain Configuration Validation.** Deploying without type-checking chain configurations against Viem's chain definitions allows connecting to wrong networks or using incorrect contract addresses silently.

*   **Ignoring TanStack Query Cache Invalidation.** Not configuring `staleTime` and `cacheTime` for contract read hooks causes either excessive RPC calls (no caching) or stale data display (over-caching).

*   **Wallet Connection Without Error Boundaries.** Not handling wallet rejection, disconnection, and chain-switching errors in the UI leaves users stuck on broken states with no recovery path.

*   **Importing Full ABI When Using Partial Functions.** Importing complete contract ABIs when only a few functions are needed prevents tree-shaking and increases bundle size unnecessarily. Use ABI fragments.

## Core Concepts

### Viem Clients and Transports

```typescript
import { createPublicClient, createWalletClient, http, webSocket } from "viem";
import { mainnet, sepolia } from "viem/chains";

// Public client for read operations
const publicClient = createPublicClient({
  chain: mainnet,
  transport: http("https://eth-mainnet.g.alchemy.com/v2/YOUR_KEY"),
});

// WebSocket transport for subscriptions
const wsClient = createPublicClient({
  chain: mainnet,
  transport: webSocket("wss://eth-mainnet.g.alchemy.com/v2/YOUR_KEY"),
});

// Wallet client for write operations
const walletClient = createWalletClient({
  chain: mainnet,
  transport: http(),
});

// Read blockchain state
const blockNumber = await publicClient.getBlockNumber();
const balance = await publicClient.getBalance({
  address: "0xAddress...",
});
```

### Viem Contract Interaction

```typescript
import { getContract, parseAbi, parseEther, formatEther } from "viem";

const abi = parseAbi([
  "function name() view returns (string)",
  "function balanceOf(address) view returns (uint256)",
  "function transfer(address to, uint256 amount) returns (bool)",
  "event Transfer(address indexed from, address indexed to, uint256 value)",
]);

// Read contract
const name = await publicClient.readContract({
  address: "0xTokenAddress...",
  abi,
  functionName: "name",
});

// Multicall (batch reads)
const results = await publicClient.multicall({
  contracts: [
    { address: "0xToken...", abi, functionName: "name" },
    { address: "0xToken...", abi, functionName: "balanceOf", args: ["0xHolder..."] },
  ],
});

// Write contract
const hash = await walletClient.writeContract({
  address: "0xTokenAddress...",
  abi,
  functionName: "transfer",
  args: ["0xRecipient...", parseEther("10")],
  account: "0xYourAddress...",
});

// Wait for transaction receipt
const receipt = await publicClient.waitForTransactionReceipt({ hash });
```

### Wagmi Configuration

```typescript
// wagmi.config.ts
import { createConfig, http } from "wagmi";
import { mainnet, sepolia, polygon } from "wagmi/chains";
import { injected, walletConnect, coinbaseWallet } from "wagmi/connectors";

export const config = createConfig({
  chains: [mainnet, sepolia, polygon],
  connectors: [
    injected(),
    walletConnect({ projectId: "YOUR_WALLETCONNECT_PROJECT_ID" }),
    coinbaseWallet({ appName: "My dApp" }),
  ],
  transports: {
    [mainnet.id]: http("https://eth-mainnet.g.alchemy.com/v2/KEY"),
    [sepolia.id]: http("https://eth-sepolia.g.alchemy.com/v2/KEY"),
    [polygon.id]: http("https://polygon-mainnet.g.alchemy.com/v2/KEY"),
  },
});
```

### Wagmi Provider Setup

```tsx
// App.tsx
import { WagmiProvider } from "wagmi";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { config } from "./wagmi.config";

const queryClient = new QueryClient();

function App() {
  return (
    <WagmiProvider config={config}>
      <QueryClientProvider client={queryClient}>
        <YourApp />
      </QueryClientProvider>
    </WagmiProvider>
  );
}
```

### Wagmi Hooks

```tsx
import {
  useAccount,
  useConnect,
  useDisconnect,
  useBalance,
  useReadContract,
  useWriteContract,
  useWaitForTransactionReceipt,
  useSwitchChain,
} from "wagmi";

function WalletProfile() {
  const { address, isConnected, chain } = useAccount();
  const { connect, connectors } = useConnect();
  const { disconnect } = useDisconnect();
  const { switchChain } = useSwitchChain();

  const { data: balance } = useBalance({ address });

  const { data: tokenBalance } = useReadContract({
    address: "0xTokenAddress...",
    abi: erc20Abi,
    functionName: "balanceOf",
    args: [address!],
    query: { enabled: !!address },
  });

  const { writeContract, data: txHash, isPending } = useWriteContract();

  const { isLoading: isConfirming, isSuccess } = useWaitForTransactionReceipt({
    hash: txHash,
  });

  const handleTransfer = () => {
    writeContract({
      address: "0xTokenAddress...",
      abi: erc20Abi,
      functionName: "transfer",
      args: ["0xRecipient...", parseEther("10")],
    });
  };

  if (!isConnected) {
    return (
      <div>
        {connectors.map((connector) => (
          <button key={connector.uid} onClick={() => connect({ connector })}>
            Connect with {connector.name}
          </button>
        ))}
      </div>
    );
  }

  return (
    <div>
      <p>Connected: {address}</p>
      <p>Chain: {chain?.name}</p>
      <p>Balance: {balance?.formatted} {balance?.symbol}</p>
      <button onClick={handleTransfer} disabled={isPending}>
        {isPending ? "Confirming..." : "Transfer"}
      </button>
      {isConfirming && <p>Waiting for confirmation...</p>}
      {isSuccess && <p>Transaction confirmed!</p>}
      <button onClick={() => switchChain({ chainId: polygon.id })}>
        Switch to Polygon
      </button>
      <button onClick={() => disconnect()}>Disconnect</button>
    </div>
  );
}
```

## Implementation Patterns

### Custom Hook for Contract Reads with Polling

```tsx
import { useReadContract } from "wagmi";

function useTokenPrice(tokenAddress: `0x${string}`) {
  return useReadContract({
    address: "0xOracleAddress...",
    abi: oracleAbi,
    functionName: "getLatestPrice",
    args: [tokenAddress],
    query: {
      refetchInterval: 15_000, // Poll every 15 seconds
      staleTime: 10_000,
    },
  });
}
```

### Simulating Transactions Before Sending

```typescript
// With Viem directly
const { request } = await publicClient.simulateContract({
  address: "0xTokenAddress...",
  abi,
  functionName: "transfer",
  args: ["0xRecipient...", parseEther("10")],
  account: "0xYourAddress...",
});

const hash = await walletClient.writeContract(request);

// With Wagmi hook
const { data } = useSimulateContract({
  address: "0xTokenAddress...",
  abi,
  functionName: "transfer",
  args: ["0xRecipient...", parseEther("10")],
});

const { writeContract } = useWriteContract();
// Only call when simulation succeeds
writeContract(data!.request);
```

### Event Watching

```typescript
// Viem
const unwatch = publicClient.watchContractEvent({
  address: "0xTokenAddress...",
  abi,
  eventName: "Transfer",
  onLogs: (logs) => {
    for (const log of logs) {
      console.log(log.args.from, log.args.to, log.args.value);
    }
  },
});

// Cleanup
unwatch();
```

### Typed Contract Instances

```typescript
import { getContract } from "viem";

const contract = getContract({
  address: "0xTokenAddress...",
  abi,
  client: { public: publicClient, wallet: walletClient },
});

// Fully typed reads and writes
const name = await contract.read.name();
const hash = await contract.write.transfer(["0xRecipient...", parseEther("10")], {
  account: "0xYourAddress...",
});
```

## Best Practices

1. **Use `useSimulateContract` before `useWriteContract`** to catch reverts before submitting transactions. This saves users gas on failed transactions.
2. **Enable TanStack Query devtools** during development to inspect cache state and refetch behavior of Wagmi hooks.
3. **Set appropriate `staleTime` and `refetchInterval`** on contract reads to balance freshness against RPC rate limits.
4. **Use the `query.enabled` option** to conditionally run hooks. Avoid calling hooks with undefined arguments.
5. **Define ABIs as `const` assertions** or use `parseAbi` for full type inference on function arguments and return types.
6. **Configure multiple transports per chain** so Wagmi can fall back if one RPC endpoint is unavailable.
7. **Use `useAccount` status checks** (`isConnecting`, `isReconnecting`, `isDisconnected`) for proper loading states.

## Common Pitfalls

- **Not wrapping the app in both `WagmiProvider` and `QueryClientProvider`.** Both are required; missing either causes runtime errors.
- **Calling `writeContract` without simulation.** The transaction may revert on-chain, wasting gas. Always simulate first.
- **Ignoring the `enabled` flag on hooks.** Hooks with undefined parameters will fire unnecessary RPC calls or throw.
- **Mixing Viem v1 and v2 APIs.** Viem v2 changed `publicClient` and `walletClient` creation patterns. Check the version in use.
- **Not handling chain switching errors.** Users may reject the chain switch or have networks not configured in their wallet.
- **Forgetting to invalidate queries after writes.** Use `queryClient.invalidateQueries` after a successful write to refresh stale reads.

## Review & Production Validation (2026-10-31)

- **Domain control (Blockchain ecosystem / development):** Confirm active network, chain ID, toolchain/API version and protocol-specific conventions.
- **Independent validation:** Use primary documentation and reproducible tests for implementation instructions.
- **Time-sensitive details:** Treat fixed rates, thresholds, package versions, protocols and jurisdiction-specific rules in the examples above as illustrative unless reconfirmed against primary documentation.
- **Before relying on the result:** State inputs and assumptions; verify calculations and edge cases, and identify what has not been executed or tested.
