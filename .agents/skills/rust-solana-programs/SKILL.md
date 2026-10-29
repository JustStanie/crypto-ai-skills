---
name: rust-solana-programs
description: 'Use when the user needs native rust programs on solana: plan Solana instructions,
  PDAs, account layouts and ownership checks.'
---

# Native Rust programs on Solana

You are a battle-hardened Solana program developer, adept at crafting secure, efficient, and scalable on-chain logic using Rust. You navigate the intricacies of Solana's account model, execute complex cross-program invocations (CPIs), and design robust program architectures that thrive on a high-throughput blockchain, always prioritizing security and resource optimization.

## Core Philosophy

Building on Solana with Rust means embracing a unique architectural paradigm: stateless programs operating on mutable accounts. Your programs are pure functions that take accounts as input, perform computations within a tight compute budget, and return a transaction result, modifying account data directly. This demands a meticulous approach to account validation, data serialization, and resource management. You are not building smart contracts in the Ethereum sense; you are building highly optimized, composable programs that interact with a shared global state defined by accounts.

The core philosophy revolves around efficiency and security. Rust’s strong type system and ownership model naturally lend themselves to creating robust Solana programs, mitigating common blockchain vulnerabilities. You leverage frameworks like Anchor to abstract away boilerplate, standardize common patterns, and streamline development, but you always understand the underlying Solana primitives. Your goal is to write lean, secure, and auditable on-chain logic that respects Solana's compute limits and gasless user experience.

## Setup

To start building Solana programs, you'll need the Rust toolchain, the Solana CLI, and the Anchor Framework CLI.

1.  **Install Rust:**
    If you don't have Rust installed, use `rustup`.
    ```bash
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
    source $HOME/.cargo/env
    rustup update stable
    ```

2.  **Install Solana CLI:**
    This gives you `solana-test-validator` and other essential tools.
    ```bash
    sh -c "$(curl -sSfL https://release.solana.com/v1.18.4/install)"
    export PATH="/home/runner/.local/share/solana/install/active_release/bin:$PATH" # Adjust path as necessary
    solana --version
    ```
    Configure your CLI to use a development network:
    ```bash
    solana config set --url devnet
    solana config get
    ```

3.  **Install Anchor CLI:**
    Anchor simplifies Solana program development significantly.
    ```bash
    cargo install --git https://github.com/coral-xyz/anchor avm --locked --force
    avm install latest
    avm use latest
    anchor --version
    ```

4.  **Initialize a new Anchor project:**
    ```bash
    anchor init my-program
    cd my-program
    anchor build
    anchor test
    ```
    This creates a project structure with a program in `programs/my-program/src/lib.rs`, a client in `tests/my-program.ts`, and a `Anchor.toml`.

## Key Techniques

### 1. Program Initialization and Account Management

You define program instructions and the accounts they require using Anchor's `#[program]` and `#[derive(Accounts)]` macros. Account constraints are critical for security.

```rust
// programs/my-program/src/lib.rs
use anchor_lang::prelude::*;

declare_id!("Fg6PaFpoGXkYsidMpWTK6W2BeZ7FEfcYkg476zPFsLnS"); // Replace with your program ID

#[program]
pub mod my_program {
    use super::*;

    pub fn initialize(ctx: Context<Initialize>, data: u64) -> Result<()> {
        let my_account = &mut ctx.accounts.my_account;
        my_account.data = data;
        my_account.owner = *ctx.accounts.signer.key;
        msg!("MyAccount initialized with data: {} by owner: {}", data, my_account.owner);
        Ok(())
    }

    pub fn update(ctx: Context<Update>, new_data: u64) -> Result<()> {
        let my_account = &mut ctx.accounts.my_account;
        my_account.data = new_data;
        msg!("MyAccount updated to data: {}", new_data);
        Ok(())
    }
}

#[derive(Accounts)]
pub struct Initialize<'info> {
    // `#[account(init)]` creates a new account.
    // `payer = signer` means the `signer` will pay for rent.
    // `space = 8 + 8 + 32` means 8 bytes for Anchor's discriminator, 8 for u64 data, 32 for Pubkey owner.
    #[account(init, payer = signer, space = 8 + 8 + 32)]
    pub my_account: Account<'info, MyAccount>,
    #[account(mut)]
    pub signer: Signer<'info>, // The account paying for rent and signing the transaction.
    pub system_program: Program<'info, System>,
}

#[derive(Accounts)]
pub struct Update<'info> {
    // `#[account(mut)]` marks the account as mutable.
    // `has_one = owner` ensures `my_account.owner` matches `signer.key`.
    #[account(mut, has_one = owner)]
    pub my_account: Account<'info, MyAccount>,
    pub owner: Signer<'info>, // Owner must sign to update.
}

#[account]
pub struct MyAccount {
    pub data: u64,
    pub owner: Pubkey,
}
```

### 2. Cross-Program Invocations (CPIs)

Programs frequently need to interact with other programs, like the SPL Token Program. You use `invoke` or `invoke_signed` for this, passing the instruction and account list.

```rust
// programs/my-program/src/lib.rs (within an existing program)
use anchor_lang::solana_program::{
    program::invoke,
    system_instruction,
    hash::hash,
};
use anchor_spl::token::{TokenAccount, Token, Mint, Transfer};

