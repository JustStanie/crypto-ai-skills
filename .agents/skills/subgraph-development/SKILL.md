---
name: subgraph-development
description: 'Use when the user needs the graph subgraph architecture: design manifests,
  mappings, entities and deterministic event indexing.'
---

# Subgraph Development with The Graph Protocol

You are a battle-hardened Web3 data engineer, an expert in building robust, performant, and reliable subgraphs that power critical dApp functionality. You understand the nuances of blockchain indexing, from handling chain reorganizations to optimizing data models for complex queries. Your subgraphs are not just data mirrors; they are highly optimized, query-friendly APIs that make on-chain data accessible and fast for any application.

## Core Philosophy

Subgraphs are your bridge between the raw, event-driven world of the blockchain and the structured, queryable data needs of your dApp. Directly querying RPC nodes for historical data is slow, resource-intensive, and often infeasible for complex aggregations. A well-designed subgraph transforms this chaos into order, providing a GraphQL API that your frontend can consume with lightning speed. The core philosophy is to index *only* what you need, model your data for efficient querying, and handle the inherent complexities of blockchain data (like reorgs) gracefully. Think of your subgraph as a materialized view of your smart contract's state, optimized for specific application queries, not a full blockchain explorer.

## Setup

To start developing subgraphs, you need The Graph CLI. This tool handles initialization, code generation, deployment, and interaction with The Graph network or a local Graph Node.

1.  **Install The Graph CLI:**
    ```bash
    npm install -g @graphprotocol/graph-cli
    ```

2.  **Initialize a new subgraph project:**
    Navigate to your desired directory and initialize a project. You can choose to initialize from an existing contract or a predefined template.
    ```bash
    graph init --from-contract <CONTRACT_ADDRESS> --network <NETWORK_NAME> <SUBGRAPH_NAME>
    # Example for an existing contract on mainnet
    graph init --from-contract 0x5a98f7e2762a4d334e3e3f4e2f3e3f4e2f3e3f4e --network mainnet my-token-subgraph
    ```
    If you prefer to start from scratch or a template:
    ```bash
    graph init --product hosted-service <SUBGRAPH_NAME>
    # Or for a decentralized network deployment
    graph init --product subgraph-studio <SUBGRAPH_NAME>
    ```
    This command will prompt you for contract address, network, and events to index, generating a basic `schema.graphql`, `graph.yaml` (manifest), and `src/mapping.ts` files.

3.  **Authenticate (for hosted service/Subgraph Studio):**
    Before deploying, you need to authenticate your CLI with your Graph account.
    ```bash
    graph auth --product hosted-service <YOUR_ACCESS_TOKEN>
    # Or for Subgraph Studio
    graph auth --product subgraph-studio <YOUR_ACCESS_TOKEN>
    ```
    Your access token can be found in your Graph dashboard.

## Key Techniques

### 1. Defining Your Schema (schema.graphql)

The `schema.graphql` file defines the data model for your subgraph. These are your entities, which correspond to the data you want to store and query. Each entity must have an `id` field.

```graphql
# schema.graphql
type Token @entity {
  id: ID! # Contract address of the token (e.g., ERC-20 token address)
  name: String!
  symbol: String!
  decimals: BigInt!
  totalSupply: BigInt!
  creator: Bytes! # Address that deployed the token
  holders: [Account!] @derivedFrom(field: "tokens") # Relationship to Account entity
}

type Account @entity {
  id: ID! # Wallet address
  balance: BigInt! # Balance of a specific token for this account
  tokens: [TokenHolder!] @derivedFrom(field: "account") # Many-to-many relationship via TokenHolder
}

# Intermediate entity for many-to-many relationship between Token and Account
type TokenHolder @entity {
  id: ID! # Combination of token and account address (e.g., tokenAddress-accountAddress)
  token: Token! # Reference to the Token entity
  account: Account! # Reference to the Account entity
  amount: BigInt! # Amount of this token held by this account
}

type TransferEvent @entity {
  id: ID! # Transaction hash + log index
  token: Token!
  from: Account!
  to: Account!
  value: BigInt!
  timestamp: BigInt!
  blockNumber: BigInt!
  transactionHash: Bytes!
}
```

### 2. Configuring the Manifest (subgraph.yaml)

The `subgraph.yaml` file is the heart of your subgraph, connecting your smart contracts to your schema and mapping logic. It specifies which events to listen to, which functions to call, and where your mapping files are located.

