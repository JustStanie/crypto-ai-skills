---
name: solana-anchor-framework
description: 'Use when the user needs solana anchor framework patterns: design accounts,
  IDLs, PDAs, constraints, CPI and Anchor tests.'
---

# Solana Anchor framework patterns

You are a seasoned Solana developer, intimately familiar with the Anchor framework, capable of designing, implementing, and deploying secure, efficient, and scalable on-chain programs and client-side interactions. You understand how Anchor streamlines the complexities of Solana's account model and instruction processing, enabling rapid development of robust decentralized applications.

## Core Philosophy

Anchor's core philosophy is to abstract away much of the boilerplate associated with Solana program development, allowing you to focus on your application's logic. It achieves this through a combination of Rust macros, an opinionated project structure, and automatic Interface Definition Language (IDL) generation. This IDL then serves as a single source of truth for both your on-chain program and your off-chain client, ensuring type safety and simplifying interactions.

The framework emphasizes security by providing declarative account validation and common constraint checks directly within your account structs. This significantly reduces the surface area for common vulnerabilities like missing signer checks, incorrect account owners, or rent attacks. By embracing Anchor, you adopt a development pattern that prioritizes clarity, testability, and a unified development experience from smart contract to client application.

## Setup

Before you can build with Anchor, ensure you have Rust, the Solana CLI, and the Anchor Version Manager (AVM) installed.

1.  **Install Rust:**
    ```bash
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
    source $HOME/.cargo/env
    rustup update
    ```

2.  **Install Solana CLI:**
    ```bash
    # Install a supported Solana CLI version from the current official documentation; do not pin an obsolete installer URL.
    export PATH="/home/youruser/.local/share/solana/install/active_release/bin:$PATH"
    solana --version
    ```
    *Replace `youruser` with your actual username.*

3.  **Install Anchor Version Manager (AVM):**
    ```bash
    cargo install --git https://github.com/coral-xyz/anchor avm --locked --force
    avm install latest
    avm use latest
    anchor --version
    ```

4.  **Create a New Anchor Project:**
    ```bash
    anchor init my-anchor-project
    cd my-anchor-project
    anchor build # Compiles your program
    anchor test  # Runs default tests
    ```

## Key Techniques

### 1. Defining an Anchor Program and Instruction

An Anchor program consists of a Rust crate with a `lib.rs` defining the program logic and an `accounts.rs` defining account validation. Every instruction takes a `Context` struct that specifies the required accounts.

```rust
// programs/my-anchor-project/src/lib.rs
use anchor_lang::prelude::*;

declare_id!("Fg6PaFpoGXkYsidMpWTK6W2BeZ7FEfcYkg476zPFsLnS"); // Replace with your program ID

#[program]
pub mod my_anchor_project {
    use super::*;

    pub fn initialize(ctx: Context<Initialize>, data: u64) -> Result<()> {
        let my_account = &mut ctx.accounts.my_account;
        my_account.data = data;
        my_account.owner = ctx.accounts.signer.key();
        msg!("Initialized MyAccount with data: {}", data);
        Ok(())
    }

    pub fn update(ctx: Context<Update>, new_data: u64) -> Result<()> {
        let my_account = &mut ctx.accounts.my_account;
        require_keys_eq!(my_account.owner, ctx.accounts.signer.key(), MyError::Unauthorized);
        my_account.data = new_data;
        msg!("Updated MyAccount data to: {}", new_data);
        Ok(())
    }
}

// accounts.rs (often defined in lib.rs for simple programs)
#[derive(Accounts)]
pub struct Initialize<'info> {
    // `init` creates the account if it doesn't exist.
    // `payer` specifies who pays for account creation (rent).
    // `space` defines the initial size of the account. Add 8 for Anchor's discriminator.
    #[account(init, payer = signer, space = 8 + MyAccount::LEN)]
    pub my_account: Account<'info, MyAccount>,
    #[account(mut)]
    pub signer: Signer<'info>,
    pub system_program: Program<'info, System>,
}

#[derive(Accounts)]
pub struct Update<'info> {
    // `mut` allows modification, `has_one` checks the owner field matches `signer.key()`
    #[account(mut)]
    pub my_account: Account<'info, MyAccount>,
    #[account(mut)]
    pub signer: Signer<'info>,
}

#[account]
pub struct MyAccount {
    pub data: u64,
    pub owner: Pubkey,
}

impl MyAccount {
    // Calculate the space needed for your account data
    const LEN: usize = 8 + 32; // u64 (8 bytes) + Pubkey (32 bytes)
}

#[error_code]
pub enum MyError {
    #[msg("You are not authorized to perform this action.")]
    Unauthorized,
}
```

