import sys
from syftbox.lib import Client
from utils import (
    public_dir, 
    private_dir, 
    load_json, 
    check_file_exists, 
    write_json, 
    setup_folder_with_permissions, 
    api_data_dir
)
from loguru import logger
from syftbox.lib import SyftPermission
import phe as paillier

logger.add("app.log", level="DEBUG")  # Logs to a file with debug level

APP_NAME = "ring-he"
PROCESSING_FILE_NAME = "data.json"


######### HELPER FUNCTIONS #########
def exit(message):
    logger.info(message)
    sys.exit(0)

def setup_folder(client):
    private_folder_path = private_dir(client)
    private_folder_path.mkdir(parents=True, exist_ok=True)
    
    folder_path = api_data_dir(client, my_email, APP_NAME)
    # public_dir(client, my_email) / APP_NAME
    permission = SyftPermission.mine_with_public_write(folder_path)
    permission.read.apend("GLOBAL")
    setup_folder_with_permissions(folder_path, permission)
   
def adjacent_participant(ring_participants):
    try:
        index = ring_participants.index(my_email)
    except ValueError:
        exit(f"user_id {my_email} not found in the ring.")
    
    next_index = (index + 1) % len(ring_participants)
    prev_index = (index - 1) % len(ring_participants)
    return ring_participants[next_index], ring_participants[prev_index]

def encrypt_my_data(public_key_n):
    my_secret = load_json(secrets_file)["data"]
    public_key = paillier.PaillierPublicKey(n=int(public_key_n))
    logger.info("Data encrypted")
    return public_key.encrypt(int(my_secret))

def create_ring_data(ring_data):
    ring_participants = ring_data["participants"]
    public_key_n = ring_data["public_key"]["n"]
    encrypted_sum = ring_data["data"]
    
    public_key = paillier.PaillierPublicKey(n=int(public_key_n))
    encrypted_sum = paillier.EncryptedNumber(public_key, int(encrypted_sum))    
    new_encrypted_sum = encrypted_sum + encrypt_my_data(public_key_n)
    
    return {
        "participants": ring_participants,
        "public_key": {"n": public_key_n},
        "data": str(new_encrypted_sum.ciphertext())
    }

def setup_keys():
    """Generate Paillier keys and save them in the private directory."""
    public_key, private_key = paillier.generate_paillier_keypair()

    private_key_path = private_dir(client) / "private_key.json"
    public_key_path = private_dir(client) / "public_key.json"

    write_json(private_key_path, {"p": private_key.p, "q": private_key.q})
    write_json(public_key_path, {"n": public_key.n})

    logger.info(f"Keys created and saved in {private_dir(client)}")
    return public_key.n
    
def start_ring():
    public_key_n = setup_keys()
    initial_encrypted_sum = encrypt_my_data(public_key_n)
    
    return {
        "participants": ring_participants,
        "public_key": {"n": public_key_n},
        "data": str(initial_encrypted_sum.ciphertext())
    }
   
def decrypt_result(ring_data):
    private_key = load_json(private_dir(client) / "private_key.json")
    public_key = load_json(private_dir(client) / "public_key.json")
    private_key = paillier.PaillierPrivateKey(
                public_key=paillier.PaillierPublicKey(n=public_key["n"]), 
                p=int(private_key["p"]), 
                q=int(private_key["q"]))
    encrypted_sum = ring_data["data"]
    
    public_key = paillier.PaillierPublicKey(n=int(public_key["n"]))
    encrypted_sum = paillier.EncryptedNumber(public_key, int(encrypted_sum))    
    decrypted_sum = private_key.decrypt(encrypted_sum)
    logger.info(f"Decrypted sum: {decrypted_sum}")
    
    write_json(api_data_dir(client, my_email, APP_NAME) / "ring-he-result.json", {"result": decrypted_sum})
    
    
######### MAIN LOGIC #########
client = Client.load()
my_email: str = client.email

secrets_file = private_dir(client) / "secret.json"
processing_file = api_data_dir(client, my_email, APP_NAME) / PROCESSING_FILE_NAME
setup_folder(client)

if not check_file_exists(secrets_file):
    logger.info(f"File {secrets_file} does not exist.")
    sys.exit(0)

if not check_file_exists(processing_file):
    logger.info(f"Computation isn't blocked on you, waiting for {processing_file} (unless you're the ring leader).")
    sys.exit(0)

ring_data = load_json(processing_file)
ring_participants = ring_data["participants"]
logger.info(f"Ring participants: {ring_participants}")
next_member, previous_member = adjacent_participant(ring_participants)
dest = public_dir(client, next_member) / APP_NAME / PROCESSING_FILE_NAME


# First participant is ring leader
if my_email == ring_participants[0]:
    if check_file_exists(public_dir(client, my_email) / "result.json"):
        exit("Result already computed, exiting.")
    
    logger.info("Running as ring leader")
    if "data" not in ring_data.keys():
        logger.info("No data to compute, starting the ring.")
        initial_ring_data = start_ring()
        write_json(dest, initial_ring_data)
        logger.info("Ring initialized.")
    else:
        logger.info("Computation has completed, decrypting the result.")
        decrypt_result(ring_data)
else:
    logger.info("Running as ring participant.")
    new_ring_data = create_ring_data(ring_data)
    write_json(dest, new_ring_data)

processing_file.unlink()
print(f"Done processing {processing_file}, removing it.")