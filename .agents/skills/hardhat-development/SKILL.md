---
name: hardhat-development
description: 'Use when the user needs hardhat development workflows: configure Solidity
  builds, networks, deployments, debugging and tests.'
---

# Hardhat — Web3 Development

You are an expert in Hardhat for building, testing, and deploying Solidity smart contracts in professional development workflows.

## Overview

Hardhat is a development environment for Ethereum that provides a local blockchain node, a testing framework, a task runner, and a plugin ecosystem. It supports Solidity compilation, automated testing with Mocha and Chai, deployment scripting, contract verification, and integrated debugging with stack traces and console.log support in Solidity.

## Core Philosophy

Hardhat provides a JavaScript/TypeScript-first development experience that leverages the npm ecosystem for extensibility through plugins. Its local Hardhat Network simulates a full EVM with features like Solidity stack traces, console.log debugging, and mainnet forking, making the development-test-debug cycle as fast as possible. The plugin architecture allows teams to compose exactly the toolchain they need while maintaining reproducible builds and deployments.

## Anti-Patterns

*   **Unversioned Compiler and Plugin Dependencies.** Using `latest` or unpinned versions for Solidity compiler or Hardhat plugins causes non-reproducible builds where the same source code produces different bytecode across environments.

*   **Console.log Left in Production Code.** Forgetting to remove Hardhat's `console.log` imports from contracts before deployment wastes gas and may leak internal state information.

*   **Testing Only Against Hardhat Network.** Running all tests exclusively on the local Hardhat Network without fork testing against mainnet state misses integration issues with deployed protocol contracts.

*   **Hardcoded Network Configuration.** Embedding RPC URLs and private keys directly in `hardhat.config.ts` instead of using environment variables exposes credentials in version control.

*   **No Task Automation for Deployment.** Performing multi-step deployments manually instead of scripting them as Hardhat tasks creates non-reproducible, error-prone deployment processes.

## Core Concepts

### Project Setup

```bash
mkdir my-project && cd my-project
npm init -y
# Install compatible Hardhat and plugin versions for the selected Hardhat major release.
# Check the current Hardhat documentation; avoid mixing incompatible toolbox/plugin generations.
npm install --save-dev hardhat
npx hardhat init
```

### Configuration

```typescript
// hardhat.config.ts
import { HardhatUserConfig } from "hardhat/config";
import "@nomicfoundation/hardhat-toolbox";
import "dotenv/config";

const config: HardhatUserConfig = {
  solidity: {
    version: "0.8.24",
    settings: {
      optimizer: {
        enabled: true,
        runs: 200,
      },
      viaIR: true, // Enable IR-based compilation for complex contracts
    },
  },
  networks: {
    hardhat: {
      forking: {
        url: `https://eth-mainnet.g.alchemy.com/v2/${process.env.ALCHEMY_KEY}`,
        blockNumber: 19000000, // Pin to a specific block for deterministic tests
      },
    },
    sepolia: {
      url: `https://eth-sepolia.g.alchemy.com/v2/${process.env.ALCHEMY_KEY}`,
      accounts: [process.env.DEPLOYER_PRIVATE_KEY!],
    },
    mainnet: {
      url: `https://eth-mainnet.g.alchemy.com/v2/${process.env.ALCHEMY_KEY}`,
      accounts: [process.env.DEPLOYER_PRIVATE_KEY!],
    },
  },
  etherscan: {
    apiKey: process.env.ETHERSCAN_API_KEY,
  },
  gasReporter: {
    enabled: true,
    currency: "USD",
  },
};

export default config;
```

### Writing Tests

```typescript
// test/Vault.test.ts
import { expect } from "chai";
import { ethers } from "hardhat";
import { loadFixture } from "@nomicfoundation/hardhat-toolbox/network-helpers";

