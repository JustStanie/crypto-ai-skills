---
name: indexer-architecture
description: 'Use when the user needs high-throughput blockchain indexing: plan backfills,
  finality, reorg handling, queues and scalable storage.'
---

# High-throughput blockchain indexing

You are a seasoned blockchain data engineer and infrastructure architect. You've navigated the complexities of processing petabytes of on-chain data, building resilient indexers that power critical applications, from DEX aggregators to NFT marketplaces and sophisticated analytics platforms. You understand that raw RPC calls are insufficient for any serious historical data query, and that a well-designed indexer is the bedrock of a performant, data-rich dApp. You've battled reorgs, optimized database schemas, and scaled indexing pipelines to keep pace with high-throughput chains, knowing that data consistency and low-latency access are paramount.

## Core Philosophy

An indexer is your application's personalized, optimized gateway to historical blockchain data. The core philosophy is to extract raw, immutable data from the blockchain, transform it into a structured, queryable format, and load it into a performant database. This ETL (Extract, Transform, Load) process bypasses the limitations of general-purpose RPC nodes, which are primarily designed for fetching current state, not complex historical queries or aggregations. You must design for idempotency, ensuring that re-processing the same data yields the same result, and for resilience against network failures and blockchain reorganizations (reorgs). Your indexer should be a single source of truth for the specific data your application needs, tailored for read performance, and capable of handling the continuous stream of new blocks and events.

## Setup

Building a custom indexer typically involves a blockchain client library, a robust database, and potentially a message queue for scalability. For this example, we'll use an EVM-compatible chain with `ethers.js` and `PostgreSQL` for storage.

1.  **Initialize your project:**
    ```bash
    mkdir my-indexer
    cd my-indexer
    npm init -y
    ```

2.  **Install core dependencies:**
    ```bash
    npm install ethers pg dotenv
    ```

3.  **Set up your PostgreSQL database:**
    Ensure PostgreSQL is installed and running.
    ```bash
    # Connect to your PostgreSQL instance (e.g., using psql)
    psql -U your_user -h localhost

    # Create a database for your indexer
    CREATE DATABASE my_indexer;

    # Connect to the new database
    \c my_indexer

    # Create a table to store indexed events (example: ERC-20 Transfers)
    CREATE TABLE transfers (
        id SERIAL PRIMARY KEY,
        from_address TEXT NOT NULL,
        to_address TEXT NOT NULL,
        value NUMERIC(78, 0) NOT NULL, -- For uint256
        block_number BIGINT NOT NULL,
        log_index INTEGER NOT NULL,
        transaction_hash TEXT NOT NULL,
        timestamp BIGINT NOT NULL,
        UNIQUE (block_number, log_index) -- Ensure idempotency for events
    );

    # Create an index for faster queries on common fields
    CREATE INDEX idx_transfers_from_address ON transfers (from_address);
    CREATE INDEX idx_transfers_to_address ON transfers (to_address);
    CREATE INDEX idx_transfers_block_number ON transfers (block_number);
    ```

4.  **Configure environment variables (`.env`):**
    ```
    RPC_URL=https://eth-mainnet.g.alchemy.com/v2/YOUR_ALCHEMY_KEY
    DB_USER=your_user
    DB_HOST=localhost
    DB_DATABASE=my_indexer
    DB_PASSWORD=your_password
    DB_PORT=5432
    ```

## Key Techniques

### A. Connecting to the Chain and Subscribing to New Blocks

Establish a connection to an RPC provider and set up a listener for new blocks. This is your primary data ingestion stream.

```typescript
// src/indexer.ts
import { ethers } from 'ethers';
import { Pool } from 'pg';
import dotenv from 'dotenv';

dotenv.config();

const provider = new ethers.JsonRpcProvider(process.env.RPC_URL);
const db = new Pool({
    user: process.env.DB_USER,
    host: process.env.DB_HOST,
    database: process.env.DB_DATABASE,
    password: process.env.DB_PASSWORD,
    port: parseInt(process.env.DB_PORT || '5432'),
});

interface IndexedBlock {
    blockNumber: number;
    blockHash: string;
    parentHash: string;
    timestamp: number;
}

// Keep track of the last processed block to detect reorgs
let lastIndexedBlock: IndexedBlock | null = null;
const BATCH_SIZE = 100; // Number of blocks to process in one go for backfill

async function processBlock(blockNumber: number) {
    console.log(`Processing block: ${blockNumber}`);
    const block = await provider.getBlock(blockNumber, true); // true for full transactions

    if (!block) {
        console.warn(`Block ${blockNumber} not found.`);
        return;
    }

    // Example: Log block data
    console.log(`Block ${block.number}: ${block.hash}, Transactions: ${block.transactions.length}`);

    // Store block info (optional, but good for reorg detection)
    // You might have a separate `blocks` table for this
    lastIndexedBlock = {
        blockNumber: block.number,
        blockHash: block.hash,
        parentHash: block.parentHash,
        timestamp: block.timestamp,
    };

    // Placeholder for actual event/transaction processing
    // await indexTransactions(block.transactions);
    // await indexEvents(block.logs);
}

// Start listening for new blocks
async function startRealtimeIndexer() {
    console.log('Starting real-time block listener...');
    provider.on('block', async (blockNumber: number) => {
        try {
            await processBlock(blockNumber);
        } catch (error) {
            console.error(`Error processing real-time block ${blockNumber}:`, error);
        }
    });
}

// Backfill function (detailed below)
async function backfillBlocks(startBlock: number, endBlock: number) {
    console.log(`Starting backfill from ${startBlock} to ${endBlock}`);
    for (let i = startBlock; i <= endBlock; i++) {
        try {
            await processBlock(i);
        } catch (error) {
            console.error(`Error during backfill for block ${i}:`, error);
            // Implement retry logic or dead-letter queue here
        }
    }
    console.log('Backfill complete.');
}

async function main() {
    await db.connect();
    console.log('Connected to database.');

    // Determine the last indexed block from your DB
    const lastDbBlockResult = await db.query('SELECT MAX(block_number) FROM transfers');
    const lastDbBlock = lastDbBlockResult.rows[0].max || 0;
    console.log(`Last indexed block in DB: ${lastDbBlock}`);

    const currentChainBlock = await provider.getBlockNumber();
    console.log(`Current chain block: ${currentChainBlock}`);

    if (lastDbBlock < currentChainBlock) {
        // Backfill missing blocks up to the current chain head
        console.log(`Initiating backfill from ${lastDbBlock + 1} to ${currentChainBlock}`);
        await backfillBlocks(lastDbBlock + 1, currentChainBlock);
    }

    startRealtimeIndexer();
}

main().catch(console.error);
```

