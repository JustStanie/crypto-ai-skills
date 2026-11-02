---
name: erc721-nft-contracts
description: 'Use when the user needs erc-721 nft contracts: design minting, royalties,
  metadata, enumeration and access control.'
---

# ERC-721 NFT contracts

You are a seasoned blockchain architect specializing in the design and deployment of robust, secure, and gas-optimized ERC-721 NFT contracts. You've launched numerous successful NFT collections, from generative art to utility-driven assets, and understand the nuances of on-chain vs. off-chain data, upgradability, and community engagement through contract design. You build for resilience, security, and long-term value.

## Core Philosophy

ERC-721 defines the standard for unique digital assets on Ethereum, making them discoverable and interoperable across various platforms. Your philosophy centers on building contracts that are fundamentally secure, gas-efficient, and extensible. While the token itself is immutable, flexibility in metadata handling (via `tokenURI` and off-chain storage like IPFS) is paramount for evolving projects. Prioritize security by leveraging battle-tested libraries like OpenZeppelin, and always consider the long-term implications of your contract's design – from minting mechanics to secondary market royalties. Upgradability via proxy patterns is a powerful tool for complex projects, allowing for future feature additions or bug fixes without redeploying the entire collection.

## Setup

For developing and deploying ERC-721 contracts, Hardhat or Foundry are your go-to development environments. We'll use Hardhat for this example, combined with OpenZeppelin Contracts for industry-standard implementations.

1.  **Initialize a Hardhat project:**
    ```bash
    mkdir my-nft-project
    cd my-nft-project
    npm init -y
    npm install --save-dev hardhat @nomicfoundation/hardhat-toolbox @openzeppelin/contracts
    npx hardhat
    # Select "Create a JavaScript project" and follow prompts
    ```

2.  **Configure Hardhat for your network (e.g., Sepolia):**
    Edit `hardhat.config.js`:
    ```javascript
    require("@nomicfoundation/hardhat-toolbox");
    require("@openzeppelin/hardhat-upgrades"); // For upgradable contracts

    const dotenv = require("dotenv");
    dotenv.config();

    module.exports = {
      solidity: "0.8.20", // Match your contract's Solidity version
      networks: {
        sepolia: {
          url: process.env.SEPOLIA_RPC_URL || "",
          accounts: process.env.PRIVATE_KEY !== undefined ? [process.env.PRIVATE_KEY] : [],
          gasPrice: 8000000000, // Example gas price (8 Gwei)
        },
        // Add other networks like mainnet, polygon, etc.
      },
      etherscan: {
        apiKey: process.env.ETHERSCAN_API_KEY,
      },
    };
    ```
    Create a `.env` file for your RPC URL and private key:
    ```
    SEPOLIA_RPC_URL="YOUR_SEPOLIA_ALCHEMY_OR_INFURA_URL"
    PRIVATE_KEY="YOUR_WALLET_PRIVATE_KEY"
    ETHERSCAN_API_KEY="YOUR_ETHERSCAN_API_KEY" # For contract verification
    ```

## Key Techniques

### 1. Basic ERC-721 Implementation with OpenZeppelin

Start with OpenZeppelin's battle-tested `ERC721` contract. This provides the core functionality, including `ownerOf`, `balanceOf`, `approve`, `transferFrom`, and `setApprovalForAll`.

```solidity
// contracts/MyCollectible.sol
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/Counters.sol";

contract MyCollectible is ERC721, Ownable {
    using Counters for Counters.Counter;
    Counters.Counter private _tokenIdCounter;

    uint256 public MAX_SUPPLY = 10000; // Example maximum supply

    // Base URI for metadata (e.g., IPFS gateway)
    string private _baseTokenURI;

    // Event for when a new token is minted
    event TokenMinted(address indexed to, uint256 indexed tokenId, string tokenURI);

    constructor(string memory name, string memory symbol, string memory baseTokenURI_)
        ERC721(name, symbol)
        Ownable(msg.sender) // Owner is the deployer
    {
        _baseTokenURI = baseTokenURI_;
    }

    // Function to mint a new token
    function mint(address to) public onlyOwner {
        require(_tokenIdCounter.current() < MAX_SUPPLY, "Max supply reached");

        _tokenIdCounter.increment();
        uint256 newItemId = _tokenIdCounter.current();
        _safeMint(to, newItemId); // _safeMint checks if 'to' is a contract that can receive NFTs

        emit TokenMinted(to, newItemId, tokenURI(newItemId));
    }

    // Override to return the full token URI for a given token ID
    function _baseURI() internal view override returns (string memory) {
        return _baseTokenURI;
    }

    // Admin function to update the base URI
    function setBaseURI(string memory newBaseURI_) public onlyOwner {
        _baseTokenURI = newBaseURI_;
    }

    // Optionally, pause minting
    // import "@openzeppelin/contracts/utils/Pausable.sol";
    // contract MyCollectible is ERC721, Ownable, Pausable { ... }
    // function mint(...) public onlyOwner whenNotPaused { ... }
    // function pause() public onlyOwner { _pause(); }
    // function unpause() public onlyOwner { _unpause(); }
}
```

