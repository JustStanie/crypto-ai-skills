---
name: chainlink-oracles
description: 'Use when the user needs chainlink oracle integration: select data feeds, validate
  freshness and decimals, and analyze oracle failure modes.'
---

# Chainlink oracle integration

You are a seasoned blockchain architect who leverages Chainlink's decentralized oracle networks to build robust, secure, and data-rich smart contracts. You understand that the true power of Web3 applications emerges when on-chain logic can reliably and securely interact with the real world. Your solutions integrate external data and arbitrary off-chain computation without sacrificing decentralization or trustlessness, ensuring your dApps are not only functional but also resilient against data manipulation and single points of failure.

## Core Philosophy

The "oracle problem" is a fundamental challenge for smart contracts: they are deterministic and isolated by design, unable to directly access real-world data or off-chain systems. Chainlink solves this by creating decentralized oracle networks that provide tamper-proof, reliable data feeds and secure off-chain computation. Your approach must always prioritize decentralization and cryptoeconomic security. Never introduce a single point of failure by relying on a centralized data source.

Think of smart contracts as the "brain" and Chainlink oracles as the "sensory organs" that connect that brain to the external environment. By using Chainlink, you build "hybrid smart contracts" that combine on-chain logic with off-chain data and computation, unlocking an entirely new class of decentralized applications—from DeFi lending protocols using real-time prices to NFT games requiring provably fair randomness. Always verify the data you receive and understand the security models of the Chainlink services you integrate.

## Setup

To develop with Chainlink, you'll primarily work with Solidity smart contracts and a local development environment like Foundry or Hardhat.

1.  **Install development tools:**
    ```bash
    # For Foundry
    # Security: download the verified official installer, inspect it before executing, and follow the current platform-specific installation guide.
    foundryup

    # For Hardhat (if preferred)
    npm install --save-dev hardhat
    npx hardhat init
    ```

2.  **Add Chainlink Contracts:** Integrate the official Chainlink smart contract interfaces and helper libraries.
    ```bash
    # For Foundry, add as a git submodule
    git submodule add https://github.com/smartcontractkit/chainlink-brownie-contracts lib/chainlink-brownie-contracts
    forge remappings > remappings.txt # Ensure remappings are updated

    # For Hardhat, install via npm
    npm install @chainlink/contracts
    ```

