---
name: aptos-development
description: 'Use when the user needs aptos application development: structure Move modules,
  resources, accounts and Aptos transaction flows.'
---

# Aptos application development

You are a battle-tested Aptos blockchain architect and Move language expert. Your deep understanding of Aptos' parallel execution engine, resource-oriented programming, and robust developer tooling allows you to craft highly performant, secure, and resilient decentralized applications. You guide agents through the intricacies of building on Aptos, from smart contract design to frontend integration.

## Core Philosophy

Building on Aptos means embracing the Move language's core tenets: safety, scarcity, and access control. Unlike EVM-based chains, Move's resource-oriented paradigm treats digital assets as first-class citizens that cannot be copied or implicitly discarded, significantly mitigating common smart contract vulnerabilities like reentrancy and asset duplication. Your approach should always prioritize designing modular, verifiable Move modules that explicitly define resource ownership and state transitions.

Aptos champions developer experience, providing a comprehensive CLI, SDKs in multiple languages, and robust local development tools. Leverage these to rapidly iterate, test, and deploy. Focus on architecting your dApps to take advantage of Aptos' parallel transaction execution, ensuring your contracts are designed for high throughput by minimizing contention and structuring data efficiently. Think about the entire lifecycle, from local testing to mainnet deployment, and build with upgradability and security audits in mind from day one.

## Setup

Before you write any Move code or interact with the Aptos network, you need to set up your development environment.

1.  **Install Rust and Cargo**: Move is built with Rust.
    ```bash
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
    source $HOME/.cargo/env
    rustup override set stable # Ensure you're on a stable Rust version
    ```

2.  **Install Aptos CLI**: This is your primary tool for managing accounts, compiling Move, and interacting with the network.
    ```bash
    curl -fsSL "https://aptos.dev/aptos-cli/install.sh" | bash
    # Ensure the Aptos CLI is in your PATH. You might need to add:
    # export PATH="$HOME/.aptos/bin:$PATH"
    # source $HOME/.aptos/bin/aptos-bash-autocomplete.sh # For autocompletion
    ```

3.  **Initialize Aptos CLI Profile**: Connect to a network (devnet, testnet, or local) and create/restore an account.
    ```bash
    aptos init --network devnet # Follow prompts to create a new account or use an existing one
    ```
    This generates a `~/.aptos/config.yaml` file with your account details and network configuration.

4.  **Fund your Account (Devnet/Testnet)**: Get some APT tokens for transactions.
    ```bash
    aptos account fund-with-faucet --account <YOUR_ACCOUNT_ADDRESS> --amount 100000000 # 1 APT = 100,000,000 Octas
    ```

## Key Techniques

### 1. Crafting Secure Move Modules

Define a Move module (smart contract) that encapsulates state and logic. Always start with a `sources/` directory inside your Move package.

```move
// sources/my_message_board.move
module <YOUR_ACCOUNT_ADDRESS>::message_board {
    use aptos_framework::signer;
    use std::string::{Self, String};
    use std::error;

    /// Error codes
    const E_MESSAGE_TOO_LONG: u64 = 1;
    const E_MESSAGE_EMPTY: u64 = 2;

    /// Represents a single message posted on the board.
    struct Message has store, drop {
        sender: address,
        content: String,
        timestamp_seconds: u64, // In a real app, use aptos_framework::timestamp for block time
    }

    /// The MessageBoard resource holds all messages.
    /// It is published under the module's owner account.
    struct MessageBoard has key {
        messages: vector<Message>,
        next_message_id: u64,
    }

    /// Called once during module deployment to initialize the MessageBoard.
    fun init_module(sender: &signer) {
        move_to(sender, MessageBoard {
            messages: vector<Message>::empty(),
            next_message_id: 0,
        });
    }

    /// Public function to post a new message.
    /// Only accessible if the MessageBoard resource exists under the sender.
    public entry fun post_message(
        sender: &signer,
        content: String,
        timestamp_seconds: u64, // For demo, we pass it. In real dapp, use system timestamp.
    ) acquires MessageBoard {
        assert!(string::length(&content) > 0, error::invalid_argument(E_MESSAGE_EMPTY));
        assert!(string::length(&content) <= 256, error::invalid_argument(E_MESSAGE_TOO_LONG)); // Max 256 chars

        let board = borrow_global_mut<MessageBoard>(signer::address_of(sender));
        vector::push_back(&mut board.messages, Message {
            sender: signer::address_of(sender),
            content,
            timestamp_seconds,
        });
        board.next_message_id = board.next_message_id + 1;
    }

    /// Public function to read a specific message.
    /// Returns a tuple of (sender, content, timestamp).
    public fun get_message(owner: address, id: u64): (address, String, u64) acquires MessageBoard {
        let board = borrow_global<MessageBoard>(owner);
        assert!(id < vector::length(&board.messages), error::out_of_bounds(0)); // Custom error code
        let msg = vector::borrow(&board.messages, id);
        (msg.sender, msg.content, msg.timestamp_seconds)
    }

    /// Public view function to get the total number of messages.
    public fun get_message_count(owner: address): u64 acquires MessageBoard {
        borrow_global<MessageBoard>(owner).next_message_id
    }
}
```

### 2. Deploying and Initializing on Aptos

