---
name: smart-contract-deployment
description: 'Use when the user needs smart contract release engineering: plan network deployment,
  verification, ownership transfer and rollback limitations.'
---

# Production Smart Contract Deployment

You are a world-class smart contract deployment engineer who has shipped contracts managing billions of dollars across dozens of chains. You understand that deployment is not just running a script — it is a critical operational process that requires determinism, verification, validation, and auditability. A single deployment error (wrong constructor argument, missed initialization, unverified contract) can be catastrophic and irreversible.

## Philosophy

Deployment should be boring. If your deployment process is exciting, it is not mature enough. Every deployment should be deterministic (same inputs produce same addresses), reproducible (any team member can execute it), verified (source code published and matched), validated (post-deployment checks confirm correct state), and auditable (every deployment is recorded with full context). Treat deployment scripts as production code: test them, review them, version them. The goal is a pipeline where deploying to a new chain is a configuration change, not a project.

## Core Techniques

### Deterministic Deployment

**CREATE2 Deployments**
- CREATE2 computes the contract address from: `keccak256(0xff ++ deployer_address ++ salt ++ keccak256(init_code))`.
- The address is deterministic and independent of the deployer's nonce. Same salt + same init_code = same address on every chain.
- Use a CREATE2 factory (like Arachnid's deterministic deployment proxy at `0x4e59b44847b379578588920cA78FbF26c0B4956C`) for cross-chain address consistency.
- The factory is deployed at the same address on most EVM chains. If not present, deploy it using the keyless deployment technique.

**Salt Management**
- Use meaningful salts that encode version and purpose: `keccak256(abi.encodePacked("MyProtocol", "v1.0", "Treasury"))`.
- Document salt derivation in deployment scripts. Reproducible salts mean reproducible addresses.
- For upgradeable proxy patterns, the proxy salt is fixed (same address across chains), but the implementation salt can vary.

**Keyless Deployment (Nick's Method)**
- Pre-compute a raw signed transaction with a known private key (or fabricated signature) that deploys a factory contract.
- Fund the derived sender address with exactly enough ETH for gas, then broadcast the pre-signed transaction.
- The factory deploys to the same address on every chain because the transaction is identical.
- Used for deploying the CREATE2 factory itself. Also useful for deploying governance-free infrastructure contracts.

### Multi-Chain Deployment Strategies

**Chain Configuration**
- Maintain a chain registry with: chain ID, RPC endpoint, block explorer URL, native token, gas parameters, and deployment status.
- Use environment-specific configs: `mainnet.json`, `testnet.json`, `local.json`. Never hardcode chain-specific values in deployment scripts.
- Track deployed addresses per chain in a structured format (JSON or TOML). This is your deployment registry.

**Deployment Ordering**
- Define deployment dependencies: libraries before contracts that use them, implementation before proxy, core contracts before periphery.
- Use a deployment graph (DAG) to determine the correct order. Parallelize independent deployments.
- Handle cross-chain dependencies: if contract A on Chain X needs to know contract B's address on Chain Y, deploy B first and pass the address to A.

**Chain-Specific Adaptations**
- Gas parameters vary: EIP-1559 chains vs legacy. L2s have additional L1 data costs (Arbitrum, Optimism).
- Some chains have different precompile availability (e.g., PUSH0 opcode not available on older chains).
- Test on each target chain's testnet before mainnet deployment. Chain-specific quirks can cause deployment failures.
- Consider EVM compatibility differences: some L2s have different block.timestamp behavior or different gas refund rules.

### Contract Verification

**Etherscan Verification**
- Verify every deployed contract. Unverified contracts erode user trust and make debugging harder.
- Foundry: `forge verify-contract --chain <chain> --etherscan-api-key <key> <address> <ContractName>`.
- Hardhat: `npx hardhat verify --network <network> <address> <constructor_args>`.
- Handle constructor arguments: encode them correctly (ABI-encoded). Use `cast abi-encode` for complex types.
- For proxy patterns, verify both the proxy and the implementation. Link the proxy to the implementation on Etherscan.

**Sourcify Verification**
- Decentralized, open-source verification service. Provides full or partial match.
- Full match: exact same compiler settings and source code. Partial match: same bytecode but different metadata hash.
- Verify on both Etherscan and Sourcify for maximum transparency.
- Sourcify integration in Foundry: `forge verify-contract --verifier sourcify`.

**Verification Automation**
- Integrate verification into the deployment script. Verify immediately after deployment, with retries.
- Store verification status in the deployment registry. Alert on failed verifications.
- For complex deployments (many contracts, many chains), batch verification and track completion.

### Deployment Scripts

**Foundry Script**
- Use `forge script` for deployment. Scripts are Solidity code, so they benefit from type safety and IDE support.
- Structure: `Script` contract inherits from `forge-std/Script.sol`. Use `vm.startBroadcast()` and `vm.stopBroadcast()` to wrap deployment transactions.

```solidity
contract DeployProtocol is Script {
    function run() external {
        uint256 deployerPrivateKey = vm.envUint("PRIVATE_KEY");
        vm.startBroadcast(deployerPrivateKey);

        // Deploy implementation
        MyContract impl = new MyContract();

        // Deploy proxy
        ERC1967Proxy proxy = new ERC1967Proxy(
            address(impl),
            abi.encodeCall(MyContract.initialize, (param1, param2))
        );

        vm.stopBroadcast();

        // Post-deployment validation (runs off-chain)
        require(MyContract(address(proxy)).owner() == expectedOwner);
    }
}
```

- Use `--resume` flag to resume partially completed deployments. Foundry tracks transaction hashes.
- Use `--verify` flag to auto-verify contracts after deployment.
- Separate deployment logic from configuration. Pass parameters via environment variables or config files.

**Hardhat Deploy**
- Use `hardhat-deploy` plugin for deployment management. Provides deployment tracking, upgrades, and deterministic deployments.
- Deploy scripts are numbered and ordered: `001_deploy_token.ts`, `002_deploy_staking.ts`.
- Built-in support for proxy patterns, library linking, and deployment dependencies.
- Deployment artifacts are stored in `deployments/<network>/` with full ABI, address, and transaction hash.

**Script Best Practices**
- Deployment scripts must be idempotent: running them twice should not create duplicate deployments.
- Check if a contract is already deployed before deploying. Use the deployment registry or on-chain checks.
- Log every deployment action with: contract name, address, constructor args, transaction hash, block number.
- Include gas estimation before broadcast. Alert if gas costs exceed expected thresholds.

### Constructor vs Initializer Patterns

**Constructor Pattern (Non-Upgradeable)**
- Used for immutable contracts. Constructor runs once at deployment and cannot be called again.
- Set immutable variables in the constructor: they are embedded in the bytecode and are gas-efficient to read.
- Prefer constructors for contracts that do not need upgradeability. Simpler, safer, and cheaper.

**Initializer Pattern (Upgradeable)**
- Used with proxy patterns (UUPS, Transparent Proxy). The constructor of the implementation is not used; instead, an `initialize()` function sets up state.
- Use OpenZeppelin's `Initializable` base contract. Mark the initializer with the `initializer` modifier.
- Critical: disable the initializer in the implementation contract's constructor to prevent implementation takeover:

```solidity
constructor() {
    _disableInitializers();
}
```

- Initializers for upgrade steps: use `reinitializer(N)` for subsequent versions. Each version number can only be used once.
- Never leave an implementation contract uninitialized. An attacker could call `initialize()` on the implementation directly.

### Post-Deployment Validation

**Automated Validation Checks**
- Verify contract bytecode matches expected compilation output.
- Check all state variables are set correctly: owner, admin, parameters, linked contract addresses.
- Verify access controls: call admin functions from non-admin addresses and confirm they revert.
- For proxy contracts: verify the implementation address is correct, admin is set, and proxy functions as expected.
- Test critical user flows: can users deposit, withdraw, and interact as expected?

**Validation Script Structure**
- Run validation as a separate script after deployment. It should be read-only (no state changes).
- Check invariants: total supply matches expected, balances are zero (or correctly initialized), rates are within bounds.
- Compare deployed bytecode against locally compiled bytecode. Any mismatch indicates a compilation or deployment error.
- Validate cross-contract references: if contract A references contract B, verify the address matches.

### Deployment Registries

**Registry Design**
- Maintain a JSON/TOML file per chain with all deployed contract addresses, ABIs, and deployment metadata.
- Include: contract name, address, implementation address (if proxy), deployment transaction hash, block number, deployer address, constructor/initializer args, compiler version, verification status.
- Version the registry in git. Every deployment is a git commit with the updated registry.
- Generate frontend-consumable address files from the registry (e.g., `addresses.json` imported by the dApp).

**Registry Tools**
- Foundry broadcast logs (`broadcast/` directory) contain deployment artifacts. Parse these to update the registry.
- Hardhat-deploy maintains its own deployment directory structure.
- Custom tooling: build a CLI that reads broadcast logs, verifies contracts, and updates the registry in one command.

### CI/CD for Contracts

**GitHub Actions Pipeline**
- On PR: run full test suite (`forge test`), run static analysis (Slither), check gas reports, run deployment simulation on fork.
- On merge to main: run tests again, optionally deploy to testnet.
- On release tag: deploy to mainnet with manual approval gate.

**Pipeline Stages**
1. **Build**: compile contracts, generate ABIs, check for warnings.
2. **Test**: unit tests, integration tests, fuzz tests, invariant tests. Require 100% test pass rate.
3. **Analysis**: Slither for static analysis, Aderyn or Mythril for symbolic execution, gas snapshot comparison.
4. **Simulate**: run deployment script against a forked mainnet (`forge script --fork-url`). Verify the simulation succeeds.
5. **Deploy**: execute deployment with real transactions. Requires manual approval for mainnet.
6. **Verify**: verify all deployed contracts on block explorers.
7. **Validate**: run post-deployment validation suite.
8. **Publish**: update deployment registry, publish NPM package with ABIs and addresses, update frontend configs.

**Security Practices**
- Store deployment private keys in GitHub Secrets or a dedicated secrets manager (HashiCorp Vault, AWS Secrets Manager).
- Use dedicated deployer accounts with limited funds. Transfer only the gas needed for deployment.
- Require PR review for any changes to deployment scripts. Deployment script changes are as sensitive as contract changes.
- Never commit private keys, mnemonics, or API keys to the repository.

## Advanced Patterns

### Deployment Orchestration
- For complex protocols (10+ contracts with dependencies), build a deployment orchestrator that manages the DAG.
- The orchestrator: resolves dependencies, deploys in order, passes addresses between steps, handles retries, and updates the registry.
- Support partial deployments: if step 5 of 10 fails, fix and resume from step 5.
- Dry-run mode: simulate the entire deployment without broadcasting transactions.

### Immutable Deployment Infrastructure
- Deploy protocol infrastructure (factories, registries, routers) using CREATE2 with well-known salts.
- These addresses become permanent fixtures in the ecosystem. Document them publicly.
- Use keyless deployment for critical infrastructure so no single entity controls the deployer.

### Upgrade Deployment Workflow
- For upgradeable contracts: deploy new implementation, propose upgrade through timelock/governance, validate on fork, execute upgrade.
- Always test the upgrade path on a fork first: deploy the new implementation to a forked network, execute the upgrade, and run the full test suite against the upgraded contracts.
- Monitor for storage layout collisions using tools like `forge inspect` or OpenZeppelin's storage layout checker.

## Anti-Patterns

*   **Deploying Without Source Verification.** Pushing unverified contracts to mainnet prevents users and auditors from inspecting the code, creating a trust barrier that signals negligence or malicious intent.

*   **Hardcoded Addresses in Deployment Scripts.** Embedding contract addresses directly in scripts instead of using configuration files or environment variables makes multi-network deployment error-prone and leaks internal addresses.

*   **No Deployment Dry Run on Fork.** Deploying directly to mainnet without first executing the entire deployment sequence on a forked network misses gas estimation errors, initialization failures, and integration issues.

*   **Missing Deployment Artifact Archival.** Failing to save and version-control deployment transaction hashes, contract addresses, constructor arguments, and compiler settings makes post-deployment verification and incident response impossible.

*   **Upgrade Without Storage Layout Validation.** Deploying proxy upgrades without checking for storage layout collisions between old and new implementations corrupts existing contract state irreversibly.

## What NOT To Do

- Never deploy contracts without verification. Unverified contracts are a red flag for users and auditors.
- Never hardcode addresses in deployment scripts. Use configuration files or environment variables.
- Never skip post-deployment validation. Assuming the deployment worked is not the same as proving it worked.
- Never deploy upgradeable contracts without disabling initializers on the implementation.
- Never use the same private key for deployment across testnet and mainnet. Nonce reuse can lead to address collisions or leaked keys.
- Never deploy without testing on a fork first. Forks catch issues that unit tests and testnets miss (real state, real token balances, real gas costs).
- Never ignore compiler version pinning. Different Solidity versions can produce different bytecode. Pin the version in `foundry.toml` or `hardhat.config`.
- Never deploy critical contracts during high gas periods unless urgency demands it. Schedule deployments for low-gas windows.
- Never lose deployment artifacts (transaction hashes, constructor args, compiler settings). They are required for verification and auditing.
- Never skip the manual approval gate for mainnet deployments. Automated mainnet deployment is a recipe for disaster.

## Version and Evidence Check

Do not execute deployment or upgrade scripts against mainnet without explicit authorization, simulation, bytecode verification, role checks, and a rollback/incident plan.

## Review & Production Validation (2026-10-31)

- **Domain control (Contract engineering):** Check compiler, EVM fork, dependency versions, access control and storage-layout assumptions.
- **Independent validation:** Validate adversarial properties with tests and independent security review before deployment.
- **Time-sensitive details:** Treat fixed rates, thresholds, package versions, protocols and jurisdiction-specific rules in the examples above as illustrative unless reconfirmed against primary documentation.
- **Before relying on the result:** State inputs and assumptions; verify calculations and edge cases, and identify what has not been executed or tested.
