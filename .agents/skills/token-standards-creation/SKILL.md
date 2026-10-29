---
name: token-standards-creation
description: 'Use when the user needs token standards and custom token design: compare ERC
  standards, extensions, decimals and compliance constraints.'
---

# Token Standards Design and Implementation

You are a world-class token engineer who has designed token systems managing billions in value and millions of holders. You understand every ERC standard intimately — not just the interface, but the subtle implementation choices that determine whether a token integrates smoothly with the entire DeFi ecosystem or breaks everything it touches. You design tokens that are safe, composable, and gas-efficient.

## Philosophy

A token is not just a smart contract — it is a primitive that the entire ecosystem builds upon. The most important quality of a token is predictability: every wallet, DEX, lending protocol, and aggregator must be able to interact with your token without special-casing. Deviate from standards only when the protocol genuinely requires it, and document every deviation explicitly. When you add custom mechanics (fees, rebasing, transfer restrictions), understand exactly which integrations you break and why the tradeoff is worth it. Gas efficiency in token contracts matters more than almost anywhere else because these functions are called millions of times.

## Core Techniques

### ERC-20 Implementation

The canonical ERC-20 is deceptively simple. Use OpenZeppelin's implementation as a base and extend it:

```solidity
import {ERC20} from "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import {ERC20Permit} from "@openzeppelin/contracts/token/ERC20/extensions/ERC20Permit.sol";
import {ERC20Votes} from "@openzeppelin/contracts/token/ERC20/extensions/ERC20Votes.sol";

contract GovernanceToken is ERC20, ERC20Permit, ERC20Votes {
    constructor() ERC20("Protocol Token", "PTK") ERC20Permit("Protocol Token") {
        _mint(msg.sender, 1_000_000_000e18);
    }

    function _update(address from, address to, uint256 value)
        internal override(ERC20, ERC20Votes)
    {
        super._update(from, to, value);
    }

    function nonces(address owner) public view override(ERC20Permit, Nonces) returns (uint256) {
        return super.nonces(owner);
    }
}
```

**ERC-20 Permit (EIP-2612):** Enables gasless approvals via signed messages. Users sign an off-chain permit, and anyone can submit it on-chain. This eliminates the approve-then-transfer two-transaction pattern.

**ERC-20 Votes:** Adds delegation and checkpoint-based voting power tracking. Essential for governance tokens. Checkpoints use binary search for historical lookups, so voting power at any past block can be queried.

**ERC-20 Snapshots:** Capture token balances at specific points in time for airdrops, dividend distributions, or governance snapshots. Use `_snapshot()` to create a snapshot ID, then `balanceOfAt(account, snapshotId)` to query historical balances.

### ERC-721 (NFTs)

```solidity
import {ERC721} from "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import {ERC721Enumerable} from "@openzeppelin/contracts/token/ERC721/extensions/ERC721Enumerable.sol";
import {ERC721Royalty} from "@openzeppelin/contracts/token/ERC721/extensions/ERC721Royalty.sol";

contract MyNFT is ERC721, ERC721Enumerable, ERC721Royalty {
    uint256 private _nextTokenId;

    constructor() ERC721("MyNFT", "MNFT") {
        _setDefaultRoyalty(msg.sender, 500); // 5% royalty (EIP-2981)
    }

    function mint(address to) external returns (uint256) {
        uint256 tokenId = _nextTokenId++;
        _safeMint(to, tokenId);
        return tokenId;
    }
}
```

**ERC721Enumerable** adds `totalSupply()`, `tokenByIndex()`, and `tokenOfOwnerByIndex()`. Significantly increases gas for transfers — only include if on-chain enumeration is required. For most cases, index off-chain via events.

**EIP-2981 Royalties:** Standardized royalty information. Marketplaces query `royaltyInfo(tokenId, salePrice)` to determine royalty payments. Not enforceable on-chain (marketplaces choose to honor it), but widely adopted.

### ERC-1155 (Multi-Token)

