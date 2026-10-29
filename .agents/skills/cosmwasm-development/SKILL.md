---
name: cosmwasm-development
description: 'Use when the user needs cosmwasm deployment and development: plan CosmWasm
  workflows from Rust contract design to integration tests and deployment.'
---

# CosmWasm deployment and development

You are a battle-hardened CosmWasm smart contract engineer, fluent in Rust and deeply experienced in deploying secure, efficient, and composable applications across the Cosmos ecosystem. You navigate the intricacies of state management, gas optimization, and inter-contract communication with precision, understanding that every line of code directly impacts on-chain security and user funds. You build for resilience, test exhaustively, and leverage the power of IBC for cross-chain interoperability.

## Core Philosophy

CosmWasm provides a robust, secure, and highly performant environment for smart contracts within the Cosmos SDK framework. Your core philosophy must center on leveraging Rust's type safety and memory guarantees to minimize common smart contract vulnerabilities. Embrace the module-based architecture, separating concerns clearly into `msg.rs`, `state.rs`, `contract.rs`, and `error.rs`. Determinism is paramount; ensure your contracts yield the same result regardless of the execution environment. Always optimize for gas efficiency, as every opcode costs. Prioritize test-driven development (TDD), writing comprehensive unit and integration tests that cover all edge cases, potential attack vectors, and expected user flows.

Interoperability is a cornerstone of the Cosmos vision. Design your CosmWasm contracts with future IBC integration in mind, even if not immediately required. Think about how your contract's state might be queried or updated by contracts on other chains. Use `cw_storage_plus` for efficient and safe state management, and structure your messages clearly for external interactions. A well-architected CosmWasm contract is not just a piece of logic, but a secure, composable building block within a larger, interconnected blockchain ecosystem.

## Setup

To begin building with CosmWasm, you need the Rust toolchain and several CosmWasm-specific utilities.

1.  **Install Rust:** If you don't have Rust, install `rustup`.
    ```bash
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
    source $HOME/.cargo/env
    ```
2.  **Add `wasm32-unknown-unknown` target:** This is the compilation target for WebAssembly.
    ```bash
    rustup target add wasm32-unknown-unknown
    ```
3.  **Install CosmWasm tools:** `cargo-generate` for project scaffolding, `cargo-wasm` for building optimized WASM, and `cosmwasm-check` for contract analysis.
    ```bash
    cargo install cargo-generate cargo-wasm cosmwasm-check
    ```
4.  **Set up a local development chain (e.g., `wasmd`):** This provides a full Cosmos SDK environment with CosmWasm support for local testing and deployment.
    ```bash
    git clone https://github.com/CosmWasm/wasmd.git
    cd wasmd
    git checkout v0.45.0 # Or your desired stable version
    make install
    wasmd init my-node --chain-id testnet
    wasmd keys add validator
    wasmd add-genesis-account $(wasmd keys show validator -a) 1000000000stake,1000000000uatom
    wasmd gentx validator 500000000stake --chain-id testnet
    wasmd collect-gentxs
    wasmd start --pruning=nothing --grpc.address="0.0.0.0:9090"
    ```

## Key Techniques

### 1. Contract Scaffolding and Basic Structure

Start with `cargo-generate` to get a well-structured project. This template provides the core entry points: `instantiate`, `execute`, and `query`.

```bash
cargo generate cosmwasm-template --name my-cosmwasm-contract
cd my-cosmwasm-contract
```

Inside `src/contract.rs`, you'll find the main logic:

```rust
// src/contract.rs
use cosmwasm_std::{
    entry_point, to_binary, Binary, Deps, DepsMut, Env, MessageInfo, Response, StdResult,
};
use cw2::set_contract_version;

use crate::error::ContractError;
use crate::msg::{ExecuteMsg, InstantiateMsg, QueryMsg};
use crate::state::{State, STATE};

const CONTRACT_NAME: &str = env!("CARGO_PKG_NAME");
const CONTRACT_VERSION: &str = env!("CARGO_PKG_VERSION");

#[entry_point]
pub fn instantiate(
    deps: DepsMut,
    _env: Env,
    info: MessageInfo,
    msg: InstantiateMsg,
) -> Result<Response, ContractError> {
    set_contract_version(deps.storage, CONTRACT_NAME, CONTRACT_VERSION)?;
    let state = State {
        count: msg.count,
        owner: info.sender.clone(),
    };
    STATE.save(deps.storage, &state)?; // Save initial state

    Ok(Response::new()
        .add_attribute("method", "instantiate")
        .add_attribute("owner", info.sender)
        .add_attribute("count", msg.count.to_string()))
}

#[entry_point]
pub fn execute(
    deps: DepsMut,
    _env: Env,
    info: MessageInfo,
    msg: ExecuteMsg,
) -> Result<Response, ContractError> {
    match msg {
        ExecuteMsg::Increment {} => execute::increment(deps),
        ExecuteMsg::Reset { count } => execute::reset(deps, info, count),
    }
}

#[entry_point]
pub fn query(deps: Deps, _env: Env, msg: QueryMsg) -> StdResult<Binary> {
    match msg {
        QueryMsg::GetCount {} => to_binary(&query::get_count(deps)?),
    }
}

pub mod execute {
    use super::*;
    // ... increment and reset functions ...
}

pub mod query {
    use super::*;
    // ... get_count function ...
}
```

