---
name: lightning-network-development
description: 'Use when the user needs bitcoin lightning applications: design channels, invoices,
  routing liquidity and payment reliability.'
---

# Bitcoin Lightning applications

You are a seasoned architect in building instant, high-volume payment solutions on Bitcoin, leveraging the Lightning Network to achieve unparalleled speed and efficiency. You navigate the complexities of channel liquidity, routing, and invoice lifecycles with expertise, ensuring robust and scalable transaction flows for your decentralized applications.

## Core Philosophy

The Lightning Network is Bitcoin's primary scaling solution for microtransactions and instant payments. Your approach should always be to offload frequent, small-value transactions from the main Bitcoin chain, benefiting from near-zero fees and immediate settlement. Think of Lightning not as a separate blockchain, but as a network of payment channels layered *on top* of Bitcoin, secured by its fundamental cryptographic primitives. Embrace its capabilities for user-facing applications requiring rapid exchanges, while reserving on-chain transactions for opening and closing channels or larger, less frequent settlements. Your goal is to provide a seamless, performant payment experience that is economically viable for even the smallest transfers.

## Setup

You'll need a running Bitcoin node (e.g., `bitcoind` or a lightweight client like `neutrino`) and a Lightning Network Daemon (LND) instance.

1.  **Install `bitcoind` (if not already running):**
    ```bash
    sudo apt-get update
    sudo apt-get install bitcoind
    # Configure bitcoind in ~/.bitcoin/bitcoin.conf (e.g., rpcuser, rpcpassword, txindex=1, zmqpubrawblock, zmqpubrawtx)
    bitcoind -daemon
    ```

2.  **Install LND:**
    ```bash
    # Ensure Go is installed (https://golang.org/doc/install)
    go get -u github.com/lightningnetwork/lnd
    cd $GOPATH/src/github.com/lightningnetwork/lnd
    make install
    ```

3.  **Configure LND:** Create `~/.lnd/lnd.conf`. Example basic configuration:
    ```ini
    [Application Options]
    debuglevel=info
    maxlogfiles=3
    maxlogrotatesize=10
    rpclisten=0.0.0.0:10009
    restlisten=0.0.0.0:8080
    bitcoin.active=true
    bitcoin.node=neutrino # or bitcoind
    bitcoin.chain=regtest # or testnet/mainnet
    bitcoin.regtest.datadir=/path/to/bitcoin/regtest/data # if using bitcoind

    [Bitcoin]
    # If using bitcoind
    bitcoind.rpchost=localhost:8332
    bitcoind.rpcuser=yourrpcuser
    bitcoind.rpcpass=yourrpcpassword
    bitcoind.zmqpubrawblock=tcp://127.0.0.1:28332
    bitcoind.zmqpubrawtx=tcp://127.0.0.1:28333

    [neutrino]
    neutrino.connect=btcd-testnet.lightning.computer:18333
    ```

4.  **Start LND:**
    ```bash
    lnd &
    ```
    Wait for LND to sync with the Bitcoin chain. Unlock your wallet if prompted.

5.  **Initialize `lncli`:**
    `lncli` is your primary command-line interface for interacting with your LND node. Ensure your `LND_DIR` environment variable is set to `~/.lnd` or provide the `--lnddir` flag.

## Key Techniques

### 1. Fund Your Wallet and Open a Channel

Before you can send or receive Lightning payments, your LND wallet needs funds, and you need open payment channels with other nodes.

```bash
# 1. Get a new on-chain address for funding
lncli newaddress p2wkh

# Send some satoshis to this address from a Bitcoin faucet (for testnet/regtest)
# or another wallet (for mainnet). Wait for a few confirmations.

# 2. Verify wallet balance (after confirmations)
lncli walletbalance

# 3. Open a payment channel with another node. You need their public key and IP address.
#    Find a suitable peer on a testnet explorer or connect to a known routing node.
#    Example: connecting to a peer with pubkey '03...' at 'ip:port' with 100,000 satoshis (100k sats)
lncli openchannel --node_key 03864ef025fde8fb587d989186ce6a4a186895ee44a926c9181d9c04959929684d --connect 34.239.230.56:9735 --local_amt 100000 --push_amt 0 --sat_per_vbyte 1
# --local_amt: amount you commit to the channel
# --push_amt: optional, amount to give to the remote peer instantly (good for inbound liquidity)
# --sat_per_vbyte: sets the on-chain fee for the channel opening transaction
```
Monitor the channel opening process with `lncli pendingchannels`. Once confirmed, it will appear in `lncli listchannels`.

### 2. Generate a Lightning Invoice

To receive a payment, you generate an invoice (payment request). This invoice contains all necessary information for the payer.

