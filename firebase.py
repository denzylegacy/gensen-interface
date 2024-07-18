# -*- coding: utf-8 -*-

import os
import firebase_admin
from typing import Union
from firebase_admin import credentials, db, initialize_app
from infra import log


class Firebase:

    @staticmethod
    def firebase_launcher(_credentials: credentials.Certificate) -> bool:
            if not firebase_admin._apps:
                initialize_app(
                    _credentials, {"databaseURL": "https://uuidgensen-default-rtdb.firebaseio.com/"}
                )

    def __init__(self) -> None:
        pass

    def firebase_connection(self, reference_path: str) -> Union[db.Reference, None]:
        try:
            if os.getenv("ENVIRONMENT") != "SERVER":
                credentials_path = "infra/uuidgensen-firebase-adminsdk-odnzh-1be5bd0dcb.json"
            else:
                credentials_path = "/app/infra/uuidgensen-firebase-adminsdk-odnzh-1be5bd0dcb.json"

            if credentials_path:
                self.firebase_launcher(credentials.Certificate(credentials_path))
                return db.reference(reference_path)
            else:
                log.info("Credentials file not found")
                return None
        except Exception as e:
            log.error(f"Error establishing Firebase connection: {e}")
            return None


if __name__ == "__main__":
    firebase = Firebase()
    connection = firebase.firebase_connection("status")
