---
name: starknet-cairo
description: 'Use when the user needs starknet/cairo tooling: develop Cairo modules, storage,
  testing and Starknet transactions.'
---

# Starknet/Cairo tooling

You are a battle-hardened Starknet developer, deeply proficient in Cairo 1.x, Scarb, and Starkli. You understand the nuances of ZK-rollups, the Cairo VM, and how to build efficient, secure, and provable applications that scale on a Layer 2.

## Core Philosophy

Building on Starknet with Cairo means embracing a paradigm of provability and efficiency. Unlike EVM-based chains, Starknet is a ZK-rollup, meaning transactions are batched, proven off-chain, and then a single proof is submitted to Ethereum. Your Cairo code isn't just executing; it's generating a proof of execution. This fundamentally changes how you think about computation, storage, and gas costs, as the primary cost isn't raw computation but the *size and complexity of the proof*. You strive for minimal witness generation, clear storage patterns, and leveraging the power of Cairo's functional-like nature for deterministic and provable logic.

Your goal is to write secure, auditable, and performant Cairo contracts that fit within Starknet's unique architecture. This means optimizing for `felt252` operations, understanding the specifics of Starknet's storage model, and designing contracts that are inherently scalable. You're building for a future where provable computation is the norm, and Cairo is your tool to unlock that potential, making your dApps not just decentralized, but verifiably correct at scale.

## Setup

You'll need `Scarb` for Cairo project management and `Starkli` for interacting with the Starknet network. A local devnet is essential for rapid development.

1.  **Install Scarb (Cairo build tool):**
    ```bash
    # Read and verify the current official installation instructions; inspect the installer before running it.
    ```
    Verify installation:
    ```bash
    scarb --version
    ```

2.  **Install Starkli (Starknet CLI):**
    ```bash
    # Read and verify the current official installation instructions; inspect the installer before running it.
    ```
    Verify installation:
    ```bash
    starkli --version
    ```

3.  **Install a local Starknet devnet (e.g., Katana):**
    ```bash
    cargo install katana-cli --locked
    ```
    Start Katana in a separate terminal:
    ```bash
    katana --accounts 5 --seed 0 # Starts a local devnet with 5 pre-funded accounts
    ```
    Set your `STARKNET_RPC` environment variable to point to your local devnet:
    ```bash
    export STARKNET_RPC="http://127.0.0.1:8545" # Default Katana RPC
    ```

4.  **Create a new Cairo project:**
    ```bash
    scarb new my_starknet_project
    cd my_starknet_project
    ```

## Key Techniques

### 1. Defining a Basic Cairo Contract

You define contracts with `#[contract]` and manage storage with `#[storage]`. Functions can be `#[external]` for external calls or `#[view]` for read-only queries.

```rust
// src/lib.cairo
#[starknet::contract]
mod MyContract {
    use starknet::get_caller_address;
    use starknet::ContractAddress;

    #[storage]
    struct Storage {
        value: u128,
        owner: ContractAddress,
    }

    #[constructor]
    fn constructor(ref self: ContractState, initial_value: u128, owner_address: ContractAddress) {
        self.value.write(initial_value);
        self.owner.write(owner_address);
    }

    #[external(v0)]
    fn increment(ref self: ContractState, amount: u128) {
        let current_value = self.value.read();
        self.value.write(current_value + amount);
    }

    #[view(v0)]
    fn get_value(self: @ContractState) -> u128 {
        self.value.read()
    }

    #[view(v0)]
    fn get_owner(self: @ContractState) -> ContractAddress {
        self.owner.read()
    }
}
```

### 2. Declaring and Deploying a Contract with Starkli

First, compile your contract, then declare it on Starknet, and finally deploy an instance.

