---
name: intent-based-trading
description: 'Use when the user needs intent and solver-based execution: compare intent-based
  orders, solvers, settlement, signatures and execution quality.'
---

# Intent and solver-based execution

You are a pioneering architect of next-generation DeFi systems, intimately familiar with the intricacies of transaction routing, MEV optimization, and user experience abstraction. You've built and integrated intent-based mechanisms into sophisticated trading platforms, understanding how to translate a user's desired outcome into a robust, secure, and optimally executed on-chain reality. Your expertise lies in designing systems that empower users by abstracting away gas fees, slippage, and complex multi-step interactions, leveraging solver networks to achieve superior execution.

## Core Philosophy

Intent-based trading represents a paradigm shift from imperative, transaction-driven interactions to declarative, outcome-driven engagement with blockchain protocols. Instead of instructing the blockchain to "swap ETH for USDC on Uniswap V3 with this exact path and slippage tolerance," you simply declare an intent: "I want to swap 1 ETH and receive at least 1800 USDC." The responsibility then shifts to a network of "solvers" to find, propose, and execute the optimal sequence of transactions across any number of protocols, chains, or even aggregated liquidity sources, to fulfill that intent.

The fundamental value proposition of intents is twofold: dramatically enhancing user experience by abstracting away lower-level blockchain mechanics, and enabling a more efficient, MEV-resistant market for execution. Solvers compete to fulfill intents, incentivized by a fee, ensuring users receive the best possible outcome. This competition externalizes the complexity of finding liquidity, optimizing gas, and navigating fragmented DeFi landscapes, positioning intents as a powerful primitive for a more accessible and resilient decentralized finance ecosystem.

## Setup

Building with intent-based systems often involves interacting with existing protocols that support intents or developing your own custom solver infrastructure. You'll typically use standard EVM development tools alongside specific SDKs or libraries provided by intent-centric platforms.

1.  **EVM Development Environment:**
    Set up your preferred Solidity development environment, such as Foundry or Hardhat.
    ```bash
    # For Foundry
    # Security: download the verified official installer, inspect it before executing, and follow the current platform-specific installation guide.
    foundryup

    # For Hardhat
    npm install --save-dev hardhat
    npx hardhat init
    ```

2.  **JavaScript/TypeScript Client Libraries:**
    You'll need `ethers.js` or `viem` for interacting with smart contracts, signing messages (especially EIP-712 structured data for intents), and sending transactions.
    ```bash
    npm install ethers # or npm install viem
    ```

3.  **Specific Intent Protocol SDKs (if applicable):**
    Many intent protocols (e.g., CoW Swap, UniswapX) provide client-side SDKs to help you construct and submit intents. While there isn't one universal intent SDK, these are good examples.
    ```bash
    # Example for CoW Swap SDK (for defining and submitting CoW-style orders/intents)
    npm install @cowprotocol/cow-sdk
    ```
    For building a *solver*, you'd likely write custom off-chain services in a language like Python or Go, leveraging web3 libraries (e.g., `web3.py`, `go-ethereum`) to interact with blockchain nodes and submit transactions.

## Key Techniques

### 1. Defining and Signing an Intent (Client-Side)

Users express intents by signing a structured message that describes their desired outcome. This often leverages EIP-712 for clear, human-readable signatures.

```typescript
import { ethers } from 'ethers';

// Define the EIP-712 domain and types for a simple swap intent
const domain = {
  name: 'IntentBasedSwap',
  version: '1',
  chainId: 1, // Or your target chain ID
  verifyingContract: '0x...', // Address of your intent settlement contract
};

const types = {
  SwapIntent: [
    { name: 'maker', type: 'address' },
    { name: 'sellToken', type: 'address' },
    { name: 'buyToken', type: 'address' },
    { name: 'sellAmount', type: 'uint256' },
    { name: 'minBuyAmount', type: 'uint256' },
    { name: 'validUntil', type: 'uint256' }, // Timestamp for intent expiry
    { name: 'solverFee', type: 'uint256' }, // Optional: Max fee willing to pay solver
    { name: 'preferredSolver', type: 'address' }, // Optional: Hint for a specific solver
  ],
};

async function signSwapIntent(
  signer: ethers.Signer,
  sellToken: string,
  buyToken: string,
  sellAmount: string,
  minBuyAmount: string,
  validUntil: number,
  solverFee: string = '0',
  preferredSolver: string = ethers.constants.AddressZero,
) {
  const makerAddress = await signer.getAddress();

  const value = {
    maker: makerAddress,
    sellToken,
    buyToken,
    sellAmount,
    minBuyAmount,
    validUntil,
    solverFee,
    preferredSolver,
  };

  // Sign the typed data
  const signature = await signer._signTypedData(domain, types, value);
  console.log(`Signed Intent:`, { value, signature });
  return { value, signature };
}

// Example usage (replace with actual signer and token addresses)
// const provider = new ethers.providers.JsonRpcProvider('http://localhost:8545');
// const wallet = new ethers.Wallet('YOUR_PRIVATE_KEY', provider);
// signSwapIntent(
//   wallet,
//   '0x...ETH_ADDRESS',
//   '0x...USDC_ADDRESS',
//   ethers.utils.parseEther('1').toString(),
//   ethers.utils.parseUnits('1800', 6).toString(),
//   Math.floor(Date.now() / 1000) + 3600 // Valid for 1 hour
// );
```

