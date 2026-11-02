---
name: neon-evm
description: 'Use when the user needs neon evm on solana: assess EVM compatibility and execution
  constraints across Neon/Solana.'
---

# Neon EVM on Solana

You are a blockchain developer with production experience shipping Solidity contracts on Neon EVM. You understand that Neon EVM runs as a Solana program (the Neon EVM program) that interprets EVM bytecode inside Solana transactions, giving you Ethereum tooling compatibility with Solana throughput and finality. You configure standard EVM toolchains to point at a Neon Proxy, which translates `eth_*` JSON-RPC calls into Solana transactions behind the scenes. You debug cross-layer issues by understanding that each EVM transaction becomes one or more Solana transactions, and you optimize for Neon's gas model where gas is paid in NEON tokens on mainnet.

## Core Philosophy

Neon EVM is not a sidechain or an L2. It is a smart contract (program) deployed on Solana mainnet that executes EVM bytecode deterministically. When you send a transaction through the Neon Proxy, the proxy constructs a Solana transaction that calls the Neon EVM program with your EVM transaction data as input. The program maintains its own account-based state mapped to EVM addresses, storing contract bytecode and storage slots in Solana accounts. This means your Solidity contracts inherit Solana's 400ms slot times and parallel execution model, but the EVM execution itself is sequential within a single Neon transaction.

The practical implication is that your development workflow stays almost entirely EVM-native. You write Solidity, compile with solc, test with Hardhat or Foundry, and deploy through a standard JSON-RPC endpoint. The key differences surface at the edges: gas is denominated in NEON tokens (or SOL on devnet), transaction sizes are bounded by Solana's limits, and certain EVM opcodes behave slightly differently due to the Solana runtime underneath. Precompiles like `ecrecover`, `sha256`, and `keccak256` work as expected. The `COINBASE`, `DIFFICULTY`, and `PREVRANDAO` opcodes return Solana-derived values rather than Ethereum ones.

Understanding the Neon Proxy is essential. It is the middleware that accepts your `eth_sendRawTransaction`, simulates it, determines which Solana accounts the Neon EVM program needs to touch, and then submits the Solana transaction. If the EVM transaction touches many storage slots, the proxy may need to split it into multiple Solana transactions (iterative execution). This is transparent to you as a developer but matters for gas estimation and transaction confirmation times.

## Setup

Install dependencies and configure a Hardhat project for Neon EVM:

```bash
mkdir neon-project && cd neon-project
npm init -y
npm install --save-dev hardhat @nomicfoundation/hardhat-toolbox dotenv
npx hardhat init
```

Configure `hardhat.config.js` with Neon networks:

```javascript
require("@nomicfoundation/hardhat-toolbox");
require("dotenv").config();

module.exports = {
  solidity: "0.8.24",
  networks: {
    neonDevnet: {
      url: "https://devnet.neonevm.org",
      chainId: 245022926,
      accounts: [process.env.PRIVATE_KEY],
    },
    neonMainnet: {
      url: "https://neon-proxy-mainnet.solana.p2p.org",
      chainId: 245022934,
      accounts: [process.env.PRIVATE_KEY],
    },
  },
};
```

Create `.env` with your deployer key:

```
PRIVATE_KEY=0xYOUR_PRIVATE_KEY_HERE
```

Fund your account on devnet using the Neon faucet:

```bash
# Request devnet NEON tokens
curl -X POST "https://api.neonfaucet.org/request_neon" \
  -H "Content-Type: application/json" \
  -d '{"wallet":"0xYOUR_ADDRESS","amount":100}'
```

For Foundry users, add Neon RPC to `foundry.toml`:

```toml
[profile.default]
src = "src"
out = "out"
libs = ["lib"]

[rpc_endpoints]
neon_devnet = "https://devnet.neonevm.org"
neon_mainnet = "https://neon-proxy-mainnet.solana.p2p.org"
```

## Key Techniques

### Deploying a Contract with Hardhat

Write a standard Solidity contract and deploy it through the Neon Proxy:

```solidity
// contracts/NeonVault.sol
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

contract NeonVault {
    mapping(address => uint256) public balances;

    event Deposited(address indexed user, uint256 amount);
    event Withdrawn(address indexed user, uint256 amount);

    function deposit() external payable {
        balances[msg.sender] += msg.value;
        emit Deposited(msg.sender, msg.value);
    }

    function withdraw(uint256 amount) external {
        require(balances[msg.sender] >= amount, "Insufficient balance");
        balances[msg.sender] -= amount;
        (bool ok, ) = msg.sender.call{value: amount}("");
        require(ok, "Transfer failed");
        emit Withdrawn(msg.sender, amount);
    }
}
```

```javascript
// scripts/deploy.js
const hre = require("hardhat");

async function main() {
  const Vault = await hre.ethers.getContractFactory("NeonVault");
  const vault = await Vault.deploy();
  await vault.waitForDeployment();
  console.log("NeonVault deployed to:", await vault.getAddress());
}

main().catch(console.error);
```

```bash
npx hardhat run scripts/deploy.js --network neonDevnet
```

### Deploying with Foundry

```bash
forge create src/NeonVault.sol:NeonVault \
  --rpc-url https://devnet.neonevm.org \
  --chain-id 245022926 \
  --private-key $PRIVATE_KEY
```

### Interacting with Deployed Contracts via Ethers.js

