---
name: solana-rpc-infrastructure
description: 'Use when the user needs solana rpc infrastructure: design Geyser ingestion,
  RPC capacity, rate limits and slot awareness.'
---

# Solana RPC infrastructure

You are a battle-hardened Solana developer and infrastructure engineer. You've built high-throughput dApps, analytics platforms, and trading bots that demand reliable, low-latency access to Solana's state. You understand that the RPC layer is the critical bottleneck for almost every Solana application, and you meticulously optimize every query, manage your provider relationships, and implement robust error handling to ensure your applications stay online and performant, even under extreme network load. You know that a poorly managed RPC strategy can sink an otherwise brilliant application.

## Core Philosophy

The Solana RPC infrastructure is not a free, infinitely scalable resource; it's the gateway to the network, and your application's performance hinges on how effectively you interact with it. Treat your RPC calls like precious commodities. Every request has a cost, whether in compute units on the RPC server, network bandwidth, or latency. Proactive optimization, intelligent caching, and thoughtful provider selection are paramount. You must understand the nuances of `commitment` levels, data fetching strategies, and the implications of rate limits. Never assume your RPC provider will magically scale with your needs; design for resilience, distribute your load, and be prepared for failures. Your goal is to extract the necessary data with the fewest, most efficient requests possible, ensuring both the reliability of your application and the sustainability of your RPC usage.

## Setup

To interact with Solana's RPC infrastructure, you primarily use the Solana CLI and the `@solana/web3.js` SDK.

1.  **Install Solana CLI (if not already installed):**
    The CLI is essential for local development, testing RPC connectivity, and deploying programs.

    ```bash
    sh -c "$(curl -sSfL https://raw.githubusercontent.com/solana-labs/solana/master/install/install-init.sh)"
    solana --version # Verify installation
    ```

2.  **Configure your RPC endpoint:**
    You can set your default RPC for the CLI using `solana config set --url`. For development, `devnet` or `testnet` are common. For production, you'll use `mainnet-beta` with a dedicated RPC provider.

    ```bash
    # For devnet
    solana config set --url devnet
    # For mainnet-beta (e.g., using a Helius/QuickNode/Alchemy endpoint)
    solana config set --url https://api.mainnet-beta.solana.com # Public endpoint (rate-limited)
    # Or your dedicated provider URL:
    # solana config set --url YOUR_MAINNET_BETA_RPC_URL
    ```

3.  **Install `@solana/web3.js` for JavaScript/TypeScript projects:**
    This is your primary programmatic interface to Solana RPCs.

    ```bash
    npm install @solana/web3.js @solana/spl-token
    # or
    yarn add @solana/web3.js @solana/spl-token
    ```

4.  **Initialize a `Connection` object in your code:**
    Always use an environment variable or configuration file for your RPC URL, never hardcode it.

    ```typescript
    import { Connection, clusterApiUrl } from '@solana/web3.js';

    // Best practice: Use an environment variable
    const rpcUrl = process.env.SOLANA_RPC_URL || clusterApiUrl('devnet');
    const connection = new Connection(rpcUrl, 'confirmed'); // 'confirmed' for most dApps
    console.log(`Connected to RPC: ${rpcUrl}`);
    ```

## Key Techniques

### 1. Connecting and Fetching Basic Account Data

You instantiate a `Connection` object with your RPC URL and a `commitment` level. Then you can query account balances, information, and transaction statuses.

```typescript
import { Connection, PublicKey, LAMPORTS_PER_SOL, clusterApiUrl } from '@solana/web3.js';

async function getAccountDetails(publicKeyString: string) {
    const rpcUrl = process.env.SOLANA_RPC_URL || clusterApiUrl('devnet');
    // Using 'finalized' commitment for highest data integrity, but 'confirmed' is faster for most UI
    const connection = new Connection(rpcUrl, 'finalized');

    const publicKey = new PublicKey(publicKeyString);

    try {
        // Fetch SOL balance
        const balanceLamports = await connection.getBalance(publicKey);
        console.log(`Account ${publicKey.toBase58()} balance: ${balanceLamports / LAMPORTS_PER_SOL} SOL`);

        // Fetch account info (owner, executable, rent epoch, data)
        const accountInfo = await connection.getAccountInfo(publicKey);
        if (accountInfo) {
            console.log(`Owner program: ${accountInfo.owner.toBase58()}`);
            console.log(`Executable: ${accountInfo.executable}`);
            console.log(`Data size: ${accountInfo.data.length} bytes`);
        } else {
            console.log(`Account ${publicKey.toBase58()} not found.`);
        }
    } catch (error) {
        console.error("Error fetching account details:", error);
    }
}

// Example usage: replace with a real Solana public key
getAccountDetails('83astBRguLMdt2HpjNnPUuxFuXpr51qi63prbytJd5JG');
```

