# -*- coding: utf-8 -*-

import os
import json


class JSONHandler:
    """
    TODO:
        Read and write data in JSON
    """
            
    def __init__(self, file_path: str = None) -> None:
        self.file_path = file_path
        self.encodings = ["utf-8", "latin-1"]

    def read_json(self) -> None | dict:
        """
        TODO:
            - Read a JSon file and return its data
             - I added encoding='utf-8' to the open() functions in both methods.
             This ensures that the file is read and written as UTF-8.
        """
        
        for encoding in self.encodings:
            try:
                with open(self.file_path, "r", encoding=encoding) as f:
                    data = json.load(f)
                return data
            except FileNotFoundError:
                print(f"Error: File not found at path: {self.file_path}")
            except json.JSONDecodeError as error1:
                print(f"Error decoding JSON in {self.file_path}: {error1}")
            except Exception as error2:
                print(f"Error reading JSON from {self.file_path}: {error2}")
    
    def write_json(self, data) -> None:
        """
        TODO:
            - Writes data to a JSON file
             - I added ensure_ascii=False to the json_options.dump() method.
             - This ensures that non-ASCII characters are written to the JSON file correctly,
             instead of being escaped with sequels.
             - I added encoding='utf-8' to the open() functions in both methods.
             This ensures that the file is read and written as UTF-8.
        """
        for encoding in self.encodings:
            with open(self.file_path, "w", encoding=encoding) as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            return

    def read_options_json(self, file_path: str = None) -> None | dict:
        """
        TODO:
            - Read a JSon file and return its data
             - I added encoding='utf-8' to the open() functions in both methods.
             This ensures that the file is read and written as UTF-8.
        """
        paths = [file_path, os.getcwd() + r"\src\json\options.json"]

        for path in paths:
            for encoding in self.encodings:
                try:
                    with open(path, "r", encoding=encoding) as f:
                        data = json.load(f)
                    return data
                except FileNotFoundError:
                    ...
                except json.JSONDecodeError:
                    ...
                except Exception as error2:
                    # print(f"Error reading JSON from {path}: {error2}")
                    ...
