---
name: staking-contracts
description: 'Use when the user needs staking contract design: design accrual, reward distribution,
  cooldowns, slashing and withdrawal logic.'
---

# Staking contract design

You are a battle-hardened DeFi architect who has designed, deployed, and secured staking protocols managing billions in value. You understand the delicate balance between economic incentives, security, and user experience. Your contracts are gas-efficient, upgradeable, and resilient against common exploits. You build staking solutions that are transparent, fair, and empower participants to earn rewards securely.

## Core Philosophy

Staking contracts are the backbone of many decentralized economies, incentivizing long-term holding and network participation. Your primary concern must be security: funds are locked, making these contracts prime targets for attackers. Design for upgradeability from day one, as economic parameters and security needs evolve. Rewards must be fair, transparent, and accurately calculated, often dynamically based on time or protocol activity. Always implement mechanisms like unbonding periods to prevent flash loan attacks and ensure network stability. Gas efficiency is paramount for frequently called functions like `stake`, `unstake`, and `claimRewards`, directly impacting user costs and protocol adoption.

## Setup

For developing and testing staking contracts, Foundry is your go-to framework. Its speed and Solidity-native testing environment are unmatched.

1.  **Install Foundry:**
    ```bash
    curl -L https://foundry.paradigm.xyz | bash
    foundryup
    ```

2.  **Initialize a new project:**
    ```bash
    forge init staking-project
    cd staking-project
    ```

3.  **Add OpenZeppelin Contracts (essential for security and standard patterns):**
    ```bash
    forge install OpenZeppelin/openzeppelin-contracts@v5.0.0 --no-commit
    ```
    Ensure your `foundry.toml`'s `libs` array includes `lib/openzeppelin-contracts/contracts`.

4.  **Configure `.env` for deployment:**
    ```
    # .env
    RPC_URL_SEPOLIA=https://sepolia.infura.io/v3/YOUR_INFURA_PROJECT_ID
    PRIVATE_KEY=YOUR_DEPLOYER_PRIVATE_KEY
    ETHERSCAN_API_KEY=YOUR_ETHERSCAN_API_KEY
    ```

## Key Techniques

### Basic Staking Contract Structure

A fundamental staking contract allows users to deposit tokens, track their stake, and potentially earn rewards.

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import {ERC20} from "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import {SafeERC20} from "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import {ReentrancyGuard} from "@openzeppelin/contracts/utils/ReentrancyGuard.sol";
import {Ownable} from "@openzeppelin/contracts/access/Ownable.sol";

contract SimpleStaking is ReentrancyGuard, Ownable {
    using SafeERC20 for IERC20;

    IERC20 public immutable stakingToken;
    uint256 public totalStaked;

    mapping(address => uint256) public stakedBalances;
    mapping(address => uint256) public lastStakeTime; // For reward calculation

    event Staked(address indexed user, uint256 amount);
    event Unstaked(address indexed user, uint256 amount);
    // Reward events will be added when implementing rewards

    constructor(address _stakingTokenAddress) Ownable(msg.sender) {
        require(_stakingTokenAddress != address(0), "Invalid staking token address");
        stakingToken = IERC20(_stakingTokenAddress);
    }

    function stake(uint256 amount) external nonReentrant {
        require(amount > 0, "Cannot stake 0");
        stakingToken.safeTransferFrom(msg.sender, address(this), amount);
        stakedBalances[msg.sender] += amount;
        totalStaked += amount;
        lastStakeTime[msg.sender] = block.timestamp; // Update for reward calculation
        emit Staked(msg.sender, amount);
    }

    function unstake(uint256 amount) external nonReentrant {
        require(amount > 0, "Cannot unstake 0");
        require(stakedBalances[msg.sender] >= amount, "Insufficient staked balance");

        stakedBalances[msg.sender] -= amount;
        totalStaked -= amount;
        stakingToken.safeTransfer(msg.sender, amount);
        emit Unstaked(msg.sender, amount);
    }
}
```

### Implementing Reward Distribution

Rewards can be calculated based on various factors (time, proportion of total stake, external oracle). A simple time-based, proportional reward system is common.

```solidity
// Add to SimpleStaking contract
uint256 public rewardRatePerSecond = 1000; // e.g., 1000 wei per second per unit of stake
IERC20 public immutable rewardToken; // If different from stakingToken

mapping(address => uint256) public userRewardPerTokenPaid;
mapping(address => uint256) public rewards;
uint256 public rewardPerTokenStored;
uint256 public lastUpdateTime;

constructor(address _stakingTokenAddress, address _rewardTokenAddress) Ownable(msg.sender) {
    require(_stakingTokenAddress != address(0) && _rewardTokenAddress != address(0), "Invalid token address");
    stakingToken = IERC20(_stakingTokenAddress);
    rewardToken = IERC20(_rewardTokenAddress);
}

function updateReward(address account) public {
    rewardPerTokenStored = getRewardPerToken();
    lastUpdateTime = block.timestamp;
    rewards[account] = earned(account);
    userRewardPerTokenPaid[account] = rewardPerTokenStored;
}

function getRewardPerToken() public view returns (uint256) {
    if (totalStaked == 0) {
        return rewardPerTokenStored;
    }
    return rewardPerTokenStored + (block.timestamp - lastUpdateTime) * rewardRatePerSecond * 1e18 / totalStaked;
}

function earned(address account) public view returns (uint256) {
    return stakedBalances[account] * (getRewardPerToken() - userRewardPerTokenPaid[account]) / 1e18 + rewards[account];
}

function stake(uint256 amount) external nonReentrant {
    updateReward(msg.sender); // Update rewards before new stake
    // ... (previous stake logic) ...
    emit Staked(msg.sender, amount);
}

