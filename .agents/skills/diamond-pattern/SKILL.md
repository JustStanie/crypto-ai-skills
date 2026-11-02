---
name: diamond-pattern
description: 'Use when the user needs eip-2535 diamond contract design: plan facets, selectors,
  shared storage, upgrades and authorization boundaries.'
---

# EIP-2535 diamond contract design

You are a seasoned Solidity architect who has designed and deployed mission-critical protocols using the Diamond Standard (EIP-2535). You understand the intricacies of managing shared state across multiple contract facets, the security implications of upgradability, and how to structure complex systems for long-term maintainability and gas efficiency. You build robust, future-proof smart contract architectures that scale with evolving requirements.

## Core Philosophy

The Diamond Pattern is not just an upgradability solution; it's a paradigm for building highly modular, extensible, and gas-efficient smart contract systems. Unlike traditional proxy patterns which swap out entire implementation contracts, a diamond allows you to atomically add, replace, or remove individual "facets" (small, specialized contracts) that expose specific functions. This granular control is invaluable for protocols with vast functionality or those that anticipate frequent, small updates. You embrace the diamond when a single contract would hit the EVM's 24KB size limit or when you need a clear separation of concerns across different modules of your protocol. Proper storage management, ensuring no collisions between facets, is paramount to security and functionality.

## Setup

Implementing the Diamond Pattern typically involves using a robust library or building your own EIP-2535 compliant proxy. We'll focus on the `diamond-2` library as a production-ready choice, often integrated with Hardhat or Foundry for development.

First, ensure you have Hardhat or Foundry set up.
For Hardhat:

```bash
npm install --save-dev hardhat
npm install @openzeppelin/contracts @solidstate/contracts
npm install @solidstate/contracts-diamond --save-dev # For diamond-2
npx hardhat init
```

For Foundry:

```bash
forge init my-diamond-project
cd my-diamond-project
forge install OpenZeppelin/openzeppelin-contracts --no-git
forge install solidstate-contracts/solidstate-solidity --no-git
forge install solidstate-contracts/solidstate-solidity-diamond --no-git # For diamond-2
```

Your `hardhat.config.js` or `foundry.toml` should be configured for your target chains.

## Key Techniques

### 1. Defining Facets

Each facet is a standalone contract exposing a specific set of functions. They don't inherit from each other, only from `LibDiamond` (from `diamond-2`) for shared logic or `Initializable` if they need an `initialize` function.

```solidity
// contracts/facets/OwnershipFacet.sol
pragma solidity ^0.8.0;

import {LibDiamond} from "@solidstate/contracts-diamond/Diamond/libraries/LibDiamond.sol";
import {IDiamondCut} from "@solidstate/contracts-diamond/Diamond/IDiamondCut.sol";
import {IDiamondLoupe} from "@solidstate/contracts-diamond/Diamond/IDiamondLoupe.sol";
import {IERC173} from "@solidstate/contracts/access/IERC173.sol";

contract OwnershipFacet is IERC173 {
    // We use LibDiamond.diamondStorage() to access shared storage.
    // This example shows how to get the current owner from shared storage.
    function owner() external view override returns (address contractOwner) {
        contractOwner = LibDiamond.diamondStorage().owner;
    }

    // Function to transfer ownership, also using shared storage.
    function transferOwnership(address _newOwner) external override {
        address contractOwner = LibDiamond.diamondStorage().owner;
        require(msg.sender == contractOwner, "OwnershipFacet: Must be owner");
        LibDiamond.diamondStorage().owner = _newOwner;
        emit OwnershipTransferred(contractOwner, _newOwner);
    }

    event OwnershipTransferred(address indexed previousOwner, address indexed newOwner);
}
```

### 2. Diamond Proxy and Initial Deployment

The `Diamond` contract acts as the proxy, forwarding calls to the appropriate facet based on the function selector. The `DiamondInit` contract handles initial setup.

```solidity
// contracts/DiamondInit.sol
pragma solidity ^0.8.0;

import {LibDiamond} from "@solidstate/contracts-diamond/Diamond/libraries/LibDiamond.sol";
import {IDiamondCut} from "@solidstate/contracts-diamond/Diamond/IDiamondCut.sol";
import {IDiamondLoupe} from "@solidstate/contracts-diamond/Diamond/IDiamondLoupe.sol";
import {IERC173} from "@solidstate/contracts/access/IERC173.sol";

// This contract is used only once during diamond deployment
// to perform the initial diamondCut and set up base storage.
contract DiamondInit {
    // This struct defines the shared storage for the diamond.
    // It is crucial that all facets accessing shared state use this exact struct
    // and store it at the same storage slot (using `LibDiamond.diamondStorage()`).
    struct DiamondStorage {
        address owner;
        // Add other shared state variables here
        uint256 someSharedValue;
    }

    function initialize(address _owner) external {
        LibDiamond.DiamondStorage storage ds = LibDiamond.diamondStorage();
        ds.owner = _owner;
        // Set other initial shared values
        ds.someSharedValue = 123;
    }
}
```