```yaml
# subgraph.yaml
specVersion: 0.0.8
schema:
  file: ./schema.graphql
dataSources:
  - kind: ethereum/contract
    name: MyToken
    network: mainnet
    source:
      address: "0x5a98f7e2762a4d334e3e3f4e2f3e3f4e2f3e3f4e" # The contract address
      abi: MyToken # ABI name defined in abis/MyToken.json
      startBlock: 12345678 # Optimize indexing by starting from the contract deployment block
    mapping:
      kind: ethereum/events
      apiVersion: 0.0.7
      language: wasm/assemblyscript
      entities:
        - Token
        - Account
        - TokenHolder
        - TransferEvent
      abis:
        - name: MyToken
          file: ./abis/MyToken.json
      eventHandlers:
        - event: Transfer(indexed address,indexed address,uint256)
          handler: handleTransfer # Function in src/mapping.ts to call for this event
        - event: Approval(indexed address,indexed address,uint256)
          handler: handleApproval
        # ... other event handlers
      file: ./src/mapping.ts
```

### 3. Writing Mapping Handlers (src/mapping.ts)

Mapping handlers are AssemblyScript functions that process blockchain events. They extract relevant data, create or update entities, and save them to the subgraph's store.

```typescript
// src/mapping.ts
import { BigInt, Bytes, store, log } from "@graphprotocol/graph-ts";
import { Transfer, Approval, MyToken as MyTokenContract } from "../generated/MyToken/MyToken";
import { Token, Account, TokenHolder, TransferEvent } from "../generated/schema";

// Helper function to get or create an Account entity
function getOrCreateAccount(address: Bytes): Account {
  let account = Account.load(address.toHexString());
  if (!account) {
    account = new Account(address.toHexString());
    account.balance = BigInt.fromI32(0); // Initialize balance
    account.save();
  }
  return account;
}

// Handler for the Transfer event
export function handleTransfer(event: Transfer): void {
  let tokenAddress = event.address.toHexString();
  let token = Token.load(tokenAddress);

  // If token doesn't exist, create it (e.g., for initial setup or first transfer)
  if (!token) {
    token = new Token(tokenAddress);
    let contract = MyTokenContract.bind(event.address);
    token.name = contract.name();
    token.symbol = contract.symbol();
    token.decimals = BigInt.fromI32(contract.decimals());
    token.totalSupply = contract.totalSupply();
    // Assuming 'creator' can be derived from the first transfer event or contract deployment
    // For a real scenario, you might need a separate event or hardcoded value
    token.creator = Bytes.fromHexString("0x0000000000000000000000000000000000000000"); // Placeholder
    token.save();
  }

  let fromAccount = getOrCreateAccount(event.params.from);
  let toAccount = getOrCreateAccount(event.params.to);

  // Update TokenHolder balances (or create if new)
  let fromTokenHolderId = tokenAddress + "-" + fromAccount.id;
  let fromTokenHolder = TokenHolder.load(fromTokenHolderId);
  if (!fromTokenHolder && event.params.from.toHexString() != "0x0000000000000000000000000000000000000000") {
    fromTokenHolder = new TokenHolder(fromTokenHolderId);
    fromTokenHolder.token = token.id;
    fromTokenHolder.account = fromAccount.id;
    fromTokenHolder.amount = BigInt.fromI32(0);
  }
  if (fromTokenHolder) { // Ensure it exists before subtracting
    fromTokenHolder.amount = fromTokenHolder.amount.minus(event.params.value);
    fromTokenHolder.save();
  }


  let toTokenHolderId = tokenAddress + "-" + toAccount.id;
  let toTokenHolder = TokenHolder.load(toTokenHolderId);
  if (!toTokenHolder) {
    toTokenHolder = new TokenHolder(toTokenHolderId);
    toTokenHolder.token = token.id;
    toTokenHolder.account = toAccount.id;
    toTokenHolder.amount = BigInt.fromI32(0);
  }
  toTokenHolder.amount = toTokenHolder.amount.plus(event.params.value);
  toTokenHolder.save();

  // Create a new TransferEvent entity
  let transferEvent = new TransferEvent(
    event.transaction.hash.toHexString() + "-" + event.logIndex.toString()
  );
  transferEvent.token = token.id;
  transferEvent.from = fromAccount.id;
  transferEvent.to = toAccount.id;
  transferEvent.value = event.params.value;
  transferEvent.timestamp = event.block.timestamp;
  transferEvent.blockNumber = event.block.number;
  transferEvent.transactionHash = event.transaction.hash;
  transferEvent.save();
}

// Handler for the Approval event (example, might not need full implementation)
export function handleApproval(event: Approval): void {
  // Logic to handle approval events, e.g., tracking allowances
  log.info("Approval event processed: owner={}, spender={}, value={}", [
    event.params.owner.toHexString(),
    event.params.spender.toHexString(),
    event.params.value.toString(),
  ]);
}
```

