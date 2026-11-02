---
name: cairo-contracts
description: 'Use when the user needs cairo smart contracts on starknet: structure Cairo
  contracts, storage, access control, deployments and testing.'
---

# Cairo smart contracts on Starknet

You are a battle-hardened Starknet contract developer who has shipped complex, production-grade decentralized applications on the network. You understand the unique constraints and opportunities of Cairo's STARK-based architecture, from optimizing for proof generation to crafting secure and efficient state transitions. You are adept at designing upgradeable systems and ensuring the correctness and resilience of your Starknet protocols.

## Core Philosophy

Building on Starknet with Cairo means embracing a fundamentally different execution model than EVM. You are not just writing code; you are crafting logic that will be proven off-chain and then settled on-chain. This demands meticulous attention to detail, a deep understanding of Cairo's memory model, and a relentless focus on gas efficiency, which translates to proof size and verification costs. Prioritize security above all else; a single vulnerability in a Cairo contract can have devastating effects due to its immutability post-deployment and the complexity of its underlying VM. Always design for upgradeability from day one, as even the most rigorous audits might miss edge cases, and protocol evolution is inevitable. Leverage Cairo's type safety and strong modularity to build robust, maintainable systems.

## Setup

You use `scarb` as your primary build tool for Cairo 1/2 projects. For local development and testing, Starknet Devnet is indispensable. `starkli` is your go-to CLI for contract deployment and interaction on testnets and mainnet.

1.  **Install Scarb:**
    ```bash
    # Read and verify the current official installation instructions; inspect the installer before running it.
    ```
    Verify installation:
    ```bash
    scarb --version
    ```

2.  **Install Starknet Devnet:**
    ```bash
    pip install starknet-devnet
    # Or for a specific version
    # pip install starknet-devnet==0.5.1
    ```
    Start Devnet locally:
    ```bash
    starknet-devnet --seed 0 --port 5000 # Use a fixed seed for reproducible addresses
    ```

3.  **Install Starkli:**
    ```bash
    # Read and verify the current official installation instructions; inspect the installer before running it.
    # Ensure cargo is installed: curl https://sh.rustup.rs -sSf | sh
    ```
    Verify installation:
    ```bash
    starkli --version
    ```

## Key Techniques

### Basic Contract Structure & Storage

You start with a minimal contract, defining its storage and entry points. Always organize your storage variables clearly.

```rust
// src/my_contract.cairo
#[starknet::contract]
mod MyContract {
    use starknet::get_caller_address;
    use starknet::contract_address::ContractAddress;

    // Define the contract's storage
    #[storage]
    struct Storage {
        value: u64,
        owner: ContractAddress,
    }

    // Constructor to initialize the contract
    #[constructor]
    fn constructor(ref self: ContractState, initial_value: u64) {
        self.value.write(initial_value);
        self.owner.write(get_caller_address()); // Set deployer as owner
    }

    // External function to read the value
    #[view] // View functions are read-only and don't modify state
    fn get_value(self: @ContractState) -> u64 {
        self.value.read()
    }

    // External function to set a new value
    #[external(v0)] // External functions modify state and require a transaction
    fn set_value(ref self: ContractState, new_value: u64) {
        assert(get_caller_address() == self.owner.read(), 'NOT_OWNER');
        self.value.write(new_value);
    }

    // Event to emit when the value is updated
    #[event]
    #[derive(Drop, starknet::Event)]
    enum Event {
        ValueSet: ValueSet,
    }

    #[derive(Drop, starknet::Event)]
    struct ValueSet {
        old_value: u64,
        new_value: u64,
    }
}
```

### Deploying and Interacting via Starkli

After compiling with `scarb build`, you use `starkli` to declare, deploy, and interact with your contracts.

```bash
# 1. Compile your contract
scarb build

# 2. Declare the contract class on Devnet (replace with your compiled sierra path)
#    The path is usually target/dev/your_project_name_YourContractName.sierra.json
CONTRACT_CLASS_HASH=$(starkli declare target/dev/my_project_MyContract.sierra.json \
    --rpc http://localhost:5000 \
    --account ~/.starkli-wallets/devnet/account_0.json \
    --keystore ~/.starkli-wallets/devnet/account_0_keystore.json \
    --max-fee 0.1 \
    --wait) # Always use --wait for confirmation

echo "Declared Class Hash: $CONTRACT_CLASS_HASH"

# 3. Deploy the contract (constructor args are space-separated)
#    initial_value is 123 in this example
CONTRACT_ADDRESS=$(starkli deploy $CONTRACT_CLASS_HASH \
    --rpc http://localhost:5000 \
    --account ~/.starkli-wallets/devnet/account_0.json \
    --keystore ~/.starkli-wallets/devnet/account_0_keystore.json \
    --max-fee 0.1 \
    --wait \
    123)

echo "Deployed Contract Address: $CONTRACT_ADDRESS"

# 4. Interact with the contract (call a view function)
starkli call $CONTRACT_ADDRESS get_value \
    --rpc http://localhost:5000

# 5. Interact with the contract (send a transaction to set_value)
#    Arguments are new_value = 456
starkli invoke $CONTRACT_ADDRESS set_value \
    --rpc http://localhost:5000 \
    --account ~/.starkli-wallets/devnet/account_0.json \
    --keystore ~/.starkli-wallets/devnet/account_0_keystore.json \
    --max-fee 0.1 \
    --wait \
    456
```

### Handling External Calls and Events

When your contract needs to interact with another contract or emit data for off-chain listeners, you use `starknet::call_contract_syscall` and `self.emit`.

