---
name: wallet-connect
description: 'Use when the user needs walletconnect integration: plan pairing, session permissions,
  network switching and rejection flows.'
---

# WalletConnect — Web3 Development

You are an expert in WalletConnect for enabling secure wallet connections between decentralized applications and mobile or desktop wallets across EVM and non-EVM chains.

## Overview

WalletConnect is an open protocol for connecting wallets to dApps using end-to-end encrypted relay communication. Version 2 (v2) supports multiple simultaneous chain sessions, improved session management, and a broader set of wallets. It works by generating a pairing URI (displayed as a QR code or deep link) that the wallet scans to establish an encrypted session over the WalletConnect relay server.

## Core Philosophy

WalletConnect enables secure, end-to-end encrypted communication between dApps and wallets without requiring the wallet to be on the same device or browser. The protocol's relay architecture means users can sign transactions on their mobile hardware wallet while interacting with a desktop dApp, maintaining the security principle that signing keys never leave the wallet device. Version 2 introduced multi-chain sessions, allowing a single connection to authorize interactions across multiple blockchains simultaneously.

## Anti-Patterns

*   **Ignoring Session Expiry and Cleanup.** Not handling session expiration events leaves stale sessions that confuse users when transactions silently fail. Implement session lifecycle management with automatic reconnection prompts.

*   **Hardcoded Relay Server URLs.** Embedding a single relay server endpoint without fallback creates a centralized point of failure for wallet communication. Use the WalletConnect cloud infrastructure with fallback configuration.

*   **No Chain Validation on Session Approval.** Accepting wallet sessions without verifying the connected chain matches the expected network allows users to submit transactions to wrong chains.

*   **Blocking UI During QR Code Pairing.** Showing only a QR code without deep link alternatives forces desktop-only wallet users to switch devices. Always provide both QR and deep link pairing options.

*   **Missing Disconnect Handling.** Not detecting wallet disconnection events (user closes wallet app, network drops) leaves the dApp in a state where it displays a connected wallet but transactions fail silently.

## Core Concepts

### WalletConnect Architecture

