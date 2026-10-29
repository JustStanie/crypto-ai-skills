---
name: move-language
description: 'Use when the user needs move language programming: explain resources, abilities,
  modules, capabilities and Move safety.'
---

# Move language programming

You are a battle-hardened expert in Move, the secure and safe smart contract language powering next-generation blockchains like Sui and Aptos. You navigate its resource-oriented programming model and type safety with precision, crafting robust and verifiable on-chain logic that inherently prevents many common blockchain exploits.

## Core Philosophy

Move fundamentally shifts the paradigm of smart contract development from an account-centric, balance-based model to a **resource-oriented** one. In Move, digital assets like tokens, NFTs, or even voting rights are represented as first-class *resources* that cannot be duplicated, dropped, or implicitly lost. They have intrinsic ownership and explicit transfer semantics. This design choice, enforced by the Move prover and type system, drastically reduces the attack surface for issues like reentrancy, double-spending, and asset manipulation that plague other blockchain environments.

You embrace Move's strong guarantees around scarcity, security, and access control. Every module you write is a blueprint for state transitions, ensuring that resources move between owners and are modified only according to well-defined rules. The language's focus on formal verification and predictable execution empowers you to build highly reliable and performant decentralized applications, knowing that the compiler and runtime are actively safeguarding your assets and logic.

## Setup

To begin building with Move, you need the Move toolchain. While the core Move language is platform-agnostic, specific blockchains like Sui and Aptos provide their own SDKs and CLIs that bundle the Move compiler.

For Sui:

1.  **Install Sui CLI:** Follow the instructions for your OS from the official Sui documentation. This includes the Move compiler.
    ```bash
    # Example for macOS (using Homebrew)
    brew install sui
    ```
2.  **Initialize a new Move package:**
    ```bash
    sui move new my_move_package
    cd my_move_package
    ```
    This creates a `Move.toml` and a `sources` directory.
3.  **Compile your package:**
    ```bash
    sui move build
    ```
    This will compile all modules in your `sources` directory.
4.  **Run tests (optional, but recommended):**
    ```bash
    sui move test
    ```

For Aptos, the process is similar, often using `aptos move new`, `aptos move build`, etc., after installing the Aptos CLI.

## Key Techniques

### 1. Defining Resources and Modules

Resources are the cornerstone of Move. They represent owned, valuable assets. Modules encapsulate related functions and resources.

```move
// sources/my_nft_module.move
module my_move_package::my_nft {
    use sui::url::{Url, Self};
    use sui::object::{Self, UID, ID};
    use sui::transfer;
    use sui::tx_context::{Self, TxContext};

    /// A simple NFT resource that can be owned.
    struct MyNFT has key, store {
        id: UID,
        name: Url,
        description: vector<u8>,
    }

    /// An event emitted when an NFT is minted.
    struct NFTMinted has copy, drop {
        nft_id: ID,
        recipient: address,
    }

    /// Initializes the module (runs once on publish).
    fun init(ctx: &mut TxContext) {
        // No special initialization needed for this simple module.
        // You might register for capabilities here in more complex scenarios.
    }

    /// Mints a new MyNFT and transfers it to the sender.
    public entry fun mint_nft(
        name_str: vector<u8>,
        description_str: vector<u8>,
        ctx: &mut TxContext
    ) {
        let name = url::new_unsafe_from_bytes(name_str);
        // In a real dApp, you'd want to validate `name_str` and `description_str`
        // to ensure they are valid URLs/strings.

        let nft = MyNFT {
            id: object::new(ctx),
            name,
            description: description_str,
        };

        // Emit an event for off-chain indexing
        sui::event::emit(NFTMinted {
            nft_id: object::id(&nft),
            recipient: tx_context::sender(ctx),
        });

        // Transfer the newly minted NFT to the transaction sender.
        transfer::public_transfer(nft, tx_context::sender(ctx));
    }

    /// Transfers an existing MyNFT from the sender to a specified recipient.
    public entry fun transfer_nft(
        nft: MyNFT, // The NFT object is passed by value, consumed by the function
        recipient: address,
        _ctx: &mut TxContext // Context needed if emitting events or other actions
    ) {
        // Since `nft` is passed by value, it's consumed by this function.
        // `transfer::public_transfer` then takes ownership and puts it into the recipient's address.
        transfer::public_transfer(nft, recipient);
    }

    /// Gets the name of an NFT (example of an immutable view function).
    public fun get_nft_name(nft: &MyNFT): &Url {
        &nft.name
    }
}
```

