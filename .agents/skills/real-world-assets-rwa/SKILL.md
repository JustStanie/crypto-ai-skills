---
name: real-world-assets-rwa
description: 'Use when the user needs on-chain real-world assets: analyze tokenization,
  custody, legal rights, compliance and oracle dependencies.'
---

# On-chain real-world assets

You are a seasoned blockchain architect and tokenization specialist, having designed and deployed numerous Real-World Asset (RWA) protocols that bridge the chasm between traditional financial instruments and the immutable ledger. You understand the intricate dance between legal frameworks, robust custody solutions, and secure smart contract engineering necessary to bring illiquid assets onto the blockchain. Your expertise spans the entire lifecycle, from structuring Special Purpose Vehicles (SPVs) to implementing sophisticated oracle networks and ensuring compliant, redeemable on-chain representations.

## Core Philosophy

Real-World Assets (RWA) tokenization is fundamentally about creating a verifiable, programmable, and often fractionalized digital claim on an underlying physical or intangible asset. This isn't just about putting a certificate on-chain; it's about embedding the rights, obligations, and economic value of that asset into a smart contract, making it accessible to DeFi's liquidity and innovation rails. The core challenge lies in maintaining a strong, legally enforceable, and transparent link between the on-chain token and its off-chain counterpart.

The true power of RWA tokenization comes from unlocking new forms of ownership, enabling instant settlement, and providing global access to asset classes traditionally siloed within national borders and opaque financial institutions. However, this hybrid nature demands a meticulous approach. You must ensure that the smart contract accurately reflects the legal reality, that custody of the physical asset is unimpeachable, and that reliable oracles constantly bridge the off-chain status to the on-chain representation. Without these foundational elements, an RWA token is merely an unbacked digital promise.

## Setup

Building with RWA primarily involves standard Ethereum/EVM development tools, augmented by specific considerations for off-chain data integration and legal compliance.

1.  **Initialize your project:** Start with a robust smart contract development environment like Hardhat or Foundry.

    ```bash
    mkdir rwa-project
    cd rwa-project
    npm init -y
    npm install --save-dev hardhat @nomicfoundation/hardhat-toolbox @openzeppelin/contracts
    npx hardhat
    # Select 'Create a basic sample project'
    ```

2.  **Install Ethers.js for client-side interaction:**

    ```bash
    npm install ethers
    ```

3.  **Integrate Chainlink for Oracle data (if needed):** Many RWA solutions require reliable off-chain data feeds (e.g., asset valuation, status updates).

    ```bash
    npm install @chainlink/contracts
    ```

