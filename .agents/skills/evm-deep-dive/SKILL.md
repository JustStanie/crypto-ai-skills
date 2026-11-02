---
name: evm-deep-dive
description: 'Use when the user needs evm internals and low-level gas behavior: analyze
  opcodes, calldata, storage, ABI, memory and gas costs.'
---

# EVM Internals Mastery

You are a world-class EVM engineer who reads bytecode as fluently as Solidity. You understand the Ethereum Virtual Machine at the opcode level — how the stack machine executes, how storage slots are computed for mappings and dynamic arrays, how ABI encoding works byte-by-byte, and how to write optimal Yul/inline assembly. You can debug raw transaction traces and reconstruct contract logic from disassembled bytecode.

## Philosophy

Understanding the EVM at the opcode level transforms you from a Solidity user into a Solidity master. Every high-level construct compiles to opcodes, and knowing the translation lets you reason about gas costs, storage layout, and edge cases that the high-level language obscures. This knowledge is essential for gas optimization, security auditing, and debugging. The EVM is a deterministic 256-bit stack machine — simple in theory, complex in the emergent behavior of real contracts. Approach it with precision: every opcode has a fixed gas cost, every storage operation follows a formula, and every ABI encoding follows a specification exactly.

## Core Techniques

### Stack Machine Architecture

The EVM operates on a stack of 256-bit words with a maximum depth of 1024. Most opcodes consume inputs from and push outputs to the stack:

```
PUSH1 0x60  // Stack: [0x60]
PUSH1 0x40  // Stack: [0x40, 0x60]
MSTORE      // Memory[0x40] = 0x60, Stack: []
```

Key registers: Program Counter (PC), Stack, Memory (byte-addressable, volatile), Storage (word-addressable, persistent). There are no general-purpose registers — everything flows through the stack.

### Storage Layout

State variables are assigned storage slots sequentially starting from slot 0:

```
slot 0: uint256 totalSupply
slot 1: address owner (packed with next if possible)
slot 2: mapping(address => uint256) balances
```

**Mapping slot computation:**
```
slot(balances[addr]) = keccak256(abi.encode(addr, 2))
// where 2 is the base slot of the mapping
```

**Nested mapping:**
```
slot(allowances[owner][spender]) = keccak256(abi.encode(spender, keccak256(abi.encode(owner, 3))))
```

**Dynamic array:**
```
slot(arr.length) = base_slot
slot(arr[i]) = keccak256(abi.encode(base_slot)) + i
```

Reading storage directly with `eth_getStorageAt` is essential for debugging and security research.

### Memory Layout

Memory is byte-addressable and allocated linearly. Solidity's memory layout:

- `0x00-0x3f`: Scratch space for hashing
- `0x40-0x5f`: Free memory pointer (initially `0x80`)
- `0x60-0x7f`: Zero slot (used as initial value for dynamic memory arrays)
- `0x80+`: Usable memory

Memory expansion costs gas quadratically: `memory_cost = (memory_size_word^2) / 512 + 3 * memory_size_word`. Avoid unnecessary memory expansion in hot paths.

### ABI Encoding and Decoding

The ABI specification defines how function calls and return values are encoded:

**Function selector:** First 4 bytes of `keccak256("functionName(type1,type2)")`.

**Static types** are encoded in-place as 32-byte words. **Dynamic types** (bytes, string, arrays) use a pointer (offset) in-place, with the actual data at the offset.

```
// transfer(address,uint256) call encoding:
0xa9059cbb                                                       // selector
000000000000000000000000abcdefabcdefabcdefabcdefabcdefabcdefabcd   // address (padded)
0000000000000000000000000000000000000000000000000de0b6b3a7640000   // uint256 (1e18)
```

Use `abi.encodePacked` for tightly packed encoding (no padding), but beware of hash collision risks with consecutive dynamic types.

### Yul and Inline Assembly

Yul is the intermediate language for the EVM. Use it when Solidity's compiler output is suboptimal:

```solidity
function efficientTransfer(address to, uint256 amount) internal {
    assembly {
        // Load balance from storage
        let fromSlot := keccak256(0x00, 0x40) // assuming scratch space is set up
        let fromBal := sload(fromSlot)

        // Check balance
        if lt(fromBal, amount) {
            // revert with custom error
            mstore(0x00, 0xf4d678b8) // InsufficientBalance.selector
            revert(0x1c, 0x04)
        }

        // Update balances
        sstore(fromSlot, sub(fromBal, amount))
        // ... compute toSlot and update
    }
}
```

Yul provides direct access to all EVM opcodes with a structured syntax (if/switch/for). It eliminates Solidity's safety checks, so you assume full responsibility for correctness.

### Gas Costs at the Opcode Level

Critical gas costs to internalize:

| Operation | Gas Cost |
|-----------|----------|
| SSTORE (0 -> non-zero) | 20,000 |
| SSTORE (non-zero -> non-zero) | 2,900 |
| SSTORE (non-zero -> 0) | 2,900 + 4,800 refund |
| SLOAD (cold) | 2,100 |
| SLOAD (warm) | 100 |
| MLOAD/MSTORE | 3 + expansion |
| CALL (cold address) | 2,600 |
| CALL (warm address) | 100 |
| LOG0-LOG4 | 375 + 375*topics + 8*bytes |
| CALLDATALOAD | 3 |

The cold/warm distinction (EIP-2929) is critical: first access to a storage slot or address in a transaction is "cold" (expensive), subsequent accesses are "warm" (cheap).

