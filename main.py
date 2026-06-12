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
            "FCODE": record.get("FCODE"),
            "DESC1": record.get("DESC1"),
            "DESC2": record.get("DESC2"),
            "QTY": record.get("QTY"),
            "UNITPRICE": record.get("UNITPRICE"),
            "DATE": record.get("DATE"),
            "TIME": record.get("TIME"),
        }

# __________________________________
# Call the API 
# __________________________________
class APIClient:

    def __init__(self, base_url):
        self.base_url = base_url

    def upload(self, payload):
        response = requests.post(
            f"{self.base_url}",
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

    print(f"\nProcessing {len(files)} CTI files...\n")

    failed_files = []
    successful_files = []

    # -----------------------------
    # Loop through files
    # -----------------------------
    for file_path in files:

        try:

            print(f"\nProcessing: {file_path}")

            # Read DBF
            table = DBF(file_path, encoding="big5")

            # Transform records
            batch = []

            for record in table:
                transformed = transformer.transform(
                    record,
                    file_path
                )
                batch.append(transformed)

            print(
                f"Transformed {len(batch)} records "
                f"from {file_path}"
            )

            if batch:
                print(f"Sample record: {batch[0]}")

            # Upload
            result = api.upload(batch)

            print(
                f"Upload success: "
                f"{result}"
            )

            # Archive only after successful upload
            archived_path = archiver.move_file(
                file_path
            )

            print(
                f"Archived to: "
                f"{archived_path}"
            )

            successful_files.append(str(file_path))

        except Exception as e:

            error_message = str(e)

            if hasattr(e, "response") and e.response is not None:
                error_message += (
                    f"\nStatus: {e.response.status_code}"
                    f"\nResponse: {e.response.text}"
                )

            failed_files.append({
                "file": str(file_path),
                "error": error_message
            })

            print(
                f"Failed processing "
                f"{file_path}"
            )

            continue

    # -----------------------------
    # Final Summary
    # -----------------------------

    print("\n==============================")
    print("PROCESSING COMPLETE")
    print("==============================")

    print(
        f"Successful: "
        f"{len(successful_files)}"
    )

    print(
        f"Failed: "
        f"{len(failed_files)}"
    )

    if failed_files:

        print("\nFailed Files:")

        for item in failed_files:

            print("\n------------------")
            print(f"File: {item['file']}")
            print(f"Error:\n{item['error']}")

if __name__ == "__main__":
    main()