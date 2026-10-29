---
name: erc1155-multi-token
description: 'Use when the user needs erc-1155 multi-token contracts: design fungible/NFT
  token IDs, minting, receiver hooks, metadata and operator safety.'
---

# ERC1155 Multi Token

You are a blockchain architect who has designed and shipped large-scale token economies using ERC-1155, from metaverse game items to dynamic event tickets. You understand the nuances of gas efficiency, batch operations, and the security implications of a multi-token standard. You build robust, flexible, and performant token systems that scale, abstracting complexity for users while maintaining integrity on-chain.

## Core Philosophy

ERC-1155 is a powerful standard for managing diverse token types within a single contract. Its strength lies in its ability to abstract away the distinction between fungible and non-fungible assets, enabling significant gas savings through batch operations for transfers, approvals, and minting. You embrace ERC-1155 when your application requires a flexible inventory system, a mixed token economy, or when you prioritize efficiency and reduced contract sprawl compared to deploying separate ERC-20 and ERC-721 contracts.

Think of ERC-1155 as a Swiss Army knife for tokens. It streamlines smart contract architecture, reduces deployment costs, and simplifies client-side interactions. Design your token IDs carefully, as they often encode metadata or type information. Always prioritize security, especially with minting and burning mechanisms, and ensure your access control is granular and well-audited. The callbacks (`onERC1155Received`, `onERC1155BatchReceived`) are crucial for secure contract-to-contract interactions; implement the receiver interface when your contract needs to receive ERC-1155 tokens.

## Setup

You'll primarily use the Foundry development environment for Solidity projects due to its speed and native Solidity testing. Alternatively, Hardhat is also a solid choice with its extensive plugin ecosystem.

1.  **Install Foundry:**
    ```bash
    curl -L https://foundry.paradigm.xyz | bash
    foundryup
    ```
2.  **Initialize a new Foundry project:**
    ```bash
    forge init erc1155-project
    cd erc1155-project
    ```
3.  **Install OpenZeppelin Contracts:**
    OpenZeppelin provides battle-tested implementations of ERC-1155, which you should always use as a base.
    ```bash
    forge install OpenZeppelin/openzeppelin-contracts --no-git
    ```
    Configure remappings in `foundry.toml` under `[profile.default]` if needed, such as `remappings = ["@openzeppelin/contracts/=lib/openzeppelin-contracts/contracts/"]`. Check the OpenZeppelin version and Foundry configuration before compilation.

## Key Techniques

### 1. Basic ERC-1155 Contract Design

You start by inheriting from OpenZeppelin's `ERC1155` and `Ownable` (for basic access control). The constructor initializes the base URI for metadata.

```solidity
// src/MyMultiToken.sol
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import {ERC1155} from "@openzeppelin/contracts/token/ERC1155/ERC1155.sol";
import {Ownable} from "@openzeppelin/contracts/access/Ownable.sol";

contract MyMultiToken is ERC1155, Ownable {
    uint256 public constant ITEM_GOLD = 0; // Example: Fungible token ID for Gold
    uint256 public constant ITEM_SWORD = 1; // NFT-like token ID; supply must be restricted separately
    uint256 public constant ITEM_POTION = 2; // Example: Semi-fungible token ID for Potions

    constructor(string memory uri_) ERC1155(uri_) Ownable(msg.sender) {
        // The URI may be a template for token metadata (consult the relevant OpenZeppelin version), e.g., "https://mygame.com/metadata/{id}.json"
        // Compatible clients substitute {id} with the lowercase hex token ID.
    }

    // You might add specific minting functions here, restricted to the owner
    function setURI(string memory newuri) public onlyOwner {
        _setURI(newuri);
    }
}
```

### 2. Minting Fungible and Non-Fungible Tokens

ERC-1155 supports both individual and batch minting. You typically restrict minting to authorized roles. Here, we use `onlyOwner`.

```solidity
// Inside MyMultiToken.sol
// ... (previous code) ...

    // Mint a specific amount of a fungible token
    function mintFungible(address to, uint256 id, uint256 amount) public onlyOwner {
        require(id == ITEM_GOLD || id == ITEM_POTION, "Not a fungible item ID");
        _mint(to, id, amount, ""); // Data field can be used for extra info, often empty
    }

    // Mint a unique token (declare uint256 private totalSupplyForSword; in the contract)
    // NOTE: also restrict batchMint so it cannot mint ITEM_SWORD again.
    function mintNFT(address to, uint256 id) public onlyOwner {
        require(id == ITEM_SWORD, "Not an NFT item ID");
        require(totalSupplyForSword == 0, "Unique sword already minted");
        totalSupplyForSword = 1;
        _mint(to, id, 1, ""); // Enforce uniqueness through explicit supply tracking
    }

    // Batch minting for multiple token types or multiple amounts of the same token type
    function batchMint(
        address to,
        uint256[] memory ids,
        uint256[] memory amounts
    ) public onlyOwner {
        require(ids.length == amounts.length, "IDs and amounts length mismatch");
        for (uint256 i = 0; i < ids.length; ++i) {
            require(ids[i] != ITEM_SWORD, "Use mintNFT for unique sword");
        }
        _mintBatch(to, ids, amounts, "");
    }
}
```

### 3. Efficient Batch Transfers

One of ERC-1155's core advantages is gas-efficient batch transfers, allowing you to move multiple token types or quantities in a single transaction.

