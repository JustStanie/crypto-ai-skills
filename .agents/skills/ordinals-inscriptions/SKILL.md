---
name: ordinals-inscriptions
description: 'Use when the user needs bitcoin ordinals and inscriptions: explain sat inscription
  flows, indexing, fees and custody impacts.'
---

# Bitcoin Ordinals and inscriptions

You are an expert in Bitcoin's low-level transaction model and the Ordinals protocol, enabling the creation of immutable digital artifacts by inscribing data directly onto individual satoshis. You build applications and tooling that leverage the unique properties of these on-chain assets, understanding the nuances of UTXO management and transaction construction for the Bitcoin network.

## Core Philosophy

Ordinals Theory assigns a unique, sequential number to each satoshi, from the first one ever mined. This numbering system allows individual satoshis to be tracked and given unique identities. The real magic happens with "inscriptions," where arbitrary data (images, text, audio, video, BRC-20 JSON) is embedded into the witness data of a Bitcoin transaction and "attached" to a specific satoshi. This makes the inscribed data an intrinsic part of that satoshi, creating a truly on-chain digital artifact.

Unlike NFTs on EVM chains, where the token often points to off-chain metadata (like IPFS), an Ordinal inscription *is* the data itself, permanently etched into the Bitcoin blockchain. This design choice offers unparalleled immutability and censorship resistance. When you work with Ordinals, you're interacting directly with Bitcoin's core transaction model, managing UTXOs, and constructing transactions that carry your digital creations. It's a deep dive into Bitcoin's architecture, providing a robust foundation for building truly decentralized digital assets.

## Setup

To work with Ordinals, you need a full Bitcoin node and the `ord` command-line tool.

1.  **Run a Bitcoin Core Node**: You need `bitcoind` synced to the Bitcoin blockchain. For inscription purposes, an unpruned node is generally recommended, but `ord` can work with pruned nodes if configured correctly.

    ```bash
    # Start bitcoind in the background (or as a service)
    bitcoind -daemon -txindex=1 -server=1 -rpcuser=your_rpc_user -rpcpassword=your_rpc_password
    # Ensure txindex is enabled for ord to function correctly.
    ```
    Wait for your node to fully sync. You can check its status: `bitcoin-cli getblockchaininfo`

2.  **Install the `ord` Client**: The official Ordinals client is built in Rust.

    ```bash
    # Install Rust if you don't have it
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
    source $HOME/.cargo/env

    # Clone and build ord
    git clone https://github.com/ordinals/ord.git
    cd ord
    cargo install --path . --locked
    ```

3.  **Configure `ord`**: The `ord` client needs to connect to your `bitcoind` node. By default, it looks for standard `bitcoin.conf` locations. If your `bitcoind` uses non-standard RPC credentials or a different data directory, you'll need to specify them.

    ```bash
    # Example: Check ord status (should connect to bitcoind)
    ord wallet balance

    # If connection issues, create or modify ~/.ord/ord.yaml
    # ~/.ord/ord.yaml
    # bitcoin_rpc_user: your_rpc_user
    # bitcoin_rpc_pass: your_rpc_password
    # bitcoin_rpc_host: 127.0.0.1
    # bitcoin_rpc_port: 8332 # Or 18332 for testnet, 18443 for regtest
    ```

## Key Techniques

### 1. Initializing Your Ordinals Wallet

Before you can inscribe, you need an `ord` wallet. This wallet generates Bitcoin addresses and manages the UTXOs that will hold your inscriptions.

```bash
# Create a new ord wallet
ord wallet create

# Get a new receive address for funding
ord wallet receive

# Check your wallet balance (after funding the address)
ord wallet balance
```
**Explanation**: Fund the address obtained from `ord wallet receive` with some satoshis. These satoshis will be used for inscription fees and to hold the inscribed data.

### 2. Inscribing Data

This is the core process of creating an Ordinal inscription. You specify a file and a fee rate. The `ord` client constructs the necessary Bitcoin transaction.

```bash
# Prepare a simple text file
echo "Hello Ordinals!" > my_inscription.txt

# Inscribe the text file
# Use a fee rate that ensures timely confirmation. Check mempool.space for current rates.
ord wallet inscribe --file my_inscription.txt --fee-rate 10 --destination <your_ord_wallet_receive_address>

# Inscribe an image (e.g., JPEG)
# Ensure the image file is not excessively large to avoid very high fees.
ord wallet inscribe --file my_image.jpg --fee-rate 20 --destination <your_ord_wallet_receive_address>
```
**Explanation**: The `--file` argument points to the data you want to inscribe. `--fee-rate` (in sat/vB) is crucial for transaction confirmation. The `--destination` is your own `ord` wallet address where you want the inscribed satoshi to reside after the inscription transaction confirms.

### 3. Managing and Viewing Inscriptions

After inscription, you can list and view details of your digital artifacts.

```bash
# List all inscriptions in your wallet
ord wallet inscriptions

# Example output:
# ID          ADDRESS                                       AMOUNT
# 1234...efgi bc1q...xyz                                    10000 sats

# View details of a specific inscription (replace with actual ID)
ord wallet inscription 1234...efgi
```
**Explanation**: `ord wallet inscriptions` shows you the unique ID, the address holding the inscription, and the satoshi amount of the UTXO it's attached to. The inscription ID is a combination of the transaction ID and the output index.

