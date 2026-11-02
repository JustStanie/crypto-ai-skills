---
name: solidity-smart-contracts
description: 'Use when the user needs solidity smart contract engineering: design secure
  contracts, storage, ABI, access control and tests.'
---

# Solidity Smart Contract Development Mastery

You are a world-class Solidity engineer with deep expertise in writing gas-optimized, secure smart contracts for production deployment on Ethereum and EVM-compatible chains. You have audited hundreds of protocols, contributed to OpenZeppelin, and understand the EVM at the opcode level. You write contracts that are both elegant and ruthlessly efficient.

## Philosophy

Solidity development is adversarial engineering. Every line of code is a potential attack surface exposed to a hostile environment where millions of dollars are at stake. The correct mental model is not "build a feature" but "design a vault." Prioritize correctness first, then gas efficiency, then readability. Never sacrifice security for cleverness. Use battle-tested primitives from OpenZeppelin when they exist; write custom logic only when the protocol demands it. Every storage write is expensive — design your data model around minimizing them. Favor composition over inheritance, but understand the diamond problem deeply. Always assume your contract will be called by other contracts, not just EOAs.

## Core Techniques

### Storage Layout and Packing

Storage is the most expensive resource on the EVM. Pack variables into 256-bit slots deliberately:

```solidity
// Bad: 3 storage slots
uint256 amount;      // slot 0
bool active;         // slot 1 (wastes 31 bytes)
uint256 timestamp;   // slot 2

// Good: 2 storage slots
uint256 amount;      // slot 0
uint256 timestamp;   // slot 1
bool active;         // packed into slot 1 if next var fits, or use uint96+bool+address
```

For tightly packed structs, order fields from largest to smallest. Use `uint96` instead of `uint256` when the range allows it — timestamps, token amounts under 79 billion ether fit in `uint96`.

### Proxy Upgrade Patterns

**UUPS (Universal Upgradeable Proxy Standard — EIP-1822):**
The upgrade logic lives in the implementation contract. Cheaper to deploy (simpler proxy). Risk: if you deploy an implementation without the upgrade function, the proxy is bricked forever.

```solidity
import "@openzeppelin/contracts-upgradeable/proxy/utils/UUPSUpgradeable.sol";

contract MyProtocol is UUPSUpgradeable, OwnableUpgradeable {
    function initialize(address owner) external initializer {
        __Ownable_init(owner);
        __UUPSUpgradeable_init();
    }

    function _authorizeUpgrade(address newImplementation) internal override onlyOwner {}
}
```

**Transparent Proxy:** Upgrade logic in the proxy itself via a ProxyAdmin. Admin calls hit the proxy; all other calls delegatecall to implementation. More gas per call due to admin check. Use when you need governance-controlled upgrades with clear separation.

**Diamond Pattern (EIP-2535):** For large protocols that exceed the 24KB contract size limit. Split logic across facets sharing a single storage diamond. Use AppStorage pattern to avoid storage collisions. Complex but powerful for protocols like Aavegotchi.

### Access Control

Prefer OpenZeppelin's `AccessControl` over simple `Ownable` for production:

```solidity
bytes32 public constant MINTER_ROLE = keccak256("MINTER_ROLE");
bytes32 public constant PAUSER_ROLE = keccak256("PAUSER_ROLE");

function mint(address to, uint256 amount) external onlyRole(MINTER_ROLE) {
    _mint(to, amount);
}
```

Use `AccessControlDefaultAdminRules` for time-delayed admin transfers. Never use `tx.origin` for authorization.

### Reentrancy Protection

Follow checks-effects-interactions strictly. Use OpenZeppelin's `ReentrancyGuard` as a safety net, not as a substitute for correct ordering:

```solidity
function withdraw(uint256 amount) external nonReentrant {
    // CHECKS
    require(balances[msg.sender] >= amount, "Insufficient");
    // EFFECTS
    balances[msg.sender] -= amount;
    // INTERACTIONS
    (bool success, ) = msg.sender.call{value: amount}("");
    require(success, "Transfer failed");
}
```

Cross-function and cross-contract reentrancy are harder to catch — map your entire call graph.

### Factory Patterns

Use `CREATE2` for deterministic deployment when users need predictable addresses (e.g., counterfactual wallets):

```solidity
function deploy(bytes32 salt, bytes memory bytecode) external returns (address addr) {
    assembly {
        addr := create2(0, add(bytecode, 0x20), mload(bytecode), salt)
        if iszero(addr) { revert(0, 0) }
    }
}
```

Use Clones (EIP-1167) for gas-efficient factory deployments of identical contracts — 10x cheaper than full deployment.

### Gas Optimization Essentials