3.  **Obtain LINK tokens:** Chainlink services require LINK tokens to pay oracle nodes for their services. For development, use testnet LINK from a faucet.
    -   Go to [faucets.chain.link](https://faucets.chain.link/)
    -   Select your desired testnet (e.g., Sepolia, Mumbai, Arbitrum Sepolia).
    -   Enter your wallet address to receive testnet LINK.

## Key Techniques

### 1. Reading Decentralized Price Feeds

Accessing real-time, tamper-proof asset prices is a cornerstone of DeFi. Chainlink Price Feeds are the most widely adopted solution.

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import {AggregatorV3Interface} from "@chainlink/contracts/src/v0.8/interfaces/AggregatorV3Interface.sol";

contract PriceConsumerV3 {
    AggregatorV3Interface internal priceFeed;

    constructor(address _priceFeedAddress) {
        priceFeed = AggregatorV3Interface(_priceFeedAddress);
    }

    /// @notice Returns the latest price and metadata.
    /// @dev Validate answer, decimals, and updatedAt against a feed-specific freshness policy.
    /// Consult the current feed interface and documentation for the semantics of answeredInRound.
    function getLatestPrice() public view returns (int256, uint80, uint256, uint256, uint80) {
        // prettier-ignore
        (
            uint80 roundID,
            int256 price,
            uint256 startedAt,
            uint256 updatedAt,
            uint80 answeredInRound
        ) = priceFeed.latestRoundData();
        require(price > 0 && updatedAt > 0 && updatedAt <= block.timestamp, "Invalid feed answer or timestamp.");
        // Check block.timestamp - updatedAt against a feed-specific maximum age in the consuming protocol.
        return (roundID, price, startedAt, updatedAt, answeredInRound);
    }

    /// @notice Returns the description of the price feed (e.g., "ETH / USD").
    function getDescription() public view returns (string memory) {
        return priceFeed.description();
    }

    /// @notice Returns the number of decimals for the price (e.g., 8 for 1800.00000000).
    function getDecimals() public view returns (uint8) {
        return priceFeed.decimals();
    }
}
```

### 2. Requesting Verifiable Randomness (VRF)

For applications requiring provably fair and unpredictable outcomes (e.g., gaming, NFTs, lotteries), Chainlink VRF provides cryptographically secure randomness.

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import {VRFConsumerBaseV2} from "@chainlink/contracts/src/v0.8/VRFConsumerBaseV2.sol";
import {VRFCoordinatorV2Interface} from "@chainlink/contracts/src/v0.8/interfaces/VRFCoordinatorV2Interface.sol";

contract RandomNumberConsumer is VRFConsumerBaseV2 {
    VRFCoordinatorV2Interface immutable i_vrfCoordinator;
    uint64 immutable i_subscriptionId;
    bytes32 immutable i_keyHash;
    uint32 immutable i_callbackGasLimit;
    uint16 immutable i_requestConfirmations;
    uint32 immutable i_numWords;

    uint256[] public s_randomWords;
    uint256 public s_requestId;
    address public s_owner;

    event RequestSent(uint256 requestId, uint32 numWords);
    event RequestFulfilled(uint256 requestId, uint256[] randomWords, uint256 payment);

    constructor(
        uint64 subscriptionId,
        address vrfCoordinator,
        bytes32 keyHash,
        uint32 callbackGasLimit,
        uint16 requestConfirmations,
        uint32 numWords
    ) VRFConsumerBaseV2(vrfCoordinator) {
        i_vrfCoordinator = VRFCoordinatorV2Interface(vrfCoordinator);
        i_subscriptionId = subscriptionId;
        i_keyHash = keyHash;
        i_callbackGasLimit = callbackGasLimit;
        i_requestConfirmations = requestConfirmations;
        i_numWords = numWords;
        s_owner = msg.sender;
    }

    function requestRandomWords() public returns (uint256 requestId) {
        require(i_vrfCoordinator.getSubscription(i_subscriptionId).balance >= i_vrfCoordinator.getRequestConfig().get  [1], "Insufficient LINK balance for subscription.");
        // Will revert if subscription is not funded with LINK
        requestId = i_vrfCoordinator.requestRandomWords(
            i_keyHash,
            i_subscriptionId,
            i_requestConfirmations,
            i_callbackGasLimit,
            i_numWords
        );
        s_requestId = requestId;
        emit RequestSent(requestId, i_numWords);
        return requestId;
    }

    function fulfillRandomWords(uint256 requestId, uint256[] memory randomWords) internal override {
        require(requestId == s_requestId, "Request ID not matched.");
        s_randomWords = randomWords;
        emit RequestFulfilled(requestId, randomWords, msg.sender.balance); // Payment is handled by VRF Coordinator
    }
}
```
*Note: Before deploying, you'll need to create a VRF Subscription on [vrf.chain.link](https://vrf.chain.link/) and fund it with LINK. Then add your `RandomNumberConsumer` contract as a consumer to that subscription.*

### 3. Making Arbitrary HTTP Requests (Chainlink Functions)

Chainlink Functions allow your smart contracts to request data from any API, perform custom computations off-chain using JavaScript, and receive the result back on-chain. This is a powerful tool for integrating with Web2 services.

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import {FunctionsClient} from "@chainlink/contracts/src/v0.8/functions/v1_0_0/FunctionsClient.sol";
import {IFunctionsRouter} from "@chainlink/contracts/src/v0.8/functions/v1_0_0/interfaces/IFunctionsRouter.sol";
import {ConfirmedOwner} from "@chainlink/contracts/src/v0.8/shared/access/ConfirmedOwner.sol";

contract APIRequestConsumer is FunctionsClient, ConfirmedOwner {
    bytes32 public s_lastRequestId;
    bytes public s_lastResponse;
    bytes public s_lastError;

    uint64 public s_subscriptionId;

    event OCRResponse(bytes32 indexed requestId, bytes response, bytes err);

    constructor(address router, uint64 subscriptionId) FunctionsClient(router) ConfirmedOwner(msg.sender) {
        s_subscriptionId = subscriptionId;
    }

    /// @notice Make a request to the Chainlink Functions network.
    /// @param source The JavaScript source code for the Chainlink Functions request.
    /// @param args An array of arguments to pass to the JavaScript source code.
    /// @param secrets The encrypted secrets to pass to the JavaScript source code.
    /// @param donId The ID of the Decentralized Oracle Network (DON) to use.
    /// @param callbackGasLimit The maximum amount of gas the Functions request can use.
    function sendRequest(
        string memory source,
        string[] memory args,
        bytes memory secrets,
        bytes32 donId,
        uint32 callbackGasLimit
    ) public onlyOwner returns (bytes32 requestId) {
        FunctionsRequest.Request memory req;
        req.initializeRequestForInlineJavaScript(source);
        if (secrets.length > 0) req.addSecrets(secrets);
        if (args.length > 0) req.addArgs(args);

        requestId = _sendRequest(
            req.encode(),
            s_subscriptionId,
            callbackGasLimit,
            donId
        );
        s_lastRequestId = requestId;
        return requestId;
    }

    /// @notice Callback function that is called by the Functions router when the request is fulfilled.
    /// @param requestId The ID of the request.
    /// @param response The response from the Chainlink Functions network.
    /// @param err The error message, if any.
    function fulfillRequest(bytes32 requestId, bytes memory response, bytes memory err) internal override {
        require(s_lastRequestId == requestId, "Request ID not matched.");
        s_lastResponse = response;
        s_lastError = err;
        emit OCRResponse(requestId, response, err);
    }
}
```
*Note: This example uses inline JavaScript `source`. You can also use IPFS for larger scripts. You'll need to create a Functions Subscription on [functions.chain.link](https://functions.chain.link/) and fund it, then add your contract as a consumer.*

### 4. Automating Smart Contract Functions (Chainlink Automation)

Chainlink Automation (formerly Keepers) allows you to reliably schedule and trigger contract functions based on time or arbitrary custom logic, without needing a centralized server.

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import {KeeperCompatibleInterface} from "@chainlink/contracts/src/v0.8/KeeperCompatible.sol";

contract AutomatedCounter is KeeperCompatibleInterface {
    uint256 public s_counter;
    uint256 public s_lastUpdated;
    uint256 public immutable i_interval; // Time in seconds between updates

    constructor(uint256 interval) {
        s_counter = 0;
        s_lastUpdated = block.timestamp;
        i_interval = interval;
    }

    /// @notice This function is called by the Chainlink Automation network.
    /// @dev Check if enough time has passed since the last update.
    /// @param checkData Arbitrary data passed to the checkUpkeep function (not used here).
    /// @return upkeepNeeded True if the upkeep should be performed.
    /// @return performData Arbitrary data to be passed to the performUpkeep function.
    function checkUpkeep(bytes calldata checkData)
        external
        view
        override
        returns (bool upkeepNeeded, bytes memory performData)
    {
        upkeepNeeded = (block.timestamp - s_lastUpdated) > i_interval;
        // The performData can be used to pass arbitrary data to the performUpkeep function.
        performData = "";
    }

    /// @notice This function is called by the Chainlink Automation network when `checkUpkeep` returns true.
    /// @param performData Arbitrary data passed from the checkUpkeep function (not used here).
    function performUpkeep(bytes calldata performData) external override {
        // We don't check `upkeepNeeded` here, as the Keeper will only call `performUpkeep` if `checkUpkeep` was true.
        // However, it's good practice to re-check conditions if external factors could change between `checkUpkeep` and `performUpkeep`.
        if ((block.timestamp - s_lastUpdated) > i_interval) {
            s_counter++;
            s_lastUpdated = block.timestamp;
        }
    }
}
```

## Anti-Patterns

*   **Using Stale Price Feed Data.** Consuming Chainlink price feed responses without checking the `updatedAt` timestamp allows contracts to operate on outdated prices during oracle downtime, leading to incorrect liquidations or arbitrage exploits.

*   **Single Oracle Source for Critical Decisions.** Relying on a single Chainlink feed without fallback oracles or circuit breakers means that any feed disruption (network congestion, heartbeat delay) halts or corrupts protocol operations.

*   **Ignoring Chainlink Feed Decimals.** Assuming all Chainlink feeds return 8 decimals when some feeds (notably ETH-denominated feeds) use 18 decimals causes price calculations to be off by orders of magnitude.

*   **Unbounded Automation Gas Consumption.** Implementing `performUpkeep` functions that consume variable and potentially unbounded gas without caps risks failed automation calls when gas prices spike, leaving time-sensitive operations unexecuted.

*   **Hardcoded Feed Addresses Across Networks.** Embedding Chainlink feed addresses directly in contract code without a registry pattern makes multi-chain deployment error-prone and prevents runtime feed updates when Chainlink migrates feed contracts.

## Version and Evidence Check

For price feeds validate answer sign, scale/decimals and freshness using updatedAt and a feed-specific timeout. Oracle round fields and supported interfaces may differ by deployment.

## Review & Production Validation (2026-10-31)

- **Domain control (Custody and security):** Treat bridge, authorization, signing, key handling and replay risk as potentially loss-causing.
- **Independent validation:** Avoid secrets in examples; validate controls, testnets, incident procedures and third-party contracts.
- **Time-sensitive details:** Treat fixed rates, thresholds, package versions, protocols and jurisdiction-specific rules in the examples above as illustrative unless reconfirmed against primary documentation.
- **Before relying on the result:** State inputs and assumptions; verify calculations and edge cases, and identify what has not been executed or tested.


## Confirmed interface update (Chainlink)

The `answeredInRound` field is deprecated for many AggregatorV3Interface deployments; do not use it as the sole freshness gate. Validate `updatedAt` with a feed-specific heartbeat and maximum-age policy, check answer sign and decimals, and review https://docs.chain.link/data-feeds/api-reference and https://docs.chain.link/data-feeds/overview before deployment.
