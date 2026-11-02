---
name: polkadot-substrate
description: 'Use when the user needs polkadot/substrate chain engineering: design pallets,
  runtimes, weights and governance upgrades.'
---

# Polkadot/Substrate chain engineering

You are a seasoned blockchain architect and parachain developer, deeply familiar with the Substrate framework and the Polkadot ecosystem. You've launched custom runtimes, integrated complex pallets, and orchestrated cross-chain communication (XCM) for high-performance, specialized blockchain applications. Your expertise lies in leveraging Substrate's flexibility to build application-specific chains tailored for specific use cases, rather than shoehorning logic into general-purpose smart contract platforms.

## Core Philosophy

Substrate is not just another blockchain client; it's a modular framework for building *any* blockchain. Its core philosophy centers on providing a "blockchain-in-a-box" experience, allowing you to customize every aspect of your chain's logic, consensus, and governance. Instead of writing smart contracts on a predefined VM, you develop directly at the runtime level using Rust, compiling your logic to WebAssembly (Wasm). This approach offers unparalleled flexibility, performance, and upgradeability.

The Polkadot network extends this philosophy by providing a shared security model (via its Relay Chain) and a robust cross-chain messaging standard (XCM) for interoperability between these custom blockchains, known as parachains. When you build with Substrate, you're not just creating an isolated chain; you're developing a potential participant in a vast, interconnected web of specialized blockchains, unlocking truly novel decentralized applications that span multiple chains. This paradigm shift from dApps on a single chain to dApps leveraging an ecosystem of specialized chains is fundamental to building on Polkadot and Substrate.

## Setup

To begin developing with Substrate, you need the Rust toolchain and the `substrate-node-template`.

1.  **Install Rust:** Substrate development requires a `nightly` Rust toolchain.
    ```bash
    # Install rustup if you don't have it
    # Read and verify the current official installation instructions; inspect the installer before running it.
    source $HOME/.cargo/env
    
    # Add the nightly toolchain and set it as default for your project
    rustup update nightly
    rustup default nightly
    
    # Add the Wasm target for compiling your runtime
    rustup target add wasm32-unknown-unknown
    ```

2.  **Clone the Substrate Node Template:** This provides a basic, runnable Substrate chain.
    ```bash
    git clone https://github.com/substrate-developer-hub/substrate-node-template.git
    cd substrate-node-template
    ```

3.  **Build the Node:** Compile your custom chain.
    ```bash
    cargo build --release
    ```

4.  **Run Your Local Node:** Start your blockchain.
    ```bash
    ./target/release/node-template --dev --ws-port 9944 --rpc-port 9933
    ```
    Your node is now running and accessible via WebSocket at `ws://127.0.0.1:9944`.

5.  **Install `polkadot-js/api` (for client interaction):**
    ```bash
    npm install @polkadot/api
    # or
    yarn add @polkadot/api
    ```

## Key Techniques

### 1. Developing a Custom Pallet

Pallets are the core logic modules of a Substrate runtime. You define storage, events, errors, and dispatchable functions (extrinsics) within them.

```rust
// In your `pallets/template/src/lib.rs` (or your custom pallet's file)

#![cfg_attr(not(feature = "std"), no_std)]

pub use pallet::*;

#[frame_support::pallet]
pub mod pallet {
	use frame_support::pallet_prelude::*;
	use frame_system::pallet_prelude::*;

	#[pallet::pallet]
	#[pallet::generate_store(pub(super) trait Store)]
	pub struct Pallet<T>(_);

	#[pallet::config]
	pub trait Config: frame_system::Config {
		type Event: From<Event<Self>> + IsType<<Self as frame_system::Config>::Event>;
	}

	#[pallet::storage]
	#[pallet::getter(fn get_value)]
	pub type ValueStore<T> = StorageValue<_, u32, ValueQuery>;

	#[pallet::event]
	#[pallet::generate_deposit(pub(super) fn deposit_event)]
	pub enum Event<T: Config> {
		/// A new value has been set. [who, new_value]
		ValueSet(T::AccountId, u32),
	}

	#[pallet::error]
	pub enum Error<T> {
		/// The provided value is too large.
		ValueTooLarge,
	}

	#[pallet::call]
	impl<T: Config> Pallet<T> {
		/// Sets a new value in the storage.
		#[pallet::weight(10_000 + T::DbWeight::get().writes(1))]
		pub fn set_new_value(origin: OriginFor<T>, new_value: u32) -> DispatchResult {
			let sender = ensure_signed(origin)?;

			// Ensure value is not too large
			ensure!(new_value <= 100, Error::<T>::ValueTooLarge);

			<ValueStore<T>>::put(new_value);
			Self::deposit_event(Event::ValueSet(sender, new_value));
			Ok(())
		}
	}
}
```
After defining your pallet, you must add it to your runtime's `src/lib.rs` file.
```rust
// In `runtime/src/lib.rs`
// ...
// Add your pallet to the `construct_runtime!` macro
construct_runtime!(
	pub enum Runtime where
		Block = Block,
		NodeBlock = opaque::Block,
		UncheckedExtrinsic = UncheckedExtrinsic,
	{
		System: frame_system,
		Balances: pallet_balances,
		// ... other pallets
		TemplateModule: pallet_template, // Your custom pallet
	}
);
// ...
// Implement the `Config` trait for your pallet
impl pallet_template::Config for Runtime {
	type Event = Event;
}
```

### 2. Interacting with Your Chain using `polkadot-js/api`

The `@polkadot/api` library is your primary tool for connecting to, querying, and submitting transactions to any Substrate-based chain.

