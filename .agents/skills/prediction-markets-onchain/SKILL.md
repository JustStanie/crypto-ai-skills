---
name: prediction-markets-onchain
description: 'Use when the user needs on-chain prediction market protocols: design markets,
  oracles, settlement, dispute resolution and incentives.'
---

# On-chain prediction market protocols

You are a seasoned architect of decentralized information markets, deeply understanding how to harness collective intelligence and financial incentives to forecast future events on-chain. You've built robust, fair, and liquid prediction market platforms, navigating the complexities of oracle integration, dispute resolution, and efficient market design. Your expertise lies in creating transparent systems where users can stake capital on outcomes, enabling powerful tools for hedging, speculation, and decentralized decision-making.

## Core Philosophy

On-chain prediction markets are decentralized platforms where participants bet on the outcome of future events. By financially incentivizing accurate predictions, these markets aim to aggregate collective intelligence, often yielding forecasts more reliable than traditional polling or expert analysis. Unlike centralized betting platforms, on-chain markets operate with transparency, censorship resistance, and global accessibility, removing intermediaries and allowing direct peer-to-peer risk transfer.

The fundamental mechanism involves users buying "outcome shares" for specific events. The fluctuating prices of these shares reflect the market's perceived probability of each outcome. When the event resolves, holders of shares corresponding to the correct outcome receive payouts, typically denominated in the collateral currency. Successfully building these systems requires meticulous design around event definition, robust oracle integration for trustless resolution, and a resilient dispute resolution framework to handle contentious outcomes. You are not just building a betting platform; you are engineering a mechanism for decentralized truth discovery and risk management.

## Setup

To build and interact with on-chain prediction markets, you'll typically work within an EVM-compatible environment. Hardhat or Foundry are your go-to development environments for smart contract creation and testing, while Ethers.js or Web3.js will be your primary tools for client-side interaction.

First, initialize your project and install core dependencies:

```bash
# Create your project directory
mkdir prediction-market-project
cd prediction-market-project

# Initialize a Node.js project
npm init -y

# Install Hardhat and Ethers.js for contract development and interaction
npm install --save-dev hardhat ethers @nomicfoundation/hardhat-toolbox

# Initialize a Hardhat project (choose 'Create a TypeScript project')
npx hardhat
```

For client-side applications (e.g., a React frontend), you'll also install `ethers`:

```bash
npm install ethers
```

If you plan to use a specific prediction market protocol's SDK (e.g., Gnosis Chain's Conditional Tokens or Reality.eth client libraries), install them as needed:

```bash
# Example for a specific protocol (replace with actual SDK if available)
# npm install @gnosis.pm/conditional-tokens-sdk
# npm install @reality.eth/reality-eth-js
```

## Key Techniques

You'll primarily interact with smart contracts that manage market creation, share trading, outcome reporting, and payout distribution. The Conditional Tokens standard (ERC-1155 based) is a common pattern for managing outcome shares.

### 1. Deploying a Market Using a Factory

Most prediction market protocols use a factory pattern to create new markets. You'll instantiate the factory contract and call a `createMarket` function, often passing event details, outcomes, and a reference to an oracle.

```typescript
import { ethers } from "ethers";

// Assume a deployed ConditionalTokens.sol factory contract
// and an oracle contract like Reality.eth
const provider = new ethers.JsonRpcProvider("YOUR_RPC_URL");
const wallet = new ethers.Wallet("YOUR_PRIVATE_KEY", provider);

// Replace with actual ABI and address
const MARKET_FACTORY_ABI = [
  "function createMarket(string memory question, string[] memory outcomes, address oracle, uint256 resolutionTime) returns (address)",
];
const MARKET_FACTORY_ADDRESS = "0x..."; // Address of your market factory

const marketFactory = new ethers.Contract(
  MARKET_FACTORY_ADDRESS,
  MARKET_FACTORY_ABI,
  wallet
);

async function deployNewMarket(
  question: string,
  outcomes: string[],
  oracleAddress: string,
  resolutionTime: number
) {
  try {
    const tx = await marketFactory.createMarket(
      question,
      outcomes,
      oracleAddress,
      resolutionTime
    );
    await tx.wait();
    console.log("Market creation transaction sent:", tx.hash);
    // You'd typically listen for an event to get the new market's address
  } catch (error) {
    console.error("Error creating market:", error);
  }
}

// Example usage:
// deployNewMarket(
//   "Will ETH price be above $3000 by 2024-12-31?",
//   ["Yes", "No"],
//   "0x...", // Reality.eth oracle address
//   Math.floor(new Date("2024-12-31T23:59:59Z").getTime() / 1000)
// );
```

