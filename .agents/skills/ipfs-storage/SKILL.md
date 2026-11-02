---
name: ipfs-storage
description: 'Use when the user needs ipfs and content-addressed storage: design pinning,
  CID verification, gateway resilience and data persistence.'
---

# IPFS and Decentralized Storage — Web3 Development

You are an expert in IPFS and decentralized storage for building content-addressed, censorship-resistant data layers in decentralized applications.

## Overview

IPFS (InterPlanetary File System) is a peer-to-peer protocol for storing and sharing data using content addressing. Files are identified by their CID (Content Identifier) derived from their hash, making them immutable and verifiable. In Web3 development, IPFS is the standard for storing NFT metadata, dApp frontends, and any data too large or expensive for on-chain storage. Pinning services like Pinata, web3.storage, and Infura ensure data persistence.

## Core Philosophy

IPFS provides content-addressed storage where data is identified by what it contains (its hash) rather than where it lives (a server URL). This creates inherent immutability, verifiability, and censorship resistance - properties that align naturally with blockchain-based applications. The key insight for Web3 developers is that IPFS solves the data availability problem for on-chain references: store the CID on-chain as a permanent, verifiable pointer to off-chain data that anyone can retrieve and validate.

## Anti-Patterns

*   **Unpinned IPFS Content.** Uploading data to IPFS without pinning it through a persistent pinning service means the data will be garbage collected and become unavailable once all caching nodes drop it.

*   **Mutable Metadata URIs on Immutable Tokens.** Using HTTP gateway URLs or centralized API endpoints for NFT metadata instead of IPFS CIDs allows the metadata to change after minting, undermining the immutability guarantee.

*   **CID Validation Skipped On-Chain.** Storing IPFS CIDs on-chain without validating their format or length allows malformed references that can never resolve to actual content.

*   **Single Gateway Dependency.** Routing all IPFS requests through one gateway (e.g., ipfs.io) creates a centralized point of failure. Use multiple gateways with fallback logic or run your own IPFS node.

*   **Large File Direct Upload Without Chunking.** Uploading files larger than a few megabytes without CAR file chunking creates unreliable uploads and poor retrieval performance across the IPFS network.

## Core Concepts

### Content Addressing and CIDs

Content identifiers (CIDs) are self-describing hashes. Unlike location-based URLs, a CID uniquely identifies the content itself. If the content changes, the CID changes.

```
CIDv0: QmYwAPJzv5CZsnA625s3Xf2nemtYgPpHdWEz79ojWnPbdG
CIDv1: bafybeigdyrzt5sfp7udm7hu76uh7y26nf3efuylqabf3oclgtqy55fbzdi
```

### Uploading with Pinata SDK

```typescript
import PinataSDK from "@pinata/sdk";
import fs from "fs";

const pinata = new PinataSDK({
  pinataApiKey: process.env.PINATA_API_KEY!,
  pinataSecretApiKey: process.env.PINATA_SECRET_KEY!,
});

// Pin a file
async function pinFile(filePath: string): Promise<string> {
  const readableStream = fs.createReadStream(filePath);
  const result = await pinata.pinFileToIPFS(readableStream, {
    pinataMetadata: { name: "my-nft-image.png" },
  });
  return result.IpfsHash; // CID
}

// Pin JSON metadata
async function pinMetadata(metadata: object): Promise<string> {
  const result = await pinata.pinJSONToIPFS(metadata, {
    pinataMetadata: { name: "token-metadata" },
  });
  return result.IpfsHash;
}
```

### NFT Metadata Standard

```typescript
interface NFTMetadata {
  name: string;
  description: string;
  image: string; // IPFS URI: ipfs://QmHash...
  external_url?: string;
  attributes: Array<{
    trait_type: string;
    value: string | number;
    display_type?: "number" | "boost_number" | "boost_percentage" | "date";
  }>;
}

async function createNFTMetadata(
  name: string,
  description: string,
  imagePath: string,
  attributes: NFTMetadata["attributes"]
): Promise<string> {
  // 1. Upload image to IPFS
  const imageCID = await pinFile(imagePath);

  // 2. Create metadata pointing to the image
  const metadata: NFTMetadata = {
    name,
    description,
    image: `ipfs://${imageCID}`,
    attributes,
  };

  // 3. Upload metadata to IPFS
  const metadataCID = await pinMetadata(metadata);
  return `ipfs://${metadataCID}`;
}
```

### Uploading Directories for Collection Metadata

```typescript
import { Blob } from "buffer";

// Upload an entire collection's metadata as a directory
async function uploadCollectionMetadata(
  items: Array<{ name: string; description: string; imageCID: string; attributes: any[] }>
): Promise<string> {
  const files = items.map((item, index) => ({
    path: `metadata/${index}`, // Results in directory structure
    content: JSON.stringify({
      name: item.name,
      description: item.description,
      image: `ipfs://${item.imageCID}`,
      attributes: item.attributes,
    }),
  }));

  // Using web3.storage client
  // Each token's metadata is at: ipfs://<dirCID>/metadata/0, /1, /2, etc.
  const dirCID = await uploadDirectory(files);
  return dirCID;
}
```

### Smart Contract Integration

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract IPFSCollection is ERC721, Ownable {
    string private _baseTokenURI;
    uint256 private _nextTokenId;

    // Base URI points to an IPFS directory
    // Token 0 metadata: ipfs://QmDirHash/0
    // Token 1 metadata: ipfs://QmDirHash/1
    constructor(string memory baseURI) ERC721("MyNFT", "MNFT") Ownable(msg.sender) {
        _baseTokenURI = baseURI;
    }

    function _baseURI() internal view override returns (string memory) {
        return _baseTokenURI;
    }

    function mint(address to) external onlyOwner {
        _safeMint(to, _nextTokenId++);
    }

    // Allow updating base URI for reveal mechanics
    function setBaseURI(string calldata newBaseURI) external onlyOwner {
        _baseTokenURI = newBaseURI;
    }
}
```

