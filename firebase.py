# -*- coding: utf-8 -*-

import os
import firebase_admin
from typing import Union
from firebase_admin import credentials, db, initialize_app
from infra import log, FIREBASE_API_KEY


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
                FIREBASE_API_KEY = "infra/uuidgensen-firebase-adminsdk-odnzh-1be5bd0dcb.json"

            self.firebase_launcher(credentials.Certificate(FIREBASE_API_KEY))
            return db.reference(reference_path)
        except Exception as e:
            log.error(f"Error establishing Firebase connection: {e}")
            return None


if __name__ == "__main__":
    firebase = Firebase()
    connection = firebase.firebase_connection("status")
