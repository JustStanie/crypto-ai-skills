---
name: solidity-patterns
description: 'Use when the user needs reusable solidity design patterns: compare factories,
  proxies, authorization and upgradeable storage designs.'
---

# Solidity Patterns — Web3 Development

You are an expert in Solidity smart contract design patterns for building secure and gas-efficient decentralized applications.

## Overview

Solidity is the primary language for Ethereum and EVM-compatible smart contracts. Writing correct, gas-efficient, and secure Solidity requires knowledge of established patterns that address common challenges such as access control, reentrancy, upgradeability, and state management. This guide covers patterns for Solidity 0.8.x and above.

## Core Philosophy

Solidity patterns exist because the EVM's execution model creates unique constraints: storage is expensive, execution is metered by gas, state changes are irreversible, and deployed code is immutable by default. Every pattern is a response to one of these constraints. The best Solidity code is simple, auditable, and follows established conventions because novelty in smart contract design is a liability, not an asset. Proven patterns reduce the surface area for bugs in code that manages real economic value.

## Anti-Patterns

*   **Custom Cryptographic Implementations.** Writing custom hashing, signature verification, or access control logic instead of using OpenZeppelin's audited implementations introduces unnecessary risk for zero benefit.

*   **Unbounded Dynamic Arrays in Storage.** Using dynamically-sized arrays that grow without bound creates gas griefing vectors where iteration costs become prohibitive. Cap sizes or use mappings with separate counters.

*   **Reentrancy Through State Reads.** Following checks-effects-interactions for state writes but reading state from external contracts (view functions on untrusted contracts) creates read-only reentrancy vulnerabilities.

*   **God Contract Architecture.** Placing all protocol logic in a single large contract instead of separating concerns into modular contracts makes auditing, testing, and upgrading exponentially harder.

*   **Event-Free State Mutations.** Modifying contract state without emitting corresponding events makes off-chain indexing, debugging, and UI synchronization impossible.

## Core Concepts

### Access Control

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/access/AccessControl.sol";

// Simple ownership
contract SimpleVault is Ownable {
    constructor() Ownable(msg.sender) {}

    function withdraw(uint256 amount) external onlyOwner {
        payable(owner()).transfer(amount);
    }
}

// Role-based access control
contract TokenSale is AccessControl {
    bytes32 public constant ADMIN_ROLE = keccak256("ADMIN_ROLE");
    bytes32 public constant MINTER_ROLE = keccak256("MINTER_ROLE");

    constructor() {
        _grantRole(DEFAULT_ADMIN_ROLE, msg.sender);
        _grantRole(ADMIN_ROLE, msg.sender);
    }

    function mint(address to, uint256 amount) external onlyRole(MINTER_ROLE) {
        // mint logic
    }

    function setPrice(uint256 newPrice) external onlyRole(ADMIN_ROLE) {
        // pricing logic
    }
}
```

### Reentrancy Protection

```solidity
import "@openzeppelin/contracts/utils/ReentrancyGuard.sol";

contract Vault is ReentrancyGuard {
    mapping(address => uint256) public balances;

    function deposit() external payable {
        balances[msg.sender] += msg.value;
    }

    // Checks-Effects-Interactions pattern with reentrancy guard
    function withdraw(uint256 amount) external nonReentrant {
        // Checks
        require(balances[msg.sender] >= amount, "Insufficient balance");

        // Effects (update state BEFORE external call)
        balances[msg.sender] -= amount;

        // Interactions (external call last)
        (bool success, ) = payable(msg.sender).call{value: amount}("");
        require(success, "Transfer failed");
    }
}
```

### Events and Indexed Parameters

```solidity
contract Marketplace {
    event ItemListed(
        uint256 indexed itemId,
        address indexed seller,
        uint256 price
    );
    event ItemSold(
        uint256 indexed itemId,
        address indexed buyer,
        address indexed seller,
        uint256 price
    );

    function listItem(uint256 itemId, uint256 price) external {
        // ... listing logic
        emit ItemListed(itemId, msg.sender, price);
    }
}
```

## Implementation Patterns

### Factory Pattern

```solidity
contract TokenFactory {
    address[] public deployedTokens;

    event TokenCreated(address indexed tokenAddress, string name, string symbol);

    function createToken(
        string calldata name,
        string calldata symbol,
        uint256 initialSupply
    ) external returns (address) {
        SimpleToken token = new SimpleToken(name, symbol, initialSupply, msg.sender);
        deployedTokens.push(address(token));
        emit TokenCreated(address(token), name, symbol);
        return address(token);
    }

    function getDeployedTokens() external view returns (address[] memory) {
        return deployedTokens;
    }
}
```

### Proxy / Upgradeable Pattern (UUPS)

```solidity
import "@openzeppelin/contracts-upgradeable/proxy/utils/Initializable.sol";
import "@openzeppelin/contracts-upgradeable/proxy/utils/UUPSUpgradeable.sol";
import "@openzeppelin/contracts-upgradeable/access/OwnableUpgradeable.sol";

contract VaultV1 is Initializable, UUPSUpgradeable, OwnableUpgradeable {
    uint256 public totalDeposits;

    /// @custom:oz-upgrades-unsafe-allow constructor
    constructor() {
        _disableInitializers();
    }

    function initialize() public initializer {
        __Ownable_init(msg.sender);
        __UUPSUpgradeable_init();
    }

    function deposit() external payable {
        totalDeposits += msg.value;
    }

    function _authorizeUpgrade(address newImplementation) internal override onlyOwner {}
}