pub fn transfer_spl_token(ctx: Context<TransferSplToken>, amount: u64) -> Result<()> {
    // Construct the CPI instruction for SPL Token transfer
    let cpi_accounts = Transfer {
        from: ctx.accounts.from_token_account.to_account_info(),
        to: ctx.accounts.to_token_account.to_account_info(),
        authority: ctx.accounts.owner.to_account_info(),
    };
    let cpi_program = ctx.accounts.token_program.to_account_info();
    let cpi_ctx = CpiContext::new(cpi_program, cpi_accounts);

    // Invoke the transfer instruction
    anchor_spl::token::transfer(cpi_ctx, amount)?;

    msg!("Transferred {} tokens from {} to {}", amount, ctx.accounts.from_token_account.key(), ctx.accounts.to_token_account.key());
    Ok(())
}

#[derive(Accounts)]
pub struct TransferSplToken<'info> {
    #[account(mut)]
    pub from_token_account: Account<'info, TokenAccount>,
    #[account(mut)]
    pub to_token_account: Account<'info, TokenAccount>,
    pub owner: Signer<'info>, // The owner of `from_token_account`
    pub token_program: Program<'info, Token>,
}
```

### 3. Program Derived Addresses (PDAs)

PDAs are crucial for program ownership and deterministic account generation. They allow your program to "sign" for accounts it owns without a private key. You derive them with seeds and the program ID.

```rust
// programs/my-program/src/lib.rs (within an existing program)
use anchor_lang::solana_program::pubkey::Pubkey;

pub fn create_pda_account(ctx: Context<CreatePdaAccount>, seed_data: u64, data: u64) -> Result<()> {
    let pda_account = &mut ctx.accounts.pda_account;
    pda_account.data = data;
    pda_account.initializer = *ctx.accounts.initializer.key;
    msg!("PDA Account created with data: {} by initializer: {}", data, pda_account.initializer);
    Ok(())
}

#[derive(Accounts)]
#[instruction(seed_data: u64)] // Instruction arguments can be used in PDA seeds
pub struct CreatePdaAccount<'info> {
    #[account(
        init,
        payer = initializer,
        space = 8 + 8 + 32, // Anchor discriminator + data + Pubkey
        seeds = [b"my_pda_seed", initializer.key().as_ref(), seed_data.to_le_bytes().as_ref()],
        bump
    )]
    pub pda_account: Account<'info, MyPdaAccount>,
    #[account(mut)]
    pub initializer: Signer<'info>,
    pub system_program: Program<'info, System>,
}

#[account]
pub struct MyPdaAccount {
    pub data: u64,
    pub initializer: Pubkey,
}
```

### 4. Custom Error Handling

You define custom errors for clearer, more specific feedback to users and client applications.

```rust
// programs/my-program/src/lib.rs (at the end of the file)
#[error_code]
pub enum MyProgramError {
    #[msg("The provided data is invalid.")]
    InvalidData,
    #[msg("Unauthorized access to account.")]
    Unauthorized,
    #[msg("Account already initialized.")]
    AlreadyInitialized,
}
```

You would then use these errors in your instruction logic:
```rust
// ... inside initialize function
if data == 0 {
    return Err(MyProgramError::InvalidData.into());
}
// ...
```

## Best Practices

*   **Validate All Inputs Rigorously:** Never trust client-side input. Check `signer`, `owner`, `has_one`, `constraint`, and other account properties. Use Anchor's constraints extensively.
*   **Use PDAs for Program Ownership:** PDAs are the canonical way for your program to own accounts, allowing deterministic address generation and signing authority without private keys.
*   **Implement Re-entrancy Guards:** If your program performs CPIs, ensure state changes are finalized *before* the CPI, or implement a re-entrancy guard to prevent malicious re-invocation.
*   **Handle Rent Exemption and Account Closure:** Provide mechanisms (e.g., `#[account(close = receiver)]`) for users to close accounts and reclaim rent, especially for temporary or user-specific state.
*   **Minimize Compute Budget Usage:** Solana programs have a strict compute budget. Optimize your code for efficiency, avoid expensive loops, and use deterministic seeds for PDAs.
*   **Thorough Testing:** Write comprehensive unit tests for individual instruction logic and integration tests (using `solana-test-validator` or Anchor's `test` command) that simulate real on-chain interactions.
*   **Design for Upgradeability:** Consider how your program will be upgraded from day one. Anchor's upgradeable programs provide a solid foundation, but understand the implications for data migrations.

## Anti-Patterns

*   **Insufficient Account Validation.** Not checking `signer`, `owner`, `has_one`, or `constraint` on accounts. This leads to critical vulnerabilities like unauthorized access or data manipulation. Always use Anchor's robust account constraints or manual checks for every account passed.
*   **Re-entrancy Vulnerabilities.** Performing a CPI to an unknown or untrusted program and then modifying internal state based on the CPI's result. This can allow the external program to call back into yours, leading to unexpected behavior. Always finalize state changes *before* making external CPIs, or use a re-entrancy guard.
*   **Unbounded Account Growth.** Allowing users to create an arbitrary number of accounts without a fee or limit. This can lead to excessive chain state and high rent costs. Implement limits, require rent payment, or design state to be shared.
*   **Lack of Rent Exemption/Closing.** Creating accounts without providing a mechanism to close them and reclaim rent. This burdens users with perpetual rent payments for unused state. Always provide a `close` instruction (e.g., `#[account(close = receiver)]`) for temporary or user-owned accounts.
*   **Predictable PDAs without Unique Seeds.** Relying solely on a base pubkey (like the initializer's key) for PDA derivation when multiple instances are expected. This can lead to PDA collisions or make it difficult to manage multiple states for a single user. Always use unique, descriptive seeds for different instances of PDAs to ensure distinctness and enhance security.
*   **Direct Raw Data Deserialization.** Manually deserializing raw account data
