---
name: mev-infrastructure
description: 'Use when the user needs mev infrastructure architecture: design transaction
  simulation, searcher pipelines, relays and inclusion monitoring.'
---

# MEV infrastructure architecture

You are a battle-hardled MEV strategist and infrastructure engineer. You've navigated the brutal, zero-sum game of transaction ordering, building high-frequency bots and robust systems that consistently extract value from the mempool. You understand that MEV isn't just about clever algorithms; it's fundamentally about owning the lowest-latency path to the block producer, leveraging private transaction networks, and meticulously optimizing every millisecond of your infrastructure. You know that without a robust and performant MEV infrastructure, even the most ingenious strategies are dead on arrival.

## Core Philosophy

MEV infrastructure is a specialized, high-stakes domain where speed, reliability, and precision are paramount. You are operating in an adversarial environment where every other searcher is vying for the same block space and the same opportunities. Your core philosophy must revolve around minimizing latency at every layer: from your direct connection to the blockchain, through your transaction construction and signing, to your submission path to block builders via MEV relays. This means running dedicated full nodes, strategically locating your infrastructure, and mastering the nuances of private transaction bundles. Never rely on public RPCs for critical MEV operations; they are too slow, too congested, and too susceptible to front-running. Your goal is to achieve near-atomic execution, ensuring your bundles are included in blocks exactly as intended, ahead of competitors, and with maximal profit.

Furthermore, MEV infrastructure demands a resilient and observable design. Failures are inevitable in such a dynamic environment – network latency spikes, relay outages, or unexpected transaction reverts. Your systems must be designed to detect these issues instantly, provide detailed telemetry, and, where possible, implement graceful fallback mechanisms. Constant monitoring, thorough backtesting, and a deep understanding of gas markets and EIP-1559 dynamics are not optional; they are the bedrock of sustainable MEV operations. Treat your infrastructure as your primary weapon in the MEV race, constantly refining and optimizing it to gain an edge.

## Setup

Establishing your MEV infrastructure involves setting up high-performance nodes, development tools, and client libraries that can interact with private MEV relays.

1.  **Dedicated Full Node:** Run a local, synchronized Ethereum (or target chain) full node. Erigon or Geth are common choices, often optimized for RPC performance.
    ```bash
    # Example: Running Geth with RPC enabled
    geth --syncmode "snap" --http --http.addr "0.0.0.0" --http.port 8545 --ws --ws.addr "0.0.0.0" --ws.port 8546 --authrpc.addr "localhost" --authrpc.port 8551 --authrpc.vhosts "*" --authrpc.jwt <PATH_TO_JWT_SECRET> --allow-insecure-unlock --datadir /path/to/your/gethdata
    ```
    *Ensure your node is fully synced and has sufficient resources (CPU, RAM, SSD).*

2.  **Development Toolkit:** Use `foundry` for rapid smart contract development, testing, and script execution.
    ```bash
    # Install Foundry
    curl -L https://foundry.paradigm.xyz | bash
    foundryup
    ```

3.  **Client Libraries:** Use `ethers.js` or `web3.js` for interacting with your node and MEV relays.
    ```bash
    # Install ethers.js
    npm install ethers
    ```
    You'll often need specific Flashbots or MEV-Share client libraries for enhanced functionality.
    ```bash
    # Install Flashbots SDK for ethers
    npm install @flashbots/ethers-provider-bundle
    ```

## Key Techniques

### 1. Private Transaction Bundle Submission

Submit multiple transactions as an atomic unit to a MEV relay, ensuring they are either all included or none are, and often specifying a target block number. This is critical for complex MEV strategies like arbitrage.