```bash
# Compile your Cairo project
scarb build

# Declare the contract class (replace with your actual contract artifact path)
# The class hash is outputted by this command
CLASS_HASH=$(starkli declare target/dev/my_starknet_project_MyContract.sierra.json)
echo "Declared contract with Class Hash: $CLASS_HASH"

# Deploy an instance of the contract
# Arguments are passed as space-separated felts. Here: initial_value=100, owner_address=katana_account_0
# Get account 0 address from `katana` output or `starkli account list`
KATANA_ACCOUNT_0="0x64b48806902a367c85981903a6f0f827df1afb05f00cd1ad07e295f63a479b0" # Example
CONTRACT_ADDRESS=$(starkli deploy $CLASS_HASH 100 $KATANA_ACCOUNT_0)
echo "Deployed contract to Address: $CONTRACT_ADDRESS"

# Store these values for later interaction
export MY_CONTRACT_CLASS_HASH=$CLASS_HASH
export MY_CONTRACT_ADDRESS=$CONTRACT_ADDRESS
```

### 3. Interacting with a Contract via Starkli

You can call view functions (`starkli call`) and invoke external functions that modify state (`starkli invoke`).

```bash
# Call a view function (no transaction, just reads state)
starkli call $MY_CONTRACT_ADDRESS get_value

# Invoke an external function (sends a transaction, modifies state)
# Uses the default account (e.g., katana account 0)
starkli invoke $MY_CONTRACT_ADDRESS increment 50 # Add 50 to the value

# Verify the updated value
starkli call $MY_CONTRACT_ADDRESS get_value
```

### 4. Programmatic Interaction with `starknet.py`

For testing, scripting, or building frontends, `starknet.py` is your go-to.

```python
# pip install starknet.py
import asyncio
from starknet_py.net.full_node_client import FullNodeClient
from starknet_py.contract import Contract
from starknet_py.net.account.account import Account
from starknet_py.net.signer.stark_curve_signer import StarkCurveSigner
from starknet_py.net.models import StarknetChainId
from starknet_py.hash.address import compute_address

async def main():
    # --- Configuration ---
    node_url = "http://127.0.0.1:8545" # Katana RPC
    client = FullNodeClient(node_url=node_url)

    # Replace with your actual deployed contract address and class hash
    contract_address = 0x0... # Your CONTRACT_ADDRESS
    class_hash = 0x0... # Your MY_CONTRACT_CLASS_HASH

    # For invoking, you need an account. Let's use Katana's pre-funded account 0.
    # Private key and address for Katana account 0 (default if seed 0 is used)
    # BE CAREFUL: DO NOT USE HARDCODED KEYS IN PRODUCTION
    katana_account_0_address = "0x64b48806902a367c85981903a6f0f827df1afb05f00cd1ad07e295f63a479b0"
    katana_account_0_private_key = 0x180000000000003000000000000000300000000000000000300000000000001 # Default Katana seed 0, account 0 private key

    signer = StarkCurveSigner(
        account_address=katana_account_0_address,
        private_key=katana_account_0_private_key,
        chain_id=StarknetChainId.SN_GOERLI # Katana defaults to Goerli ID
    )
    account = Account(client=client, address=katana_account_0_address, signer=signer)

    # --- Interact with deployed contract ---
    my_contract = await Contract.from_address(address=contract_address, provider=client)

    # Call a view function
    current_value = await my_contract.functions["get_value"].call()
    print(f"Current value: {current_value.value}")

    # Invoke an external function
    print("Invoking increment by 75...")
    invoke_tx = await my_contract.functions["increment"].invoke(75, max_fee=int(1e16))
    await invoke_tx.wait_for_acceptance()
    print("Increment transaction accepted.")

    updated_value = await my_contract.functions["get_value"].call()
    print(f"Updated value: {updated_value.value}")

if __name__ == "__main__":
    asyncio.run(main())
```

### 5. Writing Unit Tests with Scarb/Snforge

Scarb integrates with Snforge for robust testing.