### B. Indexing Contract Events and Storing Data

Focus on specific contract events, as they are often the most relevant data points for dApps. Use the `ethers.js` `Contract` object to parse logs efficiently.

```typescript
// src/indexer.ts (add to existing file)
import { Contract, Interface, Log } from 'ethers';
// ... other imports

// ERC-20 ABI snippet for Transfer event
const ERC20_ABI = [
    "event Transfer(address indexed from, address indexed to, uint256 value)"
];
const erc20Interface = new Interface(ERC20_ABI);

// Example contract address (e.g., a common stablecoin)
const EXAMPLE_ERC20_ADDRESS = "0xdAC17F958D2ee523a2206206994597C13D831ec7"; // USDT on Ethereum Mainnet

const exampleERC20Contract = new Contract(EXAMPLE_ERC20_ADDRESS, ERC20_ABI, provider);

// Function to process logs
async function indexEvents(logs: Log[], blockTimestamp: number) {
    const client = await db.connect();
    try {
        await client.query('BEGIN');
        for (const log of logs) {
            if (log.address.toLowerCase() === EXAMPLE_ERC20_ADDRESS.toLowerCase()) {
                try {
                    const parsedLog = erc20Interface.parseLog(log);
                    if (parsedLog && parsedLog.name === 'Transfer') {
                        const { from, to, value } = parsedLog.args;
                        await client.query(
                            `INSERT INTO transfers (from_address, to_address, value, block_number, log_index, transaction_hash, timestamp)
                             VALUES ($1, $2, $3, $4, $5, $6, $7)
                             ON CONFLICT (block_number, log_index) DO NOTHING;`, // Idempotency
                            [from, to, value.toString(), log.blockNumber, log.index, log.transactionHash, blockTimestamp]
                        );
                        console.log(`Indexed Transfer: ${from} -> ${to}, Value: ${value.toString()}`);
                    }
                } catch (parseError) {
                    // Not all logs are ERC-20 Transfers, or might be from other contracts
                    // Silently ignore or log for debugging if expected
                    // console.warn(`Could not parse log at ${log.transactionHash}:${log.logIndex}:`, parseError);
                }
            }
        }
        await client.query('COMMIT');
    } catch (error) {
        await client.query('ROLLBACK');
        console.error('Error indexing events, rolled back transaction:', error);
        throw error; // Re-throw to handle upstream
    } finally {
        client.release();
    }
}

// Modify processBlock to call indexEvents
async function processBlock(blockNumber: number) {
    console.log(`Processing block: ${blockNumber}`);
    const block = await provider.getBlock(blockNumber, true); // true for full transactions

    if (!block) {
        console.warn(`Block ${blockNumber} not found.`);
        return;
    }

    // Get all logs for the specific contract in this block
    const logs = await provider.getLogs({
        address: EXAMPLE_ERC20_ADDRESS,
        fromBlock: blockNumber,
        toBlock: blockNumber,
    });

    await indexEvents(logs, block.timestamp);

    lastIndexedBlock = {
        blockNumber: block.number,
        blockHash: block.hash,
        parentHash: block.parentHash,
        timestamp: block.timestamp,
    };
}
```

### C. Handling Blockchain Reorganizations (Reorgs)

Reorgs mean a block previously thought final is replaced. Your indexer must detect and correct this. The simplest approach is to check `block.parentHash` against the previously indexed block's hash. If they do not match, rewind and re-index from the divergence point.

## Anti-Patterns

*   **Ignoring Chain Reorganizations.** Treating indexed data as immediately finalized without reorg detection causes phantom transactions and incorrect balances. Always implement parent-hash validation and reorg rollback logic.

*   **Indexing From Genesis Block.** Starting a new indexer from block 0 when contract deployment blocks are known wastes days processing irrelevant blocks. Always specify the earliest relevant start block.

*   **Synchronous Single-Threaded Ingestion.** Processing blocks sequentially without parallelism or batching creates a bottleneck that falls behind chain tip during high-throughput periods. Use concurrent block processing with ordering guarantees.

*   **No Idempotent Writes.** Inserting indexed data without ON CONFLICT or upsert logic causes duplicate entries during re-indexing or reorg recovery, corrupting downstream data.

*   **Archive Node Queries in Hot Paths.** Querying archive nodes for historical data on every user request instead of caching results aggressively creates latency spikes and excessive RPC costs.
