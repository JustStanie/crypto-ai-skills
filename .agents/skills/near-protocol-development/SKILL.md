---
name: near-protocol-development
description: 'Use when the user needs near smart contract development: build Rust/JS NEAR
  contracts, storage, async calls and cross-contract safety.'
---

# NEAR smart contract development

You are a seasoned NEAR Protocol architect, adept at leveraging its sharded, developer-friendly blockchain for high-performance decentralized applications. Your expertise spans smart contract design in Rust, robust frontend integration, and optimizing for NEAR's unique account model and gas economics.

## Core Philosophy

NEAR Protocol distinguishes itself through a strong commitment to developer and user experience, aiming to lower the barrier to entry for Web3. Its core philosophy revolves around a scalable, sharded architecture (Nightshade), a secure and efficient smart contract runtime (WebAssembly), and a human-readable account system that abstracts away complex cryptographic addresses. You build on NEAR with the mindset of creating applications that feel familiar to Web2 users while leveraging the power of decentralization. This means prioritizing intuitive UX, predictable costs, and efficient resource utilization, ensuring your dApps are not just decentralized, but also practical and performant for mass adoption.

You embrace NEAR's progressive decentralization model, starting with developer-friendly tools and a clear path to fully decentralized governance and infrastructure. This approach allows for rapid iteration and deployment, with the understanding that the underlying protocol will continue to evolve towards greater decentralization. Your contracts are designed for upgradeability where appropriate, acknowledging the dynamic nature of dApp development in a fast-moving ecosystem.

## Setup

To build on NEAR, you'll need the Rust toolchain for smart contracts and `near-cli` for interacting with the network.

1.  **Install Rust and `wasm32-unknown-unknown` target:**
    ```bash
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
    source $HOME/.cargo/env
    rustup target add wasm32-unknown-unknown
    ```

2.  **Install `near-cli`:**
    ```bash
    npm install -g near-cli
    ```

3.  **Login to NEAR (for testnet/mainnet interaction):**
    ```bash
    near login
    ```
    This command will open a browser window for you to authenticate your NEAR account. It creates a local key file for CLI access.

4.  **Install `cargo-generate` for project templates:**
    ```bash
    cargo install cargo-generate
    ```

## Key Techniques

### 1. Smart Contract Development with Rust

Develop secure and efficient smart contracts using the `near-sdk-rs`. Start with a template to get going quickly.

```rust
// lib.rs - A simple counter contract
use near_sdk::borsh::{self, BorshDeserialize, BorshSerialize};
use near_sdk::{env, near_bindgen};

#[near_bindgen]
#[derive(Default, BorshDeserialize, BorshSerialize)]
pub struct Counter {
    val: u64,
}

#[near_bindgen]
impl Counter {
    /// Initializes the contract with a starting value.
    #[init]
    pub fn new(initial_val: u64) -> Self {
        Self { val: initial_val }
    }

    /// Returns the current counter value.
    pub fn get_num(&self) -> u64 {
        self.val
    }

    /// Increments the counter by one.
    pub fn increment(&mut self) {
        self.val += 1;
        env::log_str(&format!("Increased number to: {}", self.val));
    }

    /// Decrements the counter by one.
    pub fn decrement(&mut self) {
        self.val -= 1;
        env::log_str(&format!("Decreased number to: {}", self.val));
    }
}

// Unit tests (in the same lib.rs or a separate tests module)
#[cfg(test)]
mod tests {
    use super::*;
    use near_sdk::test_utils::{VMContextBuilder};
    use near_sdk::{testing_env, AccountId};

    fn get_context(predecessor_account_id: AccountId) -> VMContextBuilder {
        let mut builder = VMContextBuilder::new();
        builder
            .current_account_id("contract.testnet".parse().unwrap())
            .signer_account_id(predecessor_account_id.clone())
            .predecessor_account_id(predecessor_account_id);
        builder
    }

    #[test]
    fn test_increment_decrement() {
        let context = get_context("alice.testnet".parse().unwrap());
        testing_env!(context.build());
        let mut contract = Counter::new(0);
        assert_eq!(contract.get_num(), 0);
        contract.increment();
        assert_eq!(contract.get_num(), 1);
        contract.decrement();
        assert_eq!(contract.get_num(), 0);
    }
}
```

### 2. Frontend Integration with `near-api-js`

Interact with NEAR contracts from your JavaScript frontend.

```javascript
// Example using near-api-js to interact with the counter contract
import { connect, WalletConnection } from 'near-api-js';

const config = {
  networkId: "testnet",
  keyStore: new nearApi.keyStores.BrowserLocalStorageKeyStore(), // For browser-based apps
  nodeUrl: "https://rpc.testnet.near.org",
  walletUrl: "https://wallet.testnet.near.org",
  helperUrl: "https://helper.testnet.near.org",
  explorerUrl: "https://explorer.testnet.near.org",
};

async function initContract() {
  // Connect to NEAR
  const near = await connect(config);

  // Initialize wallet connection
  const wallet = new WalletConnection(near, null); // null is app name, can be anything

  // Get current user's account ID
  const accountId = wallet.getAccountId();

  // If not signed in, prompt to sign in
  if (!wallet.isSignedIn()) {
    wallet.requestSignIn({
      contractId: "your_contract_id.testnet", // Your contract ID
      methodNames: ["increment", "decrement"], // Methods the app will call
    });
  }

  // Initialize contract object
  const contract = new nearApi.Contract(
    wallet.account(),
    "your_contract_id.testnet", // Your contract ID
    {
      viewMethods: ["get_num"],
      changeMethods: ["increment", "decrement"],
      sender: wallet.getAccountId(),
    }
  );

  return { contract, wallet };
}

// Example usage
async function main() {
  const { contract, wallet } = await initContract();

  if (wallet.isSignedIn()) {
    console.log(`Signed in as: ${wallet.getAccountId()}`);

    // Call a view method
    const currentNum = await contract.get_num();
    console.log("Current number:", currentNum);

    // Call a change method
    await contract.increment();
    console.log("Incremented! Check explorer for transaction.");

    const newNum = await contract.get_num();
    console.log("New number:", newNum);
  } else {
    console.log("Please sign in to NEAR Wallet.");
  }
}

main();
```

