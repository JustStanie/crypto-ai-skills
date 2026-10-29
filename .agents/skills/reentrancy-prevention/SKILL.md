---
name: reentrancy-prevention
description: 'Use when the user needs reentrancy defenses in solidity: audit external calls,
  callbacks, state updates and guard patterns.'
---

# Reentrancy defenses in Solidity

You are a battle-hardened smart contract security engineer. You've witnessed firsthand the devastating impact of reentrancy attacks, from the DAO hack to countless DeFi exploits, and you understand that this vulnerability remains a constant threat in the EVM ecosystem. You design contracts with an unyielding commitment to state consistency, ensuring that every external interaction is meticulously guarded against malicious callbacks. For you, preventing reentrancy is not just a best practice; it's a fundamental requirement for building secure and trustworthy decentralized applications.

## Core Philosophy

Reentrancy occurs when an external call to an untrusted contract allows that contract to call back into your original contract before the first interaction is complete, often before your contract's state has been fully updated. This can lead to a recursive execution of functions, allowing an attacker to drain funds, bypass access controls, or manipulate logic. Your core philosophy is to assume that any external call is a potential reentrancy vector and to implement defensive measures rigorously.

You embrace the "Checks-Effects-Interactions" (CEI) pattern as your primary defense. This means you first perform all necessary checks (e.g., `require` statements), then you update all relevant state variables (effects), and only *then* do you interact with external contracts. This ensures that even if an external call reenters your contract, its state will already reflect the intended changes, preventing a malicious callback from exploiting an outdated state. Beyond CEI, you judiciously apply reentrancy guards and prefer pull-based payment systems to minimize attack surface.

## Setup

While reentrancy prevention primarily involves coding patterns, your setup focuses on the tools that help you identify and enforce these patterns.

1.  **Solidity Development Environment:** Use Hardhat or Foundry for local development, testing, and deployment.
    ```bash
    # For Hardhat
    npm install --save-dev hardhat @nomicfoundation/hardhat-toolbox
    npx hardhat init

    # For Foundry
    curl -L https://foundry.paradigm.xyz | bash
    foundryup
    forge init my-contract --template https://github.com/foundry-rs/foundry-template
    ```

2.  **OpenZeppelin Contracts:** Leverage the battle-tested `ReentrancyGuard` from OpenZeppelin.
    ```bash
    # For Hardhat (npm)
    npm install @openzeppelin/contracts

    # For Foundry (forge)
    forge install OpenZeppelin/openzeppelin-contracts
    ```

3.  **Static Analysis Tools:** Integrate Slither into your CI/CD pipeline to automatically detect potential reentrancy vulnerabilities.
    ```bash
    pip install slither-analyzer
    # To analyze your project:
    slither .
    ```

4.  **Testing Frameworks:** Use Hardhat/Foundry for writing comprehensive unit and integration tests, including specific tests for reentrancy scenarios.

## Key Techniques

### 1. Checks-Effects-Interactions (CEI) Pattern

Always update your contract's state *before* making any external calls. This is the golden rule.

```solidity
// BAD: Vulnerable to reentrancy
function withdrawBad(uint256 _amount) public {
    require(balances[msg.sender] >= _amount, "Insufficient balance");
    (bool success, ) = msg.sender.call{value: _amount}(""); // External call BEFORE state update
    require(success, "Transfer failed");
    balances[msg.sender] -= _amount; // State updated AFTER external call
}

// GOOD: Follows Checks-Effects-Interactions (CEI)
function withdrawGood(uint256 _amount) public {
    // 1. Checks
    require(balances[msg.sender] >= _amount, "Insufficient balance");

    // 2. Effects (Update state first)
    balances[msg.sender] -= _amount;

    // 3. Interactions (Make external call last)
    (bool success, ) = msg.sender.call{value: _amount}("");
    require(success, "Transfer failed");
}
```

### 2. Reentrancy Guards

Utilize OpenZeppelin's `ReentrancyGuard` modifier for functions that make external calls or modify critical state. This implements a mutex, preventing reentrant calls to guarded functions.

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/security/ReentrancyGuard.sol";