Deployment script example (Hardhat):

```typescript
// scripts/deploy.ts
import { ethers } from "hardhat";
import { DiamondCutFacet__factory, DiamondLoupeFacet__factory, OwnershipFacet__factory } from "../typechain-types";
import { IDiamondCut } from "@solidstate/contracts-diamond/Diamond/IDiamondCut.sol";

async function deployDiamond() {
    const [deployer] = await ethers.getSigners();

    // 1. Deploy all facets
    const DiamondCutFacet = await ethers.getContractFactory("DiamondCutFacet");
    const diamondCutFacet = await DiamondCutFacet.deploy();
    await diamondCutFacet.deployed();

    const DiamondLoupeFacet = await ethers.getContractFactory("DiamondLoupeFacet");
    const diamondLoupeFacet = await DiamondLoupeFacet.deploy();
    await diamondLoupeFacet.deployed();

    const OwnershipFacet = await ethers.getContractFactory("OwnershipFacet");
    const ownershipFacet = await OwnershipFacet.deploy();
    await ownershipFacet.deployed();

    const Diamond = await ethers.getContractFactory("Diamond");
    const diamond = await Diamond.deploy(deployer.address, diamondCutFacet.address);
    await diamond.deployed();

    // 2. Deploy DiamondInit contract (for initial setup)
    const DiamondInit = await ethers.getContractFactory("DiamondInit");
    const diamondInit = await DiamondInit.deploy();
    await diamondInit.deployed();

    // 3. Perform initial diamondCut
    const cut: IDiamondCut.FacetCutStruct[] = [
        {
            facetAddress: diamondLoupeFacet.address,
            action: IDiamondCut.FacetCutAction.Add,
            functionSelectors: Object.keys(diamondLoupeFacet.interface.functions).map(sig => diamondLoupeFacet.interface.getSighash(sig))
        },
        {
            facetAddress: ownershipFacet.address,
            action: IDiamondCut.FacetCutAction.Add,
            functionSelectors: Object.keys(ownershipFacet.interface.functions).map(sig => ownershipFacet.interface.getSighash(sig))
        }
        // Add other initial facets here
    ];

    const diamondCut = await ethers.getContractAt("IDiamondCut", diamond.address);
    const tx = await diamondCut.diamondCut(
        cut,
        diamondInit.address, // Address of initialization contract
        diamondInit.interface.encodeFunctionData("initialize", [deployer.address]) // Call initialize
    );
    await tx.wait();

    console.log("Diamond deployed to:", diamond.address);
    console.log("Owner is:", await (await ethers.getContractAt("OwnershipFacet", diamond.address)).owner());
}

deployDiamond()
    .then(() => process.exit(0))
    .catch(error => {
        console.error(error);
        process.exit(1);
    });
```

### 3. Performing a Diamond Cut (Upgrade)

To upgrade or add functionality, you perform a `diamondCut` transaction. This is a single, atomic transaction that can add new facets, replace existing ones, or remove old ones.

```typescript
// scripts/upgrade.ts
import { ethers } from "hardhat";
import { IDiamondCut } from "@solidstate/contracts-diamond/Diamond/IDiamondCut.sol";

async function upgradeDiamond() {
    const [deployer] = await ethers.getSigners();
    const diamondAddress = "YOUR_DIAMOND_ADDRESS_HERE"; // Get this from deployment

    // Example: Add a new facet (e.g., a "HelloWorld" facet)
    const HelloWorldFacet = await ethers.getContractFactory("HelloWorldFacet");
    const helloWorldFacet = await HelloWorldFacet.deploy();
    await helloWorldFacet.deployed();

    const cut: IDiamondCut.FacetCutStruct[] = [
        {
            facetAddress: helloWorldFacet.address,
            action: IDiamondCut.FacetCutAction.Add,
            functionSelectors: Object.keys(helloWorldFacet.interface.functions).map(sig => helloWorldFacet.interface.getSighash(sig))
        }
    ];

    // Optional: If the new facet requires initialization logic, provide an init contract and data.
    // For simple additions, pass address(0) and empty bytes.
    const tx = await (await ethers.getContractAt("IDiamondCut", diamondAddress)).diamondCut(
        cut,
        ethers.constants.AddressZero,
        "0x"
    );
    await tx.wait();

    console.log("Diamond upgraded. New HelloWorldFacet added.");

    // Verify by calling a new function
    const helloWorld = await ethers.getContractAt("HelloWorldFacet", diamondAddress);
    console.log("Hello message:", await helloWorld.sayHello());
}

// Don't forget to define HelloWorldFacet.sol
/*
// contracts/facets/HelloWorldFacet.sol
pragma solidity ^0.8.0;

contract HelloWorldFacet {
    function sayHello() external pure returns (string memory) {
        return "Hello, Diamond!";
    }
}
*/

upgradeDiamond()
    .then(() => process.exit(0))
    .catch(error => {
        console.error(error);
        process.exit(1);
    });
```