### 4. Deploying Your Subgraph

Once your schema, manifest, and mappings are complete, you can generate the necessary types, build, and deploy your subgraph.

```bash
# Generate AssemblyScript types from your GraphQL schema and contract ABIs
graph codegen

# Compile the subgraph to WebAssembly
graph build

# Deploy the subgraph to The Graph Hosted Service or Subgraph Studio
# Replace <YOUR_USERNAME>/<SUBGRAPH_NAME> with your actual details
graph deploy --product hosted-service <YOUR_USERNAME>/<SUBGRAPH_NAME>
# Or for Subgraph Studio:
# graph deploy --product subgraph-studio <SUBGRAPH_NAME>
```
The deploy command will provide you with a URL to query your subgraph.

### 5. Querying Your Subgraph

After deployment and synchronization, you can query your subgraph using GraphQL.

```graphql
query MyTokenData {
  tokens(first: 10, orderBy: totalSupply, orderDirection: desc) {
    id
    name
    symbol
    totalSupply
    creator
  }
  accounts(first: 5, orderBy: balance, orderDirection: desc) {
    id
    balance
    tokens { # Accessing related TokenHolder entities
      token {
        symbol
      }
      amount
    }
  }
  transferEvents(first: 5, orderBy: timestamp, orderDirection: desc) {
    id
    token {
      symbol
    }
    from {
      id
    }
    to {
      id
    }
    value
    timestamp
  }
}
```

## Best Practices

*   **Start with `startBlock`:** Always specify `startBlock` in your `subgraph.yaml` for data sources. This tells the indexer to start from the contract's deployment block, significantly reducing indexing time and resource consumption.
*   **Minimal Indexing:** Only index the events and data points your dApp *actually needs*. Over-indexing leads to slower sync times, higher resource usage, and more complex mappings.
*   **Efficient Data Modeling:** Design your `schema.graphql` entities to align with your dApp's query patterns. Use relationships (`@derivedFrom`) to avoid redundant data and enable powerful nested queries.
*   **Handle Edge Cases (Zero Address):** Be mindful of the zero address (`0x00...00`) for `from` or `to` in `Transfer` events, as it often represents minting or burning. Your mapping should handle these gracefully, potentially by not creating an `Account` entity for the zero address.
*   **Use `log.info` for Debugging:** The `log.info` function in AssemblyScript mappings is invaluable for debugging issues during indexing. Monitor the Graph Node logs for output.
*   **Idempotent Mappings:** Ensure your mapping handlers are idempotent. If an event is processed twice (e.g., due to a reorg and re-indexing), it should produce the same state without data corruption. `store.load()` and `store.save()` handle this well for entity updates.
*   **Test Locally:** Use a local Graph Node setup (`graph-node` Docker image) for rapid iteration and testing before deploying to the hosted service or Subgraph Studio.

## Anti-Patterns

*   **Over-indexing.** Indexing every event and transaction on a contract just because it's there. Instead, carefully select only the events and data fields your dApp requires for its specific functionality.
*   **Inefficient IDs.** Using transaction hash + log index as the `id` for every entity, even when a more natural, contract-specific ID (like a token address or user address

## Review & Production Validation (2026-10-31)

- **Domain control (Blockchain ecosystem / development):** Confirm active network, chain ID, toolchain/API version and protocol-specific conventions.
- **Independent validation:** Use primary documentation and reproducible tests for implementation instructions.
- **Time-sensitive details:** Treat fixed rates, thresholds, package versions, protocols and jurisdiction-specific rules in the examples above as illustrative unless reconfirmed against primary documentation.
- **Before relying on the result:** State inputs and assumptions; verify calculations and edge cases, and identify what has not been executed or tested.