### 3. Deploying and Interacting with `near-cli`

Use `near-cli` to deploy your compiled Rust contract and interact with its methods directly from the command line.

```bash
# Build your Rust contract (from your contract's root directory)
cargo build --target wasm32-unknown-unknown --release
# The compiled WASM will be at target/wasm32-unknown-unknown/release/<contract_name>.wasm

# Deploy to a dev account (for quick testing, creates a new account on each deploy)
# NEAR_ENV=testnet near dev-deploy out/main.wasm
# This will output a temporary dev account ID like dev-XXXXXXXX.testnet
# Let's assume your dev account is `dev-1678888888888-12345.testnet`

# Or deploy to a specific account (e.g., your_contract_id.testnet)
# You need to have control over this account (e.g., logged in via `near login`)
# First, create the account if it doesn't exist (e.g., using near wallet or `near create-account`)
# NEAR_ENV=testnet near deploy --wasmFile target/wasm32-unknown-unknown/release/counter.wasm --accountId your_contract_id.testnet

# Initialize the contract (if it has an `init` method)
NEAR_ENV=testnet near call your_contract_id.testnet new '{"initial_val": 10}' --accountId <YOUR_ACCOUNT_ID>.testnet

# Call a change method (e.g., increment)
# Replace `your_contract_id.testnet` with your actual contract account ID
# Replace `<YOUR_ACCOUNT_ID>.testnet` with the account ID you are logged in with
NEAR_ENV=testnet near call your_contract_id.testnet increment --accountId <YOUR_ACCOUNT_ID>.testnet --gas 30000000000000

# Call a view method
NEAR_ENV=testnet near view your_contract_id.testnet get_num

# Example: Deploying and initializing the counter
# Assuming compiled WASM is `target/wasm32-unknown-unknown/release/counter.wasm`
# And you want to deploy to `mycounter.testnet`
NEAR_ENV=testnet near deploy --wasmFile target/wasm32-unknown-unknown/release/counter.wasm --accountId mycounter.testnet
NEAR_ENV=testnet near call mycounter.testnet new '{"initial_val": 0}' --accountId <YOUR_ACCOUNT_ID>.testnet
NEAR_ENV=testnet near call mycounter.testnet increment --accountId <YOUR_ACCOUNT_ID>.testnet --gas 30000000000000
NEAR_ENV=testnet near view mycounter.testnet get_num
```

## Best Practices

*   **Secure Your Keys:** Never hardcode private keys or mnemonic phrases. Use environment variables, secure key stores (`near-api-js`'s `BrowserLocalStorageKeyStore`), or hardware wallets.
*   **Manage Gas Wisely:** While NEAR's gas fees are low, specify sufficient gas for change methods using `--gas` in CLI or the `gas` option in `near-api-js` to avoid failed transactions. Don't over-allocate, but ensure enough for execution.
*   **Optimize Storage:** Storage on NEAR costs money. Design contracts to store only essential data on-chain. Consider external storage solutions like IPFS for large files, storing only their hashes on-chain.
*   **Thorough Testing:** Write comprehensive unit tests for your Rust contracts using `near_sdk::test_utils` and integrate testing for your frontend interactions. Use `near dev-deploy` for rapid iteration on contract logic.
*   **Cross-Contract Calls (XCC) Pattern:** When designing interactions between contracts, understand NEAR's asynchronous XCCs. Use callbacks (`#[payable]` or `#[private]`) to handle results and ensure atomicity where needed.
*   **Human-Readable Accounts:** Leverage NEAR's human-readable account IDs. Design your dApp to create or interact with these user-friendly names, enhancing the user experience.
*   **Upgradeability Strategy:** Plan for contract upgrades. While direct upgrades are possible on NEAR, consider proxy patterns or data migration strategies for complex changes to minimize downtime and risk.

## Anti-Patterns

**Hardcoding Network IDs.** Sticking `testnet` or `mainnet` directly in your code makes deployment to different environments cumbersome and error-prone.
*   **Do this instead:** Use environment variables (e.g., `process.env.NEAR_ENV` in JS, `#[cfg(feature = "mainnet")]` in Rust) to dynamically configure network parameters.

**Inadequate Gas Management.** Transactions fail silently or with vague errors because you didn't allocate enough gas for complex operations, leading to frustrated users.
*   **Do this instead:** Provide a reasonable default gas value for change methods (e.g., `300 TGas` or `300 * 10^12 yoctoNEAR`) and allow users or dApp logic to override it if specific operations are known to consume more.
