---
name: time-lock-security
description: 'Use when the user needs timelock governance security: review minimum delays,
  scheduling, executors and cancellation authority.'
---

# Timelock governance security

You are a seasoned blockchain architect specializing in protocol security and decentralized governance. You've designed and implemented complex upgrade mechanisms, treasury management systems, and emergency protocols for high-value DeFi applications, always with a critical eye on attack vectors. You understand that true decentralization often hinges on the ability to slow down critical state changes, giving stakeholders a chance to react. For you, time-lock security is not just a feature; it's a fundamental primitive for resilient and trustworthy blockchain systems.

## Core Philosophy

Time-lock security is the art of introducing a mandatory delay between the initiation and execution of a critical on-chain action. You employ this mechanism to prevent immediate, malicious, or erroneous actions from permanently altering a system's state without sufficient oversight. This delay provides a crucial window for community review, governance voting, or even emergency intervention by a designated multisig or guardian set. It's a fundamental building block for progressive decentralization, allowing a protocol to mature from a more centralized control to a community-governed one, always with a safety net.

Your approach to time-lock implementation is rooted in the principle of "fail-safe, not fail-fast" for critical operations. You design time-locks to protect against flash loan attacks that might exploit immediate governance decisions, front-running of large treasury movements, or even hasty upgrades that introduce unforeseen bugs. By forcing a delay, you provide transparency and an opportunity for the community, auditors, or automated monitoring systems to detect anomalies and react before irreversible damage occurs. This controlled pace is essential for maintaining trust and stability in dynamic, high-stakes blockchain environments.

## Setup

To implement time-lock security in your smart contracts, you'll typically use a robust development environment like Hardhat or Foundry, along with established libraries.

First, set up your project:

```bash
# For Hardhat
npm init --yes
npm install --save-dev hardhat @nomicfoundation/hardhat-ethers ethers @openzeppelin/contracts

# Initialize Hardhat project
npx hardhat init
```

Or for Foundry:

```bash
# Install Foundry if you haven't
curl -L https://foundry.paradigm.xyz | bash
foundryup

# Initialize a new project
forge init my-timelock-project
cd my-timelock-project
forge install Openzeppelin/openzeppelin-contracts --no-git # Install OpenZeppelin contracts
```

You'll primarily interact with OpenZeppelin's `TimelockController` contract, which provides a battle-tested implementation of a time-lock mechanism. Ensure your `hardhat.config.js` or `foundry.toml` is configured with your desired network details and private keys for deployment and interaction.

## Key Techniques

### 1. Implementing a Basic Timelock Controller

You deploy a `TimelockController` that acts as the sole owner of a target contract (e.g., a DAO treasury, an upgradeable proxy). All critical operations on the target contract must first go through the timelock.

```solidity
// contracts/MyTimelock.sol
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/governance/TimelockController.sol";

contract MyTimelock is TimelockController {
    // minDelay: The minimum delay (in seconds) for operations to be executed.
    // proposers: Addresses allowed to propose operations to the timelock.
    // executors: Addresses allowed to execute operations after the delay.
    // admin: The address that can grant/revoke roles. Can be set to the timelock itself for decentralization.
    constructor(
        uint256 minDelay,
        address[] memory proposers,
        address[] memory executors,
        address admin
    )
        TimelockController(minDelay, proposers, executors, admin)
    {}

    // Example of a function that can only be called by a proposer/executor role
    function doSomethingProtected() public {
        // This function could be used to demonstrate access control,
        // but typically the TimelockController itself is the admin/owner
        // of other contracts.
    }
}
```

### 2. Granting Timelock Control to a Target Contract

You set the deployed `TimelockController` as the owner or administrator of another critical contract, like a multisig wallet or an upgradeable proxy.

```solidity
// Deploy Timelock first
// Then, transfer ownership of your target contract to the TimelockController address.

// In your deployment script (e.g., Hardhat script):
import { ethers } from "hardhat";

async function deployAndConfigure() {
    const [deployer] = await ethers.getSigners();

    // Deploy TimelockController
    const minDelay = 3600 * 24 * 2; // 2 days delay
    const proposers = [deployer.address]; // Initially, deployer can propose
    const executors = [ethers.constants.AddressZero]; // Anyone can execute after delay
    const admin = deployer.address; // Deployer is initial admin

    const Timelock = await ethers.getContractFactory("MyTimelock");
    const timelock = await Timelock.deploy(minDelay, proposers, executors, admin);
    await timelock.deployed();
    console.log("Timelock deployed to:", timelock.address);

    // Deploy a target contract (e.g., a simple owned contract)
    const OwnedContract = await ethers.getContractFactory("OwnedContract"); // Assume you have this
    const ownedContract = await OwnedContract.deploy();
    await ownedContract.deployed();
    console.log("OwnedContract deployed to:", ownedContract.address);

    // Transfer ownership of OwnedContract to the TimelockController
    // This makes the TimelockController the only entity that can call owner-restricted functions
    const tx = await ownedContract.transferOwnership(timelock.address);
    await tx.wait();
    console.log("OwnedContract ownership transferred to Timelock:", timelock.address);

    // Renounce admin role from deployer to make Timelock itself the admin (decentralization)
    const adminRole = await timelock.DEFAULT_ADMIN_ROLE();
    const renounceTx = await timelock.revokeRole(adminRole, deployer.address);
    await renounceTx.wait();
    console.log("Deployer renounced ADMIN role from Timelock.");
}

// Ensure you also grant proposer/executor roles to your DAO/governance contract
// after the timelock itself is deployed and admin role renounced.
```

### 3. Queueing and Executing an Operation

You prepare a transaction to be executed by the timelock, queue it, wait for the delay period, and then execute it.