### 2. Client-Side Interaction

Anchor generates an IDL (Interface Definition Language) that the client SDK uses to interact with your program safely.

```typescript
// tests/my-anchor-project.ts or client/src/index.ts
import * as anchor from "@coral-xyz/anchor";
import { Program } from "@coral-xyz/anchor";
import { MyAnchorProject } from "../target/types/my_anchor_project"; // Generated types

describe("my-anchor-project", () => {
  const provider = anchor.AnchorProvider.env();
  anchor.setProvider(provider);

  const program = anchor.workspace.MyAnchorProject as Program<MyAnchorProject>;
  const myAccount = anchor.web3.Keypair.generate();

  it("Is initialized!", async () => {
    const initialData = new anchor.BN(123);

    // Call the `initialize` instruction
    await program.methods
      .initialize(initialData)
      .accounts({
        myAccount: myAccount.publicKey,
        signer: provider.wallet.publicKey,
        systemProgram: anchor.web3.SystemProgram.programId,
      })
      .signers([myAccount]) // `myAccount` needs to sign if `init` creates it
      .rpc();

    // Fetch the account data to verify
    const account = await program.account.myAccount.fetch(myAccount.publicKey);
    console.log("Your account data:", account.data.toString());
    anchor.assert.equal(account.data.toString(), initialData.toString());
    anchor.assert.ok(account.owner.equals(provider.wallet.publicKey));
  });

  it("Updates the account", async () => {
    const newData = new anchor.BN(456);

    // Call the `update` instruction
    await program.methods
      .update(newData)
      .accounts({
        myAccount: myAccount.publicKey,
        signer: provider.wallet.publicKey,
      })
      .rpc();

    // Fetch the updated account data
    const account = await program.account.myAccount.fetch(myAccount.publicKey);
    anchor.assert.equal(account.data.toString(), newData.toString());
  });
});
```

### 3. Program-Derived Addresses (PDAs)

PDAs are crucial for allowing programs to own accounts without requiring a private key. Anchor simplifies their creation and validation.

```rust
// programs/my-anchor-project/src/lib.rs (within `my_anchor_project` module)
pub fn create_pda_account(ctx: Context<CreatePdaAccount>, seed_data: String, value: u64) -> Result<()> {
    let pda_account = &mut ctx.accounts.pda_account;
    pda_account.owner = ctx.accounts.signer.key();
    pda_account.seed_data = seed_data;
    pda_account.value = value;
    Ok(())
}

#[derive(Accounts)]
#[instruction(seed_data: String)] // Instruction arguments can be used in seeds
pub struct CreatePdaAccount<'info> {
    #[account(
        init,
        payer = signer,
        space = 8 + PdaAccount::LEN,
        seeds = [b"my_pda_state", signer.key().as_ref(), seed_data.as_bytes()],
        bump
    )]
    pub pda_account: Account<'info, PdaAccount>,
    #[account(mut)]
    pub signer: Signer<'info>,
    pub system_program: Program<'info, System>,
}

#[account]
pub struct PdaAccount {
    pub owner: Pubkey,
    pub seed_data: String, // String length needs to be handled carefully for fixed space
    pub value: u64,
}

impl PdaAccount {
    // For String, you often need a max length or dynamic sizing,
    // here we'll assume a max length for simplicity for `space`.
    const MAX_SEED_DATA_LEN: usize = 32;
    const LEN: usize = 32 + (4 + Self::MAX_SEED_DATA_LEN) + 8; // Pubkey + String (length prefix + data) + u64
}
```

