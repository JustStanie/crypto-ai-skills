---
name: foundry-framework
description: 'Use when the user needs foundry solidity testing and deployment: create Forge
  tests, fuzzing, fork tests, scripts and reproducible builds.'
---

# Foundry — Web3 Development

You are an expert in Foundry for writing Solidity-native tests, fuzz testing, deployment scripting, and gas optimization of smart contracts.

## Overview

Foundry is a fast, portable toolkit for Ethereum development written in Rust. It includes Forge (testing framework), Cast (CLI for chain interaction), Anvil (local node), and Chisel (Solidity REPL). Unlike Hardhat, Foundry tests are written in Solidity, enabling tighter integration with the contracts under test and powerful fuzz testing capabilities.

## Core Philosophy

Foundry embraces a Solidity-native testing philosophy: tests are written in the same language as the contracts, eliminating impedance mismatch between test and production code. This enables direct access to internal contract state, native fuzzing with type-aware input generation, and gas profiling that reflects actual EVM execution. Foundry's Rust-based toolchain prioritizes compilation speed and test execution performance, making rapid iteration the default workflow rather than an aspiration.

## Anti-Patterns

*   **Skipping Fuzz Testing for Edge Cases.** Writing only unit tests with hardcoded inputs misses the boundary conditions and unexpected state combinations that fuzzing reveals. Use `forge test --fuzz-runs` for any function with numeric inputs.

*   **Testing Against Live RPC in CI.** Using live RPC endpoints for fork tests in CI pipelines creates flaky tests that fail due to rate limits, network issues, or state changes. Pin fork block numbers and cache RPC responses.

*   **No Invariant Tests for Stateful Contracts.** Relying only on stateless fuzz tests for contracts with complex state machines misses multi-step vulnerability sequences. Write invariant tests with handler contracts for realistic action flows.

*   **Ignoring Gas Snapshots in CI.** Not running `forge snapshot` in continuous integration means gas regressions from code changes go undetected until deployment.

*   **Inline Forge Scripts Without Broadcast Safety.** Running deployment scripts without `--broadcast` flag awareness risks accidentally sending transactions during development. Always separate simulation from broadcast explicitly.

## Core Concepts

### Project Setup

```bash
# Install Foundry
curl -L https://foundry.paradigm.xyz | bash
foundryup

# Create new project
forge init my-project
cd my-project

# Install dependencies
forge install OpenZeppelin/openzeppelin-contracts
forge install transmissions11/solmate
```

### Project Structure

```
my-project/
  src/           # Contract source files
  test/          # Test files (*.t.sol)
  script/        # Deployment scripts (*.s.sol)
  lib/           # Dependencies installed via forge install
  foundry.toml   # Configuration
```

### Configuration

```toml
# foundry.toml
[profile.default]
src = "src"
out = "out"
libs = ["lib"]
solc = "0.8.24"
optimizer = true
optimizer_runs = 200
via_ir = false

[profile.default.fuzz]
runs = 1000
max_test_rejects = 65536
seed = "0x1"

[profile.ci.fuzz]
runs = 10000

[rpc_endpoints]
mainnet = "${MAINNET_RPC_URL}"
sepolia = "${SEPOLIA_RPC_URL}"

[etherscan]
mainnet = { key = "${ETHERSCAN_API_KEY}" }
```

### Remappings

```
# remappings.txt
@openzeppelin/=lib/openzeppelin-contracts/
@solmate/=lib/solmate/src/
```

### Writing Tests

```solidity
// test/Vault.t.sol
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import {Test, console2} from "forge-std/Test.sol";
import {Vault} from "../src/Vault.sol";

contract VaultTest is Test {
    Vault public vault;
    address public alice = makeAddr("alice");
    address public bob = makeAddr("bob");

    function setUp() public {
        vault = new Vault();
        // Fund test accounts
        deal(alice, 100 ether);
        deal(bob, 100 ether);
    }

    function test_Deposit() public {
        vm.prank(alice);
        vault.deposit{value: 1 ether}();

        assertEq(vault.balances(alice), 1 ether);
    }

    function test_Withdraw() public {
        vm.prank(alice);
        vault.deposit{value: 2 ether}();

        uint256 balanceBefore = alice.balance;

        vm.prank(alice);
        vault.withdraw(1 ether);

        assertEq(alice.balance, balanceBefore + 1 ether);
        assertEq(vault.balances(alice), 1 ether);
    }

    function test_RevertWhen_WithdrawInsufficientBalance() public {
        vm.prank(alice);
        vm.expectRevert(Vault.InsufficientBalance.selector);
        vault.withdraw(1 ether);
    }

    function test_EmitDepositEvent() public {
        vm.prank(alice);
        vm.expectEmit(true, false, false, true);
        emit Vault.Deposit(alice, 1 ether);
        vault.deposit{value: 1 ether}();
    }
}
```