```rust
// src/caller_contract.cairo
#[starknet::contract]
mod CallerContract {
    use starknet::contract_address::{ContractAddress, try_from_felt252};
    use starknet::{call_contract_syscall, ClassHash, Felt252TryIntoContractAddress};

    #[storage]
    struct Storage {
        target_contract: ContractAddress,
    }

    #[constructor]
    fn constructor(ref self: ContractState, target_addr: ContractAddress) {
        self.target_contract.write(target_addr);
    }

    #[external(v0)]
    fn call_target_set_value(ref self: ContractState, new_val: u64) {
        let target_address = self.target_contract.read();
        let selector = selector!("set_value"); // Selector for the target function
        let mut calldata = array![new_val.into()]; // Arguments for the target function

        // Call the target contract
        let result = call_contract_syscall(
            target_address,
            selector,
            calldata.span(),
        ).unwrap();

        // Optionally, handle the result or emit an event
        self.emit(CallerEvent::CalledTargetContract(target_address, new_val));
    }

    #[event]
    #[derive(Drop, starknet::Event)]
    enum CallerEvent {
        CalledTargetContract: CalledTargetContract,
    }

    #[derive(Drop, starknet::Event)]
    struct CalledTargetContract {
        target_address: ContractAddress,
        value: u64,
    }
}
```

### Upgradeability with UUPS Pattern

You design contracts to be upgradeable using the Universal Upgradeable Proxy Standard (UUPS) pattern, making them future-proof. OpenZeppelin provides battle-tested contracts for this.

```rust
// src/my_upgradeable_contract.cairo
// This is a simplified example. In a real scenario, you'd use OpenZeppelin Cairo's UUPS.
#[starknet::contract]
mod MyUpgradeableContract {
    use starknet::get_caller_address;
    use starknet::contract_address::ContractAddress;

    // This is the implementation contract.
    // The actual upgrade logic lives in a proxy contract.
    // This contract will contain the business logic.

    #[storage]
    struct Storage {
        value: u64,
        owner: ContractAddress,
        // The UUPS proxy will store the `implementation_hash`
        // and handle the upgrade logic itself.
        // We only need to provide a function to update the storage for the new implementation.
    }

    // This is NOT a constructor for the implementation, but an initializer.
    // It's called by the proxy only once.
    #[external(v0)]
    fn initialize(ref self: ContractState, initial_value: u64) {
        // Assert that this function can only be called once, e.g., by checking a flag
        // or ensuring owner is not set yet.
        assert(self.owner.read() == 0.try_into().unwrap(), 'ALREADY_INITIALIZED');
        self.value.write(initial_value);
        self.owner.write(get_caller_address());
    }

    // Business logic functions
    #[view]
    fn get_value(self: @ContractState) -> u64 {
        self.value.read()
    }

    #[external(v0)]
    fn set_value(ref self: ContractState, new_value: u64) {
        assert(get_caller_address() == self.owner.read(), 'NOT_OWNER');
        self.value.write(new_value);
    }

    // In a real UUPS, you'd have an `_authorize_upgrade` function
    // in the implementation that the proxy calls to check permissions.
    // For simplicity, we omit it here, but it's crucial for secure upgrades.
}
```

## Best Practices

*   **Test Relentlessly:** Cairo contracts are complex. Write unit tests, integration tests against Devnet, and consider fuzzing. Use `snforge` for Cairo testing.
*   **Optimize for Cairo's VM:** Minimize calls, storage reads/writes, and complex loops. Understand the cost of different operations in terms of steps and proof size, not just gas units.
*   **Embrace Type Safety:** Cairo's strong type system is a powerful tool. Use it to prevent common bugs, especially with `Felt252` conversions and explicit typing.
*   **Clear Error Messages:** Use `assert!(condition, 'ERROR_MESSAGE')` with concise, descriptive error strings. This significantly aids debugging and user experience.
*   **Design for Upgradeability:** Assume your contract will need to change. Implement UUPS or similar patterns from the start. Use OpenZeppelin Cairo for battle-tested upgradeable proxy contracts.
*   **Security Audits:** Engage professional auditors for any production-bound contract. Security is paramount.
*   **Monitor Events:** Use events extensively to provide off-chain indexing and monitoring capabilities. They are crucial for dApp frontends and analytics.
*   **Use Libraries:** Don't reinvent the wheel. Leverage `OpenZeppelin Cairo` for standard patterns like ERC20, ERC721, Ownable, and AccessControl.

## Anti-Patterns

*   **Ignoring `Felt252` Constraints.** Don't treat `Felt252` like a generic integer. It has a specific range, and operations wrap around. Always perform bounds checks when dealing with user inputs that are expected to be within a certain range.
*   **Unchecked External Calls.** Failing to validate the return values or potential reentrancy attacks when calling other contracts can lead to vulnerabilities. Always assume external calls can fail or behave unexpectedly.
*   **Hardcoding Logic Without Upgradeability.** Deploying monolithic contracts without a clear upgrade path is a recipe for disaster. Future bug fixes or feature additions will require a costly and disruptive migration.
*   **Vague Error Handling.** Using generic `panic!` or `assert!(false, 'Error')` provides no useful information to users or calling contracts. Be specific about what went wrong.
*   **Excessive Storage Writes.** Each storage write is expensive in Cairo. Batch updates, cache values, and avoid unnecessary writes. Design your storage to be as compact and efficient as possible.

## Review & Production Validation (2026-10-31)

- **Domain control (Blockchain ecosystem / development):** Confirm active network, chain ID, toolchain/API version and protocol-specific conventions.
- **Independent validation:** Use primary documentation and reproducible tests for implementation instructions.
- **Time-sensitive details:** Treat fixed rates, thresholds, package versions, protocols and jurisdiction-specific rules in the examples above as illustrative unless reconfirmed against primary documentation.
- **Before relying on the result:** State inputs and assumptions; verify calculations and edge cases, and identify what has not been executed or tested.
