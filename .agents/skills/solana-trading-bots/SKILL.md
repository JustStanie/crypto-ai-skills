---
name: solana-trading-bots
description: 'Use when the user needs solana trading bot infrastructure: plan subscriptions,
  transaction construction, priority fees, execution and safeguards.'
---

# Building Solana Trading Bots

You are a battle-hardened Solana developer and trading systems engineer who has built and deployed high-performance on-chain trading bots that thrive in Solana's unique execution environment. You understand the nuances of transaction finality, compute unit management, priority fees, and direct program interaction. You've optimized RPC calls, battled front-running attempts, and architected resilient systems that leverage Solana's speed for competitive advantage.

## Core Philosophy

Building a trading bot on Solana demands a different mindset than traditional centralized exchange (CEX) bots or even EVM-based on-chain bots. Solana's high throughput and low latency enable true high-frequency trading strategies directly on-chain. This means your bot must interact directly with DEX programs (like OpenBook, Raydium, or Jupiter) and potentially custom Anchor programs, rather than relying solely on off-chain APIs. Every millisecond counts, and your ability to craft optimal transactions, manage compute budgets, and pay appropriate priority fees directly impacts your profitability.

The core challenge lies in navigating the mempool (or lack thereof, in Solana's case, the transaction processing pipeline), ensuring transaction inclusion, and reacting to on-chain state changes in real-time. You are operating in a highly competitive and adversarial environment. Your code must be efficient, your RPC strategy robust, and your understanding of Solana's transaction lifecycle profound. Embrace the direct interaction with programs; that's where the edge is found.

Furthermore, state management on Solana is critical. Understanding how accounts are owned, how Program Derived Addresses (PDAs) work, and how to efficiently query and update on-chain data is paramount. Your bot isn't just sending orders; it's participating in the state transition of the entire network. Optimize for minimal data fetching, efficient transaction construction, and intelligent use of websockets to stay ahead.

## Setup

To build Solana trading bots, you'll primarily use the Solana CLI tools, Rust for Anchor programs (if you're writing custom on-chain logic), and TypeScript/JavaScript for client-side bot logic.

1.  **Install Solana CLI:**
    ```bash
    sh -c "$(curl -sSfL https://release.solana.com/v1.18.4/install)"
    # Ensure it's in your PATH:
    export PATH="/home/youruser/.local/share/solana/install/active_release/bin:$PATH"
    solana --version
    ```

2.  **Configure Solana CLI for Devnet/Mainnet-beta:**
    ```bash
    solana config set --url https://api.mainnet-beta.solana.com
    # Or for Devnet:
    # solana config set --url https://api.devnet.solana.com
    ```

3.  **Generate a Keypair (for bot operations):**
    ```bash
    solana-keygen new --outfile ~/.config/solana/bot-keypair.json --no-passphrase
    ```

4.  **Install Node.js & Yarn/NPM:**
    Ensure you have a recent version of Node.js (LTS recommended) and a package manager.

5.  **Initialize your project and install core SDKs:**
    ```bash
    mkdir solana-bot && cd solana-bot
    yarn init -y
    yarn add @solana/web3.js @project-serum/serum @coral-xyz/anchor @jup-ag/core
    yarn add -D @types/node ts-node typescript
    ```

## Key Techniques

### 1. Direct DEX Interaction (OpenBook V2)

Interacting directly with OpenBook V2 (the successor to Serum) is fundamental for on-chain market making and arbitrage. You'll need to fetch market state, parse orderbooks, and send orders.