describe("Vault", function () {
  async function deployVaultFixture() {
    const [owner, user1, user2] = await ethers.getSigners();
    const Vault = await ethers.getContractFactory("Vault");
    const vault = await Vault.deploy();
    return { vault, owner, user1, user2 };
  }

  describe("Deposits", function () {
    it("should accept deposits and update balance", async function () {
      const { vault, user1 } = await loadFixture(deployVaultFixture);

      await vault.connect(user1).deposit({ value: ethers.parseEther("1.0") });

      expect(await vault.balances(user1.address)).to.equal(
        ethers.parseEther("1.0")
      );
    });

    it("should emit Deposit event", async function () {
      const { vault, user1 } = await loadFixture(deployVaultFixture);

      await expect(
        vault.connect(user1).deposit({ value: ethers.parseEther("1.0") })
      )
        .to.emit(vault, "Deposit")
        .withArgs(user1.address, ethers.parseEther("1.0"));
    });

    it("should revert on zero deposit", async function () {
      const { vault, user1 } = await loadFixture(deployVaultFixture);

      await expect(
        vault.connect(user1).deposit({ value: 0 })
      ).to.be.revertedWithCustomError(vault, "ZeroAmount");
    });
  });

  describe("Withdrawals", function () {
    it("should revert if insufficient balance", async function () {
      const { vault, user1 } = await loadFixture(deployVaultFixture);

      await expect(
        vault.connect(user1).withdraw(ethers.parseEther("1.0"))
      ).to.be.revertedWithCustomError(vault, "InsufficientBalance");
    });

    it("should transfer correct amount", async function () {
      const { vault, user1 } = await loadFixture(deployVaultFixture);

      await vault.connect(user1).deposit({ value: ethers.parseEther("2.0") });

      await expect(
        vault.connect(user1).withdraw(ethers.parseEther("1.0"))
      ).to.changeEtherBalances(
        [user1, vault],
        [ethers.parseEther("1.0"), ethers.parseEther("-1.0")]
      );
    });
  });
});
```

### Time and Block Manipulation

```typescript
import { time, mine } from "@nomicfoundation/hardhat-toolbox/network-helpers";

it("should unlock after time lock expires", async function () {
  const { vault, user1 } = await loadFixture(deployVaultFixture);

  await vault.connect(user1).deposit({ value: ethers.parseEther("1.0") });

  // Advance time by 7 days
  await time.increase(7 * 24 * 60 * 60);

  // Or set to a specific timestamp
  await time.increaseTo((await time.latest()) + 3600);

  // Mine a specific number of blocks
  await mine(10);

  // Now withdrawal should succeed
  await vault.connect(user1).withdraw(ethers.parseEther("1.0"));
});
```

### Deployment Scripts with Hardhat Ignition

```typescript
// ignition/modules/Vault.ts
import { buildModule } from "@nomicfoundation/hardhat-ignition/modules";

const VaultModule = buildModule("VaultModule", (m) => {
  const initialFee = m.getParameter("initialFee", 100); // basis points

  const vault = m.contract("Vault", [initialFee]);

  // Deploy dependent contracts
  const token = m.contract("RewardToken", []);

  // Call setup functions after deployment
  m.call(vault, "setRewardToken", [token]);

  return { vault, token };
});

export default VaultModule;
```

```bash
# Deploy
npx hardhat ignition deploy ignition/modules/Vault.ts --network sepolia

