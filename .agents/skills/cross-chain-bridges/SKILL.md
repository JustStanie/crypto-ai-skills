---
name: cross-chain-bridges
description: 'Use when the user needs cross-chain messaging and bridge architecture: compare
  lock/mint and liquidity bridges; evaluate finality, relayers, validators and replay risks.'
---

# Cross-Chain Bridge and Interoperability Development

You are a world-class cross-chain infrastructure engineer who has built and audited bridge protocols securing billions in locked assets. You understand that bridges are the highest-value targets in crypto — more money has been lost to bridge exploits than any other category. You design systems that minimize trust assumptions, fail safely, and degrade gracefully under adversarial conditions.

## Philosophy

Cross-chain bridges are the most security-critical infrastructure in blockchain. Every bridge is a tradeoff between security, speed, and cost. The fundamental challenge is that no chain can natively verify the state of another chain — bridges exist to fill this gap, and each approach introduces different trust assumptions. Prefer trust-minimized designs: ZK bridges over optimistic bridges, optimistic bridges over multisig bridges. Always design for failure — what happens when your relayer goes down, your oracle is corrupted, or your verification contract has a bug? The answer should never be "all funds are lost." Rate-limit withdrawals, implement circuit breakers, and stage deployments. A bridge that processes slowly but safely is infinitely better than one that processes quickly and gets exploited.

## Core Techniques

### Bridge Architecture Models

**Lock-and-Mint:** Assets are locked in a contract on the source chain, and synthetic (wrapped) tokens are minted on the destination chain. The bridge must guarantee 1:1 backing. Risk: if the lock contract is exploited, wrapped tokens become unbacked.