4.  **Configuration for deployment:** Set up your `hardhat.config.js` with network providers and private keys for deployment to testnets or mainnets.

    ```javascript
    require("@nomicfoundation/hardhat-toolbox");
    require("@openzeppelin/hardhat-upgrades"); // For upgradeable contracts

    const ALCHEMY_API_KEY = process.env.ALCHEMY_API_KEY;
    const PRIVATE_KEY = process.env.PRIVATE_KEY;

    module.exports = {
      solidity: "0.8.20",
      networks: {
        sepolia: {
          url: `https://eth-sepolia.g.alchemy.com/v2/${ALCHEMY_API_KEY}`,
          accounts: [PRIVATE_KEY]
        },
        // Add other networks like Polygon, Arbitrum etc.
      }
    };
    ```

## Key Techniques

### 1. ERC-20 Tokenization with Legal Reference

Tokenizing an RWA often starts with an ERC-20 standard, representing fractional ownership or claims. Crucially, the contract must embed or reference the legal framework that underpins the asset.

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts/utils/Pausable.sol";

/**
 * @title RealEstateShareToken
 * @dev An ERC-20 token representing fractional ownership in a specific real estate asset.
 *      Includes a reference to the off-chain legal agreement and a redemption mechanism.
 */
contract RealEstateShareToken is ERC20, AccessControl, Pausable {
    bytes32 public constant MINTER_ROLE = keccak256("MINTER_ROLE");
    bytes32 public constant REDEEMER_ROLE = keccak256("REDEEMER_ROLE");

    // Reference to the URI where the legal documents (e.g., SPV agreement, prospectus) are hosted
    string public legalDocumentURI;
    // Hash of the legal document content for integrity verification
    bytes32 public legalDocumentHash;

    // Mapping to track redemption requests
    mapping(address => uint256) public redemptionRequests;

    event LegalDocumentUpdated(string newURI, bytes32 newHash);
    event RedemptionRequested(address indexed account, uint256 amount);
    event RedemptionCompleted(address indexed account, uint256 amount);

    constructor(
        string memory name,
        string memory symbol,
        string memory _legalDocumentURI,
        bytes32 _legalDocumentHash,
        address defaultAdmin
    ) ERC20(name, symbol) {
        _grantRole(DEFAULT_ADMIN_ROLE, defaultAdmin);
        _grantRole(MINTER_ROLE, defaultAdmin); // Admin can also mint initially
        _grantRole(REDEEMER_ROLE, defaultAdmin); // Admin can process redemptions

        legalDocumentURI = _legalDocumentURI;
        legalDocumentHash = _legalDocumentHash;
    }

    function setLegalDocument(string memory newURI, bytes32 newHash) public onlyRole(DEFAULT_ADMIN_ROLE) {
        legalDocumentURI = newURI;
        legalDocumentHash = newHash;
        emit LegalDocumentUpdated(newURI, newHash);
    }

    function pause() public onlyRole(DEFAULT_ADMIN_ROLE) {
        _pause();
    }

    function unpause() public onlyRole(DEFAULT_ADMIN_ROLE) {
        _unpause();
    }

    function mint(address to, uint256 amount) public onlyRole(MINTER_ROLE) whenNotPaused {
        _mint(to, amount);
    }

    function burn(uint256 amount) public whenNotPaused {
        _burn(msg.sender, amount);
    }

    /**
     * @dev Allows a token holder to request redemption of their tokens for the underlying asset.
     *      This initiates an off-chain process.
     */
    function requestRedemption(uint256 amount) public whenNotPaused {
        require(amount > 0, "Amount must be greater than zero");
        require(balanceOf(msg.sender) >= amount, "Insufficient balance for redemption");

        // Transfer tokens to the contract or burn them immediately, depending on the off-chain process
        _burn(msg.sender, amount); // Or _transfer(msg.sender, address(this), amount); if held in escrow
        redemptionRequests[msg.sender] += amount;
        emit RedemptionRequested(msg.sender, amount);
    }

    /**
     * @dev Marks an off-chain redemption as complete. Only callable by an authorized REDEEMER.
     *      This function does not handle asset transfer itself, only confirms the off-chain resolution.
     */
    function completeRedemption(address account, uint256 amount) public onlyRole(REDEEMER_ROLE) {
        require(redemptionRequests[account] >= amount, "No pending redemption for this amount");
        redemptionRequests[account] -= amount;
        emit RedemptionCompleted(account, amount);
    }

    function _beforeTokenTransfer(address from, address to, uint256 amount)
        internal
        override
        whenNotPaused
    {}
}
```

### 2. Oracle Integration for Off-Chain Valuation

RWAs often require dynamic valuation or status updates from the real world. Chainlink is the industry standard for this. This example shows fetching a price feed for a hypothetical commodity-backed token.

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@chainlink/contracts/src/v0.8/interfaces/AggregatorV3Interface.sol";

/**
 * @title RWAOracleClient
 * @dev A contract that fetches the latest price from a Chainlink Price Feed,
 *      useful for dynamic valuation of RWA tokens.
 */
contract RWAOracleClient is Ownable {
    AggregatorV3Interface internal priceFeed;

    constructor(address _priceFeedAddress) {
        priceFeed = AggregatorV3Interface(_priceFeedAddress);
    }

    /**
     * @dev Returns the latest price of the underlying asset from the Chainlink feed.
     *      Assumes the price feed is configured for the specific RWA.
     * @return price The latest price, with 8 decimals for most Chainlink feeds.
     */
    function getLatestPrice() public view returns (int256) {
        (
            /*uint80 roundID*/,
            int256 price,
            /*uint256 startedAt*/,
            /*uint256 timeStamp*/,
            /*uint80 answeredInRound*/
        ) = priceFeed.latestRoundData();
        return price;
    }

    // Function to update the price feed address if the oracle changes
    function setPriceFeed(address _newPriceFeedAddress) public onlyOwner {
        priceFeed = AggregatorV3Interface(_newPriceFeedAddress);
    }
}
```

**Client-side interaction (Ethers.js):**

```javascript
const { ethers } = require("ethers");
require('dotenv').config();

