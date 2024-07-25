# -*- coding: utf-8 -*-

import os
import json
import firebase_admin
from typing import Union
from firebase_admin import credentials, db, initialize_app
from infra import log, FIREBASE_URL, FIREBASE_API_KEY


class Firebase:

    @staticmethod
    def firebase_launcher(_credentials: credentials.Certificate) -> bool:
            if not firebase_admin._apps:
                initialize_app(
                    _credentials, {"databaseURL": FIREBASE_URL}
                )

    def __init__(self) -> None:
        pass

    def firebase_connection(self, reference_path: str) -> Union[db.Reference, None]:
        try:
            if FIREBASE_API_KEY:
                self.firebase_launcher(credentials.Certificate(json.loads(FIREBASE_API_KEY)))
            else:
                self.firebase_launcher(
                    credentials.Certificate(
                        "infra/uuidgensen-firebase-adminsdk-odnzh-1be5bd0dcb.json"
                    )
                )

            return db.reference(reference_path)
        except Exception as e:
            log.error(f"Error establishing Firebase connection: {e}")
            return None


if __name__ == "__main__":
    firebase = Firebase()
    connection = firebase.firebase_connection("status")