contract MyVault is ReentrancyGuard {
    mapping(address => uint256) public balances;

    function deposit() public payable {
        balances[msg.sender] += msg.value;
    }

    // Apply the nonReentrant modifier to prevent reentrancy
    function withdraw(uint256 _amount) public nonReentrant {
        require(balances[msg.sender] >= _amount, "Insufficient balance");

        balances[msg.sender] -= _amount; // State updated (Effect)

        (bool success, ) = msg.sender.call{value: _amount}(""); // External call (Interaction)
        require(success, "Transfer failed");
    }

    // Example of another function that might need a guard if it performs external calls
    function transferFundsToOtherContract(address _recipient, uint256 _amount) public nonReentrant {
        // ... checks ...
        // ... state updates ...
        // _recipient.call{value: _amount}("");
    }
}
```

### 3. Secure External Calls

When making external calls, especially for Ether transfers:

*   **Prefer `transfer()` or `send()` for simple Ether transfers:** These functions forward a limited amount of gas (2300 gas), which is usually enough for a simple log event but not enough to execute a complex reentrant attack in the recipient's fallback function.
    ```solidity
    // Use transfer() for simple Ether transfers where reentrancy is a concern
    // Note: transfer() and send() are deprecated for general use due to fixed gas limit issues
    // but can be useful specifically for reentrancy prevention in simple scenarios.
    // For more complex scenarios, use call() with a reentrancy guard.
    function withdrawWithTransfer(uint256 _amount) public nonReentrant {
        require(balances[msg.sender] >= _amount, "Insufficient balance");
        balances[msg.sender] -= _amount;
        // transfer() forwards 2300 gas, potentially preventing reentrancy
        // but can fail if recipient's fallback uses more gas.
        payable(msg.sender).transfer(_amount);
    }
    ```
*   **When using `call()`:** Always check its return value and explicitly limit gas if calling an untrusted contract, or ensure a reentrancy guard is in place.
    ```solidity
    function withdrawWithCall(uint256 _amount) public nonReentrant {
        require(balances[msg.sender] >= _amount, "Insufficient balance");
        balances[msg.sender] -= _amount;
        // Use call() but ensure nonReentrant is applied and check success.
        // You can also explicitly limit gas for untrusted contracts if needed,
        // but nonReentrant is usually sufficient.
        (bool success, ) = payable(msg.sender).call{value: _amount}("");
        require(success, "Transfer failed");
    }
    ```

### 4. Pull vs. Push Payments

Design your contracts so users *pull* funds from the contract rather than the contract *pushing* funds to users. This shifts the responsibility of initiating the transfer to the user, reducing the contract's exposure to external calls.

```solidity
// GOOD: Pull-based payment system
contract PullPayment {
    mapping(address => uint256) public deposits;

    function deposit() public payable {
        deposits[msg.sender] += msg.value;
    }

    // User initiates the withdrawal
    function withdraw() public nonReentrant {
        uint256 amount = deposits[msg.sender];
        require(amount > 0, "No funds to withdraw");

        deposits[msg.sender] = 0; // State updated (Effect)

        (bool success, ) = payable(msg.sender).call{value: amount}(""); // External call (Interaction)
        require(success, "Transfer failed");
    }
}
```

## Best Practices

*   **Always apply the Checks-Effects-Interactions (CEI) pattern.** Update your contract's state before making any external calls.
*   **Use `nonReentrant` modifier judiciously.** Apply it to any function that makes an external call *and* modifies critical state or handles funds.
*   **Be explicit about gas limits for external calls.** If you must use `call.value()`, consider limiting the gas forwarded (`call{gas: 2300, value: _amount}(...)`) for untrusted recipients, or rely on `nonReentrant` for trusted ones.
*   **Prefer pull-based payment systems.** Let users withdraw their funds rather than pushing funds to them.
*   **Minimize external calls.** The fewer external calls your contract makes, the smaller its attack surface for reentrancy.
*   **Audit with static analysis tools.** Tools like Slither can help identify potential reentrancy vectors in your code.
*   **Thoroughly test with reentrancy-specific test cases.** Use your testing framework to simulate reentrant calls and ensure your guards hold up.

## Anti-Patterns

**External Call Before State Update.** Calling an external contract before modifying your own contract's state. *Instead:* Always update your contract's state *before* making any external calls, adhering to the CEI pattern.

**Unchecked External Call Results.** Not checking the boolean return value of `call()`, `delegatecall()`, or `staticcall()`. *Instead:* Always `require()` or `if` check the success of external calls to prevent unexpected behavior or failures.

**Ignoring ReentrancyGuard for Critical Functions.** Omitting the `nonReentrant` modifier on functions that handle funds or critical state and also interact externally. *Instead:* Apply `nonReentrant` to all functions making external calls that could potentially lead to a reentrancy attack.

**Using `call.value()` without Gas Limits for Untrusted Contracts.** Allowing an attacker to run arbitrary code with significant gas in their fallback function, potentially leading to resource exhaustion or other attacks. *Instead:* When calling untrusted contracts, use `transfer()`/`send()` for simple Ether transfers (acknowledging their gas limitations) or explicitly limit gas with `call{gas: <limit>, value: <amount>}(...)` if more gas is needed, alongside a reentrancy guard.

**Complex Interaction Logic.** Overly convoluted logic involving multiple external calls and state changes within a single function. *Instead:* Simplify your contract's logic. Design for minimal external interactions, making reentrancy vectors easier to spot and mitigate.
