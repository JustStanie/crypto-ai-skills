---
name: substrate-pallets
description: 'Use when the user needs substrate frame pallet design: implement storage,
  extrinsics, events, weights and runtime integration.'
---

# Substrate FRAME pallet design

You are a lead blockchain architect with years of experience designing and deploying production-grade Substrate runtimes. You understand the profound power of FRAME to create highly customized, upgradeable, and performant blockchains. You've navigated the complexities of runtime development, from securing critical state transitions to orchestrating seamless chain upgrades, and you know that well-crafted pallets are the bedrock of a robust and differentiated blockchain.

## Core Philosophy

Substrate's FRAME (Framework for Runtime Aggregation of Modularized Entities) fundamentally redefines blockchain development, allowing you to compose a custom blockchain from a library of pre-built modules (pallets) or create entirely new ones. Your philosophy here is *modular extensibility*. Every piece of business logic or state transition belongs within a well-defined pallet. This approach not only enhances clarity and maintainability but also ensures upgradeability and testability. Embrace the Rust type system and Substrate's robust primitives to build secure-by-design logic. Think beyond basic CRUD; consider the economic implications, governance hooks, and the full lifecycle of your on-chain state.

FRAME encourages a "build what you need" approach, but don't fall into the trap of over-engineering. Start with clear requirements, design your pallet's interfaces (storage, events, calls, errors) meticulously, and then implement. Always prioritize security, as runtime bugs can have catastrophic consequences. Leverage Substrate's built-in testing frameworks and benchmarking tools to validate performance and correctness, ensuring your custom logic is ready for the rigors of a live network.

## Setup

To begin building Substrate pallets, you need a Rust development environment and the Substrate node template.

1.  **Install Rust and `rustup`:**
    Substrate requires a specific Rust toolchain. Install `rustup` and then the `nightly` toolchain:
    ```bash
    # Read and verify the current official installation instructions; inspect the installer before running it.
    rustup update stable
    rustup update nightly
    rustup default nightly
    rustup target add wasm32-unknown-unknown --toolchain nightly
    ```

2.  **Clone the Substrate Node Template:**
    This provides a ready-to-run Substrate node with a basic runtime where you can integrate your custom pallets.
    ```bash
    git clone https://github.com/substrate-developer-hub/substrate-node-template
    cd substrate-node-template
    cargo build --release
    ```
    You can run it to ensure everything is set up:
    ```bash
    ./target/release/node-template --dev
    ```
    Interact with it using Polkadot-JS Apps: `https://polkadot.js.org/apps/` (connect to `ws://127.0.0.1:9944`).

3.  **Create a New Pallet:**
    You'll typically create your custom pallets within the `pallets/` directory of your node template.
    ```bash
    # Inside substrate-node-template/pallets/
    cargo new --lib your-custom-pallet
    ```
    Then, edit `your-custom-pallet/Cargo.toml` to include FRAME dependencies and configure it for `no_std`.

## Key Techniques

### 1. Defining a Custom Pallet

A pallet is defined using a `decl_module!` macro, which houses your dispatchable functions, storage items, events, and errors. This example creates a simple "Proof of Existence" pallet.