### 2. Solver Logic: Identifying and Proposing Solutions (Off-Chain)

A solver's primary job is to listen for new intents, find the best way to fulfill them, and then propose an on-chain transaction bundle (or a single transaction) to a settlement contract. This typically involves complex off-chain logic.

```typescript
// Conceptual Solver Pseudo-code
// This would run as an off-chain service

function startSolverService() {
  listenForNewIntents(); // e.g., via a message queue, P2P network, or intent aggregator API
  setInterval(processIntents, 1000); // Periodically check for new intents to solve
}

async function processIntents() {
  const pendingIntents = getPendingIntents(); // Fetch intents that haven't expired or been filled

  for (const intent of pendingIntents) {
    if (intent.validUntil < Date.now() / 1000) {
      markIntentAsExpired(intent);
      continue;
    }

    // 1. Simulate and find optimal paths
    // Use DeFi SDKs (Uniswap, Curve, Balancer), aggregators (1inch, Paraswap)
    // to find the best swap path for (intent.sellToken, intent.buyToken, intent.sellAmount)
    const optimalSolution = await findOptimalSwapPath(
      intent.sellToken,
      intent.buyToken,
      intent.sellAmount
    );

    if (optimalSolution.buyAmount >= intent.minBuyAmount) {
      // 2. Construct a 'solution' transaction bundle
      // This might involve:
      //   - Approving tokens for a router
      //   - Calling a swap function on a DEX
      //   - Sending tokens to the intent maker
      const proposedTxData = constructExecutionBundle(
        intent,
        optimalSolution
      );

      // 3. Estimate gas and profitability (considering potential MEV)
      const cost = estimateTransactionCost(proposedTxData);
      const potentialProfit = calculateSolverProfit(
        optimalSolution.buyAmount,
        intent.minBuyAmount,
        intent.solverFee,
        cost
      );

      if (potentialProfit > MIN_PROFIT_THRESHOLD) {
        // 4. Submit the solution to the on-chain settlement contract
        submitSolutionToSettlementContract(intent.hash, proposedTxData);
      }
    }
  }
}
```

### 3. On-Chain Intent Settlement Contract

The settlement contract verifies the solver's proposed solution against the original signed intent and executes the necessary on-chain actions. This contract is critical for security and trustlessness.

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.17;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/utils/cryptography/ECDSA.sol";
import "@openzeppelin/contracts/utils/cryptography/EIP712.sol";

