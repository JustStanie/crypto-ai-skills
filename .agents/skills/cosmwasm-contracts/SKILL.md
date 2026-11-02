---
name: cosmwasm-contracts
description: 'Use when the user needs cosmwasm smart contract patterns: develop Rust/CosmWasm
  entry points, permissions, messages and tests.'
---

# CosmWasm Contracts — Web3 Development

You are a seasoned smart contract developer, deeply proficient in Rust and the CosmWasm framework. You build robust, secure, and gas-efficient decentralized applications for the Cosmos ecosystem, understanding the nuances of state management, cross-chain communication, and the actor model. Your expertise lies in leveraging Rust's type safety and CosmWasm's deterministic execution to create reliable on-chain logic.

## Core Philosophy

CosmWasm embraces a philosophy of secure, module-based smart contract development, leveraging Rust's powerful type system and compiler to catch errors at compile time rather than runtime. Contracts are compiled to WebAssembly (Wasm), providing a sandboxed, deterministic, and high-performance execution environment. This architecture promotes clear separation of concerns, where contracts interact via explicit message passing, minimizing reentrancy risks and fostering a more predictable execution model compared to traditional EVM environments. You design contracts with immutability, upgradeability (through migration), and gas efficiency as paramount considerations, always prioritizing security through careful state transitions and explicit error handling.

## Setup

Developing CosmWasm contracts requires a Rust development environment and a few specific tools. You'll use `rustup` to manage your Rust toolchain, `cargo-generate` for quick project scaffolding, and `wasm-optimizer` for production builds.

1.  **Install Rust:** If you don't have Rust, install `rustup`.
    ```bash
    # Read and verify the current official installation instructions; inspect the installer before running it.
    ```
    Follow the on-screen instructions, typically choosing the default installation.
2.  **Add `wasm32-unknown-unknown` target:** This target allows Rust to compile to WebAssembly.
    ```bash
    rustup target add wasm32-unknown-unknown
    ```
3.  **Install `cargo-generate`:** This tool helps create new projects from templates.
    ```bash
    cargo install cargo-generate --features=binary
    ```
4.  **Install `wasm-optimizer`:** Essential for reducing contract size and gas costs for production.
    ```bash
    cargo install wasm-optimizer
    ```
5.  **Create a new project:** Use the official CosmWasm template.
    ```bash
    cargo generate https://github.com/CosmWasm/cw-template.git --name my-cosmwasm-contract
    cd my-cosmwasm-contract
    ```
    This sets up a basic project structure with `src/contract.rs`, `src/msg.rs`, `src/state.rs`, and tests.

## Key Techniques

### 1. Contract Structure & Messages

CosmWasm contracts define three primary entry points: `instantiate`, `execute`, and `query`. Messages are explicitly defined in `src/msg.rs` and handled in `src/contract.rs`.

```rust
// src/msg.rs
use schemars::JsonSchema;
use serde::{Deserialize, Serialize};

#[derive(Serialize, Deserialize, Clone, Debug, PartialEq, JsonSchema)]
pub struct InstantiateMsg {
    pub count: i32,
}

#[derive(Serialize, Deserialize, Clone, Debug, PartialEq, JsonSchema)]
#[serde(rename_all = "snake_case")]
pub enum ExecuteMsg {
    Increment {},
    Reset { count: i32 },
}

#[derive(Serialize, Deserialize, Clone, Debug, PartialEq, JsonSchema)]
#[serde(rename_all = "snake_case")]
pub enum QueryMsg {
    GetCount {},
}

#[derive(Serialize, Deserialize, Clone, Debug, PartialEq, JsonSchema)]
pub struct GetCountResponse {
    pub count: i32,
}
```

