# -*- coding: utf-8 -

import os
import json
from typing import Dict, List, Any
from .infra import BASE_PATH, log


class JsonDB:
    def __init__(self, db: str = BASE_PATH + "/instance/db.json") -> None:
        self.db = db

    def _read_db(self) -> Dict[str, Any]:
        if not os.path.exists(self.db):
            with open(self.db, "w") as file:
                json.dump({}, file, indent=4)
            log.info(f"'{self.db}' database created successfully!")

        with open(self.db, "r") as file:
            return json.load(file)

    def _write_to_db(self, data: Dict[str, Any]) -> None:
        with open(self.db, "w") as file:
            json.dump(data, file, indent=4)

    def _create_collection(self, collection: str) -> Dict[str, Any]:
        data = self._read_db()

        if collection not in data:
            data[collection] = {}

        self._write_to_db(data)
        log.info(f"Collection '{collection}' successfully created.")

        return self._read_db()

    def create(
            self,
            collection: str,
            doc: str,
            attributes: List[Dict[str, Any]]
    ) -> None:
        data = self._read_db()

        if not data:
            data = self._create_collection(collection)
        elif collection not in data.keys():
            data = self._create_collection(collection)

        for attribute in attributes:
            data[collection][doc] = attribute
            self._write_to_db(data)
            log.info(f"'{doc}' successfully added with attributes '{attribute.keys()}'.")

    def read(
            self,
            collection: str,
            doc: str = None
    ) -> dict:
        data = self._read_db()
        docs = data.get(collection, {})

        if not doc:
            return docs

        doc_data = docs.get(doc, {})
        log.info(f"{doc}: {doc_data}")

        return doc_data

    def update(
            self,
            collection: str,
            doc: str,
            attributes: Dict[str, Any]
    ) -> None:
        data = self._read_db()
        docs = data.get(collection, {})

        if doc in docs:
            docs[doc] |= attributes
            self._write_to_db(data)
            log.info(f"'{doc}' has been updated.")
        else:
            log.error(f"'{doc}' not found.")

    def delete(self, collection: str, doc: str) -> None:
        data = self._read_db()
        if collection in data and doc in data[collection]:
            del data[collection][doc]
            self._write_to_db(data)
            log.info(f"'{doc}' successfully deleted!")
        else:
            log.error(f"'{doc}' not found in collection '{collection}'!")


if __name__ == "__main__":
    json_db = JsonDB(BASE_PATH + "/instance/db.json")
    
    user = "Anna"
    user_path = r"D:/Work/30/src/user_data"

    # Add user
    json_db.create(
        collection="users", doc=user, attributes=[{"path": user_path}]
    )

    # Display user
    user_data = json_db.read(collection=user, doc=user_path)
    print("user_data", user_data)

    # Modify user
    # json_db.update(
    #     collection="users", doc=user, attributes={"path": r"D:\Work\11\WAAPP\src\user_data"}
    # )

    # Delete user
    # json_db.delete(collection="users", doc="John")
