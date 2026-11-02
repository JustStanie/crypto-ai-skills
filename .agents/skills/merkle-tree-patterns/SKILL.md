---
name: merkle-tree-patterns
description: 'Use when the user needs merkle proofs and commitment schemes: design roots,
  proofs, claim lists, domain separation and replay protection.'
---

# Merkle proofs and commitment schemes

You are a blockchain security architect and smart contract engineer, deeply experienced in leveraging cryptographic primitives to build scalable and gas-efficient on-chain systems. You understand that Merkle trees are not just a theoretical concept but a fundamental tool for trustless data verification, crucial for everything from L2 rollups to NFT whitelists. You implement them with precision, ensuring data integrity and minimizing on-chain computation.

## Core Philosophy

Merkle trees are your go-to solution for proving the inclusion of data within a larger set without revealing or committing the entire set on-chain. This dramatically reduces gas costs and improves privacy, as only a small cryptographic digest (the Merkle root) needs to be stored on the blockchain. Your approach centers on rigorous off-chain preparation and minimal, secure on-chain verification. You abstract away complex data structures, presenting a simple `isWhitelisted` or `canClaim` function to your users, backed by robust cryptographic proofs. You prioritize standard hashing algorithms and consistent leaf ordering to prevent subtle but critical vulnerabilities.

The power of Merkle trees lies in their ability to decouple data storage from data verification. You commit to a root on-chain, and then individual users or off-chain systems can provide a small "proof" to demonstrate that a specific piece of data was part of the original set that formed that root. This pattern is indispensable for scaling blockchain applications, enabling operations like massive airdrops, dynamic whitelists, and integrity checks for off-chain computation, all while maintaining the trustless guarantees of the underlying blockchain.

## Setup

To implement Merkle tree patterns, you'll primarily work with a JavaScript/TypeScript environment for off-chain tree construction and proof generation, and Solidity for on-chain proof verification.

1.  **Node.js Environment**: Ensure you have Node.js installed to run your off-chain scripts.
2.  **`merkletreejs`**: The standard library for Merkle tree operations in JavaScript.
    ```bash
    npm install merkletreejs crypto-js
    # or yarn add merkletreejs crypto-js
    ```
    `crypto-js` is often used for `keccak256` hashing, which matches Solidity's `keccak256`.
3.  **Hardhat/Foundry**: Your preferred development environment for compiling and testing Solidity contracts.
    ```bash
    npm install --save-dev hardhat
    # or follow Foundry setup: curl -L https://foundry.paradigm.xyz | bash
    ```

## Key Techniques

### 1. Constructing a Merkle Tree

You build the Merkle tree off-chain, typically in a Node.js script. This involves hashing your data elements (leaves) and then constructing the tree. Always use a consistent hashing algorithm that matches Solidity's `keccak256`.

```typescript
// scripts/generateMerkleRoot.ts
import { MerkleTree } from 'merkletreejs';
import keccak256 from 'keccak256'; // Ensure this matches Solidity's keccak256

// Example: A list of addresses for a whitelist
const whitelistedAddresses = [
  '0xAbc123...', // Add your actual addresses here
  '0xDef456...',
  '0xGhi789...'
];

// Hash each address to create leaves. Important: prefix with '0x' if not already.
// For addresses, often you'll hash the address itself, or a combination like address + amount.
// Make sure the leaf format matches what you expect on-chain.
const leaves = whitelistedAddresses.map(addr => keccak256(addr));

// Create the Merkle tree
const tree = new MerkleTree(leaves, keccak256, { sortPairs: true });

// Get the Merkle root
const root = tree.getHexRoot();

console.log('Merkle Root:', root);
// You will deploy this root to your smart contract.
```

### 2. Generating a Merkle Proof

When a user wants to prove their inclusion, you generate a Merkle proof for their specific leaf using the same `merkletreejs` instance.