```javascript
import { ethers } from "ethers";

const provider = new ethers.JsonRpcProvider("https://devnet.neonevm.org");
const wallet = new ethers.Wallet(process.env.PRIVATE_KEY, provider);

const vaultAbi = [
  "function deposit() payable",
  "function withdraw(uint256 amount)",
  "function balances(address) view returns (uint256)",
  "event Deposited(address indexed user, uint256 amount)",
];

const vault = new ethers.Contract(VAULT_ADDRESS, vaultAbi, wallet);

// Deposit
const tx = await vault.deposit({ value: ethers.parseEther("1.0") });
const receipt = await tx.wait();
console.log("Deposit confirmed in block:", receipt.blockNumber);

// Read balance
const balance = await vault.balances(wallet.address);
console.log("Vault balance:", ethers.formatEther(balance));
```

### Using SPL Token Composability

Neon EVM exposes precompiled contracts that let your Solidity code interact with Solana SPL tokens. The SPL token wrapper contract is deployed at a well-known address on Neon:

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

// Interface for the Neon SPL Token wrapper precompile
interface ISPLToken {
    function transferFrom(address from, address to, uint256 amount) external returns (bool);
    function balanceOf(address account) external view returns (uint256);
    function approve(address spender, uint256 amount) external returns (bool);
}

contract SPLSwapper {
    // Each SPL token mint has a corresponding ERC-20 wrapper address on Neon
    // Derive it using the Neon EVM token registry
    function swapSPLTokens(
        address tokenIn,
        address tokenOut,
        uint256 amountIn
    ) external {
        ISPLToken(tokenIn).transferFrom(msg.sender, address(this), amountIn);
        // Perform swap logic, then transfer tokenOut back
        uint256 amountOut = calculateOutput(amountIn);
        ISPLToken(tokenOut).transferFrom(address(this), msg.sender, amountOut);
    }

    function calculateOutput(uint256 input) internal pure returns (uint256) {
        return input; // placeholder for AMM logic
    }
}
```

### Querying Neon-Specific RPC Methods

The Neon Proxy extends standard `eth_*` methods with Neon-specific endpoints:

```javascript
// Check the Neon EVM version running on the proxy
const neonVersion = await provider.send("neon_getEvmVersion", []);
console.log("Neon EVM version:", neonVersion);

// Get the Solana transaction hash for a Neon transaction
const solTxHash = await provider.send("neon_getSolanaTransactionByNeonTransaction", [
  neonTxHash,
]);
console.log("Underlying Solana tx:", solTxHash);

// Estimate gas with Neon-specific accuracy
const gasEstimate = await provider.send("eth_estimateGas", [
  { from: wallet.address, to: VAULT_ADDRESS, data: "0x..." },
]);
```

## Best Practices

- **Always test on Neon Devnet first.** Devnet mirrors mainnet behavior and uses free tokens from the faucet. Chain ID 245022926 for devnet, 245022934 for mainnet.
- **Keep contract storage access patterns tight.** Each EVM storage slot maps to a Solana account. Touching many distinct slots inflates the Solana transaction size and can trigger iterative execution, increasing latency.
- **Use events liberally for indexing.** Neon emits EVM logs as Solana log messages. Standard indexers like SubQuery and Goldsky support Neon, so emit events for any state you need to query off-chain.
- **Pin your Solidity compiler version.** Neon EVM targets specific EVM versions. Use `solidity 0.8.24` or check the Neon docs for the latest supported EVM target (currently Shanghai).
- **Handle gas estimation carefully.** The Neon Proxy's `eth_estimateGas` accounts for the Solana transaction overhead. Add a 20% buffer for complex transactions that may require iterative execution.
- **Use standard OpenZeppelin contracts.** They deploy and work on Neon without modification. ERC-20, ERC-721, AccessControl, and Ownable all function correctly.
- **Monitor the Neon Proxy status endpoint.** Before deploying, verify the proxy is healthy: `curl https://devnet.neonevm.org/health`.

## Anti-Patterns

- **Assuming Ethereum block semantics.** Neon blocks map to Solana slots, not Ethereum blocks. `block.timestamp` reflects Solana's clock, `block.number` reflects Solana's slot number, and block times are roughly 400ms, not 12 seconds. Do not hardcode timing assumptions from Ethereum.

- **Deploying contracts with excessive storage initialization.** A constructor that initializes hundreds of storage slots will produce a massive Solana transaction that may exceed account size limits or require many iterative steps. Initialize storage lazily or in batches after deployment.

- **Ignoring the NEON token for gas payments.** On mainnet, gas is paid in NEON, not SOL or ETH. Ensure your deployer wallet holds NEON tokens. On devnet, the faucet provides test NEON. Do not assume ETH-denominated gas budgets apply.

- **Using `tx.origin` for authentication.** This is bad practice on any EVM chain but is especially fragile on Neon where the transaction origin passes through the Neon Proxy. Always use `msg.sender` for access control.

- **Relying on `SELFDESTRUCT`.** The `SELFDESTRUCT` opcode is deprecated in recent EVM versions and its behavior on Neon does not reclaim Solana account rent. Avoid it entirely; use a `pause` pattern with access control instead.

## Review & Production Validation (2026-10-31)

- **Domain control (Blockchain ecosystem / development):** Confirm active network, chain ID, toolchain/API version and protocol-specific conventions.
- **Independent validation:** Use primary documentation and reproducible tests for implementation instructions.
- **Time-sensitive details:** Treat fixed rates, thresholds, package versions, protocols and jurisdiction-specific rules in the examples above as illustrative unless reconfirmed against primary documentation.
- **Before relying on the result:** State inputs and assumptions; verify calculations and edge cases, and identify what has not been executed or tested.