Compile your Move package and publish it to the network using the Aptos CLI.

```bash
# In your project root (e.g., aptos_message_board/)
# where `Aptos.toml` defines your package.
# Example Aptos.toml:
# [package]
# name = "aptos_message_board"
# version = "0.0.1"
# [addresses]
# message_board = "_" # This will be replaced by your account address on publish

# 1. Compile your Move package
aptos move compile --named-addresses message_board=<YOUR_ACCOUNT_ADDRESS>

# 2. Publish your compiled module to devnet
# Make sure your CLI profile (aptos init) is configured for devnet.
aptos move publish --named-addresses message_board=<YOUR_ACCOUNT_ADDRESS>
# The output will confirm the transaction hash and the published module address.
# The `init_module` function will automatically be called upon first publishing
# if it's defined.
```

### 3. Interacting with Move Contracts (TypeScript SDK)

Use the `@aptos-labs/ts-sdk` to call entry functions and read state from your dApp.

```typescript
// app.ts (Node.js or browser environment)
import { Aptos, AptosConfig, Network, Account, AccountAddress, Ed25519PublicKey, Ed25519Signature, Serializer, Deserializer } from "@aptos-labs/ts-sdk";

// Configuration for Devnet
const APTOS_NETWORK = Network.DEVNET;
const aptosConfig = new AptosConfig({ network: APTOS_NETWORK });
const aptos = new Aptos(aptosConfig);

// Your deployed module address (replace with your actual address)
const MODULE_ADDRESS = "0x..."; // Your account address where the module was published
const MODULE_NAME = "message_board"; // The name of your module

async function run() {
  // Create a sender account (in a real dApp, this would come from a connected wallet)
  // For demonstration, we'll generate a new one or use a known private key.
  const senderAccount = Account.generate(); // DO NOT USE IN PRODUCTION without proper key management
  console.log("Sender Address:", senderAccount.accountAddress.toString());

  // Fund the sender account for transactions (only needed for newly generated accounts)
  // In a real dApp, the user's wallet would already have funds.
  await aptos.fundAccount({
    accountAddress: senderAccount.accountAddress,
    amount: 100_000_000, // 0.1 APT
  });
  console.log("Sender account funded.");

  // 1. Post a message
  const messageContent = `Hello Aptos from TS SDK at ${Date.now()}`;
  const timestamp = Math.floor(Date.now() / 1000);

  const transaction = await aptos.transaction.build.simple({
    sender: senderAccount.accountAddress,
    data: {
      function: `${MODULE_ADDRESS}::${MODULE_NAME}::post_message`,
      functionArguments: [messageContent, timestamp],
    },
  });

  const committedTxn = await aptos.signAndSubmitTransaction({
    signer: senderAccount,
    transaction,
  });

  console.log("Message posted transaction hash:", committedTxn.hash);
  await aptos.waitForTransaction({ transactionHash: committedTxn.hash });
  console.log("Transaction confirmed.");

  // 2. Read the total number of messages
  const messageCount = await aptos.view({
    payload: {
      function: `${MODULE_ADDRESS}::${MODULE_NAME}::get_message_count`,
      functionArguments: [AccountAddress.from(MODULE_ADDRESS)], // Pass the owner of the board
    },
  });
  console.log("Total messages:", messageCount[0]); // messageCount is an array of returned values

  // 3. Read a specific message (e.g., the first message, if any)
  if (Number(messageCount[0]) > 0) {
    const messageId = 0; // Assuming we want the first message
    const message = await aptos.view({
      payload: {
        function: `${MODULE_ADDRESS}::${MODULE_NAME}::get_message`,
        functionArguments: [AccountAddress.from(MODULE_ADDRESS), messageId],
      },
    });
    console.log(`Message ${messageId}: Sender=${message[0]}, Content=${message[1]}, Timestamp=${message[2]}`);
  }
}

run().catch(console.error);
```

### 4. Observing On-Chain Events

Move modules can emit events that your dApp can subscribe to. This is crucial for reactive UIs and off-chain data processing.

First, modify your Move module to emit an event when a message is posted:

```move
// sources/my_message_board.move (add to your module)
module <YOUR_ACCOUNT_ADDRESS>::message_board {
    // ... (existing code) ...
    use aptos_framework::event;
    // Event emission logic follows standard Aptos patterns
}
```

## Anti-Patterns

*   **Ignoring Move's Ownership Model.** Fighting Move's linear type system by wrapping resources in unnecessary containers instead of leveraging ownership semantics leads to convoluted code that misses the language's safety guarantees.

*   **Unbounded Vectors in Global Storage.** Storing dynamically-growing vectors in global storage without size limits creates gas-unpredictable operations and potential denial-of-service when iteration costs exceed transaction gas limits.

*   **Missing Capability-Based Access Control.** Using address-based if-checks for authorization instead of Move's native capability pattern (signer references, resource ownership) bypasses the type system's security guarantees.

*   **Hardcoded Module Addresses.** Embedding deployer addresses directly in module code instead of using named addresses makes redeployment to different accounts impossible without source modification.

*   **No Event Emission for State Changes.** Modifying global storage without emitting corresponding events makes off-chain indexing and dApp state synchronization impossible, requiring expensive full-state queries.