### 2. Buying Outcome Shares

Users participate by buying shares representing a specific outcome. This often involves "merging" collateral into specific outcome tokens.

```typescript
import { ethers } from "ethers";

// Assume a deployed ConditionalTokens.sol market contract
const MARKET_ABI = [
  "function buy(uint256 outcomeIndex, uint256 amount) payable",
  "function collateralToken() view returns (address)",
  // ... other conditional tokens interface functions like merge/split
];
const MARKET_ADDRESS = "0x..."; // Address of the specific market contract

const market = new ethers.Contract(MARKET_ADDRESS, MARKET_ABI, wallet);

async function buyShares(outcomeIndex: number, amountEth: string) {
  try {
    const tx = await market.buy(outcomeIndex, ethers.parseEther(amountEth), {
      value: ethers.parseEther(amountEth),
    });
    await tx.wait();
    console.log(
      `Successfully bought ${amountEth} ETH worth of shares for outcome ${outcomeIndex}. Tx: ${tx.hash}`
    );
  } catch (error) {
    console.error("Error buying shares:", error);
  }
}

// Example usage: Buy 'Yes' shares (outcomeIndex 0) with 0.1 ETH
// buyShares(0, "0.1");
```

### 3. Reporting an Outcome via an Oracle

Market resolution depends on a reliable oracle. For many prediction markets, Reality.eth is a popular choice for human-verified outcomes. You'll interact with the oracle to report the final answer to the market's question.

```typescript
import { ethers } from "ethers";

// Reality.eth's main interface is through its `Reality.eth` contract
const REALITY_ETH_ABI = [
  "function arbitrate(bytes32 questionId, uint256 ruling) external",
  "function getQuestionHash(string memory question, string[] memory outcomes, uint256 resolutionTime, address arbitrator, uint256 timeout, uint256 bond, address bestAnswer) pure returns (bytes32)",
  "function submitAnswer(bytes32 questionId, uint256 answer) payable",
  "function getAnswer(bytes32 questionId) view returns (uint256)",
];
const REALITY_ETH_ADDRESS = "0x..."; // Reality.eth main contract address

const realityEth = new ethers.Contract(
  REALITY_ETH_ADDRESS,
  REALITY_ETH_ABI,
  wallet
);

async function reportOutcome(
  question: string,
  outcomes: string[],
  resolutionTime: number,
  arbitratorAddress: string,
  timeout: number,
  bond: number,
  winningOutcomeIndex: number
) {
  try {
    // First, get the question hash (often done by the market contract internally)
    // For manual reporting, you'd calculate it.
    const questionId = await realityEth.getQuestionHash(
      question,
      outcomes,
      resolutionTime,
      arbitratorAddress,
      timeout,
      bond,
      ethers.ZeroAddress // or a previous answer
    );

    // Submit the winning answer (e.g., 0 for 'Yes', 1 for 'No')
    // Requires a bond to be paid
    const tx = await realityEth.submitAnswer(questionId, winningOutcomeIndex, {
      value: ethers.parseEther("0.01"), // Example bond amount
    });
    await tx.wait();
    console.log(
      `Outcome reported for question ${questionId} with answer ${winningOutcomeIndex}. Tx: ${tx.hash}`
    );
  } catch (error) {
    console.error("Error reporting outcome:", error);
  }
}

// Example usage: Assuming a question is defined and ready for resolution
// reportOutcome(
//   "Will ETH price be above $3000 by 2024-12-31?",
//   ["Yes", "No"],
//   Math.floor(new Date("2024-12-31T23:59:59Z").getTime() / 1000),
//   "0x...", // Kleros or other arbitrator address
//   86400 * 3, // 3 day timeout
//   ethers.parseEther("0.01"),
//   0 // Assuming 'Yes' is the winning outcome (index 0)
// );
```

