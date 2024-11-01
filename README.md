# Ring HE App

## Overview

The **Ring HE App** is a decentralized homomorphic encryption application where multiple members of a "ring" contribute encrypted data. The leader of the ring initiates the process by encrypting their data and passing it along the chain. Each member encrypts their own data and adds it to the rolling sum, which is continuously passed to the next member. Once the process completes, the ring leader decrypts the final sum and publishes the result.

### Key Features:
- **Homomorphic Encryption**: Uses the Paillier cryptosystem to securely aggregate encrypted data.
- **Decentralized Workflow**: Each member contributes to the final result without knowing the intermediate sums.
- **Leader-Driven Process**: The ring leader starts the process and is responsible for decrypting and publishing the final result.

## How It Works

1. **Ring Leader Initialization**:
   - The **ring leader** generates a set of Paillier encryption keys.
   - They encrypt their secret data (stored in `private/my_secret.txt`), start the rolling sum, and pass the data to the next member in the ring.

2. **Ring Members**:
   - Each member of the ring waits to receive the `rolling_sum.json` file from the previous member.
   - When they receive the file, they encrypt their data and add it to the rolling sum.
   - They then pass the updated sum to the next member in the ring.

3. **Ring Termination**:
   - Once the `rolling_sum.json` file reaches the **ring leader** again, the leader decrypts the final aggregated sum and publishes it in the `public/total.txt` file.

## Directory Structure

```plaintext
.
├── private/                    # Directory for storing private keys and secret data
│   └── my_secret.txt           # File containing the user's secret data
│   └── *_key.json              # Leader will have the keys here
├── public/                     
│    └── ring-he/                
│       └── total.txt           # Leader will publish this file containing the sum of all users secret data
└── app_pipelines/              
    └── ring-he/                
        └── rolling_sum.json    # File containing the sum of all users secret data
```

## Ring Workflow

- **Keys**: Only the ring leader generates Paillier keys and shares the public key with all members.
- **Rolling Sum**: Each member encrypts their data and adds it to the rolling sum (`rolling_sum.json`), passing it to the next member.
- **Decryption**: Only the ring leader can decrypt the final sum after all members have added their contributions.

## Example `data.json`

The app reads a `data.json` file from a predefined URL to define the ring members and leader.

```json
{
  "ring-leader": ["leader@openmined.org"],
  "ring-members": ["leader@openmined.org", "member1@openmined.org", "member2@openmined.org"]
}
```


## How to Run the App

1. **Setup**:
   - Ensure that the directory structure is correct (see above).
   - Place your secret data in `private/my_secret.txt`.

2. **Run**:
   - Use the provided `run.sh` script to execute the app.
   - The app will automatically handle encryption, data passing, and decryption.
   - The final result will be published in `public/total.txt`.
