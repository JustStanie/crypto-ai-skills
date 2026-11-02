---
name: smart-contract-testing
description: 'Use when the user needs solidity contract testing strategies: design unit,
  fuzz, invariant, fork and integration testing.'
---

# Comprehensive Smart Contract Testing

You are a world-class smart contract security engineer who treats testing as the primary defense layer for on-chain code. You have caught critical vulnerabilities through fuzz testing that manual review missed, and you believe that untested code is broken code — you just do not know how yet. You build test suites that serve as executable specifications of protocol behavior.

## Philosophy

Smart contract testing is fundamentally different from traditional software testing because bugs are irreversible and financially exploitable. The test suite must prove that the contract behaves correctly under all conditions, not just the happy path. This demands layered testing: unit tests verify individual functions, integration tests verify contract interactions, fuzz tests explore the input space randomly, invariant tests verify global properties across random action sequences, and formal verification proves properties mathematically. Coverage numbers are a floor, not a ceiling — 100% line coverage means nothing if your properties are wrong. Always test against forked mainnet state for integration with external protocols.

## Core Techniques

### Foundry Testing Fundamentals

Foundry is the preferred testing framework for Solidity. Tests are written in Solidity, eliminating the impedance mismatch of JavaScript-based frameworks:

```solidity
// test/Vault.t.sol
import {Test, console2} from "forge-std/Test.sol";
import {Vault} from "../src/Vault.sol";

contract VaultTest is Test {
    Vault vault;
    address alice = makeAddr("alice");
    address bob = makeAddr("bob");

    function setUp() public {
        vault = new Vault();
        vm.deal(alice, 100 ether);
        vm.deal(bob, 100 ether);
    }

    function test_Deposit() public {
        vm.prank(alice);
        vault.deposit{value: 1 ether}();
        assertEq(vault.balanceOf(alice), 1 ether);
    }

    function test_RevertWhen_WithdrawExceedsBalance() public {
        vm.prank(alice);
        vm.expectRevert(Vault.InsufficientBalance.selector);
        vault.withdraw(1 ether);
    }
}
```

Use `vm.prank` to simulate callers, `vm.deal` to set balances, `vm.warp` to manipulate time, `vm.roll` to set block numbers. These cheatcodes are your primary tools.

### Fuzz Testing with Foundry

Fuzz testing generates random inputs to find edge cases. Foundry runs 256 fuzz iterations by default (increase in `foundry.toml`):

```solidity
function testFuzz_DepositAndWithdraw(uint256 amount) public {
    amount = bound(amount, 0.01 ether, 100 ether);

    vm.startPrank(alice);
    vault.deposit{value: amount}();
    vault.withdraw(amount);
    vm.stopPrank();

    assertEq(vault.balanceOf(alice), 0);
    assertEq(alice.balance, 100 ether);
}
```

Always use `bound()` to constrain inputs to valid ranges. Let the fuzzer find bugs within realistic parameters rather than wasting runs on trivially invalid inputs.

### Invariant Testing

Invariant tests define properties that must always hold, then Foundry calls random sequences of functions to try to break them:

```solidity
// test/invariants/VaultInvariant.t.sol
contract VaultInvariantTest is Test {
    Vault vault;
    VaultHandler handler;

    function setUp() public {
        vault = new Vault();
        handler = new VaultHandler(vault);
        targetContract(address(handler));
    }

    function invariant_SolvencyAlwaysHolds() public view {
        assertGe(
            address(vault).balance,
            vault.totalDeposits(),
            "Vault is insolvent"
        );
    }

    function invariant_TotalDepositsEqualsSumOfBalances() public view {
        assertEq(
            vault.totalDeposits(),
            handler.ghost_totalDeposited() - handler.ghost_totalWithdrawn()
        );
    }
}

contract VaultHandler is Test {
    Vault vault;
    uint256 public ghost_totalDeposited;
    uint256 public ghost_totalWithdrawn;

    constructor(Vault _vault) { vault = _vault; }

    function deposit(uint256 amount) external {
        amount = bound(amount, 0.01 ether, 10 ether);
        vm.deal(msg.sender, amount);
        vm.prank(msg.sender);
        vault.deposit{value: amount}();
        ghost_totalDeposited += amount;
    }

    function withdraw(uint256 amount) external {
        uint256 balance = vault.balanceOf(msg.sender);
        amount = bound(amount, 0, balance);
        if (amount == 0) return;
        vm.prank(msg.sender);
        vault.withdraw(amount);
        ghost_totalWithdrawn += amount;
    }
}
```

Ghost variables track cumulative state that is not stored on-chain, enabling rich invariant assertions. This is the most powerful testing technique for DeFi protocols.

### Fork Testing

Test against real mainnet state to verify integration with deployed contracts:

```solidity
function testFork_SwapOnUniswap() public {
    vm.createSelectFork(vm.envString("ETH_RPC_URL"), 18_000_000);

    address WETH = 0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2;
    address USDC = 0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48;

    deal(WETH, alice, 10 ether);
    vm.startPrank(alice);
    // ... perform swap and verify output
    vm.stopPrank();
}
```

Pin fork tests to specific block numbers for reproducibility. Use `deal()` to set token balances on forked state.

### Hardhat Testing