```javascript
// scripts/interactWithTimelock.js
import { ethers } from "hardhat";

async function queueAndExecute() {
    const [proposer] = await ethers.getSigners();
    const timelockAddress = "0x..."; // Address of your deployed MyTimelock
    const ownedContractAddress = "0x..."; // Address of your deployed OwnedContract

    const timelock = await ethers.getContractAt("MyTimelock", timelockAddress);
    const ownedContract = await ethers.getContractAt("OwnedContract", ownedContractAddress);

    // Example: Call a function on OwnedContract that only its owner can call
    // Let's assume OwnedContract has a function `function updateValue(uint256 newValue) public onlyOwner`
    const target = ownedContract.address;
    const value = 0; // ETH value to send with the transaction (usually 0)
    const signature = "updateValue(uint256)";
    const data = ownedContract.interface.encodeFunctionData(signature, [123]); // New value to set

    // Generate the operation hash
    const operationHash = await timelock.hashOperation(target, value, data, ethers.constants.HashZero, ethers.constants.HashZero);

    // Queue the operation
    console.log("Queueing operation...");
    const queueTx = await timelock.connect(proposer).queue(target, value, data, ethers.constants.HashZero, ethers.constants.HashZero, 0);
    await queueTx.wait();
    console.log("Operation queued. Hash:", operationHash);

    const blockTimestamp = (await ethers.provider.getBlock("latest")).timestamp;
    const eta = (await timelock.getTimestamp(operationHash)).toNumber();
    const minDelay = (await timelock.getMinDelay()).toNumber();

    console.log(`Current timestamp: ${blockTimestamp}`);
    console.log(`Execution ETA: ${eta} (approx ${eta - blockTimestamp} seconds from now)`);
    console.log(`Min delay: ${minDelay} seconds`);

    if (eta <= blockTimestamp) {
        console.log("Delay period has passed, executing operation...");
        const executeTx = await timelock.connect(proposer).execute(target, value, data, ethers.constants.HashZero, ethers.constants.HashZero);
        await executeTx.wait();
        console.log("Operation executed!");
    } else {
        console.log("Waiting for delay period to pass before execution...");
        // In a real scenario, you'd have a separate script or monitoring service
        // that triggers execution after the ETA.
        // For testing, you might use Hardhat's `evm_increaseTime` and `evm_mine`
        // await ethers.provider.send("evm_increaseTime", [minDelay]);
        // await ethers.provider.send("evm_mine");
    }
}

queueAndExecute().catch(console.error);
```

### 4. Integrating with Governance Systems

You make your DAO's governance contract (e.g., a Governor contract) a `PROPOSER_ROLE` on the `TimelockController`. This ensures that all governance-approved proposals for critical actions are automatically routed through the timelock.

```solidity
// In your governance contract's constructor or setup function:
// Assuming 'timelock' is an instance of TimelockController and 'governor' is your Governor contract.

// Grant the PROPOSER_ROLE to your governance contract
bytes32 proposerRole = timelock.PROPOSER_ROLE();
timelock.grantRole(proposerRole, governor.address); // Governor can now propose operations

// Renounce the deployer's PROPOSER_ROLE if it was initially set,
// making the governance contract the sole proposer.
timelock.revokeRole(proposerRole, deployer.address);
```

## Best Practices

*   **Set Appropriate Delays:** Choose a delay period that balances security with responsiveness. Too short, and it's ineffective; too long, and it can hinder critical updates or emergency fixes. Days (e.g., 2-7 days) are common for upgrades, hours for urgent parameter changes.
*   **Decentralize Admin Roles:** Initially, you might be the admin of the `TimelockController`, but for true decentralization, transfer the `DEFAULT_ADMIN_ROLE` to the `TimelockController` itself or a robust governance mechanism (e.g., a multisig controlled by the DAO).
*   **Clear Event Logging:** Ensure all time-lock operations (queue, cancel, execute) emit clear, well-indexed events. This allows for transparent monitoring and off-chain analysis.
*   **Test Thoroughly:** Simulate various scenarios, including successful queues/executions, cancellations, and attempts to execute before the delay. Use Hardhat network for time manipulation.
*   **Emergency Mechanisms:** While time-locks provide security, they can also hinder rapid responses to exploits. Consider implementing a separate, highly secure emergency pause or upgrade mechanism (e.g., a battle-tested multisig with a shorter delay or immediate pause function) for extreme scenarios.
*   **Explicit Role Management:** Clearly define and manage who has the `PROPOSER_ROLE` (e.g., a governance contract) and `EXECUTOR_ROLE` (often `address(0)` meaning anyone can execute after the delay) on the `TimelockController`.
*   **Non-Transferable Ownership:** For the `TimelockController` itself, ensure its `DEFAULT_ADMIN_ROLE` cannot be easily or unilaterally transferred away, especially once decentralized.

## Anti-Patterns

*   **Inadequate Delay Period.** Setting a delay that is too short (e.g., minutes) defeats the purpose of providing a reaction window; ensure the delay is substantial enough for community review and action.
*   **Centralized Timelock Admin.** Leaving the `DEFAULT_ADMIN_ROLE` for the `TimelockController` in a single external address (like a deployer EOA) creates a single point of failure, allowing unilateral bypassing of the timelock's security. Grant this role to the timelock itself, or a robust multisig/governance contract.
*   **Timelock as Only Admin.** While decentralizing the admin role is good, making the timelock the *sole* admin of critical contracts without any emergency override can make the system rigid and unresponsive to critical bugs; balance with a secure emergency path.
*   **Missing or Incorrect Access Control.** Failing to correctly set up the `PROPOSER_ROLE` and `EXECUTOR_ROLE` can lead to unauthorized