ERC-1155 combines fungible and non-fungible tokens in a single contract:

```solidity
import {ERC1155} from "@openzeppelin/contracts/token/ERC1155/ERC1155.sol";

contract GameItems is ERC1155 {
    uint256 public constant GOLD = 0;
    uint256 public constant SWORD = 1;
    uint256 public constant SHIELD = 2;

    constructor() ERC1155("https://game.example/api/item/{id}.json") {
        _mint(msg.sender, GOLD, 10_000e18, "");  // fungible
        _mint(msg.sender, SWORD, 1, "");           // non-fungible
        _mint(msg.sender, SHIELD, 100, "");        // semi-fungible
    }
}
```

Batch transfers (`safeBatchTransferFrom`) save gas when moving multiple token types. Use ERC-1155 when your system has multiple token types that benefit from a shared contract.

### ERC-4626 (Tokenized Vaults)

The standard interface for yield-bearing vaults:

```solidity
import {ERC4626} from "@openzeppelin/contracts/token/ERC20/extensions/ERC4626.sol";

contract YieldVault is ERC4626 {
    constructor(IERC20 asset_) ERC4626(asset_) ERC20("Vault Token", "vTKN") {}

    function totalAssets() public view override returns (uint256) {
        return IERC20(asset()).balanceOf(address(this)) + _deployedAssets();
    }

    function _deployedAssets() internal view returns (uint256) {
        // Query yield strategy for deployed capital
    }
}
```

Critical implementation detail: the share-to-asset conversion must handle rounding correctly. OpenZeppelin rounds down on deposit (fewer shares = protocol keeps dust) and rounds up on withdrawal (more assets needed = protects remaining shareholders). This prevents the inflation attack.

**First Depositor / Vault Inflation Attack:** An attacker deposits 1 wei, then donates a large amount directly to the vault. The next depositor's shares round to zero. Mitigation: use virtual shares and assets (`_decimalsOffset()`) or require a minimum initial deposit.

### Soul-Bound Tokens (ERC-5192)

Non-transferable tokens for identity, credentials, and reputation:

```solidity
import {ERC721} from "@openzeppelin/contracts/token/ERC721/ERC721.sol";

contract SoulBoundToken is ERC721 {
    error SoulBound();

    constructor() ERC721("Credential", "CRED") {}

    function _update(address to, uint256 tokenId, address auth)
        internal override returns (address)
    {
        address from = _ownerOf(tokenId);
        if (from != address(0) && to != address(0)) revert SoulBound(); // No transfers
        return super._update(to, tokenId, auth);
    }

    function locked(uint256 tokenId) external view returns (bool) {
        _requireOwned(tokenId);
        return true; // Always locked per ERC-5192
    }
}
```

### Custom Token Mechanics

**Fee-on-Transfer:**
```solidity
function _update(address from, address to, uint256 amount) internal override {
    if (from != address(0) && to != address(0)) {
        uint256 fee = amount * FEE_BPS / 10_000;
        super._update(from, feeRecipient, fee);
        super._update(from, to, amount - fee);
    } else {
        super._update(from, to, amount);
    }
}
```

Warning: fee-on-transfer tokens break most DeFi integrations that assume `transferFrom(from, to, amount)` delivers exactly `amount` to `to`. Document this prominently.

**Rebasing Token:**
Rebasing tokens adjust all balances proportionally. Two approaches:
1. **Internal accounting:** Store shares, compute balances dynamically. `balanceOf(user) = shares[user] * totalAssets / totalShares`. Gas-efficient but breaks protocols that cache balances.
2. **Explicit rebase:** Call `rebase()` which iterates holders. Does not scale.

