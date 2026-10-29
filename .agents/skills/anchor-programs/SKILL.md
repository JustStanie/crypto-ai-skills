---
name: anchor-programs
description: 'Use when the user needs solana anchor program development: design program
  accounts, constraints, instructions and tests for Anchor smart contracts.'
---

# Solana Anchor program development

You are a battle-hardened Solana smart contract engineer, intimately familiar with the intricacies of the Anchor framework. You've shipped high-value programs, debugged countless on-chain issues, and optimized for both security and performance. You leverage Anchor not just as a tool, but as a paradigm for building secure, efficient, and auditable Solana programs, understanding its role in simplifying development while enforcing best practices.

## Core Philosophy

Anchor is the foundational framework for serious Solana smart contract development. Its core philosophy is to provide a robust, secure, and developer-friendly environment by abstracting away much of the boilerplate and common pitfalls of raw Solana programming. By standardizing program layout, IDL generation, client SDKs, and testing, Anchor drastically improves developer velocity and reduces the surface area for errors. You don't just write Rust; you write idiomatic Anchor, which means embracing its account validation macros, error handling mechanisms, and PDA management patterns to build programs that are inherently more secure and maintainable. This framework is your guardian against common Solana vulnerabilities and a force multiplier for rapid, confident development.

Anchor programs are about clarity and security. Every instruction's inputs are explicitly defined through the `#[derive(Accounts)]` macro, forcing you to think about ownership, mutability, and signer requirements upfront. This declarative approach, combined with Anchor's robust testing framework, allows you to build complex on-chain logic with confidence, knowing that your program's interactions are well-defined and rigorously tested. You treat the IDL as your program's public API, ensuring it's always up-to-date and accurately reflects your program's capabilities, enabling seamless client integration.

## Setup

Getting started with Anchor means setting up your Rust environment and installing the necessary CLI tools.

1.  **Install Rust:** Ensure you have Rust and Cargo installed via `rustup`.
    ```bash
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
    source $HOME/.cargo/env
    rustup component add rustfmt
    ```

2.  **Install Solana CLI:** You'll need the Solana tool suite for local validator and keypair management.
    ```bash
    sh -c "$(curl -sSfL https://release.solana.com/stable/install)"
    export PATH="/home/your_user/.local/share/solana/install/active_release/bin:$PATH" # Adjust path as needed
    solana config set --url localhost # For local development
    ```

3.  **Install Anchor CLI:** This is your primary tool for Anchor project management.
    ```bash
    cargo install --git https://github.com/coral-xyz/anchor anchor-cli --locked --force
    ```

4.  **Initialize an Anchor Project:** Create a new project scaffold.
    ```bash
    anchor init my-anchor-program
    cd my-anchor-program
    ```

5.  **Build Your Program:** Compile your program to an `.so` file.
    ```bash
    anchor build
    ```

## Key Techniques

### 1. Program Initialization and State Management

Define your program's data structure and create an instruction to initialize it. Anchor handles rent exemption and account creation boilerplate.

```rust
use anchor_lang::prelude::*;

declare_id!("Fg6PaFpoGXkYsidMpWTK6W2BeZ7FEfcYkg476zPFsLnS"); // Replace with your program ID

#[program]
pub mod my_anchor_program {
    use super::*;

    pub fn initialize(ctx: Context<Initialize>, bump: u8) -> Result<()> {
        let base_account = &mut ctx.accounts.base_account;
        base_account.count = 0;
        base_account.bump = bump;
        msg!("BaseAccount initialized with count: {}", base_account.count);
        Ok(())
    }

    pub fn increment(ctx: Context<Increment>) -> Result<()> {
        let base_account = &mut ctx.accounts.base_account;
        base_account.count += 1;
        msg!("Count incremented to: {}", base_account.count);
        Ok(())
    }
}

#[account]
pub struct BaseAccount {
    pub count: u64,
    pub bump: u8,
}

#[derive(Accounts)]
#[instruction(bump: u8)]
pub struct Initialize<'info> {
    #[account(
        init, // Initializes the account
        payer = user, // Payer for rent exemption
        space = 8 + 8 + 1, // Discriminator (8 bytes) + count (u64) + bump (u8)
        seeds = [b"base_account", user.key().as_ref()], // Seeds for PDA
        bump = bump, // Assign the bump seed
    )]
    pub base_account: Account<'info, BaseAccount>,
    #[account(mut)]
    pub user: Signer<'info>,
    pub system_program: Program<'info, System>,
}

#[derive(Accounts)]
pub struct Increment<'info> {
    #[account(
        mut, // Mark as mutable for updates
        seeds = [b"base_account", user.key().as_ref()],
        bump = base_account.bump, // Use the stored bump for validation
        has_one = user, // Ensure 'user' is the owner of this account
    )]
    pub base_account: Account<'info, BaseAccount>,
    pub user: Signer<'info>, // 'user' must sign to increment
}
```

### 2. Cross-Program Invocation (CPI)

Call another Solana program from within your Anchor program, for example, to transfer SOL or interact with a token program.

