---
name: cosmos-sdk
description: 'Use when the user needs cosmos sdk chain architecture: design SDK modules,
  transaction handlers, governance and IBC interfaces.'
---

# Cosmos SDK chain architecture

You are a seasoned architect of sovereign blockchains, deeply proficient in the Cosmos SDK. You've launched multiple app-chains, designed custom modules, and integrated them seamlessly into the broader IBC ecosystem, understanding the nuances of state transitions, consensus, and cross-chain communication.

## Core Philosophy

The Cosmos SDK embodies a philosophy of modularity, sovereignty, and interoperability. Instead of deploying smart contracts on a shared, general-purpose blockchain, you build application-specific blockchains—app-chains—that are fully optimized for their intended purpose. This approach grants unparalleled control over your chain's governance, economic model, and technical specifications, allowing for higher throughput, lower fees, and custom features not possible on multi-purpose chains.

The SDK abstracts away the complexities of networking and consensus, providing a robust framework to focus solely on your application's business logic. By leveraging the Inter-Blockchain Communication Protocol (IBC), your app-chain isn't isolated; it can trustlessly exchange value and data with other IBC-enabled chains, fostering a truly interconnected ecosystem. Embrace this modular architecture to create resilient, scalable, and specialized decentralized applications.

## Setup

To begin building with Cosmos SDK, install the Go release compatible with the selected Cosmos SDK and CometBFT versions. Ignite CLI is one option for scaffolding; verify whether it supports the target SDK version before using its commands.

```bash
# Install Go (if not already installed)
# Follow instructions at https://go.dev/doc/install

# Install ignite CLI
# Install Ignite CLI using its current official instructions after reviewing the installer.
# Confirm compatibility with the selected Cosmos SDK release.

# Verify installation
ignite version
# Confirm the reported CLI version is compatible with your chosen stack.
```

Once `ignite CLI` is installed, you can scaffold your first chain.

```bash
# Scaffold a new chain named 'blogchain'
ignite scaffold chain blogchain --no-module
cd blogchain

# Install chain dependencies and build
go mod tidy
make install

# Initialize your chain for local development
blogchaind init mynode --chain-id blogchain

# Add a key for your local validator
blogchaind keys add validator

# Add genesis account for your validator
blogchaind add-genesis-account $(blogchaind keys show validator -a) 1000000000stake

# Set your validator as a genesis validator
blogchaind gentx validator 100000000stake --chain-id blogchain

# Collect genesis transactions
blogchaind collect-gentxs

# Start the chain
blogchaind start
```
This will start a local blockchain node, accessible via `blogchaind` CLI commands.

## Key Techniques

### 1. Scaffolding a Custom Module and Message

Cosmos SDK applications are built as a collection of modules. Use `ignite CLI` to scaffold a new module and define a custom message within it. Let's create a `posts` module and a `CreatePost` message.

```bash
# In your blogchain directory:
ignite scaffold module posts
ignite scaffold message create-post title body --module posts --signer creator
```

This command generates:
*   `x/posts/` module directory structure.
*   `x/posts/types/message_create_post.go`: Defines the `MsgCreatePost` struct and its basic validation.
*   `x/posts/keeper/msg_server_create_post.go`: The handler for processing `MsgCreatePost`.
*   `x/posts/types/post.go`: A basic `Post` struct.

### 2. Defining State and Implementing a Message Handler

After scaffolding, you define the actual state structure and implement the logic to mutate it.
Edit `x/posts/types/post.go` to define your Post structure, adding a unique ID.

```go
// x/posts/types/post.go
package types

import (
	"strconv"
)

type Post struct {
	Id      uint64 `protobuf:"varint,1,opt,name=id,proto3" json:"id,omitempty"`
	Title   string `protobuf:"bytes,2,opt,name=title,proto3" json:"title,omitempty"`
	Body    string `protobuf:"bytes,3,opt,name=body,proto3" json:"body,omitempty"`
	Creator string `protobuf:"bytes,4,opt,name=creator,proto3" json:"creator,omitempty"`
}

func (p Post) GetIdBytes() []byte {
	return []byte(strconv.FormatUint(p.Id, 10))
}
```

Now, implement the `CreatePost` message handler in `x/posts/keeper/msg_server_create_post.go`. This function validates the message, creates a new `Post` object, stores it in the module's state, and emits events.

```go
// x/posts/keeper/msg_server_create_post.go
package keeper

import (
	"context"
	"strconv"

	sdk "github.com/cosmos/cosmos-sdk/types"
	sdkerrors "github.com/cosmos/cosmos-sdk/types/errors"
	"blogchain/x/posts/types"
)

func (k msgServer) CreatePost(goCtx context.Context, msg *types.MsgCreatePost) (*types.MsgCreatePostResponse, error) {
	ctx := sdk.UnwrapSDKContext(goCtx)

	// Validate message (already done by scaffolded code, but good to remember)
	if err := msg.ValidateBasic(); err != nil {
		return nil, err
	}

	// Get the next post ID
	id := k.GetNextPostID(ctx) // Assume this helper exists to get and increment ID

	// Create the post object
	post := types.Post{
		Id:      id,
		Creator: msg.Creator,
		Title:   msg.Title,
		Body:    msg.Body,
	}

	// Store the post
	store := ctx.KVStore(k.storeKey)
	store.Set(types.KeyPrefix(types.PostKeyPrefix+strconv.FormatUint(post.Id, 10)), k.cdc.MustMarshal(&post))

	// Increment the next post ID
	k.SetNextPostID(ctx, id+1) // Assume this helper exists to set the next ID

	// Emit an event
	ctx.EventManager().EmitEvent(
		sdk.NewEvent(
			sdk.EventTypeMessage,
			sdk.NewAttribute(sdk.AttributeKeyModule, types.ModuleName),
			sdk.NewAttribute(sdk.AttributeKeySender, msg.Creator),
			sdk.NewAttribute(types.EventTypeCreatePost, strconv.FormatUint(post.Id, 10)),
		),
	)

	return &types.MsgCreatePostResponse{Id: post.Id}, nil
}
```
*Note: You would need to implement `GetNextPostID` and `SetNextPostID` in `x/posts/keeper/post.go` or similar, using the KVStore to manage a global counter for post IDs.*

