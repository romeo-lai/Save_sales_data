# __________________________________
# Import libraries
# __________________________________
import configparser
from pathlib import Path
import shutil
import requests
from dbfread import DBF

# __________________________________
# Load and parse configs
# __________________________________
class Config:
    def __init__(self, config_file="config.ini"):
        self.config = configparser.ConfigParser()

        config_path = Path(config_file)

        if not config_path.exists():
            raise FileNotFoundError(
                f"Config file not found: {config_path}"
            )

        self.config.read(config_path)

    @property
    def dbf_directory(self):
        return self.config["PATHS"]["dbf_directory"]

    @property
    def archive_directory(self):
        return self.config["PATHS"]["archive_directory"]

    @property
    def api_base_url(self):
        return self.config["API"]["base_url"]

# __________________________________
# Browse the dbf dbf_directory
# __________________________________
class DBFReader:

    def __init__(self, root_directory):
        self.root_directory = Path(root_directory)

    def find_cti_files(self):

        if not self.root_directory.exists():
            raise FileNotFoundError(
                f"Directory does not exist: {self.root_directory}"
            )

        files = [
            f for f in self.root_directory.rglob("*.dbf")
            if f.name.upper() == "CTI.DBF"
        ]

        return sorted(files)

    def print_files(self):
        files = self.find_cti_files()

        print(f"\nFound {len(files)} CTI.dbf files:\n")

        for f in files:
            print(f)

# __________________________________
# Loop the CTI files and get data
# __________________________________
class CTITransformer:

    def transform(self, record, source_file):
        return {
            "source_file": str(source_file),
            "FCODE": record.get("FCODE,C,6"),
            "DESC1": record.get("DESC1,C,26"),
            "DESC2": record.get("DESC2,C,26"),
            "QTY": record.get("QTY,N,5,0"),
            "UNITPRICE": record.get("UNITPRICE,N,10,2"),
            "DATE": record.get("DATE,C,10"),
            "TIME": record.get("TIME,C,8"),
        }

# __________________________________
# Call the API 
# __________________________________
class APIClient:

    def __init__(self, base_url):
        self.base_url = base_url

    def upload(self, payload):
        response = requests.post(
            f"{self.base_url}/upload",
            json=payload,
            headers={
                "Content-Type": "application/json"
            }
        )

        response.raise_for_status()
        return response.json()

# __________________________________
# Archive processed files
# __________________________________
class Archiver:

    def __init__(self, archive_root):
        self.archive_root = Path(archive_root)

    def move_file(self, file_path: Path):
        file_path = Path(file_path)

        date_folder = file_path.parent.name

        target_dir = self.archive_root / date_folder
        target_dir.mkdir(parents=True, exist_ok=True)

        target_path = target_dir / file_path.name

        shutil.move(str(file_path), str(target_path))

        return target_path
    

# __________________________________
# Main execution
# __________________________________
def main():
    config = Config()

    print(f"dbf_directory: {config.dbf_directory}")
    print(f"archive_directory: {config.archive_directory}")
    print(f"api_base_url: {config.api_base_url}")

    reader = DBFReader(config.dbf_directory)
    transformer = CTITransformer()
    api = APIClient(config.api_base_url)
    archiver = Archiver(config.archive_directory)

    files = reader.find_cti_files()
    print(f"Processing {len(files)} CTI files...\n")

    #________________________________
    # Loop through files
    #________________________________
    #for file_path in files:
    file_path = files[0]  # For testing, process only the first file
    print(f"Processing: {file_path}")

    table = DBF(file_path, encoding="big5")

    # 2. transform records
    batch = []
    for record in table:
        transformed = transformer.transform(record, file_path)
        batch.append(transformed)

    # Debug print
    print(f"Transformed {len(batch)} records from {file_path}")

"""
    # 3. send to API
    try:
        result = api.upload(batch)
        print("Upload success:", result)

    except Exception as e:
        print(f"Upload failed for {file_path}: {e}")
        continue

        # 4. archive file (only if upload succeeded)
    archived_path = archiver.move_file(file_path)
    print(f"Archived to: {archived_path}\n")    
"""

if __name__ == "__main__":
    main()