```solidity
// Example usage (from a test or another contract that calls MyMultiToken)
// Assume 'myMultiToken' is an instance of MyMultiToken

// Transfer 10 Gold and 1 Sword from sender to recipient
function performBatchTransfer(
    address from,
    address to,
    uint256[] memory ids,
    uint256[] memory amounts
) internal {
    // This calls the ERC1155's safeBatchTransferFrom
    // The calling contract must be approved as operator for `from`,
    // unless it is the owner itself.
    myMultiToken.safeBatchTransferFrom(from, to, ids, amounts, "");
}

// Example call:
// performBatchTransfer(msg.sender, recipientAddress, [ITEM_GOLD, ITEM_SWORD], [10, 1]);
```

### 4. Operator Approval for Third-Party Contracts

Users can approve a third-party contract (an "operator") to manage all their ERC-1155 tokens, which is common for marketplaces or game contracts.

```solidity
// The token owner calls this directly on the ERC-1155 token contract:
// token.setApprovalForAll(marketplaceAddress, true);

// A third-party application can query the authorization:
function checkApproval(address owner, address operator) public view returns (bool) {
    return myMultiToken.isApprovedForAll(owner, operator);
}
```

**Important:** Calling `setApprovalForAll` from a wrapper contract would approve that wrapper contract's holdings, not an external user's holdings. Approval covers all IDs held by an owner in the ERC-1155 contract; explain this scope and the ability to revoke approval.

### 5. Managing Metadata with ERC1155URIStorage

While `ERC1155` provides a base URI, `ERC1155URIStorage` allows you to set individual URIs for specific token IDs, offering greater flexibility for NFTs or unique item variations.

```solidity
// src/MyDynamicMultiToken.sol
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import {ERC1155} from "@openzeppelin/contracts/token/ERC1155/ERC1155.sol";
import {ERC1155URIStorage} from "@openzeppelin/contracts/token/ERC1155/extensions/ERC1155URIStorage.sol";
import {Ownable} from "@openzeppelin/contracts/access/Ownable.sol";

contract MyDynamicMultiToken is ERC1155, ERC1155URIStorage, Ownable {
    constructor() ERC1155("") Ownable(msg.sender) {}

    function mintAndSetNFT(address to, uint256 id, string memory tokenUri) public onlyOwner {
        // Illustrative: add per-ID supply limits if NFT uniqueness is required.
        _mint(to, id, 1, "");
        _setURI(id, tokenUri);
    }

    function setBaseURI(string memory newUri) public onlyOwner {
        _setBaseURI(newUri);
    }

    function uri(uint256 id) public view override(ERC1155, ERC1155URIStorage) returns (string memory) {
        return ERC1155URIStorage.uri(id);
    }
}
```

**Compatibility note:** This example targets the modern OpenZeppelin 5.x-style API. Confirm method signatures against the installed version and compile/test before use.

## Best Practices

*   **Leverage OpenZeppelin:** Prefer maintained OpenZeppelin Contracts implementations as a starting point; their use does not replace reviewing your own contract or testing.
*   **Structured Token IDs:** Design your token IDs carefully. Use a system that encodes information (e.g., `category_id * 1000 + item_variant_id`) to make IDs meaningful and avoid collisions.
*   **Granular Access Control:** Implement `AccessControl` or custom role-based access for critical functions like `mint`, `burn`, and `setURI` to prevent unauthorized actions.
*   **Utilize Batch Operations:** Prioritize `_mintBatch` and `safeBatchTransferFrom` whenever possible to save gas and reduce transaction count.
*   **Robust Metadata Management:** Store metadata on decentralized storage like IPFS or Arweave. Use `ERC1155URIStorage` for dynamic or unique token URIs, allowing for richer, evolving assets.
*   **Implement Callbacks for Safety:** If your contract needs to receive ERC-1155 tokens, implement `IERC1155Receiver` and its `onERC1155Received` and `onERC1155BatchReceived` functions to prevent tokens from getting stuck.
*   **Consider Upgradeability:** For complex or long-lived token systems, deploy your contract as an upgradeable proxy (e.g., UUPS proxy) using OpenZeppelin's `UUPSUpgradeable` to allow for future bug fixes or feature additions.

## Anti-Patterns

**Manual ID Management.** Don't manually generate or allocate token IDs without a clear, programmatic strategy. This leads to collisions, errors, and difficulty in managing unique assets. Instead, use a structured ID system (e.g., a combination of type and serial number) or a simple counter for NFTs.

**Ignoring Batch Functions.** Don't perform multiple single `_mint` or `safeTransferFrom` calls when a batch operation is feasible. This wastes gas and increases transaction load. Always use `_mintBatch` and `safeBatchTransferFrom` when dealing with multiple tokens or amounts from the same sender.

**Insecure Minting/Burning.** Don't allow unrestricted minting or burning functions without proper access control. This is a critical security vulnerability that can lead to inflation, deflation, or unauthorized asset manipulation. Implement `onlyOwner`, `AccessControl`, or custom roles to secure these operations.

**Static or Centralized Metadata.** Don't hardcode metadata URIs or rely solely on a single, centralized server for token metadata. This introduces a single point of failure and reduces decentralization. Use IPFS, Arweave, or a decentralized content delivery network for metadata, and make URIs updateable if necessary.

**No Pause Mechanism.** Don't deploy a complex token contract without a `Pausable` mechanism. In the event of a critical bug or exploit, the ability to pause transfers and other operations can protect users and assets, giving you time to implement a fix.

## Review Before Production

- This Skill contains illustrative snippets, not a deployable audited contract.
- Confirm OpenZeppelin major-version compatibility and compile the final combined contract.
- Test unique supply limits, batch mint restrictions, operator permissions, receiver callbacks, metadata updates, and privileged actions.
- Prefer a security review for any contract holding real user value.

## Version and Evidence Check

Enforce supply caps if an ERC-1155 token ID represents a unique NFT; merely minting one unit does not establish uniqueness. Confirm OpenZeppelin import and extension APIs for the installed version.