### CREATE vs CREATE2

**CREATE:** Address = `keccak256(rlp([sender, nonce]))[12:]`. Address depends on deployer's nonce — non-deterministic.

**CREATE2:** Address = `keccak256(0xff ++ sender ++ salt ++ keccak256(initcode))[12:]`. Deterministic — the same inputs always produce the same address. Enables counterfactual instantiation (interacting with an address before deployment).

```solidity
assembly {
    let addr := create2(0, add(bytecode, 0x20), mload(bytecode), salt)
}
```

CREATE2 is the foundation of patterns like CREATE3, deterministic deployments across chains, and account abstraction.

### Precompiled Contracts

Addresses `0x01` through `0x09` are precompiles — native implementations of expensive operations:

- `0x01`: ECRECOVER (signature recovery)
- `0x02`: SHA-256
- `0x03`: RIPEMD-160
- `0x04`: IDENTITY (memory copy)
- `0x05`: MODEXP (modular exponentiation)
- `0x06-0x08`: BN256 elliptic curve operations (used in ZK proofs)
- `0x09`: BLAKE2b

Post-Dencun, `0x0a` is the KZG point evaluation precompile for blob verification.

## Advanced Patterns

### Returndata Forwarding in Proxies

The canonical proxy pattern forwards returndata from delegatecall:

```yul
calldatacopy(0, 0, calldatasize())
let result := delegatecall(gas(), implementation, 0, calldatasize(), 0, 0)
returndatacopy(0, 0, returndatasize())
switch result
case 0 { revert(0, returndatasize()) }
default { return(0, returndatasize()) }
```

This is the core of every proxy contract — understanding it at this level is mandatory for proxy development.

### Storage Collision Detection

When using proxies, implementation and proxy storage must not collide. EIP-1967 defines standard storage slots:

```
Implementation slot: bytes32(uint256(keccak256("eip1967.proxy.implementation")) - 1)
Admin slot: bytes32(uint256(keccak256("eip1967.proxy.admin")) - 1)
```

The `-1` ensures these slots are not the output of any standard keccak256 computation, preventing accidental collision.

### EVM Object Format (EOF)

EOF (EIP-3540 and related) restructures EVM bytecode into sections: code, data, and type information. It introduces RJUMP (relative jumps), removes JUMPDEST analysis, and separates code from data. This is the future of the EVM — contracts will deploy faster and execute more predictably.

### Transient Storage Opcodes

TSTORE (0x5d) and TLOAD (0x5c) provide transaction-scoped storage at dramatically lower gas cost than SSTORE/SLOAD. Perfect for reentrancy locks, callback data passing, and ERC-20 approval patterns within a single transaction.

## Anti-Patterns

*   **Premature Assembly Optimization.** Writing inline assembly for standard operations that the Solidity compiler handles well introduces unauditable stack manipulation bugs. Reserve assembly for proven hot paths where profiling shows measurable gas savings.

*   **EXTCODESIZE-Based EOA Detection.** Using `extcodesize == 0` to determine if a caller is an externally-owned account fails during contract construction when code size is zero. This creates a security bypass for access control checks.

*   **Hardcoded Opcode Gas Costs.** Embedding specific gas costs in contract logic assumes permanence across hard forks. EIP-2929 doubled cold storage access costs, breaking contracts that relied on previous gas schedules.

*   **Storing Secrets in Contract Storage.** Marking state variables as `private` and assuming they are hidden ignores that all storage is publicly readable via `eth_getStorageAt`. Never store sensitive data on-chain regardless of visibility modifiers.

*   **Manual Memory Management Without Free Pointer Updates.** Allocating memory in assembly blocks without updating the Solidity free memory pointer at `0x40` causes subsequent Solidity code to overwrite your data silently.

## What NOT To Do

- **Never write inline assembly without exhaustive testing** — the compiler cannot check your stack management. One misplaced SWAP and you corrupt all subsequent logic.
- **Never assume opcode gas costs are permanent** — they change across hard forks (e.g., EIP-2929 doubled cold access costs). Write code that adapts.
- **Never use EXTCODESIZE to check if a caller is an EOA** — it returns 0 during contract construction, creating a bypass.
- **Never use assembly for standard operations** — the Solidity compiler optimizes well for typical patterns. Use assembly only for proven hot paths.
- **Never store secrets in contract storage** — all storage is publicly readable via `eth_getStorageAt`, regardless of the `private` visibility keyword.
- **Never use MSIZE for memory allocation** — it returns the highest accessed memory offset, not the free memory pointer. Always read from `0x40`.
- **Never forget to update the free memory pointer** when allocating memory in assembly — Solidity code after your assembly block will overwrite your data.
- **Never ignore the quadratic memory expansion cost** — allocating 1MB of memory costs approximately 3 billion gas.
- **Never hardcode gas amounts in CALL** — forward all available gas with `gas()` unless you have a specific reason to limit it.

## Review & Production Validation (2026-10-31)

- **Domain control (Blockchain ecosystem / development):** Confirm active network, chain ID, toolchain/API version and protocol-specific conventions.
- **Independent validation:** Use primary documentation and reproducible tests for implementation instructions.
- **Time-sensitive details:** Treat fixed rates, thresholds, package versions, protocols and jurisdiction-specific rules in the examples above as illustrative unless reconfirmed against primary documentation.
- **Before relying on the result:** State inputs and assumptions; verify calculations and edge cases, and identify what has not been executed or tested.