```typescript
// Client-side for PDA
import * as anchor from "@coral-xyz/anchor";
import { Program } from "@coral-xyz/anchor";
import { MyAnchorProject } from "../target/types/my_anchor_project";

describe("PDA interaction", () => {
  const provider = anchor.AnchorProvider.env();
  anchor.setProvider(provider);
  const program = anchor.workspace.MyAnchorProject as Program<MyAnchorProject>;

  it("Creates a PDA account", async () => {
    const seedData = "unique_seed";
    const [pdaAccountPk] = anchor.web3.PublicKey.findProgramAddressSync(
      [
        Buffer.from("my_pda_state"),
        provider.wallet.publicKey.toBuffer(),
        Buffer.from(seedData),
      ],
      program.programId
    );

    await program.methods
      .createPdaAccount(seedData, new anchor.BN(999))
      .accounts({
        pdaAccount: pdaAccountPk,
        signer: provider.wallet.publicKey,
        systemProgram: anchor.web3.SystemProgram.programId,
      })
      .rpc();

    const pdaAccount = await program.account.pdaAccount.fetch(pdaAccountPk);
    anchor.assert.equal(pdaAccount.value.toString(), "999");
    anchor.assert.equal(pdaAccount.seedData, seedData);
  });
});
```

## Best Practices

*   **Test Extensively with `anchor test`**: Leverage Anchor's built-in testing framework. It provides a local validator and a JavaScript/TypeScript test environment that mimics real-world interaction, making it easy to catch bugs early.
*   **Validate All Inputs and Constraints**: Always double-check account properties (e.g., `signer`, `mut`, `owner`, `has_one`) and instruction arguments. Anchor's declarative syntax makes this straightforward.
*   **Use PDAs for Program-Owned Data**: Design your program to use Program-Derived Addresses (PDAs) for all accounts that need to be owned or controlled by your program. This is fundamental to Solana's security model.
*   **Be Mindful of Account Space**: Accurately calculate the `space` required for new accounts. Over-allocating wastes rent, under-allocating can lead to errors or truncated data. Use constants for `LEN` on structs.
*   **Implement Robust Error Handling**: Define custom error codes using `#[error_code]` and use `require!`, `require_eq!`, `require_keys_eq!` macros for clear error messages that the client can interpret.
*   **Keep Your Program ID Consistent**: Define your `declare_id!` in `lib.rs` and ensure your client and tests use the correct program ID. Use `anchor deploy` to manage this across environments.

## Anti-Patterns

*   **Missing Account Ownership Validation.** Accepting accounts in instruction handlers without verifying their owner program ID allows attackers to pass accounts owned by malicious programs that mimic expected data layouts.

*   **Incorrect PDA Bump Seed Handling.** Not storing and reusing the canonical bump seed for PDAs causes lookup failures when a different bump is used for derivation versus validation.

*   **Inaccurate Account Space Calculation.** Under-allocating space for account data causes truncation errors, while over-allocating wastes rent SOL. Use explicit `LEN` constants derived from struct field sizes plus discriminator.

*   **Unchecked Close Account Vulnerabilities.** Closing accounts without zeroing their data and transferring all lamports allows revival attacks where the account is recreated with stale data in the same slot.

*   **Skipping Anchor Constraint Macros.** Writing manual validation logic instead of using Anchor's declarative constraints (`#[account(has_one, constraint, seeds)]`) bypasses the framework's safety guarantees and produces less readable, more error-prone code.

## Version and Evidence Check

The Solana CLI, Anchor and Rust toolchain have compatibility constraints. Resolve an explicitly supported version set from current official documentation; avoid executing version-pinned installation commands blindly.
