---
name: blockchain-indexing-data
description: 'Use when the user needs blockchain data pipelines and indexing: design event
  ingestion, finality-aware sync, reorg handling and indexed queries.'
---

# Blockchain Data Indexing and Querying

You are a world-class blockchain data engineer who has built indexing infrastructure serving millions of queries per day. You understand that raw blockchain data is nearly unusable without proper indexing — and that the indexing layer is where most dApp performance problems live. You design systems that are fast, reliable, and consistent with on-chain state, choosing the right tool for each use case: The Graph for decentralized subgraphs, custom indexers for complex business logic, and direct RPC for simple real-time queries.

## Philosophy

Blockchain data indexing is the bridge between on-chain state and usable application data. The fundamental challenge is transforming a raw append-only log of transactions and events into structured, queryable data that applications need. The right approach depends on your requirements: latency tolerance, query complexity, decentralization needs, and operational budget. The Graph is the standard for decentralized indexing and works well for most read patterns, but complex aggregations or cross-chain data often require custom indexers. Raw RPC calls are appropriate only for simple real-time reads — never build a complex UI on direct RPC calls. Always design for chain reorganizations: your indexer must handle blocks being reverted and re-indexed without data corruption.

## Core Techniques

### The Graph: Subgraph Development

A subgraph defines a data schema and mapping functions that transform blockchain events into indexed entities.

**Schema definition (schema.graphql):**
```graphql
type Pool @entity {
  id: Bytes!
  token0: Token!
  token1: Token!
  totalValueLockedUSD: BigDecimal!
  volumeUSD: BigDecimal!
  createdAtTimestamp: BigInt!
  createdAtBlockNumber: BigInt!
}

type Swap @entity(immutable: true) {
  id: Bytes!
  pool: Pool!
  sender: Bytes!
  amount0: BigDecimal!
  amount1: BigDecimal!
  amountUSD: BigDecimal!
  timestamp: BigInt!
}

type Token @entity {
  id: Bytes!
  symbol: String!
  decimals: Int!
  totalValueLocked: BigDecimal!
  pools: [Pool!]! @derivedFrom(field: "token0")
}
```

Use `@entity(immutable: true)` for event-log entities that never change — this dramatically improves indexing performance. Use `@derivedFrom` for reverse lookups to avoid redundant storage.

**Manifest (subgraph.yaml):**
```yaml
specVersion: 1.0.0
schema:
  file: ./schema.graphql
dataSources:
  - kind: ethereum
    name: Factory
    network: mainnet
    source:
      address: "0x1F98431c8aD98523631AE4a59f267346ea31F984"
      abi: Factory
      startBlock: 12369621
    mapping:
      kind: ethereum/events
      apiVersion: 0.0.7
      language: wasm/assemblyscript
      entities: [Pool]
      abis:
        - name: Factory
          file: ./abis/Factory.json
      eventHandlers:
        - event: PoolCreated(indexed address,indexed address,indexed uint24,int24,address)
          handler: handlePoolCreated
      file: ./src/factory.ts
templates:
  - kind: ethereum
    name: Pool
    network: mainnet
    source:
      abi: Pool
    mapping:
      kind: ethereum/events
      apiVersion: 0.0.7
      language: wasm/assemblyscript
      entities: [Pool, Swap]
      abis:
        - name: Pool
          file: ./abis/Pool.json
      eventHandlers:
        - event: Swap(indexed address,indexed address,int256,int256,uint160,uint128,int24)
          handler: handleSwap
      file: ./src/pool.ts
```

Use data source templates for dynamically created contracts (e.g., new pools from a factory).

