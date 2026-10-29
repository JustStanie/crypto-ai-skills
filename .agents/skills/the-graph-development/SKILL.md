---
name: the-graph-development
description: 'Use when the user needs the graph indexing development: configure subgraphs,
  mappings, schema entities and deployment workflows.'
---

# The Graph — Web3 Development

You are an expert in The Graph protocol for building subgraphs that index blockchain events and expose queryable GraphQL APIs for decentralized applications.

## Overview

The Graph is a decentralized indexing protocol that allows developers to build and publish subgraphs -- open APIs that index blockchain data and make it queryable via GraphQL. Instead of reading blockchain state directly (which is slow and limited), dApps query subgraphs for historical event data, aggregated metrics, and complex relational queries. The Graph supports Ethereum, Polygon, Arbitrum, Optimism, and many other EVM chains.

## Core Philosophy

The Graph transforms raw blockchain event logs into structured, queryable data through deterministic indexing. The fundamental insight is that blockchains are write-optimized append-only logs, but applications need read-optimized relational data. Subgraphs bridge this gap by defining entity schemas and event-to-entity mapping handlers that run deterministically across the decentralized Graph network. Build subgraphs as the canonical data layer for your dApp rather than maintaining custom indexing infrastructure.

## Anti-Patterns

*   **Call Handlers Instead of Event Handlers.** Using call handlers when event handlers would suffice dramatically slows indexing and is not supported on all networks. Emit events for all state changes and index those.

*   **Storing Derived Data That Can Be Computed.** Persisting values that could be calculated from existing entities using `@derivedFrom` wastes storage and creates sync issues when source data changes.

*   **No Start Block Specification.** Deploying subgraphs without specifying `startBlock` in the manifest causes indexing from genesis, processing millions of irrelevant blocks before reaching your contract's deployment.

*   **Unbounded Entity Queries Without Pagination.** Fetching entities without `first` and `skip` parameters silently truncates results at The Graph's 1000-entity default limit, producing incomplete data.

*   **Synchronous Frontend Queries Against Indexing Subgraph.** Displaying real-time data from a subgraph that is still syncing historical blocks shows stale or incomplete data without indication to the user. Always check indexing status.

## Core Concepts

### Subgraph Components

A subgraph consists of three files:

1. **`subgraph.yaml`** -- manifest that defines data sources, contracts, and event handlers
2. **`schema.graphql`** -- GraphQL schema defining entity types to store
3. **`mapping.ts`** -- AssemblyScript handlers that process events and update entities

### Subgraph Manifest

```yaml
# subgraph.yaml
specVersion: 1.0.0
indexerHints:
  prune: auto
schema:
  file: ./schema.graphql
dataSources:
  - kind: ethereum
    name: Vault
    network: mainnet
    source:
      address: "0x1234567890abcdef1234567890abcdef12345678"
      abi: Vault
      startBlock: 18000000  # Block when contract was deployed
    mapping:
      kind: ethereum/events
      apiVersion: 0.0.7
      language: wasm/assemblyscript
      entities:
        - Deposit
        - Withdrawal
        - User
      abis:
        - name: Vault
          file: ./abis/Vault.json
      eventHandlers:
        - event: Deposit(indexed address,uint256)
          handler: handleDeposit
        - event: Withdrawal(indexed address,uint256)
          handler: handleWithdrawal
      file: ./src/mapping.ts
```

### GraphQL Schema

```graphql
# schema.graphql
type User @entity {
  id: Bytes!  # address
  totalDeposited: BigInt!
  totalWithdrawn: BigInt!
  currentBalance: BigInt!
  deposits: [Deposit!]! @derivedFrom(field: "user")
  withdrawals: [Withdrawal!]! @derivedFrom(field: "user")
  lastActiveAt: BigInt!
}

type Deposit @entity(immutable: true) {
  id: Bytes!  # tx hash + log index
  user: User!
  amount: BigInt!
  timestamp: BigInt!
  blockNumber: BigInt!
  transactionHash: Bytes!
}

type Withdrawal @entity(immutable: true) {
  id: Bytes!
  user: User!
  amount: BigInt!
  timestamp: BigInt!
  blockNumber: BigInt!
  transactionHash: Bytes!
}

type VaultStats @entity {
  id: Bytes!  # singleton: 0x00
  totalDeposits: BigInt!
  totalWithdrawals: BigInt!
  totalValueLocked: BigInt!
  uniqueUsers: BigInt!
}
```

### Event Handlers (Mappings)