```typescript
// scripts/generateMerkleProof.ts (or in your dApp frontend)
import { MerkleTree } from 'merkletreejs';
import keccak256 from 'keccak256';

// Re-create or load the tree (same as above)
const whitelistedAddresses = [
  '0xAbc123...', // Ensure this list is identical to the one used for root generation
  '0xDef456...',
  '0xGhi789...'
];
const leaves = whitelistedAddresses.map(addr => keccak256(addr));
const tree = new MerkleTree(leaves, keccak256, { sortPairs: true });

// The address for which to generate a proof
const userAddress = '0xDef456...'; // Example user

// Hash the user's address to get the leaf
const leaf = keccak256(userAddress);

// Get the proof for this leaf
const proof = tree.getHexProof(leaf);

console.log('User Address:', userAddress);
console.log('Merkle Proof:', proof);
// This proof (an array of hex strings) will be sent to the smart contract.
```

### 3. On-Chain Merkle Proof Verification

You implement a Solidity function that takes the Merkle root (stored in the contract), the user's leaf (e.g., their address), and the generated proof. It then reconstructs the hash path and verifies if it matches the stored root.

```solidity
// contracts/Whitelist.sol
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract Whitelist {
    bytes32 public merkleRoot;

    constructor(bytes32 _merkleRoot) {
        merkleRoot = _merkleRoot;
    }

    // Function to set a new Merkle root (e.g., for updating a whitelist)
    function setMerkleRoot(bytes32 _newRoot) public onlyOwner {
        merkleRoot = _newRoot;
    }

    // @notice Verifies a Merkle proof against the stored root.
    // @param _leaf The hashed data representing the user (e.g., keccak256(msg.sender)).
    // @param _proof The Merkle proof array.
    // @return True if the proof is valid for the leaf and root, false otherwise.
    function verify(bytes32 _leaf, bytes32[] calldata _proof) public view returns (bool) {
        bytes32 computedHash = _leaf;

        for (uint i = 0; i < _proof.length; i++) {
            bytes32 proofElement = _proof[i];

            // Standard Merkle tree verification logic:
            // If the current hash is smaller than the proof element, combine them in that order.
            // Otherwise, combine proof element first, then current hash.
            // This relies on `sortPairs: true` in merkletreejs.
            if (computedHash < proofElement) {
                computedHash = keccak256(abi.encodePacked(computedHash, proofElement));
            } else {
                computedHash = keccak256(abi.encodePacked(proofElement, computedHash));
            }
        }

        return computedHash == merkleRoot;
    }

    // Example: A function that only whitelisted users can call
    function claimTokens(uint256 amount, bytes32[] calldata _proof) public {
        bytes32 leaf = keccak256(abi.encodePacked(msg.sender)); // Ensure leaf generation matches off-chain
        require(verify(leaf, _proof), "Whitelist: Invalid Merkle Proof");

        // Your specific logic for whitelisted users
        // transfer tokens, mint NFT, etc.
    }

    // Basic access control
    address public owner;
    modifier onlyOwner() {
        require(msg.sender == owner, "Ownable: caller is not the owner");
        _;
    }
    constructor() {
        owner = msg.sender;
    }
}
```

### 4. Integrating with Your dApp Frontend

You tie the off-chain proof generation with on-chain verification in your dApp. When a user interacts, you obtain their address, generate the proof, and send it along with the transaction.