function unstake(uint256 amount) external nonReentrant {
    updateReward(msg.sender); // Update rewards before unstake
    // ... (previous unstake logic) ...
    emit Unstaked(msg.sender, amount);
}

function claimRewards() external nonReentrant {
    updateReward(msg.sender);
    uint256 rewardAmount = rewards[msg.sender];
    require(rewardAmount > 0, "No rewards to claim");
    rewards[msg.sender] = 0;
    rewardToken.safeTransfer(msg.sender, rewardAmount);
    emit RewardsClaimed(msg.sender, rewardAmount);
}

event RewardsClaimed(address indexed user, uint256 amount);
```

### Unbonding Periods and Cooldowns

To prevent rapid withdrawal attacks or ensure network stability, implement an unbonding period where unstaked tokens are locked for a duration.

```solidity
// Add to SimpleStaking contract
uint256 public constant UNBONDING_PERIOD = 7 days; // Example: 7 days

struct UnstakeRequest {
    uint256 amount;
    uint256 withdrawableTime;
}

mapping(address => UnstakeRequest[]) public unstakeRequests;
mapping(address => uint256) public totalUnbondingAmount; // Track total amount pending withdrawal

event UnbondingInitiated(address indexed user, uint256 amount, uint256 withdrawableTime);
event UnbondClaimed(address indexed user, uint256 amount);


function initiateUnstake(uint256 amount) external nonReentrant {
    require(amount > 0, "Cannot unstake 0");
    require(stakedBalances[msg.sender] >= amount, "Insufficient staked balance");

    updateReward(msg.sender); // Update rewards before unbonding
    stakedBalances[msg.sender] -= amount;
    totalStaked -= amount;

    uint256 withdrawableTime = block.timestamp + UNBONDING_PERIOD;
    unstakeRequests[msg.sender].push(UnstakeRequest(amount, withdrawableTime));
    totalUnbondingAmount[msg.sender] += amount;

    emit UnbondingInitiated(msg.sender, amount, withdrawableTime);
}

function claimUnbonded() external nonReentrant {
    uint256 totalClaimable = 0;
    uint256 currentTimestamp = block.timestamp;
    UnstakeRequest[] storage requests = unstakeRequests[msg.sender];

    for (uint256 i = 0; i < requests.length; ) {
        if (currentTimestamp >= requests[i].withdrawableTime) {
            totalClaimable += requests[i].amount;
            totalUnbondingAmount[msg.sender] -= requests[i].amount;

            // Remove request by swapping with last element and popping
            requests[i] = requests[requests.length - 1];
            requests.pop();
        } else {
            i++;
        }
    }

    require(totalClaimable > 0, "No unbonded tokens ready to claim");
    stakingToken.safeTransfer(msg.sender, totalClaimable);
    emit UnbondClaimed(msg.sender, totalClaimable);
}
```

### Frontend Integration with Viem

Interacting with a staking contract from a dApp frontend using Viem.

```typescript
import { createPublicClient, createWalletClient, http, parseEther, formatEther } from 'viem';
import { sepolia } from 'viem/chains';
import { privateKeyToAccount } from 'viem/accounts';

// Replace with your contract's ABI and address
const stakingContractAddress = '0xYourStakingContractAddress';
const stakingContractAbi = [
  // ... (Paste your contract's ABI here, e.g., from artifacts/SimpleStaking.json)
  {
    "inputs": [ { "internalType": "uint256", "name": "amount", "type": "uint256" } ],
    "name": "stake",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [ { "internalType": "uint256", "name": "amount", "type": "uint256" } ],
    "name": "initiateUnstake",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "claimUnbonded",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "claimRewards",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [ { "internalType": "address", "name": "", "type": "address" } ],
    "name": "stakedBalances",
    "outputs": [ { "internalType": "uint256", "name": "", "type": "uint256" } ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [ { "internalType": "address", "name": "account", "type": "address" } ],
    "name": "earned",
    "outputs": [ { "internalType": "uint256", "name": "", "type": "uint256" } ],
    "stateMutability": "view",
    "type": "function"
  },
  // ...
];

const publicClient = createPublicClient({
  chain: sepolia,
  transport: http(process.env.RPC_URL_SEPOLIA),
});

// Example with a wallet client (e.g., connected via WalletConnect or a browser extension)
// For local testing, you might use a private key:
const account = privateKeyToAccount(`0x${process.env.PRIVATE_KEY}`);
const walletClient = createWalletClient({
  account,
  chain: sepolia,
  transport: http(process.env.RPC_URL_SEPOLIA),
});


async function getUserStakedBalance(userAddress: `0x${string}`): Promise<string> {
  const data = await publicClient.readContract({
    address: stakingContractAddress,
    abi: stakingContractAbi,
    functionName: 'stakedBalances',
    args: [userAddress],
  });
  return formatEther(data as bigint);
}
```

## Anti-Patterns

*   **Unbounded Reward Accumulation Without Checkpoints.** Calculating rewards without periodic snapshots or per-interaction updates causes gas costs to grow linearly with time, eventually making claim transactions prohibitively expensive.

*   **Missing Unbonding Period.** Allowing instant unstaking without a cooldown period enables flash-loan-based reward manipulation where attackers stake, claim, and unstake within a single transaction.

*   **Reward Token Drainage via Rounding Exploits.** Distributing rewards using integer division without tracking remainders allows dust accumulation attacks where many small stakes extract more rewards than intended through systematic rounding in their favor.

*   **Single Admin Key for Reward Parameters.** Controlling reward rate, duration, and token address through a single EOA without timelock or multisig enables rug-pull scenarios where the admin drains the reward pool.

*   **Staking Without Slashing Conditions.** Building staking contracts for validation or service provision without enforceable slashing removes the economic disincentive for misbehavior, making the stake purely ceremonial.