### 2. Publishing Modules

After writing your Move modules, you must publish them to the blockchain. This makes your smart contracts available for interaction.

```bash
# From your package root (my_move_package)
sui client publish --gas-budget 10000000 --json
```

The `--json` flag provides structured output, including the `packageId` (the address of your published module) and any `objectChanges`. You'll need this `packageId` to interact with your contracts.

### 3. Interacting with Entry Functions via SDK (Sui TypeScript SDK)

Once published, users interact with your contracts by calling their `public entry fun`s.

```typescript
// Example using @mysten/sui.js
import { getFullnodeUrl, SuiClient } from '@mysten/sui.js/client';
import { Ed25519Keypair } from '@mysten/sui.js/keypairs/ed25519';
import { TransactionBlock } from '@mysten/sui.js/transactions';

const SUI_RPC_URL = getFullnodeUrl('devnet');
const client = new SuiClient({ url: SUI_RPC_URL });

// Replace with your actual private key or a test keypair
const mnemonic = "YOUR_MNEMONIC_HERE"; // Be cautious with actual private keys!
const keypair = Ed25519Keypair.deriveKeypair(mnemonic);
const senderAddress = keypair.getPublicKey().toSuiAddress();

// Replace with the actual package ID obtained after publishing
const PACKAGE_ID = "0x..."; // Your published package ID

async function mintAndTransferNFT() {
    console.log(`Sender Address: ${senderAddress}`);

    // Create a transaction block
    const tx = new TransactionBlock();

    // Call the `mint_nft` entry function
    tx.moveCall({
        target: `${PACKAGE_ID}::my_nft::mint_nft`,
        arguments: [
            tx.pure('My Awesome NFT'), // name_str
            tx.pure('A very unique digital collectible.'), // description_str
        ],
    });

    // Sign and execute the transaction
    try {
        const result = await client.signAndExecuteTransactionBlock({
            signer: keypair,
            transactionBlock: tx,
            options: {
                showEffects: true,
                showEvents: true,
            },
        });
        console.log('Mint NFT Transaction Result:', JSON.stringify(result, null, 2));

        // You can parse events to find the newly minted NFT ID
        const mintedEvent = result.events?.find(e => e.type === `${PACKAGE_ID}::my_nft::NFTMinted`);
        if (mintedEvent && 'parsedJson' in mintedEvent) {
            const nftId = (mintedEvent.parsedJson as any).nft_id;
            console.log(`Minted NFT ID: ${nftId}`);

            // Now, let's transfer it to another address (replace with a test recipient)
            const recipientAddress = "0x..."; // A different test address
            const txTransfer = new TransactionBlock();

            // Pass the NFT object by ID to the `transfer_nft` entry function
            // The SUI SDK automatically handles wrapping/unwrapping objects for entry functions
            txTransfer.moveCall({
                target: `${PACKAGE_ID}::my_nft::transfer_nft`,
                arguments: [
                    txTransfer.object(nftId), // Pass the NFT object ID
                    txTransfer.pure(recipientAddress), // Recipient address
                ],
            });

            const transferResult = await client.signAndExecuteTransactionBlock({
                signer: keypair,
                transactionBlock: txTransfer,
                options: {
                    showEffects: true,
                },
            });
            console.log('Transfer NFT Transaction Result:', JSON.stringify(transferResult, null, 2));
        }

    } catch (error) {
        console.error('Transaction failed:', error);
    }
}

mintAndTransferNFT();
```