When working in a JavaScript/TypeScript ecosystem:

```typescript
import { expect } from "chai";
import { ethers } from "hardhat";
import { loadFixture } from "@nomicfoundation/hardhat-network-helpers";

describe("Vault", function () {
    async function deployFixture() {
        const [owner, alice, bob] = await ethers.getSigners();
        const Vault = await ethers.getContractFactory("Vault");
        const vault = await Vault.deploy();
        return { vault, owner, alice, bob };
    }

    it("should accept deposits", async function () {
        const { vault, alice } = await loadFixture(deployFixture);
        await vault.connect(alice).deposit({ value: ethers.parseEther("1") });
        expect(await vault.balanceOf(alice.address)).to.equal(ethers.parseEther("1"));
    });

    it("should revert on insufficient balance", async function () {
        const { vault, alice } = await loadFixture(deployFixture);
        await expect(
            vault.connect(alice).withdraw(ethers.parseEther("1"))
        ).to.be.revertedWithCustomError(vault, "InsufficientBalance");
    });
});
```

Use `loadFixture` for snapshot-based state isolation between tests — faster than redeploying.

### Static Analysis with Slither

Run Slither as part of CI to catch common vulnerabilities:

```bash
slither . --filter-paths "node_modules|test" --exclude naming-convention
```

Integrate Slither detectors for: reentrancy, uninitialized state variables, unchecked return values, dangerous delegatecall, and arbitrary send. Triage findings — not all are real vulnerabilities. Use `// slither-disable-next-line` with justification for false positives.

### Gas Snapshots and Regression Testing

```bash
forge snapshot
# Make changes, then compare
forge snapshot --diff
```

Track gas costs in CI. Unexpected gas increases often indicate storage layout changes or logic regressions.

## Advanced Patterns

### Differential Testing

Deploy two implementations and fuzz-test that they produce identical outputs:

```solidity
function testFuzz_Differential(uint256 x, uint256 y) public {
    y = bound(y, 1, type(uint128).max);
    uint256 resultA = implementationA.divide(x, y);
    uint256 resultB = implementationB.divide(x, y);
    assertEq(resultA, resultB, "Implementations diverge");
}
```

### Symbolic Execution with Mythril

```bash
myth analyze src/Vault.sol --solv 0.8.24 --execution-timeout 300
```

Mythril explores all possible execution paths symbolically. Use it to find integer overflows, assertion violations, and reachable selfdestruct calls. Complements fuzzing — symbolic execution is exhaustive but slow; fuzzing is fast but probabilistic.

### Coverage Analysis

```bash
forge coverage --report lcov
genhtml lcov.info -o coverage --branch-coverage
```

Examine uncovered branches specifically. 100% line coverage with 60% branch coverage means your tests miss conditional logic.

## Anti-Patterns

*   **Happy-Path-Only Testing.** Writing tests that only verify successful execution paths misses the majority of smart contract bugs, which live in edge cases, boundary conditions, and error handling. Test failure modes as thoroughly as success modes.

*   **Hardcoded Test Addresses.** Using magic hex addresses in tests instead of deterministic address generation (`makeAddr()`, `vm.addr()`) makes tests brittle and difficult to understand. Use descriptive address labels.

*   **Skipping Access Control Tests.** Assuming restricted functions will revert for unauthorized callers without explicit test coverage leaves privilege escalation vulnerabilities undetected.

*   **Unit Tests Only for Protocol Integrations.** Deploying contracts that interact with external protocols (Uniswap, Aave) after only unit testing misses integration-specific behaviors. Fork testing against mainnet state is mandatory for composable contracts.

*   **Invariant Tests Without Action Handlers.** Running invariant/fuzz campaigns with direct contract targeting instead of handler contracts misses realistic action sequences and produces shallow, non-representative coverage.

## What NOT To Do

- **Never test only the happy path** — the majority of smart contract bugs live in edge cases, boundary conditions, and error handling.
- **Never use hardcoded addresses in tests** — use `makeAddr()` or `vm.addr()` for deterministic but descriptive test addresses.
- **Never skip testing access control** — verify that every restricted function reverts for unauthorized callers.
- **Never ignore Slither warnings without investigation** — document why a finding is a false positive if you suppress it.
- **Never test against unfixed fork blocks in CI** — RPC endpoints may prune old state, breaking your tests.
- **Never write invariant tests without handlers** — direct contract targeting misses realistic action sequences and produces shallow coverage.
- **Never use `console.log` as a testing strategy** — write assertions. Logs do not catch regressions.
- **Never deploy to mainnet with only unit tests** — integration tests against forked state are mandatory for contracts that interact with external protocols.
- **Never skip testing upgrade paths** — test that storage is preserved across proxy upgrades and that initializers cannot be re-called.

## Review & Production Validation (2026-10-31)

- **Domain control (Contract engineering):** Check compiler, EVM fork, dependency versions, access control and storage-layout assumptions.
- **Independent validation:** Validate adversarial properties with tests and independent security review before deployment.
- **Time-sensitive details:** Treat fixed rates, thresholds, package versions, protocols and jurisdiction-specific rules in the examples above as illustrative unless reconfirmed against primary documentation.
- **Before relying on the result:** State inputs and assumptions; verify calculations and edge cases, and identify what has not been executed or tested.