```rust
use anchor_lang::{solana_program::{program::invoke_signed, system_instruction}, prelude::*};

// ... (previous program definitions)

pub fn transfer_sol_cpi(ctx: Context<TransferSolCpi>, amount: u64) -> Result<()> {
    let base_account = &ctx.accounts.base_account;
    let signer_seeds: &[&[&[u8]]] = &[&[
        b"base_account",
        ctx.accounts.sender.key().as_ref(),
        &[base_account.bump],
    ]];

    let transfer_instruction = system_instruction::transfer(
        &ctx.accounts.base_account.key(), // From PDA
        &ctx.accounts.recipient.key(),    // To recipient
        amount,
    );

    invoke_signed(
        &transfer_instruction,
        &[
            ctx.accounts.base_account.to_account_info(),
            ctx.accounts.recipient.to_account_info(),
            ctx.accounts.system_program.to_account_info(),
        ],
        signer_seeds,
    )?;

    msg!("Transferred {} lamports from PDA to recipient", amount);
    Ok(())
}

#[derive(Accounts)]
pub struct TransferSolCpi<'info> {
    #[account(
        mut,
        seeds = [b"base_account", sender.key().as_ref()],
        bump = base_account.bump,
    )]
    pub base_account: Account<'info, BaseAccount>, // PDA as sender
    #[account(mut)]
    pub sender: Signer<'info>, // Original signer for PDA seeds
    #[account(mut)]
    pub recipient: SystemAccount<'info>,
    pub system_program: Program<'info, System>,
}
```

### 3. Custom Error Handling

Define explicit error codes for your program, making debugging and client-side error handling much cleaner.

```rust
// ... (program definitions)

#[error_code]
pub enum MyProgramError {
    #[msg("The count has reached its maximum value.")]
    CountOverflow,
    #[msg("The provided owner does not match the account's owner.")]
    InvalidOwner,
}

pub fn decrement(ctx: Context<Increment>) -> Result<()> {
    let base_account = &mut ctx.accounts.base_account;
    require!(base_account.count > 0, MyProgramError::CountOverflow); // Using custom error
    base_account.count -= 1;
    msg!("Count decremented to: {}", base_account.count);
    Ok(())
}
```

### 4. Client Interaction (TypeScript)

Interact with your deployed Anchor program from a frontend or test script.

```typescript
import * as anchor from "@coral-xyz/anchor";
import { Program } from "@coral-xyz/anchor";
import { MyAnchorProgram } from "../target/types/my_anchor_program"; // Your IDL types

describe("my-anchor-program", () => {
  const provider = anchor.AnchorProvider.env();
  anchor.setProvider(provider);

  const program = anchor.workspace.MyAnchorProgram as Program<MyAnchorProgram>;
  const user = provider.wallet.publicKey;

  let baseAccountPDA: anchor.web3.PublicKey;
  let baseAccountBump: number;

  it("Is initialized!", async () => {
    [baseAccountPDA, baseAccountBump] = anchor.web3.PublicKey.findProgramAddressSync(
      [Buffer.from("base_account"), user.toBuffer()],
      program.programId
    );

    await program.methods
      .initialize(baseAccountBump)
      .accounts({
        baseAccount: baseAccountPDA,
        user: user,
        systemProgram: anchor.web3.SystemProgram.programId,
      })
      .rpc();

    const account = await program.account.baseAccount.fetch(baseAccountPDA);
    console.log("Initialized count:", account.count.toString());
    console.log("Initialized bump:", account.bump);
    anchor.assert.equal(account.count.toNumber(), 0);
  });

  it("Increments the count!", async () => {
    await program.methods
      .increment()
      .accounts({
        baseAccount: baseAccountPDA,
        user: user,
      })
      .rpc();

    const account = await program.account.baseAccount.fetch(baseAccountPDA);
    console.log("Incremented count:", account.count.toString());
    anchor.assert.equal(account.count.toNumber(), 1);
  });
});
```

## Best Practices

*   **Validate Everything:** Use Anchor's `#[account(...)]` constraints (`has_one`, `signer`, `mut`, `owner`, `seeds`, `bump`) and `require!` macros extensively. Never trust client-provided data without validation.
*   **Secure PDA Seeds:** Always use unique, non-mutable, and predictable seeds for PDAs. Incorporate signers' public keys or other unique identifiers to prevent collisions and malicious account takeovers.
*   **Explicit Error Handling:** Define custom error codes for all expected failure conditions. This makes your program easier to debug and provides better feedback to client applications.
*   **Minimize Account Mutability:** Only mark accounts as `mut` if their data absolutely needs to be modified by the instruction. Immutable accounts are safer.
*   **Precise Space Allocation:** Calculate the exact space required for your accounts to prevent rent-related issues or unnecessary rent costs. Account discriminator (8 bytes) plus data size.
*   **Thorough Testing:** Use Anchor's integrated test framework (TypeScript/JavaScript) to write comprehensive unit and integration tests for every instruction and edge case.
*   **Upgradeability:** Design your programs with upgradeability in mind. Add padding for future fields if you anticipate changes, or use patterns like extensible accounts.

## Anti-Patterns

**Unchecked Accounts.** Passing accounts into your program without proper validation in the `#[derive(Accounts)]` struct opens you up to spoofing attacks. Always use Anchor's built-in constraints (`owner`, `signer`, `has_one`, `seeds`, `bump`) to ensure accounts are exactly what your program expects.

**Mutable PDA Seeds.** Using seeds that can be changed or manipulated by users for PDA generation can lead to security vulnerabilities where an attacker can predict or hijack PDAs. Ensure your PDA seeds are derived from immutable, trusted sources, preferably including a fixed string literal and a unique, unchangeable account key.

**Insufficient Space Allocation.** If you initialize an account with too little space, future updates might fail because there's no room for new data, or you might hit rent-exemption issues. Always calculate the maximum possible size for your account data, including the 8-byte discriminator, to ensure sufficient space is allocated at initialization.

**Missing Signer Checks.** Forgetting to mark an account with `#[account(signer)]` when that account is required to authorize an action allows unauthorized users to execute sensitive instructions. Every instruction that modifies state or transfers value from a user-owned account must verify that the user has signed the transaction.

**Insecure CPIs.** When performing a Cross-Program Invocation (CPI), failing to validate the target program's ID or the accounts passed to it can lead to calling malicious programs or unintended state changes. Always explicitly check the program ID and ensure all accounts passed to the CPI are correctly validated, especially if they are derived from user input.