```bash
# Generate an invoice for 5000 satoshis with a description "Coffee purchase"
# Invoices can have an expiry (default is 3600 seconds)
lncli addinvoice --amt 5000 --memo "Coffee purchase" --expiry 3600

# Example output:
# {
#     "r_hash": "...",
#     "payment_request": "lnbc50000n1p...",
#     "add_index": "1",
#     "payment_addr": "..."
# }

# The 'payment_request' (starting with 'lnbc' or 'lntb' etc.) is what you provide to the payer.
```

### 3. Pay a Lightning Invoice Programmatically

Integrate with LND's gRPC API using an SDK (e.g., `grpc` for Python, `lnrpc` for Node.js) to programmatically handle payments.

First, ensure you have the `admin.macaroon` and `tls.cert` files from your LND node (`~/.lnd/data/chain/bitcoin/regtest/`).

```python
# Python example using grpc to pay an invoice
import grpc
import os
from lnd_grpc import lnd_grpc

# Path to LND credentials
LND_DIR = os.path.expanduser('~/.lnd')
TLS_CERT = os.path.join(LND_DIR, 'tls.cert')
MACAROON_PATH = os.path.join(LND_DIR, 'data/chain/bitcoin/regtest/admin.macaroon') # Adjust for testnet/mainnet

# Connect to LND
client = lnd_grpc.LNDClient(
    lnd_dir=LND_DIR,
    macaroon_path=MACAROON_PATH,
    tls_cert_path=TLS_CERT,
    grpc_host='localhost:10009' # Your LND gRPC host
)

# Example: Invoice to pay (replace with a real invoice)
payment_request = "lnbc1pvjl..." # A real BOLT11 payment request

try:
    print(f"Attempting to pay invoice: {payment_request}")
    # The 'send_payment' method handles pathfinding and payment execution
    response = client.send_payment(payment_request)

    print("\nPayment Response:")
    print(f"Payment Hash: {response.payment_hash.hex()}")
    print(f"Preimage: {response.payment_preimage.hex()}")
    print(f"Status: {response.payment_status}")
    print(f"Total Satoshis Sent: {response.value_sat}")
    print(f"Total Fees Paid: {response.fee_sat}")

except grpc.RpcError as e:
    print(f"Payment failed: {e.details()}")
except Exception as e:
    print(f"An unexpected error occurred: {e}")

```
This `send_payment` abstraction handles the complexities of route finding and multi-path payments for you.

## Best Practices

*   **Manage Channel Liquidity Actively:** Understand inbound vs. outbound capacity. Use `lncli listchannels` to monitor. For receiving payments, you need inbound capacity (remote node has funds in the channel). For sending, you need outbound capacity (you have funds in the channel).
*   **Utilize AMP (Atomic Multipath Payments):** Modern Lightning implementations automatically use AMP for more reliable payments by splitting a payment across multiple paths, increasing success rates for larger amounts.
*   **Set Realistic Invoice Expirations:** Don't create invoices that expire too quickly for users, but also don't make them last indefinitely if prices or availability change.
*   **Implement Robust Error Handling:** Payment failures are common due to routing issues, insufficient liquidity, or temporary node unreachability. Implement retry mechanisms and clear error messages for users.
*   **Monitor Node Health and Channels:** Regularly check `lncli getinfo` and `lncli listchannels` to ensure your node is online, synced, and channels are active. Consider setting up monitoring alerts.
*   **Secure Your LND Node:** Restrict gRPC/REST API access, use strong macaroons, and ensure your `tls.cert` and `admin.macaroon` are never exposed or shared publicly.
*   **Keep LND Software Updated:** Regularly update your LND client to benefit from the latest security patches, performance improvements, and protocol features.

## Anti-Patterns

**Ignoring Channel Rebalancing.** You have ample funds on-chain but cannot receive payments because your channels lack inbound liquidity. Instead, actively rebalance channels using tools like `lncli sendpayment` (to yourself via a circular route) or `loop out` services to shift liquidity, ensuring you always have capacity to receive.

**Hardcoding Payment Logic.** Attempting to manually find routes or manage payment attempts without leveraging LND's built-in pathfinding and retry mechanisms. Instead, always use `lncli payinvoice` or the `send_payment` API, which intelligently handles routing, retries, and AMP for you.

**Exposing LND's RPC/REST API Publicly.** Opening your LND's gRPC or REST ports directly to the internet without proper authentication or an API gateway. Instead, always place a secure proxy or API gateway in front of your LND node, ensuring all requests are authenticated and authorized with macaroons.

**Neglecting Invoice Expiration.** Generating invoices with no expiration or an excessively long one, leading to potential stale payment requests or holding funds hostage. Instead, set appropriate `expiry` times on invoices (`lncli addinvoice --expiry <seconds>`) and handle expired invoices gracefully in your application logic.

**Underestimating On-Chain Fees for Channel Management.** Opening and closing channels are on-chain transactions subject to Bitcoin network fees. Opening too many small channels or frequently closing/reopening can become expensive. Instead, plan your channel strategy to minimize on-chain operations, preferring larger, long-lived channels and using rebalancing for liquidity management.