### 2. Optimizing Data Fetches with `commitment` and `dataSlice`

Don't fetch more data than you need. Use `dataSlice` to retrieve only a portion of an account's data, and select the least strict `commitment` level that satisfies your application's requirements for faster responses.

```typescript
import { Connection, PublicKey, clusterApiUrl } from '@solana/web3.js';
import { TOKEN_PROGRAM_ID, AccountLayout } from '@solana/spl-token';

async function getPartialTokenAccountData(tokenAccountAddress: string) {
    const rpcUrl = process.env.SOLANA_RPC_URL || clusterApiUrl('devnet');
    // 'confirmed' is often sufficient for UI updates, faster than 'finalized'.
    const connection = new Connection(rpcUrl, 'confirmed');

    const tokenAccountPk = new PublicKey(tokenAccountAddress);

    try {
        // Fetch only the first few bytes of the token account data
        // For example, to quickly check if it's a valid token account structure
        const accountInfo = await connection.getAccountInfo(
            tokenAccountPk,
            {
                commitment: 'confirmed',
                dataSlice: { offset: 0, length: AccountLayout.span } // Fetch the entire SPL Token AccountLayout
            }
        );

        if (accountInfo && accountInfo.owner.equals(TOKEN_PROGRAM_ID)) {
            console.log(`Fetched token account ${tokenAccountPk.toBase58()}.`);
            console.log(`Data length: ${accountInfo.data.length} bytes.`);
            // You can deserialize `accountInfo.data` here if needed
            // const tokenAccount = AccountLayout.decode(accountInfo.data);
            // console.log(`Mint: ${new PublicKey(tokenAccount.mint).toBase58()}`);
        } else {
            console.log(`Account ${tokenAccountPk.toBase58()} is not a valid SPL Token Account or not found.`);
        }
    } catch (error) {
        console.error("Error fetching partial token account data:", error);
    }
}

// Example usage: replace with a real SPL token account address
getPartialTokenAccountData('FqA4qtLhH3s8mK3216t9p7N943D5vKzVf7N8X4J5Z6R');
```

### 3. Batching Requests with `getMultipleAccounts`

Instead of making multiple `getAccountInfo` calls, batch them into a single `getMultipleAccounts` request to reduce RPC round trips and improve efficiency.

```typescript
import { Connection, PublicKey, clusterApiUrl } from '@solana/web3.js';
import { AccountLayout, MintLayout, TOKEN_PROGRAM_ID } from '@solana/spl-token';

async function getMultipleTokenAccounts(accountAddresses: string[]) {
    const rpcUrl = process.env.SOLANA_RPC_URL || clusterApiUrl('devnet');
    const connection = new Connection(rpcUrl, 'confirmed');

    const publicKeys = accountAddresses.map(addr => new PublicKey(addr));

    try {
        const accountInfos = await connection.getMultipleAccountsInfo(publicKeys, {
            commitment: 'confirmed',
            dataSlice: { offset: 0, length: AccountLayout.span } // Fetch only token account data
        });

        accountInfos.forEach((info, index) => {
            const address = publicKeys[index].toBase58();
            if (info && info.owner.equals(TOKEN_PROGRAM_ID)) {
                console.log(`Account ${address}: Found. Data size: ${info.data.length} bytes.`);
                // Deserialize if needed
                // const tokenAccount = AccountLayout.decode(info.data);
                // console.log(`  Mint: ${new PublicKey(tokenAccount.mint).toBase58()}`);
            } else {
                console.log(`Account ${address}: Not found or not a token account.`);
            }
        });
    } catch (error) {
        console.error("Error fetching multiple accounts:", error);
    }
}

// Example usage: replace with real SPL token account addresses
getMultipleTokenAccounts([
    'FqA4qtLhH3s8mK3216t9p7N943D5vKzVf7N8X4J5Z6R',
    '3F2K9M6iQ2YtC8X7J5F4G3H1D0S9A8B7C6E5W4R3T2Y1', // Example placeholder
    'B5Z7A6X9Y1C2V3B4N5M6L7K8J9H0G1F2D3S4A5Q6W7E8'  // Example placeholder
]);
```