### Cheatcodes

```solidity
contract CheatcodeExamples is Test {
    function test_Pranking() public {
        // Execute next call as alice
        vm.prank(alice);
        vault.deposit{value: 1 ether}();

        // Execute all subsequent calls as alice until stopPrank
        vm.startPrank(alice);
        vault.deposit{value: 1 ether}();
        vault.withdraw(0.5 ether);
        vm.stopPrank();
    }

    function test_TimeManipulation() public {
        // Set block timestamp
        vm.warp(block.timestamp + 7 days);

        // Set block number
        vm.roll(block.number + 100);

        // Combine both
        skip(1 hours); // Advance time by 1 hour
        rewind(30 minutes); // Go back 30 minutes
    }

    function test_StorageManipulation() public {
        // Set storage slot directly
        vm.store(address(vault), bytes32(uint256(0)), bytes32(uint256(42)));

        // Read storage slot
        bytes32 value = vm.load(address(vault), bytes32(uint256(0)));

        // Set ETH balance
        deal(alice, 1000 ether);

        // Set ERC-20 balance
        deal(address(token), alice, 1000e18);
    }

    function test_ExpectRevert() public {
        // Expect any revert
        vm.expectRevert();
        vault.withdraw(1 ether);

        // Expect specific custom error
        vm.expectRevert(abi.encodeWithSelector(
            Vault.InsufficientBalance.selector,
            1 ether,
            0
        ));
        vault.withdraw(1 ether);
    }

    function test_Snapshot() public {
        uint256 snapshotId = vm.snapshot();

        vault.deposit{value: 1 ether}();
        assertEq(vault.totalDeposits(), 1 ether);

        vm.revertTo(snapshotId); // Restore state
        assertEq(vault.totalDeposits(), 0);
    }
}
```

## Implementation Patterns

### Fuzz Testing

```solidity
contract VaultFuzzTest is Test {
    Vault vault;

    function setUp() public {
        vault = new Vault();
    }

    // Foundry generates random inputs automatically
    function testFuzz_DepositAndWithdraw(uint256 amount) public {
        // Bound inputs to reasonable ranges
        amount = bound(amount, 0.01 ether, 100 ether);

        deal(address(this), amount);
        vault.deposit{value: amount}();

        assertEq(vault.balances(address(this)), amount);

        vault.withdraw(amount);
        assertEq(vault.balances(address(this)), 0);
    }

    // Fuzz with multiple parameters
    function testFuzz_PartialWithdraw(uint256 deposit, uint256 withdraw) public {
        deposit = bound(deposit, 1 ether, 100 ether);
        withdraw = bound(withdraw, 0, deposit); // withdraw <= deposit

        deal(address(this), deposit);
        vault.deposit{value: deposit}();
        vault.withdraw(withdraw);

        assertEq(vault.balances(address(this)), deposit - withdraw);
    }
}
```

### Invariant Testing

```solidity
// test/invariants/VaultInvariant.t.sol
contract VaultHandler is Test {
    Vault public vault;
    uint256 public ghost_totalDeposited;
    uint256 public ghost_totalWithdrawn;

    constructor(Vault _vault) {
        vault = _vault;
    }

    function deposit(uint256 amount) external {
        amount = bound(amount, 0, 10 ether);
        deal(address(this), amount);
        vault.deposit{value: amount}();
        ghost_totalDeposited += amount;
    }

    function withdraw(uint256 amount) external {
        uint256 balance = vault.balances(address(this));
        amount = bound(amount, 0, balance);
        if (amount == 0) return;
        vault.withdraw(amount);
        ghost_totalWithdrawn += amount;
    }

    receive() external payable {}
}

contract VaultInvariantTest is Test {
    Vault public vault;
    VaultHandler public handler;

    function setUp() public {
        vault = new Vault();
        handler = new VaultHandler(vault);
        targetContract(address(handler));
    }

    function invariant_SolvencyHolds() public view {
        assertEq(
            address(vault).balance,
            handler.ghost_totalDeposited() - handler.ghost_totalWithdrawn()
        );
    }

    function invariant_BalanceMatchesDeposits() public view {
        assertGe(
            handler.ghost_totalDeposited(),
            handler.ghost_totalWithdrawn()
        );
    }
}
```