```typescript
// src/mapping.ts
import { Deposit as DepositEvent, Withdrawal as WithdrawalEvent } from "../generated/Vault/Vault";
import { Deposit, Withdrawal, User, VaultStats } from "../generated/schema";
import { BigInt, Bytes } from "@graphprotocol/graph-ts";

const STATS_ID = Bytes.fromHexString("0x00");

function getOrCreateUser(address: Bytes): User {
  let user = User.load(address);
  if (user == null) {
    user = new User(address);
    user.totalDeposited = BigInt.zero();
    user.totalWithdrawn = BigInt.zero();
    user.currentBalance = BigInt.zero();
    user.lastActiveAt = BigInt.zero();

    // Increment unique users count
    let stats = getOrCreateStats();
    stats.uniqueUsers = stats.uniqueUsers.plus(BigInt.fromI32(1));
    stats.save();
  }
  return user;
}

function getOrCreateStats(): VaultStats {
  let stats = VaultStats.load(STATS_ID);
  if (stats == null) {
    stats = new VaultStats(STATS_ID);
    stats.totalDeposits = BigInt.zero();
    stats.totalWithdrawals = BigInt.zero();
    stats.totalValueLocked = BigInt.zero();
    stats.uniqueUsers = BigInt.zero();
  }
  return stats;
}

export function handleDeposit(event: DepositEvent): void {
  // Create immutable Deposit entity
  let deposit = new Deposit(
    event.transaction.hash.concatI32(event.logIndex.toI32())
  );
  deposit.user = event.params.user;
  deposit.amount = event.params.amount;
  deposit.timestamp = event.block.timestamp;
  deposit.blockNumber = event.block.number;
  deposit.transactionHash = event.transaction.hash;
  deposit.save();

  // Update user aggregates
  let user = getOrCreateUser(event.params.user);
  user.totalDeposited = user.totalDeposited.plus(event.params.amount);
  user.currentBalance = user.currentBalance.plus(event.params.amount);
  user.lastActiveAt = event.block.timestamp;
  user.save();

  // Update global stats
  let stats = getOrCreateStats();
  stats.totalDeposits = stats.totalDeposits.plus(event.params.amount);
  stats.totalValueLocked = stats.totalValueLocked.plus(event.params.amount);
  stats.save();
}

export function handleWithdrawal(event: WithdrawalEvent): void {
  let withdrawal = new Withdrawal(
    event.transaction.hash.concatI32(event.logIndex.toI32())
  );
  withdrawal.user = event.params.user;
  withdrawal.amount = event.params.amount;
  withdrawal.timestamp = event.block.timestamp;
  withdrawal.blockNumber = event.block.number;
  withdrawal.transactionHash = event.transaction.hash;
  withdrawal.save();

  let user = getOrCreateUser(event.params.user);
  user.totalWithdrawn = user.totalWithdrawn.plus(event.params.amount);
  user.currentBalance = user.currentBalance.minus(event.params.amount);
  user.lastActiveAt = event.block.timestamp;
  user.save();

  let stats = getOrCreateStats();
  stats.totalWithdrawals = stats.totalWithdrawals.plus(event.params.amount);
  stats.totalValueLocked = stats.totalValueLocked.minus(event.params.amount);
  stats.save();
}
```

### Querying a Subgraph

```typescript
const SUBGRAPH_URL = "https://api.studio.thegraph.com/query/YOUR_ID/vault/version/latest";

// Fetch top depositors
async function getTopDepositors(limit: number = 10) {
  const query = `
    query TopDepositors($limit: Int!) {
      users(
        first: $limit
        orderBy: currentBalance
        orderDirection: desc
        where: { currentBalance_gt: "0" }
      ) {
        id
        totalDeposited
        currentBalance
        lastActiveAt
        deposits(first: 5, orderBy: timestamp, orderDirection: desc) {
          amount
          timestamp
          transactionHash
        }
      }
    }
  `;

  const response = await fetch(SUBGRAPH_URL, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query, variables: { limit } }),
  });

  const { data } = await response.json();
  return data.users;
}

// Fetch vault statistics
async function getVaultStats() {
  const query = `
    {
      vaultStats(id: "0x00") {
        totalDeposits
        totalWithdrawals
        totalValueLocked
        uniqueUsers
      }
    }
  `;

  const response = await fetch(SUBGRAPH_URL, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query }),
  });

  const { data } = await response.json();
  return data.vaultStats;
}

// Time-series query for deposits
async function getRecentDeposits(since: number) {
  const query = `
    query RecentDeposits($since: BigInt!) {
      deposits(
        where: { timestamp_gte: $since }
        orderBy: timestamp
        orderDirection: asc
        first: 1000
      ) {
        id
        user { id }
        amount
        timestamp
      }
    }
  `;

  const response = await fetch(SUBGRAPH_URL, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query, variables: { since: since.toString() } }),
  });

  const { data } = await response.json();
  return data.deposits;
}
```