### 4. Simulating Transactions Off-Chain

Always `simulateTransaction` before sending a complex or critical transaction to the network. This allows you to catch errors, predict gas fees (compute units), and ensure the transaction will succeed without actually incurring costs or state changes.

```typescript
import { Connection, Keypair, SystemProgram, Transaction, LAMPORTS_PER_SOL, clusterApiUrl } from '@solana/web3.js';

async function simulateTransfer(sender: Keypair, receiverAddress: string, amountSol: number) {
    const rpcUrl = process.env.SOLANA_RPC_URL || clusterApiUrl('devnet');
    const connection = new Connection(rpcUrl, 'confirmed');

    const receiverPublicKey = new PublicKey(receiverAddress);
    const amountLamports = amountSol * LAMPORTS_PER_SOL;

    const transaction = new Transaction().add(
        SystemProgram.transfer({
            fromPubkey: sender.publicKey,
            toPubkey: receiverPublicKey,
            lamports: amountLamports,
        })
    );

    // Get a recent blockhash
    transaction.recentBlockhash = (await connection.getLatestBlockhash()).blockhash;
    transaction.feePayer = sender.publicKey;

    // Sign the transaction (required for simulation to calculate fees accurately)
    transaction.sign(sender);

    try {
        const { value: simulationResult } = await connection.simulateTransaction(transaction);

        if (simulationResult.err) {
            console.error("Transaction simulation failed:", simulationResult.err);
            if (simulationResult.logs) {
                console.error("Simulation logs:");
                simulationResult.logs.forEach(log => console.error(`  ${log}`));
            }
        } else {
            console.log("Transaction simulation successful!");
            console.log(`Compute units consumed: ${simulationResult.unitsConsumed}`);
            console.log(`Transaction logs:`);
            simulationResult.logs?.forEach(log => console.log(`  ${log}`));
            // Now you can confidently send the actual transaction if simulation passed
            // const signature = await connection.sendRawTransaction(transaction.serialize());
            // console.log(`Transaction sent: ${signature}`);
        }
    } catch (error) {
        console.error("Error during transaction simulation:", error);
    }
}

// Example usage: Generate a new keypair for the sender (DO NOT USE IN PROD)
const senderKeypair = Keypair.generate();
```

## Anti-Patterns

*   **Single Solana RPC Node Without Failover.** Running production Solana applications through a single RPC endpoint guarantees downtime during node maintenance, validator restarts, or network congestion events.

*   **Ignoring Solana Transaction Confirmation Levels.** Treating `processed` commitment level as finalized leads to acting on transactions that may be rolled back. Use `confirmed` for most operations and `finalized` for irreversible actions.

*   **Unbounded getProgramAccounts Queries.** Calling `getProgramAccounts` without filters on programs with thousands of accounts creates multi-second queries that time out or overwhelm the RPC node. Always apply data size and memcmp filters.

*   **No Transaction Simulation Before Sending.** Submitting Solana transactions without prior simulation via `simulateTransaction` wastes transaction fees on failures and misses compute unit estimation for priority fee calculation.

*   **Hardcoded Compute Unit Limits.** Setting fixed compute unit budgets instead of dynamically estimating via simulation either wastes SOL on overbudgeted transactions or causes failures on underbudgeted ones.

## Review & Production Validation (2026-10-31)

- **Domain control (Blockchain ecosystem / development):** Confirm active network, chain ID, toolchain/API version and protocol-specific conventions.
- **Independent validation:** Use primary documentation and reproducible tests for implementation instructions.
- **Time-sensitive details:** Treat fixed rates, thresholds, package versions, protocols and jurisdiction-specific rules in the examples above as illustrative unless reconfirmed against primary documentation.
- **Before relying on the result:** State inputs and assumptions; verify calculations and edge cases, and identify what has not been executed or tested.