const RWA_ORACLE_ADDRESS = "0x9326BFA02ADD2366b30f60f34E269D63Bae5093E"; // Example: ETH/USD on Sepolia
const RWA_ORACLE_ABI = [
    "function getLatestPrice() view returns (int256)",
    "function setPriceFeed(address _newPriceFeedAddress)"
];

async function fetchRwaPrice() {
    const provider = new ethers.JsonRpcProvider(process.env.ALCHEMY_URL_SEPOLIA);
    const rwaOracle = new ethers.Contract(RWA_ORACLE_ADDRESS, RWA_ORACLE_ABI, provider);

    try {
        const price = await rwaOracle.getLatestPrice();
        console.log(`Latest RWA asset price: ${ethers.formatUnits(price, 8)} USD`); // Chainlink typically uses 8 decimals
    } catch (error) {
        console.error("Error fetching RWA price:", error);
    }
}

fetchRwaPrice();
```

### 3. Access Control and Whitelisting for Regulatory Compliance

Many RWA tokens, especially those representing securities, require Know Your Customer (KYC) and Anti-Money Laundering (AML) checks. This often translates to whitelisting approved addresses for transfers.

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/AccessControl.sol";

/**
 * @title WhitelistedRWAToken
 * @dev An ERC-20 token where transfers are restricted to whitelisted addresses.
 */
contract WhitelistedRWAToken is ERC20, AccessControl {
    bytes32 public constant WHITELIST_ADMIN_ROLE = keccak256("WHITELIST_ADMIN_ROLE");
    bytes32 public constant WHITELISTED_ROLE = keccak256("WHITELISTED_ROLE");

    constructor(
        string memory name,
        string memory symbol,
        address defaultAdmin
    ) ERC20(name, symbol) {
        _grantRole(DEFAULT_ADMIN_ROLE, defaultAdmin);
        _grantRole(WHITELIST_ADMIN_ROLE, defaultAdmin);
        _grantRole(WHITELISTED_ROLE, defaultAdmin); // Admin is whitelisted by default
    }

    /**
     * @dev Adds an address to the whitelist.
     */
    function addToWhitelist(address account) public onlyRole(WHITELIST_ADMIN_ROLE) {
        _grantRole(WHITELISTED_ROLE, account);
    }

    function _beforeTokenTransfer(address from, address to, uint256 amount) internal override {
        if (from != address(0) && to != address(0)) {
            require(hasRole(WHITELISTED_ROLE, from), "Sender not whitelisted");
            require(hasRole(WHITELISTED_ROLE, to), "Recipient not whitelisted");
        }
    }
}
```

## Anti-Patterns

*   **Tokenizing Without Legal Enforceability.** Minting tokens that claim to represent real-world assets without a legally binding link (SPV, trust deed, or regulatory registration) creates unbacked digital promises. Always establish the legal structure before deploying the smart contract.

*   **Stale Off-Chain Valuation Oracles.** Using infrequently updated price feeds for illiquid real-world assets leads to mispriced collateral and incorrect liquidation thresholds. Implement staleness checks and circuit breakers that pause protocol operations when oracle data exceeds acceptable age.

*   **Single Custodian Dependency.** Trusting a single custodian to hold the underlying asset without insurance, audit obligations, or multi-party verification creates unacceptable counterparty risk. Use multiple custodians or proof-of-reserve attestation chains.

*   **Ignoring Jurisdictional Transfer Restrictions.** Allowing unrestricted on-chain transfers of security tokens violates securities regulations in most jurisdictions. Implement transfer restriction hooks that enforce whitelist and compliance checks at the smart contract level.

*   **Omitting Redemption Mechanisms.** Deploying RWA tokens without a clear, auditable redemption path back to the underlying asset traps holders in a one-way tokenization. Always implement and test the full lifecycle including redemption, with documented off-chain processes.

## Review & Production Validation (2026-10-31)

- **Domain control (Regulated crypto activity):** Establish the applicable jurisdiction, legal status and effective date before making compliance claims.
- **Independent validation:** Require professional review for custody, marketing, reporting and licensing decisions.
- **Time-sensitive details:** Treat fixed rates, thresholds, package versions, protocols and jurisdiction-specific rules in the examples above as illustrative unless reconfirmed against primary documentation.
- **Before relying on the result:** State inputs and assumptions; verify calculations and edge cases, and identify what has not been executed or tested.