```rust
// src/contract.rs (simplified)
use cosmwasm_std::{entry_point, to_binary, Binary, Deps, DepsMut, Env, MessageInfo, Response, StdResult};
use crate::error::ContractError;
use crate::msg::{ExecuteMsg, GetCountResponse, InstantiateMsg, QueryMsg};
use crate::state::{State, STATE};

#[entry_point]
pub fn instantiate(
    deps: DepsMut,
    _env: Env,
    info: MessageInfo,
    msg: InstantiateMsg,
) -> Result<Response, ContractError> {
    let state = State {
        count: msg.count,
        owner: info.sender.clone(),
    };
    STATE.save(deps.storage, &state)?; // Persist initial state
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
        ExecuteMsg::Increment {} => execute_increment(deps),
        ExecuteMsg::Reset { count } => execute_reset(deps, info, count),
    }
}

pub fn execute_increment(deps: DepsMut) -> Result<Response, ContractError> {
    STATE.update(deps.storage, |mut state| -> Result<_, ContractError> {
        state.count += 1;
        Ok(state)
    })?;
    Ok(Response::new().add_attribute("method", "increment"))
}

pub fn execute_reset(deps: DepsMut, info: MessageInfo, count: i32) -> Result<Response, ContractError> {
    STATE.update(deps.storage, |mut state| -> Result<_, ContractError> {
        if info.sender != state.owner {
            return Err(ContractError::Unauthorized {});
        }
        state.count = count;
        Ok(state)
    })?;
    Ok(Response::new()
        .add_attribute("method", "reset")
        .add_attribute("count", count.to_string()))
}

#[entry_point]
pub fn query(deps: Deps, _env: Env, msg: QueryMsg) -> StdResult<Binary> {
    match msg {
        QueryMsg::GetCount {} => to_binary(&query_count(deps)?),
    }
}

fn query_count(deps: Deps) -> StdResult<GetCountResponse> {
    let state = STATE.load(deps.storage)?;
    Ok(GetCountResponse { count: state.count })
}
```

### 2. State Management with `cw_storage_plus`

`cw_storage_plus` provides safe and efficient ways to manage persistent state. Use `Item` for single values and `Map` for key-value stores.

```rust
// src/state.rs
use schemars::JsonSchema;
use serde::{Deserialize, Serialize};
use cosmwasm_std::Addr;
use cw_storage_plus::Item;

#[derive(Serialize, Deserialize, Clone, Debug, PartialEq, JsonSchema)]
pub struct State {
    pub count: i32,
    pub owner: Addr,
}

// Define storage items for your contract
pub const STATE: Item<State> = Item::new("state");
// Example of a Map for storing user balances
// pub const BALANCES: Map<&Addr, Uint128> = Map::new("balances");
```
When using `Map`, you can interact with it like this:
```rust
// To save:
// BALANCES.save(deps.storage, &info.sender, &Uint128::new(100))?;
// To load:
// let balance = BALANCES.load(deps.storage, &info.sender)?;
```

### 3. Executing & Querying the Contract

Once deployed, you interact with your contract using CLI tools for the specific Cosmos chain (e.g., `wasmd` for a generic chain, `osmosisd` for Osmosis, `junod` for Juno).

First, compile your contract:
```bash
RUSTFLAGS='-C link-arg=-s' cargo build --release --target wasm32-unknown-unknown
# Optimize for production
wasm-optimizer target/wasm32-unknown-unknown/release/my_cosmwasm_contract.wasm -o my_cosmwasm_contract.wasm
```

**Deploying a contract (example using `wasmd`):**
1.  **Upload the Wasm code:** This registers the contract code on-chain.
    ```bash
    wasmd tx wasm store my_cosmwasm_contract.wasm --from wallet --chain-id testnet-1 --gas auto --gas-adjustment 1.2 -y -o json | jq
    # Note the 'code_id' from the output
    ```
2.  **Instantiate the contract:** Create an instance of the contract from the uploaded code.
    ```bash
    wasmd tx wasm instantiate <code_id> '{"count": 100}' --label "My Counter" --admin <admin_address> --from wallet --chain-id testnet-1 --gas auto --gas-adjustment 1.2 -y -o json | jq
    # Note the 'contract_address' from the output
    ```

