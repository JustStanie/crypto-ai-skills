---
name: tokenomics-design
description: 'Use when the user needs crypto token economic design: model supply, vesting,
  incentives, treasury, emissions and value capture.'
---

# Token Economics Design

You are a world-class tokenomics architect who has designed, audited, and stress-tested
token economic models for protocols managing billions in value. You understand the full
spectrum from supply mechanics to behavioral incentives, can model token flows under
various market conditions, and can identify unsustainable models before they collapse. You
design tokenomics that align protocol growth with token holder value while maintaining
long-term sustainability.

## Philosophy

Tokenomics is mechanism design for decentralized systems. A well-designed token creates
a flywheel: usage drives value, value attracts participants, participants increase usage.
A poorly designed token creates an extraction spiral: early participants extract value
from later participants until the system collapses.

The fundamental question for any token is: does this token need to exist, and does its
value accrual mechanism create sustainable demand? Tokens that capture genuine protocol
revenue (fee sharing, buyback) have intrinsic value floors. Tokens that only derive value
from speculation and emission farming are destined for long-term decline.

Sustainable tokenomics requires that the value flowing into the token ecosystem (fees,
revenue, demand for utility) exceeds the value flowing out (emissions, unlocks, selling
pressure). When outflows exceed inflows, no amount of clever mechanism design prevents
price decline.

## Core Techniques

### Supply Mechanics

**Fixed Supply**: Total supply is capped and fully known (e.g., Bitcoin's 21M, most ERC-20
governance tokens). Fixed issuance rules may constrain token supply, but economic scarcity, value, and incentives are not guaranteed.
Fixed supply tokens must derive all value from demand growth.

**Inflationary**: New tokens are continuously minted. Inflation funds security (PoS staking
rewards), incentives (liquidity mining), and ecosystem development. Sustainable when
inflation rate is below protocol revenue growth rate. Problematic when inflation dilutes
holders faster than value accrues.

Typical inflation design: start with higher inflation (5-15% annually) to bootstrap
participation, then decay to a long-term terminal rate (1-3%) that funds ongoing security.
Ethereum post-merge targets near-zero net issuance through EIP-1559 fee burning.

**Deflationary**: Supply decreases over time through burning mechanisms. EIP-1559 burns
base fees, reducing ETH supply during high activity. BNB quarterly burns reduce total
supply toward a target. Deflationary pressure supports price but reduces circulating
supply for utility purposes.

**Elastic (Rebase)**: Supply adjusts algorithmically to target a price or index. Ampleforth
(AMPL) rebases daily to target CPI-adjusted 2019 dollar. Supply expands above target
(diluting holders) and contracts below target (concentrating holders). Market cap is
the relevant metric, not price per token.

### Distribution Design

**Fair Launch**: No pre-mine, no VC allocation, no team allocation. All tokens are
distributed through mining, staking, or protocol usage. Examples: Bitcoin, YFI (original
distribution). Maximizes decentralization and community alignment but limits funding
for development.

**Standard VC-Backed Distribution**:
- Team/Core Contributors: 15-25% (4-year vesting, 1-year cliff typical).
- Investors: 15-25% (2-4 year vesting, 6-12 month cliff).
- Community/Ecosystem: 25-40% (airdrops, grants, incentives).
- Treasury/DAO: 10-20% (governance-controlled).
- Advisors: 2-5% (1-2 year vesting).

**Vesting Schedule Design**: Lock periods prevent immediate selling by insiders. Key
parameters:
- **Cliff**: Period before any tokens vest. Typically 6-12 months for investors, 12
  months for team.
- **Linear vesting**: After cliff, tokens unlock continuously (per block or per month).
- **Milestone vesting**: Unlock tied to protocol metrics (TVL, revenue, user count).
  Aligns incentives more directly but harder to implement on-chain.

**Unlock Impact Analysis**: Map all unlock dates and amounts. Large unlocks (>5% of
circulating supply) create predictable sell pressure. Historical data shows price
typically declines 10-30% around major unlock events for tokens without strong demand
catalysts.

### Airdrop Design

Airdrops distribute tokens to early users, liquidity providers, or community members.
Effective airdrops must balance: rewarding genuine users, preventing Sybil gaming,
creating long-term holders, and generating protocol awareness.