### 4. Claiming Winnings

Once a market has resolved and the oracle has reported the outcome, users holding shares of the winning outcome can redeem them for their collateral.

```typescript
import { ethers } from "ethers";

// Assume the same market contract from previous examples
const MARKET_ADDRESS = "0x..."; // Address of the specific market contract

// Conditional Tokens use a `redeemPositions` function
const CONDITIONAL_TOKENS_ABI = [
  "function redeemPositions(address collateralToken, bytes32 parentCollectionId, bytes32 conditionId, uint256[] calldata indexSets) external",
  "function getConditionId(address oracle, bytes32 questionId, uint256 outcomeSlotCount) pure returns (bytes32)",
  // ... other necessary functions to get collateralToken, parentCollectionId, conditionId
];

const conditionalTokens = new ethers.Contract(
  MARKET_ADDRESS,
  CONDITIONAL_TOKENS_ABI,
  wallet
);

async function claimMarketWinnings(
  collateralTokenAddress: string,
  parentCollectionId: string, // Typically bytes32(0) for top-level markets
  conditionId: string,
  winningOutcomeIndex: number
) {
  try {
    // For a single winning outcome, the indexSet would be the bitmask
    // E.g., for outcome 0,
    const indexSet = 1 << winningOutcomeIndex;

    const tx = await conditionalTokens.redeemPositions(
      collateralTokenAddress,
      parentCollectionId,
      conditionId,
      [indexSet]
    );
    await tx.wait();
    console.log(`Winnings claimed. Tx: ${tx.hash}`);
  } catch (error) {
    console.error("Error claiming winnings:", error);
  }
}
```

## Anti-Patterns

*   **Centralized Oracle Single Point of Failure.** Relying on a single oracle source for market resolution creates a critical trust assumption. Use decentralized oracle networks with bond-escalation dispute mechanisms, or implement multi-oracle consensus with fallback arbitration.

*   **Unbounded Market Resolution Windows.** Allowing markets to remain unresolved indefinitely locks user capital and erodes trust. Always enforce maximum resolution timeframes with default outcomes or refund mechanisms if the oracle fails to report.

*   **Front-Runnable Resolution Transactions.** If outcome reporting transactions are visible in the mempool before execution, searchers can front-run by buying winning shares. Use commit-reveal schemes or private transaction submission for resolution.

*   **Ignoring Sybil Resistance in Dispute Resolution.** Allowing anyone to dispute outcomes without meaningful economic commitment enables grief attacks. Require escalating bonds for disputes and slash incorrect challengers to make frivolous disputes costly.

*   **Fixed Liquidity Without Incentives.** Deploying a prediction market with no liquidity mining or market-maker incentive program results in wide spreads and poor price discovery. Bootstrap liquidity with subsidized initial positions or automated market maker seeding.

## Version and Evidence Check

Assess oracle, settlement, disputed-outcome, liquidity and jurisdiction-specific restrictions separately; do not assume a listed market or venue is legal everywhere.

## Review & Production Validation (2026-10-31)

- **Domain control (Blockchain ecosystem / development):** Confirm active network, chain ID, toolchain/API version and protocol-specific conventions.
- **Independent validation:** Use primary documentation and reproducible tests for implementation instructions.
- **Time-sensitive details:** Treat fixed rates, thresholds, package versions, protocols and jurisdiction-specific rules in the examples above as illustrative unless reconfirmed against primary documentation.
- **Before relying on the result:** State inputs and assumptions; verify calculations and edge cases, and identify what has not been executed or tested.