### 4. Testing Move Modules

Writing unit tests for your Move modules is crucial. Move has a built-in testing framework that allows you to simulate on-chain execution.

```move
// sources/my_nft_module.move (add to the end of the file)

#[test_only] // Marks this module as only for testing
module my_move_package::my_nft_tests {
    use sui::test_scenario::{Self as test, TestScenario};
    use sui::tx_context;
    use sui::object;
    use sui::event;
    use my_move_package::my_nft::{Self, MyNFT, NFTMinted};

    const USER_ADDR: address = @0xCAFEE;
    const RECIP_ADDR: address = @0xDEADBEEF;

    #[test]
    fun test_mint_and_transfer_nft() {
        let scenario = test::begin(USER_ADDR);
        let ctx = scenario.ctx();

        // Simulate minting an NFT
        test::next_tx(&mut scenario, USER_ADDR);
        my_nft::mint_nft(b"TestNFT", b"A test description", ctx);

        // Verify that an NFTMinted event was emitted
        assert!(event::exists<NFTMinted>(ctx), 0);
        let events = event::pop_events_for_sender<NFTMinted>(object::id(tx_context::sender(ctx)), ctx);
        assert!(vector::length(&events) == 1, 1);
        let minted_event = vector::pop_back(&mut events);
        let nft_id = minted_event.nft_id;

        // User should now own the NFT.
        // Simulate a new transaction to transfer the NFT.
        test::next_tx(&mut scenario, USER_ADDR); // USER_ADDR is the sender for this tx
        let nft_obj = test::take_from_sender<MyNFT>(&scenario, nft_id); // USER_ADDR takes the NFT object
        my_nft::transfer_nft(nft_obj, RECIP_ADDR, ctx);

        // Verify the NFT is now owned by RECIP_ADDR
        test::next_tx(&mut scenario, RECIP_ADDR); // RECIP_ADDR is the sender for this tx
        assert!(test::has_entity<MyNFT>(&scenario, nft_id), 2); // Check if RECIP_ADDR has the NFT
        let _ = test::take_from_sender<MyNFT>(&scenario, nft_id); // RECIP_ADDR takes the NFT from its address

        test::end(scenario);
    }

    // Add more test cases for edge cases, error conditions, etc.
}
```

## Best Practices

*   **Embrace Resource-Oriented Design:** Think of everything valuable as a `resource`. Design your structs with `has key` and `has store` (or `has drop`, `has copy`) abilities to enforce ownership and scarcity.
*   **Utilize Move's Type System:** Leverage the strong type system and ownership model to prevent common errors. Let the compiler be your first line of defense against bugs.
*   **Write Comprehensive Unit Tests:** Move's `#[test]` attribute and `test_scenario` framework make it easy to simulate on-chain interactions. Test all critical paths, including edge cases and error conditions.
*   **Keep Modules Focused:** Design modules to be small, single-purpose, and reusable. Avoid monolithic contracts.
*   **Manage Gas Wisely:** While Move is efficient, be mindful of computational complexity, especially in loops or when creating/mutating large data structures.
*   **Use `public_transfer` for Ownership Changes:** When a resource's ownership needs to change, use `sui::transfer::public_transfer` (or `aptos_framework::transfer::public_transfer`) to ensure it's correctly assigned to a new address.
*   **Immutable References for View Functions:** For functions that merely read data without modifying state, use immutable references (`&T`) to enforce non-mutating behavior.
*   **Understand Abilities:** Pay close attention to `key`, `store`, `drop`, and `copy`. Misusing them can lead to compile errors or unintended behavior.

## Anti-Patterns

*   **Ignoring Resource Abilities.** Attempting to use a struct as an on-chain object without `has key` and `has store` will result in compilation errors. Not using `has drop` when a resource should be able to be deleted will also cause issues.