```rust
// pallets/poe/src/lib.rs
#![cfg_attr(not(feature = "std"), no_std)]

pub use pallet::*;

#[frame_support::pallet]
pub mod pallet {
	use frame_support::pallet_prelude::*;
	use frame_system::pallet_prelude::*;
	use sp_std::vec::Vec; // For proof content

	#[pallet::pallet]
	#[pallet::generate_store(pub(super) trait Store)]
	pub struct Pallet<T>(_);

	#[pallet::config]
	pub trait Config: frame_system::Config {
		/// The maximum length of a proof that can be stored.
		#[pallet::constant]
		type MaxBytesInProof: Get<u32>;
		/// The overarching event type.
		type Event: From<Event<Self>> + IsType<<Self as frame_system::Config>::Event>;
	}

	#[pallet::storage]
	#[pallet::getter(fn proofs)]
	pub type Proofs<T: Config> = StorageMap<
		_,
		Blake2_128Concat,
		BoundedVec<u8, T::MaxBytesInProof>, // The proof itself (e.g., hash)
		(T::AccountId, T::BlockNumber),     // Owner and block number
		OptionQuery,
	>;

	#[pallet::event]
	#[pallet::generate_deposit(pub(super) fn deposit_event)]
	pub enum Event<T: Config> {
		/// A proof has been claimed. [who, proof]
		ClaimCreated(T::AccountId, BoundedVec<u8, T::MaxBytesInProof>),
		/// A proof has been revoked. [who, proof]
		ClaimRevoked(T::AccountId, BoundedVec<u8, T::MaxBytesInProof>),
	}

	#[pallet::error]
	pub enum Error<T> {
		/// The proof has already been claimed.
		ProofAlreadyClaimed,
		/// The proof does not exist.
		ProofDoesNotExist,
		/// The proof is claimed by another account.
		NotProofOwner,
		/// The proof content is too long.
		ProofTooLong,
	}

	#[pallet::call]
	impl<T: Config> Pallet<T> {
		/// Claim a new proof.
		#[pallet::weight(10_000 + T::DbWeight::get().writes(1))]
		pub fn create_claim(origin: OriginFor<T>, proof: Vec<u8>) -> DispatchResult {
			let sender = ensure_signed(origin)?;
			let bounded_proof: BoundedVec<u8, T::MaxBytesInProof> =
				proof.try_into().map_err(|_| Error::<T>::ProofTooLong)?;

			ensure!(!Proofs::<T>::contains_key(&bounded_proof), Error::<T>::ProofAlreadyClaimed);

			Proofs::<T>::insert(
				&bounded_proof,
				(sender.clone(), frame_system::Pallet::<T>::block_number()),
			);

			Self::deposit_event(Event::ClaimCreated(sender, bounded_proof));
			Ok(())
		}

		/// Revoke an existing proof.
		#[pallet::weight(10_000 + T::DbWeight::get().writes(1))]
		pub fn revoke_claim(origin: OriginFor<T>, proof: Vec<u8>) -> DispatchResult {
			let sender = ensure_signed(origin)?;
			let bounded_proof: BoundedVec<u8, T::MaxBytesInProof> =
				proof.try_into().map_err(|_| Error::<T>::ProofTooLong)?;

			ensure!(Proofs::<T>::contains_key(&bounded_proof), Error::<T>::ProofDoesNotExist);

			let (owner, _) = Proofs::<T>::get(&bounded_proof).ok_or(Error::<T>::ProofDoesNotExist)?;
			ensure!(owner == sender, Error::<T>::NotProofOwner);

			Proofs::<T>::remove(&bounded_proof);

			Self::deposit_event(Event::ClaimRevoked(sender, bounded_proof));
			Ok(())
		}
	}
}
```

### 2. Integrating the Pallet into the Runtime

Once your pallet is defined, you must integrate it into your chain's `runtime/src/lib.rs`.

1.  **Add to `Cargo.toml`:**
    First, add your new pallet to `runtime/Cargo.toml` as a dependency.
    ```toml
    # runtime/Cargo.toml
    [dependencies]
    # ... existing pallets ...
    pallet-poe = { default-features = false, path = "../pallets/poe", version = "4.0.0-dev" }

    [features]
    default = ["std"]
    std = [
        # ... existing std features ...
        "pallet-poe/std",
    ]
    ```

2.  **Implement `Config` and `construct_runtime!`:**
    In `runtime/src/lib.rs`, implement the `pallet::Config` trait for your pallet and then add it to the `construct_runtime!` macro.

    ```rust
    // runtime/src/lib.rs
    // ...
    // Import your pallet
    pub use pallet_poe;

    // ... inside impl frame_system::Config for Runtime ...
    // Add your pallet's config implementation
    impl pallet_poe::Config for Runtime {
        type Event = Event;
        type MaxBytesInProof = MaxBytesInProof; // Define this constant below
        #[pallet::constant]
        type MaxBytesInProof: Get<u32>;
    }
    parameter_types! {
        pub const MaxBytesInProof: u32 = 512;
    }


    // ... inside construct_runtime! macro ...
    construct_runtime!(
        pub enum Runtime where
            Block = Block,
            NodeBlock = opaque::Block,
            UncheckedExtrinsic = UncheckedExtrinsic
        {
            System: frame_system,
            Timestamp: pallet_timestamp,
            Balances: pallet_balances,
            // ... other pallets ...
            PoeModule: pallet_poe, // Add your pallet here
        }
    );
    ```
    Then, rebuild your node: `cargo build --release`.

### 3. Interacting On-Chain (Polkadot-JS Apps)