**Executing a message:**
```bash
wasmd tx wasm execute <contract_address> '{"increment":{}}' --from wallet --chain-id testnet-1 --gas auto --gas-adjustment 1.2 -y -o json | jq
```

**Querying the contract:**
```bash
wasmd query wasm contract-state smart <contract_address> '{"get_count":{}}' -o json | jq
```

### 4. Unit & Integration Testing

CosmWasm provides `cw-multi-test` for robust off-chain testing, simulating a blockchain environment.

```rust
// tests/integration_test.rs (example)
#[cfg(test)]
mod tests {
    use cosmwasm_std::{Addr, Coin, Empty, Uint128};
    use cw_multi_test::{App, Contract, ContractWrapper, Executor};

    use crate::msg::{ExecuteMsg, InstantiateMsg, QueryMsg, GetCountResponse};

    // Helper to get a Contract object from your code
    fn contract_template() -> Box<dyn Contract<Empty>> {
        let contract = ContractWrapper::new(
            crate::contract::execute,
            crate::contract::instantiate,
            crate::contract::query,
        );
        Box::new(contract)
    }

    #[test]
    fn proper_initialization() {
        let mut app = App::default();
        let code_id = app.store_code(contract_template());

        let msg = InstantiateMsg { count: 17 };
        let addr = app
            .instantiate_contract(
                code_id,
                Addr::unchecked("owner"),
                &msg,
                &[],
                "test contract",
                None,
            )
            .unwrap();

        let resp: GetCountResponse = app
            .wrap()
            .query_wasm_smart(addr.clone(), &QueryMsg::GetCount {})
            .unwrap();
        assert_eq!(resp.count, 17);
    }

    #[test]
    fn increment() {
        let mut app = App::default();
        let code_id = app.store_code(contract_template());
        let owner = Addr::unchecked("owner");
        let msg = InstantiateMsg { count: 17 };
        let addr = app
            .instantiate_contract(code_id, owner.clone(), &msg, &[], "test contract", None)
            .unwrap();

        app.execute_contract(owner.clone(), addr.clone(), &ExecuteMsg::Increment {}, &[])
            .unwrap();

        let resp: GetCountResponse = app
            .wrap()
            .query_wasm_smart(addr, &QueryMsg::GetCount {})
            .unwrap();
        assert_eq!(resp.count, 18);
    }
}
```

## Best Practices

*   **Explicit Error Handling:** Always return `Result<Response, ContractError>` and define custom, descriptive `ContractError` enum variants. Avoid panicking with `unwrap()` or `expect()` in production code.
*   **Use `cw_storage_plus`:** This library provides safe, idiomatic, and gas-efficient ways to manage contract state with `Item`, `Map`, and `Key` structs.
*   **Gas Optimization:** Minimize storage reads/writes, avoid large iterations, and always optimize your Wasm binary with `wasm-optimizer` before deployment.
*   **Thorough Testing:** Write comprehensive unit tests for individual functions and integration tests using `cw-multi-test` to simulate complex scenarios and inter-contract interactions.
*   **Immutability by Default:** Design your contract state to be immutable where possible. For mutable state, ensure clear access controls and validation.
*   **Upgradeability Strategy:** Plan for contract upgrades from the start. Implement an `admin` pattern and a `migrate` entry point to enable future code changes and data migrations.
*   **Security Audits:** Treat security as paramount. Engage with professional auditors and follow community best practices for smart contract security.
*   **Clear Event Logging:** Use `Response::add_attribute` to emit meaningful events for off-chain indexing and user interfaces.

## Review & Production Validation (2026-10-31)

- **Domain control (Blockchain ecosystem / development):** Confirm active network, chain ID, toolchain/API version and protocol-specific conventions.
- **Independent validation:** Use primary documentation and reproducible tests for implementation instructions.
- **Time-sensitive details:** Treat fixed rates, thresholds, package versions, protocols and jurisdiction-specific rules in the examples above as illustrative unless reconfirmed against primary documentation.
- **Before relying on the result:** State inputs and assumptions; verify calculations and edge cases, and identify what has not been executed or tested.
