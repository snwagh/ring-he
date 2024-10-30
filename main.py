# File: main.py
import os
import json
import requests
from app_base import ApplicationBase, create_directory, create_file, check_file_exists
from loguru import logger
from pathlib import Path
import phe as paillier

logger.add("app.log", level="DEBUG")  # Logs to a file with debug level

RING_DATA_FILE = "https://raw.githubusercontent.com/snwagh/ring-he/data/data.json"

class RingHe(ApplicationBase):
    """This class manages the ring encryption and decryption process with homomorphic encryption."""

    def __init__(self):
        self.app_name = "ring-he"
        super().__init__(os.environ.get("SYFTBOX_CLIENT_CONFIG_PATH"))
        self.my_user_id = self.client_config["email"]
        self.ring_leader, self.ring_members = self.get_ring_data()
        self.prev_user_id, self.next_user_id = self.get_neighbors()

    def get_ring_data(self):
        """Fetch the ring leader and ring members from the online data.json."""
        response = requests.get(RING_DATA_FILE)
        if response.status_code == 200:
            data = response.json()
            ring_leader = data["ring-leader"][0]  # Assuming ring-leader is a list with one entry
            ring_members = data["ring-members"]
            return ring_leader, ring_members
        else:
            raise Exception("Failed to retrieve ring data.")

    def get_neighbors(self):
        """Get the previous and next neighbors in the ring based on ring-members."""
        try:
            index = self.ring_members.index(self.my_user_id)
        except ValueError:
            raise ValueError(f"user_id {self.my_user_id} not found in the ring.")

        prev_index = (index - 1) % len(self.ring_members)
        next_index = (index + 1) % len(self.ring_members)
        return self.ring_members[prev_index], self.ring_members[next_index]

    def setup_keys(self):
        """Generate Paillier keys and save them in the private directory."""
        public_key, private_key = paillier.generate_paillier_keypair()

        private_path = self.private_dir(self.my_user_id)
        create_directory(private_path)

        # Serialize and save keys
        with open(private_path / "public_key.json", "w") as f:
            json.dump({"n": public_key.n}, f)

        with open(private_path / "private_key.json", "w") as f:
            json.dump({"p": private_key.p, "q": private_key.q}, f)

        logger.info(f"Keys created and saved in {private_path}")

    def encrypt_and_pass_data(self):
        """Encrypt and pass data to the next ring member."""
        # Load public key from the received JSON
        pipeline_path = self.app_dir(self.my_user_id) / "rolling_sum.json"
        if not check_file_exists(pipeline_path):
            logger.info(f"Waiting for {pipeline_path} to be available.")
            return False

        with open(pipeline_path) as f:
            rolling_data = json.load(f)

        public_key = paillier.PaillierPublicKey(n=int(rolling_data["public_key"]["n"]))
        encrypted_sum = paillier.EncryptedNumber(public_key, int(rolling_data["data"]))

        # Read own secret data and encrypt it
        with open(self.private_dir(self.my_user_id) / "my_secret.txt") as f:
            my_secret = int(f.read().strip())

        encrypted_data = public_key.encrypt(my_secret)
        new_encrypted_sum = encrypted_sum + encrypted_data

        # Write updated rolling sum to the next member
        next_pipeline_path = self.app_dir(self.next_user_id) / "rolling_sum.json"
        create_file(next_pipeline_path, json.dumps({
            "public_key": {"n": public_key.n},
            "data": str(new_encrypted_sum.ciphertext())
        }))
        logger.info(f"Data encrypted and passed to {next_pipeline_path}")

    def decrypt_and_publish(self):
        """Decrypt the final sum and publish the result."""
        pipeline_path = self.app_dir(self.my_user_id) / "rolling_sum.json"
        if not check_file_exists(pipeline_path):
            logger.info(f"Waiting for {pipeline_path} to be available.")
            return False

        # Load final encrypted sum
        with open(pipeline_path) as f:
            rolling_data = json.load(f)

        # Load private key
        with open(self.private_dir(self.my_user_id) / "private_key.json") as f:
            private_key_data = json.load(f)
            private_key = paillier.PaillierPrivateKey(
                public_key=paillier.PaillierPublicKey(n=int(rolling_data["public_key"]["n"])),
                p=int(private_key_data["p"]),
                q=int(private_key_data["q"])
            )

        encrypted_sum = paillier.EncryptedNumber(private_key.public_key, int(rolling_data["data"]))
        decrypted_sum = private_key.decrypt(encrypted_sum)

        # Publish result in public directory
        public_result_path = self.public_dir(self.my_user_id) / self.app_name / "total.txt"
        create_file(public_result_path, str(decrypted_sum))
        logger.info(f"Decrypted total result published at {public_result_path}")

    def ring_leader(self):
        """Initialize the process for the ring leader by setting up keys and starting the encryption."""
        # Step 1: Setup keys if not already set
        if not check_file_exists(self.private_dir(self.my_user_id) / "public_key.json"):
            self.setup_keys()

        # Step 2: Check if the rolling_sum.json has been created by the leader
        if not check_file_exists(self.app_dir(self.next_user_id) / "rolling_sum.json"):
            # Encrypt the leader's data and start the rolling sum
            public_key_path = self.private_dir(self.my_user_id) / "public_key.json"
            with open(public_key_path, "r") as f:
                public_key_data = json.load(f)
            public_key = paillier.PaillierPublicKey(n=int(public_key_data["n"]))

            with open(self.private_dir(self.my_user_id) / "my_secret.txt") as f:
                my_secret = int(f.read().strip())

            encrypted_data = public_key.encrypt(my_secret)

            # Write the initial rolling sum to the next member
            next_pipeline_path = self.app_dir(self.next_user_id) / "rolling_sum.json"
            create_file(next_pipeline_path, json.dumps({
                "public_key": {"n": public_key.n},
                "data": str(encrypted_data.ciphertext())
            }))
            logger.info(f"Ring leader started the process and passed data to {next_pipeline_path}")

        # Step 3: If rolling sum comes back to leader, they decrypt the final result
        else:
            self.decrypt_and_publish()

    def run(self):
        """Main execution logic."""
        if self.my_user_id == self.ring_leader:
            self.ring_leader()  
        else:
            self.encrypt_and_pass_data()  


if __name__ == "__main__":
    runner = RingHe()
    runner.run()