### 2. Deploying the Contract

Create a deployment script in `scripts/deploy.js`:

```javascript
// scripts/deploy.js
const { ethers } = require("hardhat");

async function main() {
  const [deployer] = await ethers.getSigners();
  console.log("Deploying contracts with the account:", deployer.address);

  const MyCollectible = await ethers.getContractFactory("MyCollectible");
  const name = "My Awesome NFT Collection";
  const symbol = "MANC";
  const baseTokenURI = "ipfs://Qmbn3t7X.../"; // Placeholder IPFS CID

  const myCollectible = await MyCollectible.deploy(name, symbol, baseTokenURI);
  await myCollectible.waitForDeployment();

  console.log("MyCollectible deployed to:", await myCollectible.getAddress());
  console.log("Base URI set to:", await myCollectible.baseURI());
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
```

Deploy to Sepolia:
```bash
npx hardhat run scripts/deploy.js --network sepolia
```

### 3. Interacting with the Contract (Minting)

You can interact with your deployed contract using Hardhat's console or a separate script.

```javascript
// scripts/mint.js
const { ethers } = require("hardhat");

async function main() {
  const contractAddress = "YOUR_DEPLOYED_CONTRACT_ADDRESS"; // Replace with your contract address
  const [minter] = await ethers.getSigners(); // Assumes minter is the contract owner
  const recipientAddress = "0xYourRecipientAddressHere"; // Address to mint to

  const MyCollectible = await ethers.getContractFactory("MyCollectible");
  const myCollectible = MyCollectible.attach(contractAddress);

  console.log(`Minting token to ${recipientAddress}...`);
  const tx = await myCollectible.connect(minter).mint(recipientAddress);
  await tx.wait(); // Wait for the transaction to be mined

  const latestTokenId = await myCollectible.totalSupply();
  console.log(`Token ${latestTokenId} minted successfully to ${recipientAddress}`);
  console.log(`Token URI: ${await myCollectible.tokenURI(latestTokenId)}`);
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
```
Run the mint script:
```bash
npx hardhat run scripts/mint.js --network sepolia
```

### 4. Handling Upgradability with UUPS Proxies

For contracts that may need future updates, implement UUPS (Universal Upgradeable Proxy Standard) via OpenZeppelin's Hardhat Upgrades plugin. This allows you to deploy a proxy that points to your implementation, and later change the implementation without changing the proxy address.

```solidity
// contracts/MyUpgradeableCollectible.sol
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts-upgradeable/token/ERC721/ERC721Upgradeable.sol";
import "@openzeppelin/contracts-upgradeable/access/OwnableUpgradeable.sol";
import "@openzeppelin/contracts-upgradeable/proxy/utils/Initializable.sol";
import "@openzeppelin/contracts-upgradeable/utils/CountersUpgradeable.sol";

contract MyUpgradeableCollectible is Initializable, ERC721Upgradeable, OwnableUpgradeable {
    using CountersUpgradeable for CountersUpgradeable.Counter;
    CountersUpgradeable.Counter private _tokenIdCounter;

    uint256 public MAX_SUPPLY;
    string private _baseTokenURI;

    /// @custom:oz-upgrades-unsafe-allow constructor
    constructor() {
        _disableInitializers(); // Required for upgradeable contracts using UUPS
    }

    function initialize(string memory name, string memory symbol, string memory baseTokenURI_, uint256 maxSupply_) public initializer {
        __ERC721_init(name, symbol);
        __Ownable_init(msg.sender); // Owner is the deployer
        MAX_SUPPLY = maxSupply_;
        _baseTokenURI = baseTokenURI_;
    }

    function mint(address to) public onlyOwner {
        require(_tokenIdCounter.current() < MAX_SUPPLY, "Max supply reached");
        _tokenIdCounter.increment();
        uint256 newItemId = _tokenIdCounter.current();
        _safeMint(to, newItemId);
    }

    function _baseURI() internal view override returns (string memory) {
        return _baseTokenURI;
    }

    function setBaseURI(string memory newBaseURI_) public onlyOwner {
        _baseTokenURI = newBaseURI_;
    }
}
```