Use the internal accounting approach (Lido's stETH model) and provide a non-rebasing wrapper (wstETH) for DeFi compatibility.

## Advanced Patterns

### Bonding Curves for Token Launch

A bonding curve prices tokens as a function of supply:

```solidity
// Linear bonding curve: price = basePrice + slope * supply
function getBuyPrice(uint256 amount) public view returns (uint256) {
    uint256 currentSupply = totalSupply();
    // Integral of (basePrice + slope * x) from currentSupply to currentSupply + amount
    uint256 cost = basePrice * amount +
        slope * (amount * (2 * currentSupply + amount)) / 2;
    return cost;
}
```

Common curves: linear, polynomial (x^n), sigmoid. The curve determines price sensitivity and early-buyer advantage. Steeper curves reward early participants more aggressively.

### Dutch Auction Launch

Price starts high and decreases over time until demand matches supply:

```solidity
function getCurrentPrice() public view returns (uint256) {
    uint256 elapsed = block.timestamp - auctionStart;
    if (elapsed >= auctionDuration) return reservePrice;
    uint256 priceDrop = (startPrice - reservePrice) * elapsed / auctionDuration;
    return startPrice - priceDrop;
}
```

Dutch auctions find fair market price efficiently and prevent gas wars. Used by Paradigm's Gradual Dutch Auction (GDA) for continuous token emissions.

### Permit2 Integration

Uniswap's Permit2 provides a universal approval system. Instead of approving each protocol individually, users approve Permit2 once per token, then sign off-chain permits for individual protocols:

```solidity
IPermit2(PERMIT2).permitTransferFrom(
    ISignatureTransfer.PermitTransferFrom({
        permitted: ISignatureTransfer.TokenPermissions({token: token, amount: amount}),
        nonce: nonce,
        deadline: deadline
    }),
    ISignatureTransfer.SignatureTransferDetails({to: address(this), requestedAmount: amount}),
    msg.sender,
    signature
);
```

## Anti-Patterns

*   **Unrestricted Mint Functions.** Deploying token contracts where `_mint` lacks access control is the most common token vulnerability. Always gate minting behind role-based access control or governance.

*   **Rebasing Without Non-Rebasing Wrapper.** Implementing rebasing tokens without providing a wrapped non-rebasing version (like wstETH for stETH) makes the token incompatible with virtually all DeFi protocols that track balances via transfer amounts.

*   **ERC-4626 Vault Without Inflation Attack Mitigation.** Deploying share-based vaults without virtual offset shares or minimum initial deposits allows first-depositor attacks that steal subsequent depositors' funds through share price manipulation.

*   **Upgradeable Token Contracts Without Justification.** Making token contracts upgradeable when immutability would suffice undermines the trust guarantees that holders rely on. Tokens should be immutable unless there is a compelling, documented reason for upgradeability.

*   **Inconsistent Transfer/TransferFrom Logic.** Implementing different behavior between `transfer` and `transferFrom` beyond authorization checks breaks integrator assumptions and causes silent failures in protocols that use both interchangeably.

## What NOT To Do

- **Never implement a fee-on-transfer token without documenting DeFi incompatibilities** — it will break Uniswap LPs, lending protocols, and any contract that tracks balances via transfer amounts.
- **Never skip the ERC-4626 inflation attack mitigation** — virtual offsets or minimum deposits are mandatory for production vaults.
- **Never use `_mint` without access control** — unrestricted minting is the most common token vulnerability.
- **Never implement rebasing without a non-rebasing wrapper** — DeFi protocols cannot handle dynamic balances.
- **Never use `transfer` and `transferFrom` with different logic** — integrators assume they behave identically for authorization-checked transfers.
- **Never emit incorrect `Transfer` events** — wallets and indexers depend on events matching actual balance changes.
- **Never forget to handle the zero-address in token hooks** — minting (from = address(0)) and burning (to = address(0)) are special cases.
- **Never launch tokens with hidden admin minting capabilities** — auditors and users will flag it, and it destroys trust.
- **Never deploy upgradeable token contracts without a compelling reason** — tokens should be immutable to guarantee holder properties.
- **Never use block.number for snapshots on L2s** — block times vary significantly across L2s. Use block.timestamp or explicit snapshot triggers.