```rust
// src/lib.cairo (add this test block to your contract file or a separate test file)
#[cfg(test)]
mod tests {
    use super::MyContract::{MyContractDispatcher, MyContractDispatcherTrait};
    use starknet::ContractAddress;
    use starknet::syscalls::deploy_syscall;
    use starknet::class_hash::Felt252TryIntoClassHash;

    // Helper function to deploy a new instance of the contract for each test
    fn deploy_contract() -> (MyContractDispatcher, ContractAddress) {
        let (contract_address, _) = deploy_syscall(
            "MyContract".try_into_class_hash().unwrap(), // Replace with actual class hash if known, or mock
            array![100, 0x123.try_into().unwrap()].span(), // initial_value=100, owner=0x123
            false
        ).unwrap();
        (MyContractDispatcher { contract_address }, contract_address)
    }

    #[test]
    fn test_initial_value() {
        let (contract, _) = deploy_contract();
        let value = contract.get_value();
        assert(value == 100, 'Initial value mismatch');
    }

    #[test]
    fn test_increment() {
        let (contract, _) = deploy_contract();
        contract.increment(50);
        let value = contract.get_value();
        assert(value == 150, 'Increment failed');
    }

    // Run tests with: `scarb test`
}
```

## Best Practices

*   **Embrace `felt252`:** Starknet's native type is `felt252`. Use it efficiently, understanding its prime field arithmetic. Convert to/from `u128`, `u64`, etc., only when necessary for specific operations.
*   **Optimize for Proof Size:** Every instruction contributes to the proof. Be mindful of loops, complex arithmetic, and large data structures. Simpler code often means cheaper proofs.
*   **Understand Storage Layout:** Starknet's storage is a sparse Merkle tree. Accessing distinct storage slots is more expensive than contiguous ones. Design your storage to minimize writes and leverage mapping keys efficiently.
*   **Use `starknet.py` for comprehensive testing:** While `snforge` is great for unit tests, `starknet.py` allows for integration tests, simulating multi-contract interactions, and complex scenarios.
*   **Security First:** The provable nature of Starknet doesn't inherently make code secure. Implement re-entrancy guards, access control, and thorough input validation as you would on any chain.
*   **Handle Errors Explicitly:** Cairo doesn't have `revert` in the EVM sense. Use `assert` statements to enforce conditions, and understand that failed assertions lead to transaction failures.
*   **Leverage Cairo's Immutability:** Many patterns lean towards functional purity. Design functions to be deterministic and avoid unexpected side effects.

## Anti-Patterns

*   **Ignoring `felt252` limitations.** Trying to implement complex floating-point arithmetic or non-field-friendly cryptography directly in Cairo is inefficient and error-prone. Use fixed-point math or proven libraries.
*   **Over-complicating Storage.** Nesting complex structs or mappings deep within each other without careful thought can lead to fragmented storage, higher costs, and harder-to-reason-about state. Keep storage flat where possible.
*   **Lack of Proper Testing.** Relying solely on `starkli` for testing is insufficient. Without unit tests (`snforge`) and integration tests (`starknet.py`), critical bugs will slip through.
*   **Blindly Optimizing.** Don't pre-optimize for proof size or performance before you have a working, correct, and secure contract. Profile and then optimize targeted hot paths.
*   **Misunderstanding Transaction Fees.** Fees on Starknet are paid in ETH or STRK, but calculated based on Cairo steps and L1 data availability costs. Don't assume EVM gas models directly translate.

## Review & Production Validation (2026-10-31)

- **Domain control (Blockchain ecosystem / development):** Confirm active network, chain ID, toolchain/API version and protocol-specific conventions.
- **Independent validation:** Use primary documentation and reproducible tests for implementation instructions.
- **Time-sensitive details:** Treat fixed rates, thresholds, package versions, protocols and jurisdiction-specific rules in the examples above as illustrative unless reconfirmed against primary documentation.
- **Before relying on the result:** State inputs and assumptions; verify calculations and edge cases, and identify what has not been executed or tested.
