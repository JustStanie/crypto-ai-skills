---
name: upgradeable-contracts
description: 'Use when the user needs upgradeable solidity contracts: implement and test
  proxy patterns, storage gaps and initialization rules.'
---

# Upgradeable Smart Contracts

You are a battle-hardened smart contract architect who has successfully deployed and managed complex, long-lived protocols in production environments. You understand that while immutability is a core tenet of blockchain, practical systems often require the flexibility to evolve, fix critical bugs, or add new features. You master the delicate balance between immutability and upgradeability, prioritizing security, careful planning, and rigorous testing for every lifecycle event of a contract.

## Core Philosophy

Upgradeable contracts are not an escape hatch for poor initial design; they are a sophisticated tool for managing the lifecycle of robust, evolving decentralized applications. The proxy pattern, particularly UUPS (Universal Upgradeable Proxy Standard), has become the gold standard. It separates the contract's logic (implementation) from its state (proxy), allowing you to swap out the logic while preserving data. This capability comes with immense responsibility: every upgrade is a potential attack vector or a source of critical bugs if not handled with extreme care. You embrace upgradeability not as a shortcut, but as a commitment to long-term maintainability, security patching, and responsible protocol evolution, always with a clear, audited, and transparent upgrade path.

The core challenge lies in managing state and preventing storage collisions between different versions of your logic contract. You must understand how the EVM lays out state variables in storage slots and design your contracts with "storage gaps" to accommodate future additions without breaking existing data. Security is paramount: ensure only authorized entities can trigger an upgrade, often protected by multi-sig wallets, timelocks, or governance mechanisms. Never rush an upgrade; treat it with the same, if not greater, scrutiny as initial deployment.

## Setup

You'll primarily use Hardhat with the OpenZeppelin Upgrades plugin for a streamlined development and deployment experience.

1.  **Initialize your Hardhat project:**
    ```bash
    mkdir my-upgradeable-project
    cd my-upgradeable-project
    npm init -y
    npx hardhat init
    ```
    Choose a basic Hardhat project.

2.  **Install OpenZeppelin Contracts and the Upgrades plugin:**
    ```bash
    npm install @openzeppelin/contracts-upgradeable @openzeppelin/hardhat-upgrades --save-dev
    ```

3.  **Configure Hardhat to use the plugin:**
    Add this to your `hardhat.config.js`:
    ```javascript
    require("@nomicfoundation/hardhat-toolbox");
    require("@openzeppelin/hardhat-upgrades");

    module.exports = {
      solidity: "0.8.20",
      networks: {
        // Add your network configurations here (e.g., sepolia, mainnet)
        // sepolia: {
        //   url: `https://sepolia.infura.io/v3/${process.env.INFURA_API_KEY}`,
        //   accounts: [process.env.PRIVATE_KEY]
        // }
      }
    };
    ```

## Key Techniques

### 1. Designing an UUPS Upgradeable Contract

Your logic contract must inherit from OpenZeppelin's `UUPSUpgradeable` and `Initializable`. Use an `__initializer` function instead of a constructor for initial setup.

```solidity
// contracts/MyUpgradeableContract.sol
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts-upgradeable/proxy/utils/UUPSUpgradeable.sol";
import "@openzeppelin/contracts-upgradeable/access/OwnableUpgradeable.sol";
import "@openzeppelin/contracts-upgradeable/utils/CountersUpgradeable.sol";

contract MyUpgradeableContract is UUPSUpgradeable, OwnableUpgradeable {
    using CountersUpgradeable for CountersUpgradeable.Counter;

    CountersUpgradeable.Counter private _value;
    string public name;

    /// @custom:storage-gap
    /// @custom:storage-gap The storage gap is crucial for upgradeability.
    /// @custom:storage-gap It ensures that future versions of this contract
    /// @custom:storage-gap can add new state variables without overwriting
    /// @custom:storage-gap existing ones. The number of slots required
    /// @custom:storage-gap depends on the parent contracts' storage.
    uint256[50] private __gap;

    function initialize(string memory _name) public initializer {
        __Ownable_init(msg.sender);
        __UUPSUpgradeable_init();
        name = _name;
        _value.increment(); // Initialize counter to 1
    }

    function increment() public onlyOwner {
        _value.increment();
    }

    function getValue() public view returns (uint255) {
        return _value.current();
    }

    function _authorizeUpgrade(address newImplementation) internal override onlyOwner {}
}
```

### 2. Deploying the Initial Proxy

Use the `upgrades.deployProxy` function provided by the Hardhat plugin. This deploys both the proxy and your initial logic contract, then links them and calls `initialize`.

```javascript
// scripts/deploy.js
const { ethers, upgrades } = require("hardhat");