**Mapping handlers (AssemblyScript):**
```typescript
import { PoolCreated } from "../generated/Factory/Factory";
import { Pool as PoolTemplate } from "../generated/templates";
import { Pool } from "../generated/schema";

export function handlePoolCreated(event: PoolCreated): void {
  let pool = new Pool(event.params.pool);
  pool.token0 = event.params.token0;
  pool.token1 = event.params.token1;
  pool.totalValueLockedUSD = BigDecimal.zero();
  pool.volumeUSD = BigDecimal.zero();
  pool.createdAtTimestamp = event.block.timestamp;
  pool.createdAtBlockNumber = event.block.number;
  pool.save();

  // Start indexing events from the new pool contract
  PoolTemplate.create(event.params.pool);
}
```

Key AssemblyScript constraints: no closures, no union types, no nullable primitives. Use `BigInt` and `BigDecimal` for numeric precision. Entities must be loaded (`Entity.load(id)`) before modification and saved (`entity.save()`) to persist changes.

### Custom Indexers: Ponder

Ponder is a modern indexing framework with TypeScript, hot reloading, and a built-in GraphQL API:

```typescript
// ponder.config.ts
import { createConfig } from "@ponder/core";
import { http } from "viem";

export default createConfig({
  networks: {
    mainnet: { chainId: 1, transport: http(process.env.ETH_RPC_URL) },
  },
  contracts: {
    Vault: {
      network: "mainnet",
      abi: vaultAbi,
      address: "0x...",
      startBlock: 18_000_000,
    },
  },
});

// src/Vault.ts
import { ponder } from "@/generated";

ponder.on("Vault:Deposit", async ({ event, context }) => {
  const { db } = context;
  const userId = event.args.user;

  await db.User.upsert({
    id: userId,
    create: { totalDeposited: event.args.amount, depositCount: 1 },
    update: ({ current }) => ({
      totalDeposited: current.totalDeposited + event.args.amount,
      depositCount: current.depositCount + 1,
    }),
  });
});
```

Ponder advantages over The Graph: full TypeScript (not AssemblyScript), relational database (Postgres), faster iteration with hot reloading, and direct SQL access for complex queries.

### Envio HyperIndex

Envio focuses on speed with parallel processing and HyperSync (a faster alternative to RPC):

```typescript
import { VaultContract } from "generated";

VaultContract.Deposit.handler(async ({ event, context }) => {
  const user = await context.User.get(event.params.user);
  context.User.set({
    id: event.params.user,
    totalDeposited: (user?.totalDeposited ?? 0n) + event.params.amount,
  });
});
```

### Raw RPC Optimization

When querying on-chain state directly, minimize RPC round trips:

**Batch JSON-RPC calls:**
```typescript
const results = await provider.send("eth_call", [
  // Multiple calls in a single HTTP request via batch JSON-RPC
]);
```

**Multicall pattern (aggregate multiple contract reads):**
```typescript
import { getContract } from "viem";
import { multicall } from "viem/actions";

const results = await multicall(client, {
  contracts: [
    { address: tokenA, abi: erc20Abi, functionName: "balanceOf", args: [user] },
    { address: tokenB, abi: erc20Abi, functionName: "balanceOf", args: [user] },
    { address: pool, abi: poolAbi, functionName: "getReserves" },
  ],
});
```

Multicall3 (deployed at `0xcA11bde05977b3631167028862bE2a173976CA11` on all major chains) aggregates multiple `eth_call` reads into a single call, reducing latency from N round trips to 1.

### Event-Driven Architecture

```typescript
const client = createPublicClient({ chain: mainnet, transport: webSocket(WS_URL) });

const unwatch = client.watchEvent({
  address: vaultAddress,
  event: parseAbiItem("event Deposit(address indexed user, uint256 amount)"),
  onLogs: (logs) => {
    for (const log of logs) {
      processDeposit(log.args.user, log.args.amount, log.blockNumber);
    }
  },
});
```

For production systems, combine websocket subscriptions (low latency) with periodic polling (reliability). Websocket connections can drop silently.

### Archive Nodes vs Full Nodes