// This is a simplified example. A real settlement contract would be much more complex.
contract IntentSettlement is EIP712 {
    using ECDSA for bytes32;

    struct SwapIntent {
        address maker;
        address sellToken;
        address buyToken;
        uint256 sellAmount;
        uint256 minBuyAmount;
        uint256 validUntil;
        uint256 solverFee;
        address preferredSolver; // Not strictly enforced here, but could be.
    }

    // Mapping to prevent replay attacks and track filled intents
    mapping(bytes32 => bool) public isIntentFilled;

    bytes32 private constant _SWAP_INTENT_TYPEHASH = keccak256(
        "SwapIntent(address maker,address sellToken,address buyToken,uint256 sellAmount,uint256 minBuyAmount,uint256 validUntil,uint256 solverFee,address preferredSolver)"
    );

    constructor() EIP712("IntentBasedSwap", "1") {}

    function _hashTypedDataV4(bytes32 structHash) internal view virtual override returns (bytes32) {
        return _hashTypedDataV4(structHash);
    }

    /**
     * @notice Solvers call this function to execute a fulfilled intent.
     * @param intent The structured intent data signed by the maker.
     * @param signature The EIP-712 signature from the maker.
     * @param callData The encoded call data for the actual swap execution (e.g., Uniswap swap).
     * @param targetContract The contract to call for the swap (e.g., Uniswap Router).
     */
    function executeIntent(
        SwapIntent calldata intent,
        bytes memory signature,
        bytes calldata callData,
        address targetContract
    ) external returns (uint256 actualBuyAmount) {
        // 1. Reconstruct and verify intent hash
        bytes32 intentHash = _hashTypedDataV4(
            keccak256(
                abi.encode(
                    _SWAP_INTENT_TYPEHASH,
                    intent.maker,
                    intent.sellToken,
                    intent.buyToken,
                    intent.sellAmount,
                    intent.minBuyAmount,
                    intent.validUntil,
                    intent.solverFee,
                    intent.preferredSolver
                )
            )
        );

        // 2. Recover signer and verify it's the intent maker
        address signer = intentHash.recover(signature);
        require(signer == intent.maker, "Invalid signature or maker mismatch");

        // 3. Check intent validity
        require(block.timestamp <= intent.validUntil, "Intent expired");
        require(!isIntentFilled[intentHash], "Intent already filled");

        // 4. Transfer sell tokens from maker to this contract for the swap
        // (Maker must have approved this contract beforehand)
        IERC20(intent.sellToken).transferFrom(
            intent.maker,
            address(this),
            intent.sellAmount
        );

        // 5. Execute the actual swap
        // Record initial balance of buyToken
        uint256 initialBuyBalance = IERC20(intent.buyToken).balanceOf(address(this));

        // Call the target contract (e.g., a DEX router) with the provided callData
        // This is where the actual swap happens using the tokens transferred in step 4.
        (bool success, bytes memory returnData) = targetContract.call(callData);
        require(success, string(abi.encodePacked("Swap failed: ", returnData)));

        // Record final balance of buyToken
        uint256 finalBuyBalance = IERC20(intent.buyToken).balanceOf(address(this));
        actualBuyAmount = finalBuyBalance - initialBuyBalance;

        // 6. Verify min buy amount
        require(actualBuyAmount >= intent.minBuyAmount, "Slippage too high or minBuyAmount not met");

        // 7. Transfer buy tokens to the maker
        IERC20(intent.buyToken).transfer(intent.maker, actualBuyAmount);

        // 8. Mark intent as filled
        isIntentFilled[intentHash] = true;

        return actualBuyAmount;
    }
}
```

## Anti-Patterns

*   **Replay-Vulnerable Intent Signatures.** Failing to include nonces, chain IDs, or expiry timestamps in the signed intent data allows solvers to replay intents across chains or after they should have expired. Always use EIP-712 with full domain separation and enforce on-chain uniqueness checks.

*   **Unrestricted Target Contract Calls.** Allowing solvers to call arbitrary contracts with arbitrary calldata through the settlement contract opens the door to token theft via malicious approvals. Whitelist permitted target contracts or use a restricted execution model.

*   **Solver Centralization Without Competition.** Relying on a single solver or a small trusted set eliminates the competitive pressure that drives optimal execution. Design open solver networks with permissionless participation and transparent performance metrics.

*   **Missing Intent Expiry Enforcement.** Accepting intents without validating expiry timestamps on-chain allows stale intents to be filled at outdated prices. Always check `block.timestamp <= intent.validUntil` before execution.

*   **Ignoring Partial Fill Scenarios.** Designing intents that must be filled entirely or not at all reduces fill rates for large orders. Support partial fills with proportional minimum output requirements to improve execution across fragmented liquidity.

## Review & Production Validation (2026-10-31)

- **Domain control (Trading and execution):** Use venue-specific rules, actual order-book depth, fees, slippage, latency and position limits.
- **Independent validation:** Separate backtests from live execution; check look-ahead bias, failure recovery, and negative tail scenarios.
- **Time-sensitive details:** Treat fixed rates, thresholds, package versions, protocols and jurisdiction-specific rules in the examples above as illustrative unless reconfirmed against primary documentation.
- **Before relying on the result:** State inputs and assumptions; verify calculations and edge cases, and identify what has not been executed or tested.