### 3. Querying Chain State (gRPC)

To read data from your chain, you define gRPC queries. `ignite CLI` can scaffold a query for a list of items.

```bash
# Scaffold a query to list all posts
ignite scaffold query list-post --module posts
```

Now, implement the `ListPost` query in `x/posts/keeper/grpc_query_list_post.go`.

```go
// x/posts/keeper/grpc_query_list_post.go
package keeper

import (
	"context"

	"google.golang.org/grpc/codes"
	"google.golang.org/grpc/status"

	"blogchain/x/posts/types"
	sdk "github.com/cosmos/cosmos-sdk/types"
	"github.com/cosmos/cosmos-sdk/store/prefix"
)

func (k Keeper) ListPost(goCtx context.Context, req *types.QueryListPostRequest) (*types.QueryListPostResponse, error) {
	if req == nil {
		return nil, status.Error(codes.InvalidArgument, "invalid request")
	}

	ctx := sdk.UnwrapSDKContext(goCtx)
	var posts []types.Post
	store := ctx.KVStore(k.storeKey)
	postStore := prefix.NewStore(store, types.KeyPrefix(types.PostKeyPrefix))

	iterator := postStore.Iterator(nil, nil)
	defer iterator.Close()

	for ; iterator.Valid(); iterator.Next() {
		var post types.Post
		k.cdc.MustUnmarshal(iterator.Value(), &post)
		posts = append(posts, post)
	}

	return &types.QueryListPostResponse{Post: posts}, nil
}
```

### 4. Interacting with Your Chain (CLI & TS Client)

After building and running your chain (`blogchaind start`), you can interact using the generated CLI.

**CLI Transaction:**
```bash
# Add a new account for testing
blogchaind keys add alice

# Send some tokens to alice (from validator account)
blogchaind tx bank send validator alice 10000000stake --chain-id blogchain --fees 200stake --node tcp://localhost:26657 -y

# Create a post using alice's account
blogchaind tx posts create-post "My First Post" "This is the body of my first post on Blogchain." --from alice --chain-id blogchain --fees 200stake --node tcp://localhost:26657 -y
```

**CLI Query:**
```bash
# Query all posts
blogchaind query posts list-post --node tcp://localhost:26657
```

**TypeScript Client (`@cosmjs/stargate`):**

For frontend or external service integration, `@cosmjs/stargate` provides a powerful way to interact.

```typescript
import { SigningStargateClient, StdFee, GasPrice } from "@cosmjs/stargate";
import { DirectSecp256k1Wallet } from "@cosmjs/proto-signing";
import { stringToPath } from "@cosmjs/bip39";
import { coins } from "@cosmjs/proto-signing";

// Define your custom message type URL and encoder
const typeUrl = "/blogchain.posts.MsgCreatePost";
const customMessages = {
  createPost: {
    typeUrl: typeUrl,
    encode: (msg: { creator: string; title: string; body: string }, writer?: any) => {
      // Your custom encoding logic for MsgCreatePost
      const enc = new (require("protobufjs/minimal")).Writer(writer);
      enc.string(msg.creator, 1); // creator is field 1
      enc.string(msg.title, 2);   // title is field 2
      enc.string(msg.body, 3);    // body is field 3
      return enc;
    },
    // No decode needed for sending
  },
};

async function createPost() {
  // Implementation with mnemonic-based wallet setup and transaction signing
}

createPost().catch(console.error);
```

## Anti-Patterns

*   **Panicking in Message Handlers.** Using `panic!` or `unwrap()` in Cosmos SDK message handlers causes non-deterministic state corruption across nodes. Always return proper error types through the `sdk.Error` mechanism.

*   **Unbounded Iteration in BeginBlock/EndBlock.** Processing unbounded data structures during block lifecycle hooks creates block production delays that can halt the chain when data grows.

*   **Missing Input Validation on Custom Messages.** Accepting user-provided parameters in custom transaction messages without bounds checking and type validation enables denial-of-service through malformed transactions.

*   **Ignoring IBC Channel Versioning.** Deploying IBC-enabled modules without proper channel version negotiation causes silent failures when connecting to chains running different module versions.

*   **State Store Reads in Simulation.** Performing expensive state store reads during transaction simulation (ante handlers) without caching causes gas estimation to be significantly slower than actual execution.

## Version and Evidence Check

Cosmos SDK, CometBFT, IBC and Ignite version compatibility and module APIs vary significantly. Verify each command and generated scaffold against current official docs; pin compatible releases.

## Review & Production Validation (2026-10-31)

- **Domain control (Blockchain ecosystem / development):** Confirm active network, chain ID, toolchain/API version and protocol-specific conventions.
- **Independent validation:** Use primary documentation and reproducible tests for implementation instructions.
- **Time-sensitive details:** Treat fixed rates, thresholds, package versions, protocols and jurisdiction-specific rules in the examples above as illustrative unless reconfirmed against primary documentation.
- **Before relying on the result:** State inputs and assumptions; verify calculations and edge cases, and identify what has not been executed or tested.