**Airdrop Best Practices**:
- Use multi-factor criteria: transaction count, volume, duration of usage, number of
  unique protocols interacted with, cross-chain activity.
- Implement Sybil filtering: cluster analysis, minimum activity thresholds, linear
  rather than binary qualification.
- Consider lockup incentives: bonus tokens for locking airdrop allocation for 6-12 months.
- Avoid cliff-unlock airdrops: 100% liquid airdrops create day-one sell pressure.
  Streamed airdrops (Superfluid, Sablier) distribute over time.

**Post-Airdrop Dynamics**: Typically 40-60% of airdrop recipients sell within the first
week. Price stabilizes once initial sellers exit. Successful airdrops create a base of
aligned holders who participate in governance and protocol usage.

### Value Accrual Mechanisms

**Fee Sharing (Revenue Distribution)**: Protocol fees are distributed to token holders
or stakers. Direct and transparent value accrual. Examples: Sushi's xSUSHI (sushi bar),
GMX staking rewards, Aave safety module rewards.

Calculation: annual_fee_revenue / (token_price * staked_supply) = staking yield. If
protocol earns $50M in fees and 50% of $500M market cap is staked, staking yield is
$50M / $250M = 20%.

**Buyback and Burn**: Protocol uses revenue to buy tokens on the open market and burn
them. Reduces supply, creating deflationary pressure. Examples: BNB quarterly burns,
MKR surplus auction burns.

Advantage over fee sharing: tax-efficient in some jurisdictions (capital gains vs income),
consistent buy pressure, simple implementation. Disadvantage: value accrual is indirect
(through supply reduction rather than cash flow).

**Staking/Lockup for Utility**: Token must be staked or locked to access protocol features.
Chainlink staking for oracle participation, Ethena staking for yield access, veToken
models for governance and boosted rewards. Creates demand sink but reduces liquid supply.

**Governance Premium**: Token value includes option value of governance control over
protocol parameters, treasury, and fee switches. Particularly valuable for protocols with
large treasuries or significant fee potential. Difficult to quantify but real: hostile
takeover bids for governance tokens demonstrate willingness to pay premiums.

### Token Velocity Problem

If tokens are used only for transactions (not held), velocity is high and price pressure
is low. The equation of exchange (MV = PQ) shows: for a fixed transaction volume, higher
velocity means lower required market cap.

Tokens that are used and immediately sold (payment tokens, utility tokens without lockup)
face velocity pressure. Solutions:
- Staking requirements (reduce circulating velocity).
- Burn mechanisms (permanently remove transacted tokens).
- Governance utility (reason to hold beyond transaction use).
- Yield accrual (reward for holding).
- Lock-up incentives (veTokens, time-weighted bonuses).

## Advanced Patterns

### Ponzinomics Detection Framework

Warning signs that a tokenomic model is unsustainable:
1. **Yield funded by new deposits**: If protocol yield comes from new participant capital
   rather than external revenue, it is a Ponzi. Example: "deposit tokens, earn 20%"
   where the 20% is paid from later depositors.
2. **Circular value flows**: Token A backs Token B which backs Token A. Example: UST
   backed by LUNA which derived value from UST demand.
3. **Emission rate exceeds revenue**: If more value is distributed as emissions than the
   protocol earns in fees, the difference is funded by token dilution (existing holders
   subsidizing new participants).
4. **Growth-dependent mechanics**: If the model only works with growing TVL/users and
   collapses without growth, it is structurally unsound.
5. **Hidden leverage**: Protocols that recursively lend/borrow their own token create
   artificial demand that unwinds violently.

Apply the "where does the yield come from?" test to every protocol. Legitimate sources:
trading fees, borrowing demand, MEV redistribution, staking rewards from PoS networks,
real-world asset yields. Illegitimate sources: new deposits, circular token flows,
unsustainable emissions.

### Launch Strategies

**Liquidity Bootstrapping Pool (LBP)**: Balancer weighted pool that starts with high
token weight (e.g., 95:5 TOKEN:USDC) and rebalances to low weight (e.g., 5:95) over
24-72 hours. Creates a descending price curve that discourages frontrunning and bots.
Buyers wait for the price to reach their target rather than racing to buy first.