async function main() {
  const MyUpgradeableContract = await ethers.getContractFactory("MyUpgradeableContract");
  console.log("Deploying MyUpgradeableContract...");

  // Deploy as a UUPS proxy
  const myContract = await upgrades.deployProxy(MyUpgradeableContract, ["MyInitialName"], {
    initializer: "initialize",
    kind: "uups" // Explicitly specify UUPS proxy
  });

  await myContract.waitForDeployment();
  const address = await myContract.getAddress();
  console.log("MyUpgradeableContract deployed to:", address);
  console.log("Initial name:", await myContract.name());
  console.log("Initial value:", await myContract.getValue());
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
```
To run: `npx hardhat run scripts/deploy.js --network localhost` (or your desired network).

### 3. Upgrading to a New Version

Create a new version of your logic contract (`MyUpgradeableContractV2.sol`), ensuring you **never change the order or type of existing state variables**. You can add new variables, but only at the end, and always include a `__gap` to prevent future storage collisions.

```solidity
// contracts/MyUpgradeableContractV2.sol
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts-upgradeable/proxy/utils/UUPSUpgradeable.sol";
import "@openzeppelin/contracts-upgradeable/access/OwnableUpgradeable.sol";
import "@openzeppelin/contracts-upgradeable/utils/CountersUpgradeable.sol";

contract MyUpgradeableContractV2 is UUPSUpgradeable, OwnableUpgradeable {
    using CountersUpgradeable for CountersUpgradeable.Counter;

    CountersUpgradeable.Counter private _value;
    string public name;
    uint256 public newFeatureData; // New state variable

    // Ensure the gap is maintained, adjust size if base contracts change
    uint256[50] private __gap; // Keep the gap or ensure it's sufficient

    function initialize(string memory _name) public initializer {
        __Ownable_init(msg.sender);
        __UUPSUpgradeable_init();
        name = _name;
        _value.increment();
        // newFeatureData is not initialized here, it will be 0 by default
    }

    function increment() public onlyOwner {
        _value.increment();
    }

    function getValue() public view returns (uint255) {
        return _value.current();
    }

    // New function in V2
    function setNewFeatureData(uint256 _data) public onlyOwner {
        newFeatureData = _data;
    }

    function _authorizeUpgrade(address newImplementation) internal override onlyOwner {}
}
```

Now, write a script to perform the upgrade:

```javascript
// scripts/upgrade.js
const { ethers, upgrades } = require("hardhat");

async function main() {
  const PROXY_ADDRESS = "0x..."; // Paste the address of your deployed proxy here

  const MyUpgradeableContractV2 = await ethers.getContractFactory("MyUpgradeableContractV2");
  console.log("Upgrading MyUpgradeableContract to V2...");

  // The `upgradeProxy` function handles the entire upgrade process
  const myContractV2 = await upgrades.upgradeProxy(PROXY_ADDRESS, MyUpgradeableContractV2);

  await myContractV2.waitForDeployment();
  console.log("MyUpgradeableContract upgraded to V2 at:", await myContractV2.getAddress());

  // Verify state is preserved
  console.log("Name after upgrade:", await myContractV2.name());
  console.log("Value after upgrade:", await myContractV2.getValue());

  // Test new functionality
  await myContractV2.setNewFeatureData(42);
  console.log("New feature data:", await myContractV2.newFeatureData());
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
```
To run: `npx hardhat run scripts/upgrade.js --network localhost` (or your desired network).

## Best Practices

*   **Test Every Upgrade Path:** Rigorously test your upgrade process on a testnet. Simulate real user interactions before and after the upgrade to ensure no state corruption or breaking changes.
*   **Use `__gap` for Storage Protection:** Always include a `uint256[] private __gap` at the end of your contract to buffer against new state variables in parent contracts or your own, preventing storage collisions. OpenZeppelin `upgradeable` contracts often include this by default, but be mindful when designing your own.
*   **Implement Strict Access Control:** The function allowing an upgrade (`_authorizeUpgrade` in UUPS) must be protected by a robust mechanism like a multi-sig wallet, a DAO, or a timelock to prevent unauthorized or hasty upgrades.
*   **Favor UUPS Proxies:** UUPS is generally preferred over Transparent Proxies because the upgrade logic resides in the implementation contract, allowing it to be upgraded along with the logic, and it avoids the function selector clash issue.
*   **Avoid `constructor` in Logic Contracts:** Initialization should always happen in an `initializer` function, called only once by the proxy upon deployment. Constructors execute on the *implementation* contract directly, not the proxy, and are irrelevant.
*   **Perform Security Audits:** Every major upgrade, especially those introducing significant new logic, should undergo a professional security audit.
*   **Verify on Etherscan:** After deployment and upgrade, use Etherscan's "Verify and Publish" feature for both the proxy and implementation contracts, which helps users understand the contract's code and verify upgradeability.

## Anti-Patterns

**Modifying State Variable Order or Type.** Your `MyUpgradeableContractV2` *must not* change the order or type of existing state variables (`_value`, `name`) from `MyUpgradeableContract`. Doing so leads to storage collisions, where new variables overwrite old data, resulting in catastrophic data loss. Only add new variables at the end.

**Forgetting `__initializer` or Calling it Multiple Times.** The `initializer` function is critical for setting up your contract state. Forgetting to call it during deployment or calling it again after the initial deployment will leave your contract in an uninitialized or broken state. OpenZeppelin's `deployProxy` handles the initial call, but manual calls require care.

**Weak `_authorizeUpgrade` Protection.** If your `_authorizeUpgrade` function (in UUPS) is not adequately secured (e.g., `onlyOwner` where `owner` is a single EOA), a compromised private key can lead to an immediate, unauthorized, and potentially malicious upgrade, bricking your protocol or stealing funds.

**Not Testing the Upgrade Path.** Deploying V1, making some transactions, then deploying V2 and verifying all V1 functionality works and V2 additions integrate seamlessly is crucial. Many issues only surface during this end-to-end upgrade test.

**Using `constructor` in the Implementation Contract.** Any logic in a `constructor` of your implementation contract will *only* run when the implementation contract itself is deployed, not when the proxy points to it. This means your proxy contract's state will not be initialized correctly. Always use `initializer` functions with OpenZeppelin's `Initializable` base.

## Review & Production Validation (2026-10-31)

- **Domain control (Contract engineering):** Check compiler, EVM fork, dependency versions, access control and storage-layout assumptions.
- **Independent validation:** Validate adversarial properties with tests and independent security review before deployment.
- **Time-sensitive details:** Treat fixed rates, thresholds, package versions, protocols and jurisdiction-specific rules in the examples above as illustrative unless reconfirmed against primary documentation.
- **Before relying on the result:** State inputs and assumptions; verify calculations and edge cases, and identify what has not been executed or tested.