### Deployment Scripts

```solidity
// script/Deploy.s.sol
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import {Script, console2} from "forge-std/Script.sol";
import {Vault} from "../src/Vault.sol";
import {RewardToken} from "../src/RewardToken.sol";

contract DeployScript is Script {
    function run() external {
        uint256 deployerKey = vm.envUint("DEPLOYER_PRIVATE_KEY");

        vm.startBroadcast(deployerKey);

        Vault vault = new Vault();
        console2.log("Vault deployed at:", address(vault));

        RewardToken token = new RewardToken();
        vault.setRewardToken(address(token));

        vm.stopBroadcast();
    }
}
```

```bash
# Dry run
forge script script/Deploy.s.sol --rpc-url sepolia

# Broadcast transactions
forge script script/Deploy.s.sol --rpc-url sepolia --broadcast --verify

# Resume a failed broadcast
forge script script/Deploy.s.sol --rpc-url sepolia --resume
```

### Mainnet Fork Testing

```solidity
contract ForkTest is Test {
    uint256 mainnetFork;

    function setUp() public {
        mainnetFork = vm.createFork(vm.envString("MAINNET_RPC_URL"), 19000000);
        vm.selectFork(mainnetFork);
    }

    function test_SwapOnUniswap() public {
        address whale = 0xAb5801a7D398351b8bE11C439e05C5B3259aeC9B;
        vm.startPrank(whale);

        IERC20 usdc = IERC20(0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48);
        uint256 balance = usdc.balanceOf(whale);
        assertGt(balance, 0, "Whale should have USDC");

        vm.stopPrank();
    }

    function test_MultipleForks() public {
        uint256 optimismFork = vm.createFork(vm.envString("OPTIMISM_RPC_URL"));

        vm.selectFork(mainnetFork);
        assertEq(block.chainid, 1);

        vm.selectFork(optimismFork);
        assertEq(block.chainid, 10);
    }
}
```

## Best Practices

1. **Use `bound()` instead of `vm.assume()`** in fuzz tests. `assume` discards runs, while `bound` clamps inputs to valid ranges and never wastes iterations.
2. **Name test functions with `test_` prefix for passing tests and `testFuzz_` for fuzz tests.** Use `testFail_` only when you cannot use `vm.expectRevert`.
3. **Use `forge snapshot`** to track gas costs across changes. Commit the `.gas-snapshot` file and compare in CI.
4. **Write invariant tests** for critical system properties like solvency, total supply consistency, or access control.
5. **Use `deal` and `makeAddr`** instead of managing private keys manually in tests.
6. **Use `forge coverage`** to identify untested code paths. Aim for high branch coverage on security-critical contracts.
7. **Use `--via-ir` only when needed.** It produces more optimized bytecode but significantly slows compilation.

## Common Pitfalls

- **Forgetting `receive()` or `fallback()` on test contracts.** If a test contract needs to receive ETH, it must have a `receive` function.
- **Not using `vm.startPrank` / `vm.stopPrank` correctly.** `vm.prank` only affects the next call. Use `startPrank` for multiple calls from the same sender.
- **Fuzz tests with overly restrictive `vm.assume`.** If too many inputs are rejected, Foundry may fail with "too many rejects." Use `bound` instead.
- **Incorrect remappings.** Import errors often stem from wrong remapping paths. Run `forge remappings` to debug.
- **Deploying with `forge create` in production.** Use `forge script` with `--broadcast` instead, as it provides simulation, gas estimation, and transaction management.
- **Not pinning fork block numbers.** Unpinned forks cause nondeterministic test results as on-chain state changes.

## Version and Evidence Check

Verify the installed Foundry version, OpenZeppelin dependency version, remappings and network settings before copying deployment commands.