```typescript
import { Connection, PublicKey, Keypair, Transaction, VersionedTransaction } from '@solana/web3.js';
import { OpenBookV2Client, Market, Orderbook } from '@openbook-dex/openbook-v2';
import BN from 'bn.js';

// Replace with your actual keypair and OpenBook V2 program ID
const WALLET_KEYPAIR = Keypair.fromSecretKey(Uint8Array.from(JSON.parse(require('fs').readFileSync('~/.config/solana/bot-keypair.json', 'utf-8'))));
const OPENBOOK_V2_PROGRAM_ID = new PublicKey('opnb2LAfSTL6c2pdTfKqGyFJbZRm49pNq7ieRxf4ETQ'); // Example ID, verify current
const USDC_SOL_MARKET_ID = new PublicKey('7z275t4j5V2c2pdTfKqGyFJbZRm49pNq7ieRxf4ETQ'); // Example market ID, verify current

async function placeOpenBookOrder() {
    const connection = new Connection('https://api.mainnet-beta.solana.com', 'confirmed');
    const client = new OpenBookV2Client(OPENBOOK_V2_PROGRAM_ID, connection);

    // Fetch market data
    const market = await client.getMarket(USDC_SOL_MARKET_ID);
    if (!market) {
        console.error('Market not found.');
        return;
    }

    // Fetch orderbooks
    const bids = await client.getBidOrderbook(market);
    const asks = await client.getAskOrderbook(market);

    console.log('Top Bid:', bids.getL2(1));
    console.log('Top Ask:', asks.getL2(1));

    // Example: Place a limit buy order for 0.01 SOL at 20 USDC
    const price = 20; // USDC per SOL
    const quantity = 0.01; // SOL
    const limitPriceBn = new BN(price * Math.pow(10, market.quoteDecimals));
    const maxBaseQtyBn = new BN(quantity * Math.pow(10, market.baseDecimals));
    const maxQuoteQtyBn = new BN(maxBaseQtyBn.mul(limitPriceBn).div(new BN(Math.pow(10, market.quoteDecimals))));

    // Build the place order instruction (simplified example, actual params are complex)
    // You'd typically use client.placeOrder() which handles account derivation
    const placeOrderIx = await client.getPlaceOrderInstruction(
        market.address,
        WALLET_KEYPAIR.publicKey,
        'buy', // 'buy' or 'sell'
        limitPriceBn,
        maxBaseQtyBn,
        maxQuoteQtyBn,
        'limit', // 'limit', 'ioc', 'postOnly'
        true, // selfTradeBehavior: 'decrementTake'
        undefined, // clientOrderId
        undefined, // referral
    );

    const transaction = new Transaction().add(placeOrderIx);
    const signature = await connection.sendTransaction(transaction, [WALLET_KEYPAIR]);
    console.log('Order placed, signature:', signature);
    await connection.confirmTransaction(signature, 'processed');
    console.log('Transaction confirmed.');
}

// placeOpenBookOrder();
```

### 2. Transaction Building & Priority Fees

Solana transactions require careful construction, especially when competing for block space. Using `ComputeBudget` instructions allows you to specify compute units and pay priority fees.

```typescript
import { Connection, PublicKey, Keypair, Transaction, SystemProgram, ComputeBudgetProgram } from '@solana/web3.js';

const WALLET_KEYPAIR = Keypair.fromSecretKey(Uint8Array.from(JSON.parse(require('fs').readFileSync('~/.config/solana/bot-keypair.json', 'utf-8'))));

async function sendTransactionWithPriority() {
    const connection = new Connection('https://api.mainnet-beta.solana.com', 'confirmed');

    // Create a dummy transaction (e.g., transfer 0 SOL to self)
    const transaction = new Transaction().add(
        SystemProgram.transfer({
            fromPubkey: WALLET_KEYPAIR.publicKey,
            toPubkey: WALLET_KEYPAIR.publicKey,
            lamports: 0,
        })
    );

    // Add ComputeBudget instructions
    // Set max compute units for the transaction (e.g., 200,000)
    transaction.add(
        ComputeBudgetProgram.setComputeUnitLimit({ units: 200_000 })
    );
    // Set priority fee in micro-lamports per compute unit (e.g., 1000 micro-lamports = 0.000001 SOL per CU)
    // A high fee (e.g., 100_000) might be needed for urgent transactions
    transaction.add(
        ComputeBudgetProgram.setComputeUnitPrice({ microLamports: 1000 })
    );

    // Get the latest blockhash
    transaction.recentBlockhash = (await connection.getLatestBlockhash('finalized')).blockhash;
    transaction.feePayer = WALLET_KEYPAIR.publicKey;

    // Sign and send the transaction
    try {
        const signature = await connection.sendTransaction(transaction, [WALLET_KEYPAIR], {
            skipPreflight: false, // Always preflight in production
            preflightCommitment: 'confirmed'
        });
        console.log('Transaction sent with priority, signature:', signature);
        await connection.confirmTransaction(signature, 'confirmed');
        console.log('Transaction confirmed.');
    } catch (error) {
        console.error('Transaction failed:', error);
        // Implement retry logic or more granular error handling
    }
}

// sendTransactionWithPriority();
```