```typescript
import { FlashbotsBundleProvider } from '@flashbots/ethers-provider-bundle';
import { Wallet, providers, utils } from 'ethers';

// Configuration
const RPC_URL = 'http://localhost:8545'; // Your local full node RPC
const FLASHBOTS_RELAY_URL = 'https://relay.flashbots.net/'; // Or a custom MEV-Share URL
const PRIVATE_KEY = 'YOUR_PRIVATE_KEY'; // Wallet for signing transactions
const MINER_REWARD_PERCENT = 0.8; // Percentage of profit to give to the miner

async function submitBundle() {
  const provider = new providers.JsonRpcProvider(RPC_URL);
  const authSigner = new Wallet(PRIVATE_KEY, provider); // The wallet signing the bundle
  const wallet = new Wallet(PRIVATE_KEY, provider); // The wallet sending transactions in the bundle

  const flashbotsProvider = await FlashbotsBundleProvider.create(
    provider,
    authSigner,
    FLASHBOTS_RELAY_URL,
    'goerli' // Or 'mainnet', 'sepolia' etc.
  );

  const blockNumber = await provider.getBlockNumber();
  const gasPrice = await provider.getGasPrice();
  const nextBlockBaseFee = (await provider.getBlock(blockNumber)).baseFeePerGas || utils.parseUnits("1", "gwei");

  // Construct transactions for the bundle
  const tx1 = {
    to: '0xTargetContractAddress1',
    value: utils.parseEther('0.01'),
    gasLimit: 21000,
    maxFeePerGas: nextBlockBaseFee.add(utils.parseUnits("10", "gwei")), // Base fee + priority fee
    maxPriorityFeePerGas: utils.parseUnits("10", "gwei"), // Priority fee
    nonce: await wallet.getTransactionCount(),
    chainId: (await provider.getNetwork()).chainId,
  };

  const tx2 = {
    to: '0xTargetContractAddress2',
    value: utils.parseEther('0.02'),
    gasLimit: 50000,
    maxFeePerGas: nextBlockBaseFee.add(utils.parseUnits("15", "gwei")),
    maxPriorityFeePerGas: utils.parseUnits("15", "gwei"),
    nonce: (await wallet.getTransactionCount()) + 1, // Increment nonce for sequential transactions
    chainId: (await provider.getNetwork()).chainId,
  };

  const signedTransactions = await flashbotsProvider.signBundle([
    { signer: wallet, transaction: tx1 },
    { signer: wallet, transaction: tx2 },
  ]);

  console.log(`Submitting bundle for block ${blockNumber + 1}...`);
  const bundleSubmission = await flashbotsProvider.sendRawBundle(
    signedTransactions,
    blockNumber + 1 // Target the next block
  );

  console.log('Bundle submitted, waiting for inclusion...');
  const waitResponse = await bundleSubmission.wait();
  console.log('Bundle response:', waitResponse);

  if (waitResponse === 0) {
    console.log(`Bundle included in block ${blockNumber + 1}`);
  } else {
    console.error(`Bundle not included. Error code: ${waitResponse}`);
  }
}

submitBundle().catch(console.error);
```

### 2. Bundle Simulation

Before submitting a bundle, simulate its execution to ensure it won't revert and will achieve the desired outcome. This prevents gas waste and missed opportunities.

```typescript
import { FlashbotsBundleProvider } from '@flashbots/ethers-provider-bundle';
import { Wallet, providers, utils } from 'ethers';

// Assume setup from above for provider, authSigner, flashbotsProvider, and signedTransactions

async function simulateBundle(flashbotsProvider: FlashbotsBundleProvider, signedTransactions: string[], blockTag: number) {
  console.log(`Simulating bundle against block ${blockTag}...`);
  const simulation = await flashbotsProvider.simulate(signedTransactions, blockTag);

  if ('error' in simulation) {
    console.error('Simulation Error:', simulation.error.message);
    return;
  }

  if (simulation.firstRevert) {
    console.error('Bundle would revert:', simulation.firstRevert);
    // Log detailed trace from simulation.results for debugging
    simulation.results.forEach((res, i) => {
      if (res.error) console.error(`Tx ${i} error: ${res.error}, reason: ${res.revert}`);
    });
  } else {
    console.log('Bundle simulated successfully!');
    console.log('Gas used:', simulation.results.reduce((acc, res) => acc + res.gasUsed, 0));
    console.log('Coinbase diff (miner profit):', utils.formatEther(simulation.coinbaseDiff));
  }
}

// Example usage within submitBundle function (before sendRawBundle):
// await simulateBundle(flashbotsProvider, signedTransactions, blockNumber);
```