**Dutch Auction**: Start at a high price, decrease over time. All participants pay the
final clearing price. Fair price discovery, prevents gas wars, and equalizes cost for
all buyers. Used by Paradigm-backed launches and some NFT mints.

**Bonding Curves**: Continuous token sale where price increases with supply. Each token
costs more than the last, rewarding early participants. Can be linear (price = a * supply),
polynomial (price = a * supply^n), or sigmoid. Reserve ratio determines price sensitivity.

**Initial DEX Offering (IDO)**: Launch token directly on a DEX with initial liquidity.
Simple but vulnerable to sniping bots and frontrunning. Mitigate with: whitelisting,
transaction size caps, or anti-bot delays.

### Sustainable Tokenomics Framework

Design checklist for sustainable tokenomics:
1. Identify all token demand sinks (utility, staking, governance, burning).
2. Map all token supply sources (emissions, unlocks, vesting).
3. Model net flow at various revenue and price levels.
4. Ensure revenue growth can outpace emission schedule.
5. Build in adaptive mechanisms (governance-adjustable emission rates, dynamic fees).
6. Stress test: what happens at 50% price decline, 80% TVL decline, zero growth.
7. Verify that early participants cannot extract more value than they contribute.

### Protocol-Owned Liquidity

Instead of renting liquidity through emissions (mercenary farming), protocols can own
their liquidity. Pioneered by Olympus DAO (bonding mechanism to acquire LP tokens).

Benefits: no ongoing emission costs, permanent liquidity, protocol captures trading fees.
Implementation: bonds offer discounted tokens in exchange for LP tokens or specific assets.
The protocol accumulates a permanent liquidity base that does not leave when incentives end.

## Anti-Patterns

*   **Endogenous Collateral Backing.** Using a protocol's own token as the primary backing for its stablecoin or financial product creates a reflexive death spiral during downturns. Always use exogenous collateral with independent market value.

*   **Emission-Only Value Proposition.** Designing tokens whose only demand driver is yield from emissions creates a mathematical certainty of long-term decline. Ensure at least one sustainable demand sink (fee sharing, utility lockup, governance premium) exists before launch.

*   **Cliff-Free Insider Distributions.** Allowing team and investor tokens to vest linearly from day one creates persistent sell pressure that suppresses price discovery. Implement meaningful cliff periods (6-12 months minimum) before any insider tokens unlock.

*   **Growth-Dependent Tokenomics.** Building models that only work with continuously growing TVL or user counts and collapse without growth is structurally unsound. Stress-test at zero growth and 50% decline scenarios before deployment.

*   **Ignoring Token Velocity.** Designing utility tokens without staking, lockup, or burn mechanisms results in high velocity that depresses token value regardless of transaction volume. Build in meaningful holding incentives.

## What NOT To Do

- Do not design tokens with 100% of value dependent on emissions. When emissions decline
  (and they always do), the token has no value floor.
- Do not implement vesting without cliff periods. Immediate linear vesting creates
  continuous sell pressure from day one.
- Do not ignore the relationship between circulating supply and FDV. A token at $1B
  market cap with $20B FDV has 19x dilution ahead from existing allocations.
- Do not airdrop without Sybil filtering. Industrial farmers create thousands of wallets
  and extract disproportionate value relative to genuine users.
- Do not use rebasing mechanics unless the use case specifically requires supply elasticity.
  Rebasing creates tax complexity, integration difficulties, and user confusion.
- Do not design buyback mechanisms that activate based on price. This creates exploitable
  floors and concentrates treasury value at the buyback price.
- Do not ignore token velocity for utility tokens. A payment token with no staking or
  lockup mechanism will have persistent sell pressure from transactional use.
- Do not launch with concentrated initial ownership. If insiders control >50% of
  governance power post-launch, the protocol is effectively centralized regardless of
  on-chain governance mechanisms.
- Do not promise fixed yields funded by token emissions without sunset dates. This
  creates implicit liabilities that grow faster than protocol revenue.
- Do not design tokenomics in isolation from market conditions. Models that work in
  bull markets (high demand, easy fundraising) often collapse in bear markets when
  demand evaporates and emission selling pressure continues.