### 3. Real-time Data with Websockets

For immediate reactions to market changes or portfolio updates, websockets are essential. `onAccountChange` and `onProgramAccountChange` provide near-instant notifications.

```typescript
import { Connection, PublicKey, AccountChangeCallback } from '@solana/web3.js';

const connection = new Connection('https://api.mainnet-beta.solana.com', 'processed'); // 'processed' for faster updates

async function subscribeToAccountChanges() {
    // Example: Subscribe to a specific token account (e.g., your USDC account)
    const myUsdcAccount = new PublicKey('YOUR_USDC_TOKEN_ACCOUNT_ADDRESS_HERE');

    const callback: AccountChangeCallback = (accountInfo, context) => {
        console.log(`Account ${myUsdcAccount.toBase58()} changed at slot ${context.slot}`);
        // Parse accountInfo.data to get new balance, owner, etc.
        // For token accounts, you'd deserialize with @solana/spl-token
        console.log('New data length:', accountInfo.data.length);
        console.log('New lamports:', accountInfo.lamports);
    };

    const subscriptionId = connection.onAccountChange(
        myUsdcAccount,
        callback,
        'processed' // Commitment level for updates
    );

    console.log(`Subscribed to ${myUsdcAccount.toBase58()}, subscription ID: ${subscriptionId}`);

    // To unsubscribe later:
    // await connection.removeAccountChangeListener(subscriptionId);
}

async function subscribeToProgramAccountChanges() {
    // Example: Subscribe to all accounts owned by a specific program (e.g., all OpenBook V2 markets)
    const openbookProgramId = new PublicKey('opnb2LAfSTL6c2pdTfKqGyFJbZRm49pNq7ieRxf4ETQ');

    const subscriptionId = connection.onProgramAccountChange(
        openbookProgramId,
        (keyedAccountInfo, context) => {
            console.log(`Program account ${keyedAccountInfo.pubkey.toBase58()} changed at slot ${context.slot}`);
            // keyedAccountInfo.accountInfo contains the new data
            // You can filter or parse based on account type (e.g., market, orderbook, event queue)
        },
        'processed', // Commitment level
        [{ dataSize: 3200 }] // Optional: Filter by data size for OpenBook V2 Market accounts
    );

    console.log(`Subscribed to program ${openbookProgramId.toBase58()}, subscription ID: ${subscriptionId}`);

    // To unsubscribe later:
    // await connection.removeProgramAccountChangeListener(subscriptionId);
}

// subscribeToAccountChanges();
// subscribeToProgramAccountChanges();
```

### 4. Anchor Program Client Interaction

If your bot relies on custom on-chain logic, you'll use Anchor to define and interact with your programs. This example shows how to initialize an Anchor client and call an instruction.

```typescript
import * as anchor from '@coral-xyz/anchor';
import { Program, AnchorProvider, web3 } from '@coral-xyz/anchor';
// Anchor client setup would follow standard patterns
```

## Anti-Patterns

*   **Ignoring Solana Transaction Confirmation Semantics.** Treating `processed` commitment as final leads to acting on transactions that may be rolled back during slot leader changes. Use `confirmed` for trading decisions and `finalized` for settlement.

*   **Single RPC Endpoint Without Failover.** Running a trading bot through one Solana RPC node means any node downtime or rate limiting halts trading. Use multiple RPC providers with health-check-based failover.

*   **No Priority Fee Calculation.** Submitting transactions without compute unit price during network congestion causes trades to be dropped or delayed indefinitely. Dynamically calculate priority fees based on recent block statistics.

*   **Polling Account State Instead of Subscribing.** Using repeated `getAccountInfo` calls instead of WebSocket subscriptions for price and order updates introduces unnecessary latency and RPC overhead.

*   **Unbounded Compute Unit Budget.** Setting excessively high compute unit limits wastes SOL on priority fees proportional to the budget. Simulate transactions to determine actual compute needs and set tight budgets with a small buffer.

## Version and Evidence Check

Verify current priority-fee, blockhash validity, transaction lifecycle, RPC commitment and anti-duplicate mechanisms before live execution.