// V2 adds new functionality without losing state
contract VaultV2 is VaultV1 {
    uint256 public withdrawalFee; // New state variable appended

    function setWithdrawalFee(uint256 fee) external onlyOwner {
        withdrawalFee = fee;
    }

    function withdraw(uint256 amount) external {
        uint256 fee = (amount * withdrawalFee) / 10000;
        totalDeposits -= amount;
        payable(msg.sender).transfer(amount - fee);
    }
}
```

### Pull Payment Pattern

```solidity
contract Auction {
    mapping(address => uint256) public pendingReturns;
    address public highestBidder;
    uint256 public highestBid;

    function bid() external payable {
        require(msg.value > highestBid, "Bid too low");

        if (highestBidder != address(0)) {
            // Don't send directly; record the pending return
            pendingReturns[highestBidder] += highestBid;
        }

        highestBidder = msg.sender;
        highestBid = msg.value;
    }

    // Users pull their own funds
    function withdrawBid() external {
        uint256 amount = pendingReturns[msg.sender];
        require(amount > 0, "Nothing to withdraw");

        pendingReturns[msg.sender] = 0;

        (bool success, ) = payable(msg.sender).call{value: amount}("");
        require(success, "Transfer failed");
    }
}
```

### Merkle Proof Allowlisting

```solidity
import "@openzeppelin/contracts/utils/cryptography/MerkleProof.sol";

contract AllowlistMint {
    bytes32 public merkleRoot;
    mapping(address => bool) public hasClaimed;

    constructor(bytes32 _merkleRoot) {
        merkleRoot = _merkleRoot;
    }

    function claim(bytes32[] calldata proof) external {
        require(!hasClaimed[msg.sender], "Already claimed");

        bytes32 leaf = keccak256(abi.encodePacked(msg.sender));
        require(MerkleProof.verify(proof, merkleRoot, leaf), "Invalid proof");

        hasClaimed[msg.sender] = true;
        // mint or distribute tokens
    }
}
```

### Gas-Efficient Patterns

```solidity
contract GasOptimized {
    // Use custom errors instead of require strings (saves ~50 gas per revert)
    error InsufficientBalance(uint256 requested, uint256 available);
    error Unauthorized();

    // Pack storage variables (each slot is 32 bytes)
    uint128 public totalSupply;   // slot 0 (first 16 bytes)
    uint64 public startTime;      // slot 0 (next 8 bytes)
    uint64 public endTime;        // slot 0 (next 8 bytes)
    address public owner;         // slot 1 (20 bytes)
    bool public paused;           // slot 1 (1 byte, packed with address)

    // Use unchecked blocks when overflow is impossible
    function increment(uint256 i) internal pure returns (uint256) {
        unchecked { return i + 1; } // Safe when bounded by array length
    }

    // Cache storage reads in memory
    function processItems(uint256[] calldata items) external {
        uint128 _totalSupply = totalSupply; // Single SLOAD
        for (uint256 i = 0; i < items.length; i = increment(i)) {
            _totalSupply += uint128(items[i]);
        }
        totalSupply = _totalSupply; // Single SSTORE
    }

    // Use calldata instead of memory for read-only arrays
    function sum(uint256[] calldata values) external pure returns (uint256 total) {
        for (uint256 i = 0; i < values.length; i = increment(i)) {
            total += values[i];
        }
    }
}
```

## Best Practices

1. **Use OpenZeppelin contracts** as battle-tested building blocks rather than writing security-critical primitives from scratch.
2. **Follow Checks-Effects-Interactions** ordering in every function that makes external calls.
3. **Use custom errors** over `require` strings for gas savings and structured error data.
4. **Pack storage variables** to minimize storage slots. Order struct members by size.
5. **Emit events for all state changes** to enable off-chain indexing and transparency.
6. **Use `immutable` and `constant`** for values set once at deploy time. They cost zero gas to read.
7. **Prefer `calldata` over `memory`** for function parameters that are not modified.
8. **Write NatSpec documentation** on all public and external functions for generated documentation and tooling support.

## Common Pitfalls

- **Reentrancy attacks.** External calls before state updates allow recursive exploitation. Always update state first.
- **Integer overflow in Solidity < 0.8.** Versions before 0.8 do not have built-in overflow checks. Use SafeMath or upgrade.
- **Unbounded loops over dynamic arrays.** Gas limits can cause transactions to fail. Use pagination or pull patterns.
- **Storage collisions in upgradeable contracts.** Never reorder or remove state variables between upgrades. Only append new ones.
- **Using `tx.origin` for authorization.** This is vulnerable to phishing attacks. Always use `msg.sender`.
- **Missing zero-address checks.** Validate that critical address parameters are not `address(0)`.
- **Front-running vulnerability.** Public mempool transactions can be observed and front-run. Use commit-reveal schemes or private mempools for sensitive operations.

## Review & Production Validation (2026-10-31)

- **Domain control (Contract engineering):** Check compiler, EVM fork, dependency versions, access control and storage-layout assumptions.
- **Independent validation:** Validate adversarial properties with tests and independent security review before deployment.
- **Time-sensitive details:** Treat fixed rates, thresholds, package versions, protocols and jurisdiction-specific rules in the examples above as illustrative unless reconfirmed against primary documentation.
- **Before relying on the result:** State inputs and assumptions; verify calculations and edge cases, and identify what has not been executed or tested.