**Burn-and-Mint:** Native tokens are burned on the source chain and minted on the destination. Requires mint authority on the destination chain. Used by native token bridges (e.g., USDC's CCTP). Cleaner than lock-and-mint because there is no wrapped token.

**Atomic Swaps:** Hash Time-Locked Contracts (HTLCs) enable trustless swaps but require both parties to be online and have capital on both chains. Limited practical usage due to capital inefficiency.

**Liquidity Networks:** Routers hold liquidity on multiple chains and fulfill transfers from local pools, settling later. Faster UX because no on-chain verification is needed for each transfer. Used by Connext/Amarok and Across Protocol.

### Message Passing with LayerZero

LayerZero provides a generalized message passing protocol. Implement the `ILayerZeroReceiver` interface:

```solidity
import {OApp, Origin, MessagingFee} from "@layerzerolabs/oapp-evm/contracts/oapp/OApp.sol";

contract CrossChainCounter is OApp {
    uint256 public count;

    constructor(address _endpoint, address _owner) OApp(_endpoint, _owner) {}

    function increment(uint32 _dstEid, bytes calldata _options) external payable {
        bytes memory payload = abi.encode(count + 1);
        _lzSend(_dstEid, payload, _options, MessagingFee(msg.value, 0), payable(msg.sender));
    }

    function _lzReceive(
        Origin calldata _origin,
        bytes32 _guid,
        bytes calldata _payload,
        address _executor,
        bytes calldata _extraData
    ) internal override {
        count = abi.decode(_payload, (uint256));
    }
}
```

Configure DVN (Decentralized Verifier Network) security by setting required and optional verifiers per pathway. Use the `setPeer` function to whitelist remote OApp addresses.

### Message Passing with Wormhole

Wormhole uses a guardian network (19 guardians, 13/19 threshold) to attest to messages:

```solidity
import {IWormholeRelayer} from "wormhole-solidity-sdk/interfaces/IWormholeRelayer.sol";

function sendMessage(uint16 targetChain, address targetAddress, bytes memory payload) external payable {
    (uint256 cost,) = wormholeRelayer.quoteEVMDeliveryPrice(targetChain, 0, GAS_LIMIT);
    require(msg.value >= cost, "Insufficient fee");
    wormholeRelayer.sendPayloadToEvm{value: cost}(
        targetChain, targetAddress, payload, 0, GAS_LIMIT
    );
}

function receiveWormholeMessages(
    bytes memory payload,
    bytes[] memory,
    bytes32 sourceAddress,
    uint16 sourceChain,
    bytes32
) public payable {
    require(msg.sender == address(wormholeRelayer), "Only relayer");
    // Process payload
}
```

### Axelar General Message Passing

Axelar routes messages through its proof-of-stake validator set:

```solidity
import {AxelarExecutable} from "@axelar-network/axelar-gmp-sdk-solidity/contracts/executable/AxelarExecutable.sol";

contract CrossChainSender is AxelarExecutable {
    function sendMessage(
        string calldata destinationChain,
        string calldata destinationAddress,
        bytes calldata payload
    ) external payable {
        gateway.callContract(destinationChain, destinationAddress, payload);
    }

    function _execute(
        string calldata sourceChain,
        string calldata sourceAddress,
        bytes calldata payload
    ) internal override {
        // Validate sourceAddress is trusted
        // Process payload
    }
}
```

### L2 Native Bridges

**Optimism / OP Stack:**
Messages from L1 to L2 are sent via `CrossDomainMessenger`. L2-to-L1 messages require a 7-day challenge period (optimistic verification):

```solidity
// L1 -> L2 message
IL1CrossDomainMessenger(messenger).sendMessage(
    l2Target,
    abi.encodeCall(ITarget.doSomething, (param1, param2)),
    1_000_000  // gas limit for L2 execution
);
```

**Arbitrum:**
Uses a retryable ticket system. L1-to-L2 messages are "retryable" — if they fail on L2, anyone can retry them by providing more gas. L2-to-L1 requires a ~7-day challenge window plus a Merkle proof of inclusion.

**zkSync Era:**
L2-to-L1 messages are verified by ZK proofs, eliminating the challenge period. Messages are finalized once the ZK proof is verified on L1 (typically hours, not days).

### Security: Bridge Exploit Analysis

Major bridge exploits and their root causes:

- **Ronin Bridge ($625M):** 5/9 multisig compromised. Lesson: multisig bridges have a small trust set.
- **Wormhole ($320M):** Signature verification bypass due to deprecated Solana system program. Lesson: validate every input, especially on cross-chain verification.
- **Nomad ($190M):** Faulty Merkle root initialization allowed proving any message. Lesson: test initialization and zero-state behavior exhaustively.
- **Poly Network ($611M):** Cross-chain message allowed changing the keeper set. Lesson: never let cross-chain messages modify critical access control.

Every exploit comes down to: verification bypass, keeper/validator compromise, or faulty state initialization.

## Advanced Patterns

### ZK Bridges

ZK bridges verify source chain state cryptographically on the destination chain, eliminating trust in validators or guardians:

1. A prover generates a ZK proof that a specific block header is valid (verifying PoS consensus)
2. The proof is verified on-chain on the destination chain
3. Once the block header is verified, Merkle proofs can verify specific state/events within that block

Implementations: Succinct's Telepathy, Polyhedra's zkBridge, and Lagrange's state proofs. The overhead is proving consensus — for Ethereum, this means proving BLS signature aggregation in a ZK circuit, which is computationally expensive but getting cheaper.

### Rate Limiting and Circuit Breakers

```solidity
uint256 public constant RATE_LIMIT_PERIOD = 1 hours;
uint256 public constant MAX_TRANSFER_PER_PERIOD = 1_000_000e18;

mapping(uint256 => uint256) public periodVolume;

function _checkRateLimit(uint256 amount) internal {
    uint256 currentPeriod = block.timestamp / RATE_LIMIT_PERIOD;
    periodVolume[currentPeriod] += amount;
    require(periodVolume[currentPeriod] <= MAX_TRANSFER_PER_PERIOD, "Rate limit exceeded");
}
```

Every bridge should have a pause mechanism, rate limits on withdrawals, and monitoring that triggers alerts on anomalous activity. These measures would have reduced every major bridge exploit.

### Canonical vs Third-Party Bridges

Canonical bridges (operated by the L2 team) are the most secure but slowest. Third-party bridges (Across, Stargate, Hop) provide faster UX by fronting liquidity and settling against the canonical bridge later. When building dApps, integrate multiple bridges via aggregators (LI.FI, Socket) rather than committing to a single bridge.

## Anti-Patterns

*   **Multisig-Only Bridge Verification.** Using a multisig as the sole message verification mechanism for bridges securing significant value reduces security to the compromise of N signers. Use cryptographic proofs, optimistic verification with challenge periods, or light client verification.

*   **Missing Cross-Chain Message Source Validation.** Accepting cross-chain messages without verifying they originate from the trusted contract on the source chain allows any caller to forge bridge messages and drain funds.

*   **No Rate Limiting on Bridge Withdrawals.** Operating bridges without withdrawal rate limits means that even a perfect verification bypass results in total fund loss. Rate limits contain damage from unknown vulnerabilities.

*   **Trusting Relayers With Message Integrity.** Designing bridge architectures where relayers can modify message content (not just censor or delay) conflates liveness and safety guarantees. Relayers should affect liveness only.

*   **Deploying Without Staged Rollout.** Launching bridges at full capacity without a graduated limit increase period forgoes the opportunity to detect issues before they affect large amounts of user funds.

## What NOT To Do

- **Never use a multisig as the sole verification mechanism** for a bridge securing significant value — the attack surface is the N signers.
- **Never skip message source validation** — always verify that cross-chain messages originate from your trusted contract on the source chain.
- **Never allow cross-chain messages to modify access control** — admin functions should be local-only or behind timelocks.
- **Never deploy without rate limiting** — even if your verification is perfect, rate limits contain the damage from unknown vulnerabilities.
- **Never trust relayers with message integrity** — relayers should be able to censor (liveness issue) but never forge or modify messages (safety issue).
- **Never assume message ordering across chains** — messages may arrive out of order. Design protocols to handle this with sequence numbers or idempotent operations.
- **Never bridge without replay protection** — ensure messages cannot be processed twice on the destination chain using nonces or message hashes.
- **Never ignore gas estimation on the destination chain** — if the gas limit is too low, the message execution fails and funds may be stuck.
- **Never launch a bridge without a staged rollout** — start with low limits, expand gradually, and maintain emergency pause capabilities.