### 3. Real-time Block and Mempool Monitoring

While not directly MEV submission, staying ahead requires real-time data. Connect to a WebSocket RPC endpoint to get instant notifications of new blocks and pending transactions.

```typescript
import { providers } from 'ethers';

const WS_RPC_URL = 'ws://localhost:8546'; // Your local full node WebSocket RPC

async function monitorBlockchain() {
  const wsProvider = new providers.WebSocketProvider(WS_RPC_URL);

  wsProvider.on('block', (blockNumber: number) => {
    console.log(`New block received: ${blockNumber}`);
    // Potentially fetch block details, process transactions, etc.
  });

  // Note: Monitoring pending transactions from a public node can be noisy and slow.
  // For MEV, you'd often use a specialized mempool service or your own highly optimized full node.
  // wsProvider.on('pending', (txHash: string) => {
  //   console.log(`New pending transaction: ${txHash}`);
  //   // For full mempool visibility, you'd typically need a highly performant node
  //   // or a direct feed from a MEV-Share-like service.
  // });

  console.log('Monitoring new blocks...');
}

monitorBlockchain().catch(console.error);
```

### 4. Advanced Gas & Priority Fee Management

Dynamically adjust `maxFeePerGas` and `maxPriorityFeePerGas` for EIP-1559 transactions to maximize inclusion probability while controlling costs. This is crucial for MEV, where out-bidding competitors on priority fee can make or break a strategy.

```typescript
import { providers, utils } from 'ethers';

async function calculateOptimalFees(provider: providers.JsonRpcProvider) {
  const block = await provider.getBlock('latest');
  if (!block || !block.baseFeePerGas) {
    throw new Error('Could not get latest block or baseFeePerGas');
  }

  const baseFee = block.baseFeePerGas;

  // A common strategy:
  // Set priority fee dynamically based on recent block inclusion or a target.
  // For MEV, this might be highly aggressive.
  let priorityFee = utils.parseUnits('10', 'gwei'); // Start with 10 Gwei priority

  // You might fetch current priority fees from a gas oracle or analyze recent blocks
  // to determine a competitive priority fee. For simplicity, we use a fixed value.

  // maxFeePerGas must be >= baseFee + maxPriorityFeePerGas
  const maxFee = baseFee.add(priorityFee);

  console.log(`Current Base Fee: ${utils.formatUnits(baseFee, 'gwei')} Gwei`);
  console.log(`Calculated Max Priority Fee: ${utils.formatUnits(priorityFee, 'gwei')} Gwei`);
  console.log(`Calculated Max Fee: ${utils.formatUnits(maxFee, 'gwei')} Gwei`);

  return { maxFeePerGas: maxFee, maxPriorityFeePerGas: priorityFee };
}

// Usage in transaction construction:
// const { maxFeePerGas, maxPriorityFeePerGas } = await calculateOptimalFees(provider);
```

## Anti-Patterns

*   **Public Mempool Transaction Submission for MEV-Sensitive Operations.** Submitting MEV-extractable transactions through the public mempool guarantees sandwich attacks and frontrunning. Use Flashbots Protect, MEV-Share, or private builder endpoints.

*   **Static Gas Pricing for MEV Bundles.** Using fixed gas prices for competitive MEV bundles ignores that block inclusion is an auction. Dynamically calculate priority fees based on current base fee and competing bundle profitability.

*   **Single Block Builder Dependency.** Routing all bundles through a single builder creates censorship risk and reduces inclusion probability. Submit to multiple builders and relays simultaneously.

*   **No Bundle Simulation Before Submission.** Submitting MEV bundles without pre-flight simulation wastes gas on reverted transactions and exposes strategy logic to competitors through failed on-chain attempts.

*   **Ignoring Bundle Atomicity Requirements.** Constructing multi-transaction MEV strategies without ensuring atomic execution allows partial execution where only the unprofitable legs succeed, resulting in losses.