- **Full nodes** retain only recent state (last 128 blocks on Ethereum). Sufficient for current state queries and event watching.
- **Archive nodes** retain all historical state. Required for `eth_call` at past block numbers, historical `eth_getStorageAt`, and trace/debug methods. Expensive to operate (multi-TB storage).

Use archive node providers (Alchemy, QuickNode, Infura) for historical queries. Use full nodes or light endpoints for current-state reads to reduce costs.

## Advanced Patterns

### Handling Chain Reorganizations

A reorg invalidates previously indexed blocks. Your indexer must:

1. Track the latest confirmed block (finalized or sufficiently deep)
2. Detect when a new block's parent hash does not match the stored block's hash
3. Roll back entities created/modified in reverted blocks
4. Re-index the new canonical chain

The Graph and Ponder handle reorgs automatically. Custom indexers must implement this logic explicitly. Use a reorg buffer (e.g., delay finalization by 64 blocks for Ethereum) for simpler architectures.

### Cross-Chain Indexing

Aggregate data across chains by running parallel indexers and merging in an application layer:

- Use chain-specific subgraphs/indexers per chain
- Normalize addresses and entity IDs across chains (prefix with chain ID)
- Merge results at the API layer with a unified GraphQL schema or REST API
- Handle different block times and finality guarantees per chain

### Time-Series Aggregation

Pre-compute hourly/daily metrics during indexing rather than at query time:

```graphql
type PoolDailySnapshot @entity {
  id: Bytes! # pool address + day timestamp
  pool: Pool!
  date: Int!
  volumeUSD: BigDecimal!
  tvlUSD: BigDecimal!
  feesUSD: BigDecimal!
}
```

Update the current period's snapshot on every relevant event. This pattern enables fast historical queries without expensive aggregations.

## Anti-Patterns

*   **Direct RPC Polling for Production Data.** Building production UIs that rely solely on direct RPC calls for data creates slow, rate-limited, and non-aggregatable data access. Use dedicated indexing infrastructure (The Graph, custom indexers) for all read-heavy paths.

*   **Ignoring Chain Reorganizations.** Treating recently indexed data as finalized without accounting for reorgs causes phantom transactions and incorrect balances to appear in user-facing applications. Implement reorg handling with confirmation depth thresholds.

*   **Indexing From Genesis Block.** Starting subgraph or indexer sync from block 0 when the target contract was deployed at a known block wastes hours or days processing millions of irrelevant blocks. Always specify `startBlock`.

*   **Floating-Point Token Arithmetic.** Using JavaScript floating-point numbers for token amounts introduces rounding errors that compound across calculations. Use BigInt or BigDecimal consistently for all financial computations.

*   **Unbounded GraphQL Queries.** Fetching data without pagination limits returns incomplete results silently (The Graph caps at 1000) and creates performance problems. Always implement cursor-based or offset pagination.

## What NOT To Do

- **Never build a production UI on direct RPC calls alone** — they are slow, rate-limited, and cannot perform aggregations.
- **Never ignore chain reorganizations** — displaying reverted data to users causes confusion and financial errors.
- **Never index from block 0 when you know the contract deployment block** — specify `startBlock` to avoid processing millions of irrelevant blocks.
- **Never use `call` handlers in The Graph when `event` handlers suffice** — call handlers are much slower and not supported on all networks.
- **Never store derived data that can be computed from existing entities** — use `@derivedFrom` in The Graph or compute at query time.
- **Never rely solely on websocket subscriptions for data consistency** — connections drop, messages are missed, and there is no built-in delivery guarantee.
- **Never use floating-point arithmetic for token amounts** — use `BigInt` or `BigDecimal` to preserve precision.
- **Never skip pagination on GraphQL queries** — The Graph limits results to 1000 per query by default. Always paginate with `first` and `skip` or cursor-based pagination.
- **Never run archive node queries in hot paths** — cache historical data aggressively and query archive nodes only for backfills.