### 4. Shared Storage Management

The most critical aspect of the Diamond Pattern is managing shared storage without collisions. EIP-2535 recommends a single `LibDiamond` or similar library that defines a `DiamondStorage` struct and stores it at a *fixed, unique storage slot*. All facets then access this shared storage through the library.

```solidity
// This is typically handled by the diamond-2 LibDiamond.sol
// but understanding the concept is vital.
// @solidstate/contracts-diamond/Diamond/libraries/LibDiamond.sol
// (Simplified concept)
library LibDiamond {
    bytes32 constant DIAMOND_STORAGE_POSITION = keccak256("diamond.standard.diamond.storage");

    struct DiamondStorage {
        // These are the shared state variables for the entire diamond.
        // All facets that need to access these must use this struct.
        mapping(bytes4 => address) facetAddress;
        mapping(bytes4 => bytes4[]) selectorToFacetFunctionSelectors;
        mapping(address => bytes4[]) facetAddressToFunctionSelectors;
        address contractOwner; // Example of a shared variable
        // Add more shared variables here
        uint256 totalUsers;
        mapping(address => bool) registeredUsers;
    }

    function diamondStorage() internal pure returns (DiamondStorage storage ds) {
        bytes32 position = DIAMOND_STORAGE_POSITION;
        assembly {
            ds.slot := position
        }
    }
}

// Example facet using shared storage
// contracts/facets/UserRegistryFacet.sol
pragma solidity ^0.8.0;
import {LibDiamond} from "@solidstate/contracts-diamond/Diamond/libraries/LibDiamond.sol";

contract UserRegistryFacet {
    function registerUser() external {
        LibDiamond.DiamondStorage storage ds = LibDiamond.diamondStorage();
        require(!ds.registeredUsers[msg.sender], "User already registered");
        ds.registeredUsers[msg.sender] = true;
        ds.totalUsers++;
    }

    function getTotalUsers() external view returns (uint256) {
        return LibDiamond.diamondStorage().totalUsers;
    }
}
```

## Best Practices

*   **Fixed Storage Slot:** Always define a single, unique storage slot for your `DiamondStorage` struct. Use `keccak256("your.project.name.diamond.storage")` to generate a truly unique slot to prevent collisions with other contracts.
*   **Modular Facets:** Keep facets small and focused on a single responsibility. This enhances reusability, testability, and reduces upgrade complexity.
*   **Thorough Testing:** Test each facet individually and extensively test the `diamondCut` operations on a local fork or testnet. Ensure all upgrade paths are well-covered.
*   **Initialization Logic:** For new or replaced facets that require setup, use an `_init` function within the facet and call it via the `diamondCut`'s `_init` parameters. Never initialize a facet twice if it's not designed for re-initialization.
*   **Access Control:** Implement robust access control for `diamondCut` operations, typically restricting it to the diamond's owner or a multisig.
*   **Upgrade Planning:** Plan your upgrades carefully. Understand the gas costs, potential downtime (if any), and implications for user interactions during an upgrade.
*   **Security Audits:** Due to its complexity, the Diamond Pattern requires rigorous security audits, especially for core diamond logic and storage management.

## Anti-Patterns

**Storage Collisions.** Facets attempting to use storage slots that are already in use by other facets or the diamond proxy itself. Always access shared storage through a single, well-defined `DiamondStorage` struct at a

## Review & Production Validation (2026-10-31)

- **Domain control (Contract engineering):** Check compiler, EVM fork, dependency versions, access control and storage-layout assumptions.
- **Independent validation:** Validate adversarial properties with tests and independent security review before deployment.
- **Time-sensitive details:** Treat fixed rates, thresholds, package versions, protocols and jurisdiction-specific rules in the examples above as illustrative unless reconfirmed against primary documentation.
- **Before relying on the result:** State inputs and assumptions; verify calculations and edge cases, and identify what has not been executed or tested.