### Fetching IPFS Content

```typescript
// Resolve IPFS URIs through a gateway
function ipfsToHttp(ipfsUri: string): string {
  if (ipfsUri.startsWith("ipfs://")) {
    const cid = ipfsUri.replace("ipfs://", "");
    // Use a dedicated gateway; avoid the public gateway for production
    return `https://gateway.pinata.cloud/ipfs/${cid}`;
  }
  return ipfsUri;
}

// Fetch NFT metadata with fallback gateways
async function fetchMetadata(tokenURI: string): Promise<NFTMetadata> {
  const gateways = [
    "https://gateway.pinata.cloud/ipfs/",
    "https://cloudflare-ipfs.com/ipfs/",
    "https://ipfs.io/ipfs/",
  ];

  const cid = tokenURI.replace("ipfs://", "");

  for (const gateway of gateways) {
    try {
      const response = await fetch(`${gateway}${cid}`, {
        signal: AbortSignal.timeout(10000),
      });
      if (response.ok) {
        return await response.json();
      }
    } catch {
      continue; // Try next gateway
    }
  }
  throw new Error(`Failed to fetch metadata for ${tokenURI}`);
}
```

## Implementation Patterns

### On-Chain + Off-Chain Hybrid Storage

```solidity
contract HybridStorage {
    // Store only the content hash on-chain (32 bytes)
    mapping(uint256 => bytes32) public contentHashes;

    event ContentUpdated(uint256 indexed id, bytes32 contentHash, string ipfsUri);

    function setContent(uint256 id, bytes32 contentHash, string calldata ipfsUri) external {
        contentHashes[id] = contentHash;
        emit ContentUpdated(id, contentHash, ipfsUri);
    }

    // Verify off-chain content matches on-chain hash
    function verifyContent(uint256 id, bytes calldata content) external view returns (bool) {
        return keccak256(content) == contentHashes[id];
    }
}
```

### Lazy Reveal Pattern

```typescript
// Pre-reveal: all tokens point to a placeholder
const placeholderCID = await pinMetadata({
  name: "Unrevealed",
  description: "This NFT has not been revealed yet.",
  image: `ipfs://${placeholderImageCID}`,
});

// Deploy with placeholder
const contract = await deploy("IPFSCollection", [`ipfs://${placeholderCID}/`]);

// After mint completes, upload real metadata directory
const realMetadataCID = await uploadCollectionMetadata(allItems);

// Reveal by updating base URI
await contract.setBaseURI(`ipfs://${realMetadataCID}/`);
```

### Arweave for Permanent Storage

```typescript
import Arweave from "arweave";

const arweave = Arweave.init({
  host: "arweave.net",
  port: 443,
  protocol: "https",
});

async function uploadToArweave(data: Buffer, contentType: string): Promise<string> {
  const transaction = await arweave.createTransaction({ data });
  transaction.addTag("Content-Type", contentType);

  const wallet = JSON.parse(fs.readFileSync("arweave-wallet.json", "utf-8"));
  await arweave.transactions.sign(transaction, wallet);
  await arweave.transactions.post(transaction);

  return `ar://${transaction.id}`;
}
```

## Best Practices

1. **Use IPFS directories for collection metadata** so all token URIs share a single base CID, enabling efficient base URI updates and reveal mechanics.
2. **Pin content with at least two providers** for redundancy. If one pinning service goes down, the data remains accessible.
3. **Use CIDv1 in base32** format for better compatibility with subdomains and case-insensitive systems.
4. **Store content hashes on-chain** when data integrity verification is required. The CID itself serves as a commitment.
5. **Use a dedicated IPFS gateway** for production dApps. The public `ipfs.io` gateway is rate-limited and unreliable under load.
6. **Implement gateway fallback logic** in your frontend to try multiple gateways if the primary is unavailable.
7. **Consider Arweave for permanent storage** when data must persist indefinitely without ongoing pinning fees.

## Common Pitfalls

- **Assuming IPFS data is permanent by default.** Unpinned data is garbage-collected. Always pin with a reliable service.
- **Using mutable IPFS URIs for on-chain references.** IPNS names can change resolution targets. For immutable on-chain references, use raw CIDs.
- **Storing large files on-chain.** Even calldata is expensive. Use IPFS for anything larger than a few hundred bytes and store only the CID on-chain.
- **Hardcoding a single IPFS gateway URL.** Gateways have rate limits and downtime. Always implement fallback logic.
- **Not validating metadata schema.** Marketplaces expect specific fields (name, description, image, attributes). Missing fields cause display issues.
- **Forgetting to URL-encode CIDs.** Some CIDv1 formats contain characters that need encoding in URLs.

## Review & Production Validation (2026-10-31)

- **Domain control (Blockchain ecosystem / development):** Confirm active network, chain ID, toolchain/API version and protocol-specific conventions.
- **Independent validation:** Use primary documentation and reproducible tests for implementation instructions.
- **Time-sensitive details:** Treat fixed rates, thresholds, package versions, protocols and jurisdiction-specific rules in the examples above as illustrative unless reconfirmed against primary documentation.
- **Before relying on the result:** State inputs and assumptions; verify calculations and edge cases, and identify what has not been executed or tested.
