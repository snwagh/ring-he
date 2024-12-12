import json
from pathlib import Path
from syftbox.lib import SyftPermission
from loguru import logger
from syftbox.lib.constants import PERM_FILE



def check_file_exists(file_path):
    return file_path.exists()

def public_dir(client, user_id):
    return client.datasite_path.parent / user_id / "public"

def private_dir(client):
    # Dropping the second argument to only support your own private folder
    # return client.datasite_path.parent / user_id / "private"
    return client.workspace.data_dir / "private"
    
def api_data_dir(client, user_id, app_name):
    return client.api_data(app_name, user_id)

def setup_folder_with_permissions(folder_path, permission: SyftPermission):
    folder_path.mkdir(parents=True, exist_ok=True)
    permission.save(folder_path / PERM_FILE)
    
def write_json(file_path: Path, result: dict) -> None:
    print(f"Writing to {file_path}.")
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with open(file_path, "w") as f:
        json.dump(result, f)

def load_json(file_path):
    if not check_file_exists(file_path):
        logger.info(f"File {file_path} does not exist.")
        return None
    with open(file_path, "r") as f:
        return json.load(f)

def create_directory(path):
    path.mkdir(parents=True, exist_ok=True)
    logger.info(f"Created directory at: {path}")