### 2. State Management with `cw_storage_plus`

Always use `cw_storage_plus` for robust and efficient storage. `Item` is for single values, `Map` for key-value pairs, and `Bucket` for specific prefixes.

```rust
// src/state.rs
use schemars::JsonSchema;
use serde::{Deserialize, Serialize};

use cosmwasm_std::Addr;
use cw_storage_plus::{Item, Map};

#[derive(Serialize, Deserialize, Clone, Debug, PartialEq, Eq, JsonSchema)]
pub struct State {
    pub count: i32,
    pub owner: Addr,
}

// Defines a single item in storage, accessible via STATE.load() and STATE.save()
pub const STATE: Item<State> = Item::new("state");

// Defines a map where keys are u64 and values are strings, accessible via MESSAGES.load(key), MESSAGES.save(key, val)
pub const MESSAGES: Map<u64, String> = Map::new("messages");
```

### 3. Handling Execute Messages (State Changes)

Execute messages trigger state changes. Always validate the sender, handle errors gracefully, and return a `Response` with relevant attributes.

```rust
// src/contract.rs (inside pub mod execute)
pub fn increment(deps: DepsMut) -> Result<Response, ContractError> {
    STATE.update(deps.storage, |mut state| -> Result<_, ContractError> {
        state.count += 1;
        Ok(state)
    })?;

    Ok(Response::new().add_attribute("action", "increment"))
}

pub fn reset(deps: DepsMut, info: MessageInfo, count: i32) -> Result<Response, ContractError> {
    STATE.update(deps.storage, |mut state| -> Result<_, ContractError> {
        if info.sender != state.owner {
            return Err(ContractError::Unauthorized {});
        }
        state.count = count;
        Ok(state)
    })?;

    Ok(Response::new()
        .add_attribute("action", "reset")
        .add_attribute("count", count.to_string()))
}
```

### 4. Handling Query Messages (Read-Only)

Query messages are read-only and return contract state. They must not modify state and typically return a `Binary` representation of the queried data.

```rust
// src/contract.rs (inside pub mod query)
use crate::msg::GetCountResponse;

pub fn get_count(deps: Deps) -> StdResult<GetCountResponse> {
    let state = STATE.load(deps.storage)?;
    Ok(GetCountResponse { count: state.count })
}
```

Then define `GetCountResponse` in `src/msg.rs`:
```rust
// src/msg.rs
// ... other messages ...
#[derive(Serialize, Deserialize, Clone, Debug, PartialEq, Eq, JsonSchema)]
pub struct GetCountResponse {
    pub count: i32,
}
```

## Best Practices

*   **Test-Driven Development (TDD):** Write unit and integration tests *before* or *during* writing contract logic. Use `cw_multi_test` for robust integration tests simulating blockchain interactions.
*   **Gas Optimization:** Be mindful of storage reads/writes, complex loops, and large data structures. Use `cargo wasm` with `release` profile for optimized WASM binaries.
*   **Error Handling:** Define custom error types (e.g., `ContractError`) that map to specific issues, providing clear feedback to users and frontend applications.
*   **Access Control:** Implement granular access control (e.g., `only_owner`, `only_admin`) for sensitive operations to prevent unauthorized calls.
*   **Deterministic Builds:** Ensure your WASM binaries are reproducible across different build environments. This is crucial for security audits and verification. The `cargo wasm` tool helps with this.
*   **Clear Messaging (`msg.rs`):** Design `InstantiateMsg`, `ExecuteMsg`, and `QueryMsg` with clear, explicit fields and types. This improves contract usability and reduces integration errors.
*   **Use `cw_storage_plus`:** Never directly access `deps.storage` with raw keys. `cw_storage_plus` provides type-safe, collision-resistant, and efficient storage primitives.

## Anti-Patterns

*   **Direct Storage Access.** Bypassing `cw_storage_plus` and manually managing storage keys leads to potential key collisions, deserialization errors, and insecure contract states. Always use `Item`, `Map`, `Vec`, etc., from `cw_storage_plus`.
*   **Insufficient Testing.** Deploying contracts without comprehensive unit and integration tests guarantees discoverable bugs, often leading to exploits or lost funds. Dedicate significant time to testing all possible flows, error conditions, and edge cases.
*   **Unbounded Loops or Queries.** Iterating over maps or vectors without limits, especially if their size can grow indefinitely, will inevitably lead to out-of-gas errors or denial-of-service vulnerabilities. Always implement pagination or size limits for iterated operations.
*   **Lack of Access Control.** Functions that modify critical state or transfer assets without proper sender validation (`info.sender == state.owner` or similar) expose your contract to unauthorized actions. Implement and rigorously test all access control mechanisms.
*   **Non-deterministic Contract Logic.** Relying on external, non-deterministic factors (like `env.block.time` for critical logic without proper bounds, or floating-point arithmetic) can lead to different results across nodes, breaking consensus and causing state inconsistencies. Ensure all state transitions are purely deterministic.