Deployment script for upgradeable contract (`scripts/deploy-upgradeable.js`):
```javascript
// scripts/deploy-upgradeable.js
const { ethers, upgrades } = require("hardhat");

async function main() {
  const [deployer] = await ethers.getSigners();
  console.log("Deploying upgradeable contracts with the account:", deployer.address);

  const MyUpgradeableCollectible = await ethers.getContractFactory("MyUpgradeableCollectible");
  const name = "My Upgradeable NFT";
  const symbol = "MUNFT";
  const baseTokenURI = "ipfs://QmWf.../";
  const maxSupply = 5000;

  // Deploy as a UUPS proxy
  const myUpgradeableCollectible = await upgrades.deployProxy(
    MyUpgradeableCollectible,
    [name, symbol, baseTokenURI, maxSupply],
    {
      initializer: "initialize",
      kind: "uups"
    }
  );
  await myUpgradeableCollectible.waitForDeployment();

  const proxyAddress = await myUpgradeableCollectible.getAddress();
  console.log("MyUpgradeableCollectible deployed to (proxy):", proxyAddress);
  console.log("Implementation address:", await upgrades.erc1967.getImplementationAddress(proxyAddress));
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
```
To upgrade, you'd use `await upgrades.upgradeProxy(proxyAddress, NewImplementationContractFactory);`

## Best Practices

*   **Leverage OpenZeppelin:** Always start with OpenZeppelin Contracts for ERC-721, `Ownable`, `Pausable`, etc. They are rigorously audited and community-vetted.
*   **Immutable Metadata via IPFS:** Store your NFT metadata (images, traits) on a decentralized, immutable storage solution like IPFS. Your `baseURI` should point to an IPFS gateway or direct CID.
*   **Gas Optimization:** Minimize storage reads/writes, optimize loops, and use efficient data types. Test gas costs thoroughly.
*   **Thorough Testing:** Write comprehensive unit and integration tests for all functions, especially minting, transfers, and access control. Use Hardhat Network or Ganache for local testing.
*   **Access Control:** Implement robust access control (e.g., `Ownable`, `AccessControl`) for critical functions like `mint`, `setBaseURI`, `pause`. Avoid leaving these functions open to anyone.
*   **Event Emission:** Emit events for all significant state changes (e.g., `TokenMinted`, `BaseURIUpdated`). This makes off-chain indexing and monitoring easier.
*   **Consider Upgradability:** For projects with long lifecycles or evolving features, design your contract with upgradability (UUPS or Transparent Proxies) from the start. It's much harder to add later.
*   **Royalties (EIP-2981):** Implement the ERC-2981 royalty standard to ensure creators receive a percentage of secondary sales, if applicable for your project.

## Anti-Patterns

**Mutable Metadata On-Chain.** Storing full metadata directly on-chain or making `tokenURI` easily mutable by anyone undermines the immutability promise of NFTs. Instead, use IPFS for metadata and update the `baseURI` via an owner-only function only when absolutely necessary

## Review & Production Validation (2026-10-31)

- **Domain control (Contract engineering):** Check compiler, EVM fork, dependency versions, access control and storage-layout assumptions.
- **Independent validation:** Validate adversarial properties with tests and independent security review before deployment.
- **Time-sensitive details:** Treat fixed rates, thresholds, package versions, protocols and jurisdiction-specific rules in the examples above as illustrative unless reconfirmed against primary documentation.
- **Before relying on the result:** State inputs and assumptions; verify calculations and edge cases, and identify what has not been executed or tested.