```javascript
// index.js
import { ApiPromise, WsProvider, Keyring } from '@polkadot/api';

async function main() {
  const provider = new WsProvider('ws://127.0.0.1:9944');
  const api = await ApiPromise.create({ provider });

  console.log(`Connected to: ${api.genesisHash.toHex()}`);

  // 1. Query chain state (e.g., account balance)
  const keyring = new Keyring({ type: 'sr25519' });
  const alice = keyring.addFromUri('//Alice');
  const bob = keyring.addFromUri('//Bob');

  const { data: balanceAlice } = await api.query.system.account(alice.address);
  console.log(`Alice's balance: ${balanceAlice.free}`);

  // Query your custom pallet's storage
  const customValue = await api.query.templateModule.valueStore();
  console.log(`Custom value from pallet: ${customValue.toNumber()}`);

  // 2. Submit a transaction (e.g., transfer funds)
  const transfer = api.tx.balances.transfer(bob.address, 12345);
  const hash = await transfer.signAndSend(alice);
  console.log(`Transfer sent with hash ${hash.toHex()}`);

  // 3. Submit a transaction to your custom pallet
  const setNewValueTx = api.tx.templateModule.setNewValue(42);
  const setValueHash = await setNewValueTx.signAndSend(alice);
  console.log(`Set new value with hash ${setValueHash.toHex()}`);

  // 4. Subscribe to events
  console.log('Listening for events...');
  const unsubscribe = await api.query.system.events((events) => {
    events.forEach((record) => {
      const { event, phase } = record;
      const types = api.registry.lookup.getSiType(event.typeDef.type);
      console.log(`\t${event.section}:${event.method}:: (phase=${phase.toString()})`);
      console.log(`\t\t${event.meta.docs.toString()}`);
      event.data.forEach((data, index) => {
        console.log(`\t\t\t${types.def.asVariant.variants[event.index].fields[index].name}: ${data.toString()}`);
      });
    });
  });

  // Keep subscription open for a bit, then close
  setTimeout(() => {
    unsubscribe();
    console.log('Unsubscribed from events.');
    process.exit(0);
  }, 30000);
}

main().catch(console.error);
```

### 3. Runtime Upgrades

One of Substrate's killer features is its forkless runtime upgrade capability. You can deploy new logic to your chain without a hard fork. This is typically done via a `set_code` extrinsic from a privileged account (e.g., sudo or governance).

1.  **Build your new runtime Wasm blob:**
    ```bash
    cargo build --release --features runtime-wasm
    ```
    This generates `target/release/wbuild/node-template-runtime/node_template_runtime.compact.compressed.wasm`.

2.  **Submit the upgrade transaction using `polkadot-js/api`:**
    ```javascript
    import { ApiPromise, WsProvider, Keyring } from '@polkadot/api';
    import { readFileSync } from 'fs';

    async function upgradeRuntime() {
      const provider = new WsProvider('ws://127.0.0.1:9944');
      const api = await ApiPromise.create({ provider });
      const keyring = new Keyring({ type: 'sr25519' });
      const sudoAccount = keyring.addFromUri('//Alice'); // Assuming Alice is sudo

      // Read the new runtime Wasm blob
      const code = readFileSync('./target/release/wbuild/node-template-runtime/node_template_runtime.compact.compressed.wasm');

      // Create the `set_code` extrinsic, wrapped in a `sudo` call
      const setCodeTx = api.tx.system.setCode(code);
      const sudoCall = api.tx.sudo.sudo(setCodeTx);

      console.log('Submitting runtime upgrade...');
      const hash = await sudoCall.signAndSend(sudoAccount, ({ status }) => {
        if (status.isInBlock) {
          console.log(`Runtime upgrade included in block: ${status.asInBlock}`);
        } else if (status.isFinalized) {
          console.log(`Runtime upgrade finalized. Chain is now running new code.`);
          process.exit(0);
        }
      });
      console.log(`Transaction hash: ${hash.toHex()}`);
    }

    upgradeRuntime().catch(console.error);
    ```

### 4. Cross-Consensus Message Format (XCM) Basics

XCM is the language for cross-chain communication in Polkadot. It allows parachains to send messages, transfer assets, and execute logic across chains using a standardized instruction set.

## Anti-Patterns

*   **Unbounded Storage Growth in Pallets.** Using StorageMaps or StorageValues that grow without bound allows state bloat that degrades node performance. Implement storage deposits or bounded collections.

*   **Runtime Upgrades Without Migration Testing.** Deploying forkless runtime upgrades without testing storage migrations on a forked chain risks corrupting live state when storage layouts change between versions.

*   **Ignoring Weight Estimation.** Assigning incorrect or hardcoded weights to dispatchable functions allows transactions that consume more resources than budgeted, potentially stalling block production.

*   **Sudo-Only Governance Long-Term.** Maintaining sudo access as the primary governance mechanism beyond the initial bootstrap phase centralizes control and undermines the decentralization properties that Substrate-based chains should provide.

*   **Tight Coupling Between Pallets.** Building pallets with direct dependencies on other pallets' storage or internal functions instead of using trait-based interfaces prevents modular composition and makes runtime upgrades fragile.

## Review & Production Validation (2026-10-31)

- **Domain control (Blockchain ecosystem / development):** Confirm active network, chain ID, toolchain/API version and protocol-specific conventions.
- **Independent validation:** Use primary documentation and reproducible tests for implementation instructions.
- **Time-sensitive details:** Treat fixed rates, thresholds, package versions, protocols and jurisdiction-specific rules in the examples above as illustrative unless reconfirmed against primary documentation.
- **Before relying on the result:** State inputs and assumptions; verify calculations and edge cases, and identify what has not been executed or tested.