# Verify on Etherscan
npx hardhat verify --network sepolia DEPLOYED_ADDRESS constructor_arg1
```

## Implementation Patterns

### Mainnet Fork Testing

```typescript
describe("Uniswap Integration", function () {
  it("should swap tokens on mainnet fork", async function () {
    // Impersonate a whale address
    const whale = await ethers.getImpersonatedSigner("0xWhaleAddress...");

    // Fund the impersonated account with ETH for gas
    await ethers.provider.send("hardhat_setBalance", [
      "0xWhaleAddress...",
      "0x56BC75E2D63100000", // 100 ETH
    ]);

    const usdc = await ethers.getContractAt("IERC20", USDC_ADDRESS);
    const router = await ethers.getContractAt("ISwapRouter", UNISWAP_ROUTER);

    const balanceBefore = await usdc.balanceOf(whale.address);

    await usdc.connect(whale).approve(UNISWAP_ROUTER, ethers.MaxUint256);
    await router.connect(whale).exactInputSingle({
      tokenIn: USDC_ADDRESS,
      tokenOut: WETH_ADDRESS,
      fee: 3000,
      recipient: whale.address,
      amountIn: 1000_000000n, // 1000 USDC
      amountOutMinimum: 0,
      sqrtPriceLimitX96: 0,
    });

    const balanceAfter = await usdc.balanceOf(whale.address);
    expect(balanceBefore - balanceAfter).to.equal(1000_000000n);
  });
});
```

### Custom Hardhat Tasks

```typescript
// tasks/accounts.ts
import { task } from "hardhat/config";

task("balances", "Prints account balances")
  .addOptionalParam("network", "Network name", "hardhat")
  .setAction(async (taskArgs, hre) => {
    const accounts = await hre.ethers.getSigners();
    for (const account of accounts) {
      const balance = await hre.ethers.provider.getBalance(account.address);
      console.log(`${account.address}: ${hre.ethers.formatEther(balance)} ETH`);
    }
  });
```

### Gas Optimization Testing

```typescript
describe("Gas benchmarks", function () {
  it("should use less than 100k gas for transfer", async function () {
    const { token, user1, user2 } = await loadFixture(deployFixture);

    const tx = await token.connect(user1).transfer(user2.address, 1000n);
    const receipt = await tx.wait();

    expect(receipt!.gasUsed).to.be.lessThan(100_000n);
  });
});
```

## Best Practices

1. **Use `loadFixture`** for test setup. It snapshots and reverts the blockchain state between tests, making tests fast and isolated.
2. **Pin fork block numbers** in `hardhat.config.ts` for deterministic tests. Unpinned forks produce flaky results as mainnet state changes.
3. **Use Hardhat Ignition** for deployment instead of raw scripts. It handles idempotent deployments, dependency ordering, and resumability.
4. **Enable the gas reporter** during development to catch gas regressions early.
5. **Use `console.log` in Solidity** (`import "hardhat/console.sol"`) for debugging. Remove before deploying to production.
6. **Write both positive and negative test cases.** Test that functions revert correctly with custom errors, not just that they succeed.
7. **Configure the optimizer** with a `runs` value that matches expected usage: low runs for rarely called contracts, high runs for frequently called ones.

## Common Pitfalls

- **Not resetting fork state between tests.** Without `loadFixture`, tests share state and produce order-dependent results.
- **Leaving `console.log` imports in production code.** This increases deployment gas cost. Use a linter rule or pre-deploy script to catch it.
- **Forgetting to fund impersonated signers.** Impersonated accounts start with their real balance, which may be zero ETH for gas.
- **Using `hardhat` network for deployment.** The default Hardhat network is ephemeral. Always specify a persistent network for real deployments.
- **Not verifying contracts on block explorers.** Unverified contracts erode user trust. Verify immediately after deployment.
- **Ignoring compiler warnings.** Solidity warnings often indicate real issues such as shadowed variables or unused returns.

## Version and Evidence Check

Hardhat major versions differ in configuration format, network connection APIs, plugin packages and test runners. Select one major version and verify examples against its official documentation.

## Review & Production Validation (2026-10-31)

- **Domain control (Contract engineering):** Check compiler, EVM fork, dependency versions, access control and storage-layout assumptions.
- **Independent validation:** Validate adversarial properties with tests and independent security review before deployment.
- **Time-sensitive details:** Treat fixed rates, thresholds, package versions, protocols and jurisdiction-specific rules in the examples above as illustrative unless reconfirmed against primary documentation.
- **Before relying on the result:** State inputs and assumptions; verify calculations and edge cases, and identify what has not been executed or tested.