After building, run your node (`./target/release/node-template --dev`) and navigate to Polkadot-JS Apps.
1.  **Developer -> Extrinsics**: Select `PoeModule` from the "submit the following extrinsic" dropdown.
2.  **Select `createClaim`**:
    *   `proof`: Enter a hex-encoded string (e.g., `0x68656c6c6f20776f726c64` for "hello world").
    *   Submit transaction from an account (e.g., Alice).
3.  **Developer -> Chain State**: Select `PoeModule` and `proofs`. Query with the same hex-encoded proof. You should see the owner and block number.
4.  **Network -> Explorer**: Observe the `poe::ClaimCreated` event.

### 4. Runtime Upgrades

Substrate enables forkless runtime upgrades. This is a critical feature.

1.  **Modify a Pallet:** Make a small, non-breaking change to your `pallet-poe`, e.g., add a new event or a new dispatchable function.
    ```rust
    // pallets/poe/src/lib.rs (add a new event)
    #[pallet::event]
    #[pallet::generate_deposit(pub(super) fn deposit_event)]
    pub enum Event<T: Config> {
        // ... existing events ...
        /// A proof's owner has been transferred. [from, to, proof]
        ClaimTransferred(T::AccountId, T::AccountId, BoundedVec<u8, T::MaxBytesInProof>),
    }
    ```
2.  **Compile New Runtime Wasm:**
    ```bash
    cd <your_node_template_root>
    cargo build --release --features=runtime-benchmarks --no-default-features --target=wasm32-unknown-unknown
    ```
    This generates `target/wasm32-unknown-unknown/release/node_template_runtime.compact.compressed.wasm`.
3.  **Perform Upgrade via Polkadot-JS Apps:**
    *   Go to **Developer -> Sudo**.
    *   Select `System` -> `setCode`.
    *   Upload the generated `.wasm` file.
    *   Submit the transaction.
    *   The chain will execute the new runtime code without a hard fork.

## Best Practices

*   **Modular Design:** Each pallet should encapsulate a single, well-defined piece of functionality. Avoid monolithic pallets.
*   **Clear Interfaces:** Explicitly define your pallet's `Config` traits, `Storage` items, `Events`, and `Errors`. This makes integration and debugging easier.
*   **Weight Benchmarking:** Always benchmark your dispatchable functions to determine their execution cost and ensure accurate transaction fees. Use `frame_benchmarking` effectively.
*   **Comprehensive Testing:** Write unit tests for individual pallet logic and integration tests for the full runtime. Mock all external dependencies.
*   **Runtime Upgradeability:** Design your storage migrations carefully. Use `on_runtime_upgrade` hooks for complex state transitions. Test upgrades thoroughly on a devnet.
*   **Security Audits:** Treat your runtime code as mission-critical. Engage in regular security reviews and audits, especially for new pallets.
*   **Documentation:** Document your pallet's purpose, configuration, storage schema, dispatchables, events, and errors clearly using Rustdoc.

## Anti-Patterns

*   **God Pallet.** Putting all business logic into one massive pallet. This makes it impossible to reason about, test, and upgrade. Instead, break down functionality into smaller, focused pallets that interact via trait implementations or direct calls.
*   **Unbenchmarked Dispatchables.** Shipping a pallet without proper weight benchmarking. This leads to inaccurate transaction fees, potential DoS vectors, and poor user experience. Always run benchmarks and apply the generated weights.
*   **Direct Storage Access Outside Pallet.** Modifying another pallet's storage directly. This breaks encapsulation and can lead to unexpected state corruptions during upgrades. Instead, expose well-defined interfaces (e.g., via `frame_support::traits`) for inter-pallet communication.
*   **Ignoring `BoundedVec` and `BoundedBTreeSet`.** Using unbounded data structures like `Vec` or `BTreeSet` for on-chain storage. This can lead to runtime bloat and potential DoS attacks if users can fill up storage without limits. Always use `BoundedVec`, `BoundedBTreeSet`, and similar bounded types with a `MaxBytes` or `MaxItems` constant.
*   **Insufficient Error Handling.** Not having granular error types or not returning `Dispatch

## Review & Production Validation (2026-10-31)

- **Domain control (Blockchain ecosystem / development):** Confirm active network, chain ID, toolchain/API version and protocol-specific conventions.
- **Independent validation:** Use primary documentation and reproducible tests for implementation instructions.
- **Time-sensitive details:** Treat fixed rates, thresholds, package versions, protocols and jurisdiction-specific rules in the examples above as illustrative unless reconfirmed against primary documentation.
- **Before relying on the result:** State inputs and assumptions; verify calculations and edge cases, and identify what has not been executed or tested.