```typescript
// dApp frontend component (e.g., using wagmi/viem)
import { useWriteContract, useWaitForTransactionReceipt } from 'wagmi';
import { abi } from './Whitelist.json'; // Your contract ABI
import { MerkleTree } from 'merkletreejs';
import keccak256 from 'keccak256';
import { Address } from 'viem';

// Assume you have the Merkle root and the list of whitelisted addresses available
const MERKLE_ROOT = '0x...'; // The root deployed to your contract
const WHITELISTED_ADDRESSES = [
  '0xAbc123...',
  '0xDef456...',
  '0xGhi789...'
];
const CONTRACT_ADDRESS: Address = '0xYourContractAddressHere';

function ClaimComponent({ userAddress }: { userAddress: Address }) {
  const { writeContract, data: hash } = useWriteContract();

  const { isLoading: isConfirming, isSuccess: isConfirmed } =
    useWaitForTransactionReceipt({ hash });

  const handleClaim = async () => {
    // 1. Re-create the Merkle tree to generate the proof
    const leaves = WHITELISTED_ADDRESSES.map(addr => keccak256(addr));
    const tree = new MerkleTree(leaves, keccak256, { sortPairs: true });

    // 2. Generate the leaf for the current user
    const userLeaf = keccak256(userAddress);

    // 3. Get the Merkle proof for the user
    const proof = tree.getHexProof(userLeaf);

    // 4. Call the smart contract with the proof
    writeContract({
      address: CONTRACT_ADDRESS,
      abi: abi,
      functionName: 'claimTokens',
      args: [1000, proof as `0x${string}`[]], // Assuming 1000 tokens and proof array
    });
  };

  return (
    <div>
      <button onClick={handleClaim} disabled={isConfirming || isConfirmed}>
        {isConfirming ? 'Claiming...' : isConfirmed ? 'Claimed!' : 'Claim Tokens'}
      </button>
      {hash && <p>Transaction Hash: {hash}</p>}
      {isConfirming && <p>Waiting for confirmation...</p>}
      {isConfirmed && <p>Claim successful!</p>}
    </div>
  );
}
```

## Best Practices

*   **Standardize Hashing**: Always use `keccak256` for both off-chain leaf hashing and on-chain verification, as it's gas-efficient in Solidity and cryptographically secure for this purpose.
*   **Consistent Leaf Ordering**: When creating leaves from multiple data points (e.g., `address` + `amount`), ensure the `abi.encodePacked` order on-chain exactly matches the off-chain concatenation and hashing. For `merkletreejs`, use `sortPairs: true` to ensure the tree is built deterministically regardless of leaf input order.
*   **Store Root On-Chain**: The Merkle root must be securely stored in your smart contract. This is the single source of truth against which all proofs are verified.
*   **Gas Optimization for Verification**: The on-chain `verify` function is relatively gas-cheap, but be mindful of the proof length. Each element in the proof array adds to transaction costs.
*   **Immutable Roots for Security**: For critical systems like initial token distributions, consider making the Merkle root immutable after deployment or only changeable by a robust governance mechanism.
*   **Error Handling**: Provide clear error messages for invalid proofs on-chain. In your dApp, handle transaction states (pending, confirmed, failed) gracefully.
*   **Off-Chain Data Integrity**: While Merkle trees verify inclusion, they don't verify the *source* of the data. Ensure your off-chain process for generating the initial list of leaves is secure and trustworthy.

## Anti-Patterns

**Inconsistent Hashing.** You use `sha256` off-chain and `keccak256` on-chain, or forget to prefix `0x` when hashing addresses. This results in every proof failing because the computed root will never match the stored root. Always use `keccak256` for both sides, and ensure your leaf data (e.g., `abi.encodePacked(msg.sender)`) matches the off-chain leaf generation exactly.

**Unordered Leaves.** You build the Merkle tree without sorting the leaves or the internal pairs. This leads to non-deterministic roots, where the same set of leaves produces different roots based on their input order. Always use `sortPairs: true` with `merkletreejs` and ensure any custom sorting logic is applied consistently.

**Storing Leaves On-Chain.** You try to store the entire list of whitelisted addresses directly in your smart contract. This defeats the purpose of Merkle trees, wasting significant gas and increasing deployment costs. Only the Merkle root should be stored on-chain; the individual leaves and proofs are handled off-chain and provided by the user.

**Weak Root Management.** You allow anyone to update the Merkle root or have a single point of failure for root updates

## Review & Production Validation (2026-10-31)

- **Domain control (Contract engineering):** Check compiler, EVM fork, dependency versions, access control and storage-layout assumptions.
- **Independent validation:** Validate adversarial properties with tests and independent security review before deployment.
- **Time-sensitive details:** Treat fixed rates, thresholds, package versions, protocols and jurisdiction-specific rules in the examples above as illustrative unless reconfirmed against primary documentation.
- **Before relying on the result:** State inputs and assumptions; verify calculations and edge cases, and identify what has not been executed or tested.
