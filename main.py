# __________________________________
# Import libraries
# __________________________________
import configparser
from pathlib import Path

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

    def list_dbf_files(self):
        """
        Recursively find all .dbf files
        """

        if not self.root_directory.exists():
            raise FileNotFoundError(
                f"Directory does not exist: {self.root_directory}"
            )

        dbf_files = []

        for file in self.root_directory.rglob("*.dbf"):
            dbf_files.append(file)

        return sorted(dbf_files)

    def print_dbf_files(self):
        files = self.list_dbf_files()

        print(f"\nFound {len(files)} DBF files:\n")

        for file in files:
            print(file)

# __________________________________
# Main execution
# __________________________________
def main():
    config = Config()

    print(f"dbf_directory: {config.dbf_directory}")
    print(f"archive_directory: {config.archive_directory}")
    print(f"api_base_url: {config.api_base_url}")

    reader = DBFReader(config.dbf_directory)
    reader.print_dbf_files()

if __name__ == "__main__":
    main()