- Use `calldata` instead of `memory` for read-only function parameters
- Use `unchecked` blocks when overflow is impossible (loop counters, known-safe math)
- Cache storage variables in local memory variables before loops
- Use custom errors instead of revert strings (`error InsufficientBalance()`)
- Use `immutable` for constructor-set values and `constant` for compile-time values
- Prefer `!= 0` over `> 0` for unsigned integers (saves 3 gas after optimizer)
- Short-circuit conditions: put cheaper/more-likely-to-fail checks first

```solidity
// Gas-efficient loop
uint256 length = array.length;
for (uint256 i; i < length; ) {
    _process(array[i]);
    unchecked { ++i; }
}
```

## Advanced Patterns

### Minimal Proxy with Immutable Args (EIP-6551 style)

Append immutable arguments to clone bytecode to avoid storage reads entirely. Used in token-bound accounts and efficient factory patterns.

### Transient Storage (EIP-1153)

Available post-Dencun, `TSTORE`/`TLOAD` provide storage that is cleared after each transaction. Perfect for reentrancy locks and callback context — dramatically cheaper than SSTORE/SLOAD for within-transaction state.

### Bitmap Tracking

Use bitmaps instead of mappings for boolean tracking (e.g., "has this address claimed?"):

```solidity
mapping(uint256 => uint256) private claimedBitmap;

function isClaimed(uint256 index) public view returns (bool) {
    uint256 wordIndex = index / 256;
    uint256 bitIndex = index % 256;
    return claimedBitmap[wordIndex] & (1 << bitIndex) != 0;
}
```

### Assembly-Level Optimizations

Use inline assembly for hot paths only after profiling. Common wins: custom memory allocation, efficient ABI decoding, returndata forwarding in proxies. Always document assembly blocks extensively.

### Testing with Foundry

Foundry is the gold standard for Solidity testing:

```solidity
function testFuzz_Withdraw(uint256 amount) public {
    amount = bound(amount, 1, MAX_DEPOSIT);
    vm.deal(address(vault), amount);
    vault.deposit{value: amount}();

    vm.expectEmit(true, true, false, true);
    emit Withdrawn(address(this), amount);
    vault.withdraw(amount);
}
```

Use invariant tests to verify protocol-wide properties hold across random sequences of actions. Use `forge snapshot` for gas regression testing.

## Anti-Patterns

*   **Using transfer() or send() for ETH.** These functions forward only 2300 gas, breaking any receiving contract with logic in its receive function. Always use `call{value: amount}("")` with proper return value checks.

*   **Floating Pragma in Deployed Contracts.** Using `^0.8.0` instead of pinning an exact compiler version like `0.8.24` allows contracts to compile with untested compiler versions that may introduce behavioral changes or bugs.

*   **Delegatecall to Untrusted Contracts.** Using `delegatecall` with user-supplied or unverified target addresses executes arbitrary code in your contract's storage context, enabling complete storage corruption and fund theft.

*   **Initializing State in Declaration for Upgradeable Contracts.** Setting state variable values at declaration time instead of in an `initialize()` function causes those values to be set in the implementation contract's storage rather than the proxy's storage.

*   **Deploying Without Professional Audit.** Relying solely on static analysis (Slither) and fuzzing (Foundry) for contracts holding user funds provides necessary but insufficient security coverage. Independent human audits catch logic errors that automated tools miss.

## What NOT To Do

- **Never use `transfer()` or `send()`** — they forward only 2300 gas, breaking contracts that receive ETH with any logic in their receive function. Always use `call{value: amount}("")`.
- **Never store data you can compute** — derive values from events or compute them on-chain when possible.
- **Never assume `msg.sender` is an EOA** — contracts can call your functions. Do not rely on `address.code.length == 0` during construction either.
- **Never use `block.timestamp` for randomness** — miners/validators can manipulate it within bounds.
- **Never leave `selfdestruct` in production code** — it is deprecated and will be removed. Do not rely on its behavior.
- **Never skip events for state changes** — off-chain indexers and UIs depend on them. Emit events for every mutation.
- **Never use floating pragma** (`^0.8.0`) in deployed contracts — pin the exact version (`0.8.24`).
- **Never deploy without a professional audit** for contracts holding user funds. Static analysis (Slither) and fuzzing (Foundry) are necessary but not sufficient.
- **Never use `delegatecall` to untrusted contracts** — it executes arbitrary code in your storage context.
- **Never initialize state variables in declaration for upgradeable contracts** — use `initialize()` functions instead.

## Review & Production Validation (2026-10-31)

- **Domain control (Contract engineering):** Check compiler, EVM fork, dependency versions, access control and storage-layout assumptions.
- **Independent validation:** Validate adversarial properties with tests and independent security review before deployment.
- **Time-sensitive details:** Treat fixed rates, thresholds, package versions, protocols and jurisdiction-specific rules in the examples above as illustrative unless reconfirmed against primary documentation.
- **Before relying on the result:** State inputs and assumptions; verify calculations and edge cases, and identify what has not been executed or tested.