## Implementation Patterns

### Dynamic Data Sources (Factory Pattern)

```yaml
# subgraph.yaml
dataSources:
  - kind: ethereum
    name: PoolFactory
    # ...
    eventHandlers:
      - event: PoolCreated(indexed address,indexed address,address)
        handler: handlePoolCreated
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
      entities:
        - Swap
      abis:
        - name: Pool
          file: ./abis/Pool.json
      eventHandlers:
        - event: Swap(indexed address,uint256,uint256)
          handler: handleSwap
      file: ./src/pool.ts
```

```typescript
// src/factory.ts
import { PoolCreated } from "../generated/PoolFactory/PoolFactory";
import { Pool as PoolTemplate } from "../generated/templates";
import { Pool } from "../generated/schema";

export function handlePoolCreated(event: PoolCreated): void {
  // Create entity
  let pool = new Pool(event.params.pool);
  pool.token0 = event.params.token0;
  pool.token1 = event.params.token1;
  pool.createdAt = event.block.timestamp;
  pool.save();

  // Start indexing the new pool contract
  PoolTemplate.create(event.params.pool);
}
```

### Pagination for Large Datasets

```typescript
async function getAllUsers(): Promise<any[]> {
  const PAGE_SIZE = 1000;
  let allUsers: any[] = [];
  let lastId = "";

  while (true) {
    const query = `
      query Users($lastId: String!, $pageSize: Int!) {
        users(
          first: $pageSize
          where: { id_gt: $lastId }
          orderBy: id
          orderDirection: asc
        ) {
          id
          currentBalance
          totalDeposited
        }
      }
    `;

    const response = await fetch(SUBGRAPH_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        query,
        variables: { lastId, pageSize: PAGE_SIZE },
      }),
    });

    const { data } = await response.json();
    const users = data.users;

    if (users.length === 0) break;

    allUsers = allUsers.concat(users);
    lastId = users[users.length - 1].id;

    if (users.length < PAGE_SIZE) break;
  }

  return allUsers;
}
```

### Full-Text Search

```graphql
# schema.graphql
type Token @entity {
  id: Bytes!
  name: String!
  symbol: String!
  decimals: Int!
}

type _Schema_
  @fulltext(
    name: "tokenSearch"
    language: en
    algorithm: rank
    include: [{ entity: "Token", fields: [{ name: "name" }, { name: "symbol" }] }]
  )
```

```graphql
# Query with full-text search
{
  tokenSearch(text: "Uniswap") {
    id
    name
    symbol
  }
}
```

## Best Practices

1. **Set `startBlock`** to the contract deployment block. Without it, the subgraph scans from genesis, wasting hours of indexing time.
2. **Mark historical entities as `immutable`** with `@entity(immutable: true)`. Immutable entities are never updated after creation, enabling significant indexing performance improvements.
3. **Use `@derivedFrom` for reverse lookups** instead of storing arrays of IDs. Derived fields are computed at query time and keep storage lean.
4. **Use `Bytes` type for addresses and IDs** rather than `String`. Bytes comparisons are more efficient.
5. **Paginate with `id_gt` cursor pattern** instead of `skip`. The `skip` parameter becomes very slow for large offsets.
6. **Test mappings with `matchstick`** (The Graph's unit testing framework) before deploying.
7. **Use Subgraph Studio** for development and testing before publishing to the decentralized network.

## Common Pitfalls

- **Missing events in the contract ABI.** If an event is not in the ABI JSON, the handler will not be generated. Regenerate ABIs from the source contract.
- **Using `store.get` on entities that may not exist without null checks.** Always check for null when loading entities.
- **Not handling BigInt arithmetic correctly in AssemblyScript.** AS does not support operator overloading; use `.plus()`, `.minus()`, `.times()`, `.div()` methods.
- **Exceeding the 1000-entity default query limit.** The Graph returns at most 1000 entities per query by default (max 5000 with `first`). Implement pagination for larger datasets.
- **Deploying without testing on a local Graph Node.** Local testing catches mapping errors before they consume indexing credits on the hosted service.
- **Indexing too many events.** Only index events your frontend actually queries. Each additional handler slows indexing.

## Version and Evidence Check

Check the current Graph CLI, manifest spec version, chain support and hosted/decentralized deployment options before using command examples.
