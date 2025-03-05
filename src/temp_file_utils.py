import os
import logging

logger = logging.getLogger(__name__)

class TempFile:
    def __init__(self, file_path: str):
        self.file_path = file_path

    def get_data(self):
        try:
            with open(self.file_path, 'r') as file:
                return file.read()
        except FileNotFoundError:
            return None

    def save_data(self, data: str):
        with open(self.file_path, 'w') as file:
            file.write(data)
            logger.debug(f"Data saved to {self.file_path}")

    def cleanup(self):
        try:
            os.remove(self.file_path)
        except FileNotFoundError:
            pass

def temp_file_factory(file_path: str) -> TempFile:
    return TempFile(file_path)