The protocol uses three components:
- **dApp** -- initiates pairing requests and sends JSON-RPC calls
- **Wallet** -- approves sessions and signs transactions
- **Relay Server** -- passes encrypted messages between dApp and wallet (wss://relay.walletconnect.com)

### Web3Modal (Recommended Integration)

Web3Modal is WalletConnect's official modal component that provides a unified wallet connection UI supporting WalletConnect, injected wallets, Coinbase Wallet, and email/social login.

```bash
npm install @web3modal/wagmi wagmi viem @tanstack/react-query
```

```typescript
// config.ts
import { createConfig, http } from "wagmi";
import { mainnet, polygon, arbitrum } from "wagmi/chains";
import { createWeb3Modal } from "@web3modal/wagmi/react";
import { walletConnect, injected, coinbaseWallet } from "wagmi/connectors";

const projectId = "YOUR_WALLETCONNECT_PROJECT_ID"; // From cloud.walletconnect.com

const metadata = {
  name: "My dApp",
  description: "My decentralized application",
  url: "https://mydapp.com",
  icons: ["https://mydapp.com/icon.png"],
};

export const config = createConfig({
  chains: [mainnet, polygon, arbitrum],
  connectors: [
    walletConnect({ projectId, metadata, showQrModal: false }),
    injected({ shimDisconnect: true }),
    coinbaseWallet({ appName: metadata.name }),
  ],
  transports: {
    [mainnet.id]: http(),
    [polygon.id]: http(),
    [arbitrum.id]: http(),
  },
});

createWeb3Modal({
  wagmiConfig: config,
  projectId,
  enableAnalytics: true,
  themeMode: "dark",
  themeVariables: {
    "--w3m-accent": "#3b82f6",
    "--w3m-border-radius-master": "2px",
  },
});
```

### React App Setup

```tsx
// App.tsx
import { WagmiProvider } from "wagmi";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { config } from "./config";

const queryClient = new QueryClient();

export default function App() {
  return (
    <WagmiProvider config={config}>
      <QueryClientProvider client={queryClient}>
        <ConnectButton />
        <YourApp />
      </QueryClientProvider>
    </WagmiProvider>
  );
}
```

### Connect Button Component

```tsx
import { useWeb3Modal } from "@web3modal/wagmi/react";
import { useAccount, useDisconnect, useBalance } from "wagmi";

function ConnectButton() {
  const { open } = useWeb3Modal();
  const { address, isConnected, chain } = useAccount();
  const { disconnect } = useDisconnect();
  const { data: balance } = useBalance({ address });

  if (!isConnected) {
    return <button onClick={() => open()}>Connect Wallet</button>;
  }

  return (
    <div>
      <p>
        {address?.slice(0, 6)}...{address?.slice(-4)}
      </p>
      <p>{chain?.name}</p>
      <p>{balance?.formatted} {balance?.symbol}</p>
      <button onClick={() => open({ view: "Networks" })}>
        Switch Network
      </button>
      <button onClick={() => open({ view: "Account" })}>
        Account Details
      </button>
      <button onClick={() => disconnect()}>Disconnect</button>
    </div>
  );
}
```

### Handling Session Events

```tsx
import { useAccountEffect } from "wagmi";

function SessionHandler() {
  useAccountEffect({
    onConnect(data) {
      console.log("Connected:", data.address, "Chain:", data.chainId);
      // Initialize user session, fetch balances, etc.
    },
    onDisconnect() {
      console.log("Disconnected");
      // Clear local state, redirect to connect page
    },
  });

  return null;
}
```

## Implementation Patterns

### Signing Messages for Authentication

```tsx
import { useSignMessage, useAccount } from "wagmi";

function SignInWithEthereum() {
  const { address } = useAccount();
  const { signMessageAsync } = useSignMessage();

  const handleSignIn = async () => {
    // Create SIWE message
    const nonce = await fetchNonceFromServer();
    const message = createSiweMessage({
      domain: window.location.host,
      address: address!,
      statement: "Sign in to My dApp",
      uri: window.location.origin,
      version: "1",
      chainId: 1,
      nonce,
    });

    try {
      const signature = await signMessageAsync({ message });

      // Send signature to backend for verification
      const response = await fetch("/api/auth/verify", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message, signature }),
      });

      if (response.ok) {
        const { token } = await response.json();
        localStorage.setItem("auth_token", token);
      }
    } catch (error) {
      console.error("Sign-in failed:", error);
    }
  };

  return <button onClick={handleSignIn}>Sign In with Ethereum</button>;
}

// Server-side verification
import { verifyMessage } from "viem";

async function verifySignature(message: string, signature: `0x${string}`) {
  const address = await verifyMessage({ message, signature });
  // Validate SIWE message fields (nonce, domain, expiration)
  return address;
}
```

### Transaction Signing Flow

```tsx
import { useWriteContract, useWaitForTransactionReceipt } from "wagmi";
import { parseEther } from "viem";

function SendTransaction() {
  const { writeContract, data: hash, error, isPending } = useWriteContract();
  const { isLoading: isConfirming, isSuccess } = useWaitForTransactionReceipt({
    hash,
  });

  const handleSend = () => {
    writeContract({
      address: "0xContractAddress...",
      abi: contractAbi,
      functionName: "deposit",
      value: parseEther("0.1"),
    });
  };

  return (
    <div>
      <button onClick={handleSend} disabled={isPending}>
        {isPending ? "Check Wallet..." : "Deposit 0.1 ETH"}
      </button>
      {isConfirming && <p>Confirming transaction...</p>}
      {isSuccess && <p>Transaction confirmed!</p>}
      {error && <p>Error: {error.message}</p>}
    </div>
  );
}
```

### Multi-Chain Support

```tsx
import { useSwitchChain, useAccount } from "wagmi";
import { mainnet, polygon, arbitrum, optimism } from "wagmi/chains";

const SUPPORTED_CHAINS = [mainnet, polygon, arbitrum, optimism];

function ChainSwitcher() {
  const { chain } = useAccount();
  const { switchChain, isPending } = useSwitchChain();

  return (
    <div>
      <p>Current chain: {chain?.name ?? "Not connected"}</p>
      {SUPPORTED_CHAINS.map((c) => (
        <button
          key={c.id}
          onClick={() => switchChain({ chainId: c.id })}
          disabled={isPending || chain?.id === c.id}
        >
          {chain?.id === c.id ? `${c.name} (active)` : c.name}
        </button>
      ))}
    </div>
  );
}
```

### Handling Connection Errors

```tsx
import { useConnect } from "wagmi";

function ConnectWithErrorHandling() {
  const { connect, connectors, error, isPending } = useConnect();

  return (
    <div>
      {connectors.map((connector) => (
        <button
          key={connector.uid}
          onClick={() => connect({ connector })}
          disabled={isPending}
        >
          {connector.name}
        </button>
      ))}
      {error && (
        <div>
          {error.message.includes("User rejected")
            ? "Connection was rejected. Please try again."
            : error.message.includes("Already processing")
            ? "Please complete the pending request in your wallet."
            : `Connection failed: ${error.message}`}
        </div>
      )}
    </div>
  );
}
```

### Persistent Sessions

```tsx
import { useEffect } from "react";
import { useReconnect } from "wagmi";

function AutoReconnect() {
  const { reconnect } = useReconnect();

  useEffect(() => {
    // Wagmi automatically persists and restores sessions
    // This hook triggers reconnection on page load
    reconnect();
  }, [reconnect]);

  return null;
}
```

## Best Practices

1. **Get a WalletConnect Project ID** from cloud.walletconnect.com. The free tier is sufficient for development, but production apps should monitor usage.
2. **Use Web3Modal** instead of building custom connection UIs. It handles QR codes, deep links, wallet detection, and session management.
3. **Always provide wallet metadata** (name, description, URL, icons) so wallets can display your dApp's identity to users.
4. **Handle all connection states** -- connecting, connected, disconnecting, disconnected, and reconnecting -- for a smooth user experience.
5. **Implement Sign-In with Ethereum (SIWE)** for authentication instead of custom signature schemes. SIWE is a standard (EIP-4361) supported by most wallets.
6. **Support multiple chains** and provide a chain switcher. Users expect to operate on their preferred network.
7. **Show clear transaction status feedback** -- pending wallet approval, pending confirmation, and final result.
8. **Test with multiple wallets** (MetaMask, Rainbow, Trust Wallet, Coinbase Wallet) to ensure compatibility across the ecosystem.

## Common Pitfalls

- **Using WalletConnect v1.** Version 1 is deprecated and shut down. Always use v2 with a Project ID.
- **Not handling user rejection.** Users frequently reject connection or transaction requests. Always catch and display friendly error messages.
- **Missing `showQrModal: false`** when using Web3Modal with the WalletConnect connector. Web3Modal manages its own modal; enabling both creates duplicate QR codes.
- **Not persisting connection state.** Wagmi handles this by default with `localStorage`, but custom implementations must save and restore sessions explicitly.
- **Ignoring chain ID mismatches.** When a user's wallet is on a different chain than expected, prompt them to switch rather than failing silently.
- **Blocking the UI during wallet interactions.** Wallet approvals can take time (especially on mobile). Keep the UI responsive with proper loading states.
- **Hardcoding chain configurations.** Use Viem's chain definitions from `viem/chains` to get correct RPC URLs, block explorers, and native currencies.

## Version and Evidence Check

Confirm the WalletConnect protocol/SDK major version and current session or namespace semantics; older examples may not work unchanged.

## Review & Production Validation (2026-10-31)

- **Domain control (Custody and security):** Treat bridge, authorization, signing, key handling and replay risk as potentially loss-causing.
- **Independent validation:** Avoid secrets in examples; validate controls, testnets, incident procedures and third-party contracts.
- **Time-sensitive details:** Treat fixed rates, thresholds, package versions, protocols and jurisdiction-specific rules in the examples above as illustrative unless reconfirmed against primary documentation.
- **Before relying on the result:** State inputs and assumptions; verify calculations and edge cases, and identify what has not been executed or tested.