### 4. Transferring Inscriptions

Inscriptions are transferred by sending the Bitcoin UTXO they are attached to.

```bash
# Transfer an inscription to another Bitcoin address
# This sends the UTXO containing the inscription.
ord wallet send <recipient_bitcoin_address> <inscription_id> --fee-rate 10
```
**Explanation**: When you `send` an `inscription_id`, `ord` creates a transaction that transfers the specific UTXO containing that inscription to the recipient. The `fee-rate` ensures the transfer transaction confirms.

### 5. Interacting with BRC-20 Tokens (Deploy, Mint, Transfer)

BRC-20 tokens are a specific type of Ordinal inscription using JSON data following a predefined standard.

```bash
# 1. Deploy a BRC-20 token
# Create a JSON file, e.g., deploy_token.json
cat << EOF > deploy_token.json
{
  "p": "brc-20",
  "op": "deploy",
  "tick": "ordi",
  "max": "21000000",
  "lim": "1000"
}
EOF

ord wallet inscribe --file deploy_token.json --fee-rate 15 --destination <your_ord_wallet_receive_address>

# 2. Mint BRC-20 tokens
# Create a JSON file, e.g., mint_token.json
cat << EOF > mint_token.json
{
  "p": "brc-20",
  "op": "mint",
  "tick": "ordi",
  "amt": "1000"
}
EOF

ord wallet inscribe --file mint_token.json --fee-rate 15 --destination <your_ord_wallet_receive_address>

# 3. Transfer BRC-20 tokens
# This is essentially a "transfer inscription" operation.
# Create a JSON file, e.g., transfer_token.json
cat << EOF > transfer_token.json
{
  "p": "brc-20",
  "op": "transfer",
  "tick": "ordi",
  "amt": "500"
}
EOF

# First, inscribe the transfer instruction JSON. This creates a *transfer inscription*.
ord wallet inscribe --file transfer_token.json --fee-rate 15 --destination <your_ord_wallet_receive_address>

# After the transfer inscription confirms, find its inscription ID using `ord wallet inscriptions`.
# Then, send *that specific transfer inscription* to the recipient.
# This "sending the transfer inscription" is what moves the BRC-20 balance.
ord wallet send <recipient_bitcoin_address> <transfer_inscription_id> --fee-rate 10
```
**Explanation**: BRC-20 operations are distinct JSON inscriptions. Deploy defines the token, mint creates new units, and transfer stages a transfer that must then be "sent" by transferring its specific inscription.

## Best Practices

*   **Always Test on Testnet First**: Before spending real Bitcoin, perform all inscription and transfer operations on Bitcoin Testnet to understand the flow and confirm your commands.
*   **Monitor Fee Rates**: Bitcoin transaction fees fluctuate wildly. Use reliable fee estimators (e.g., mempool.space) to choose an appropriate `--fee-rate` to avoid stuck transactions or overpaying.
*   **Understand UTXO Management**: Inscriptions are tied to specific UTXOs. Be mindful of which UTXOs you're spending to avoid accidentally sending an inscription or incurring high fees due to complex change outputs. `ord` handles this for you, but understanding the underlying mechanism is key.
*   **Backup Your Wallet Seed Phrase**: Your `ord` wallet is a standard Bitcoin wallet. Securely back up your seed phrase (mnemonic) immediately after creation.
*   **Verify Inscription Content**: Double-check the file you are inscribing. Once it's on-chain, it's immutable. Ensure no sensitive data is included unintentionally.
*   **Monitor Inscription Confirmation**: Use a block explorer (e.g., mempool.space or ordinals.com) with your transaction ID to track the confirmation status of your inscription.
*   **Use `ord` Directly**: For critical inscriptions, rely on your own `ord` client connected to your `bitcoind` node. Avoid third-party inscription services unless you fully trust them and understand their fee structures.

## Anti-Patterns

**Ignoring Transaction Fees.**
What goes wrong: Transactions with too low a fee rate can get stuck in the mempool for hours or days, delaying your inscription.
What to do instead: Always consult a real-time mempool fee estimator and set a competitive `fee-rate`. Don't just use a default or arbitrary low number.

**Inscribing Excessively Large Data.**
What goes wrong: While technically possible, inscribing very large files (e.g., multi-MB videos) incurs extremely high transaction fees and can bloat the blockchain unnecessarily.
What to do instead: Optimize your inscription content. Compress images, use efficient formats, and consider if the data truly needs to be entirely on-chain or if a smaller, meaningful artifact suffices.

**Mismanaging Inscription UTXOs.**
What goes wrong: Accidentally spending the UTXO that holds an inscription as part of a regular Bitcoin transaction, effectively sending your inscription to an unintended address or burning it if it's sent to an unspendable output.
What to do instead: `ord` wallets are designed to prevent accidental spending of inscription UTXOs for regular transactions. However, if you're using custom scripts or other wallets, be extremely careful to isolate and manage inscription-bearing UTXOs distinctively.

**Relying Solely on Third-Party Explorers for Wallet Status.**
What goes wrong: Third-party services might have delays, display incorrect data, or censor certain inscriptions, leading to confusion about your assets.
What to do instead: Use your own `ord wallet inscriptions` and `ord wallet balance` commands as the single source of truth
