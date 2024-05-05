import time

from tinydb.table import Table
from tinydb import Query

import utils.ed25519


class NodeManager:
    def __init__(self, db: Table):
        self.db = db

    def add(self, identifier: str, description: str, creator: str) -> dict:
        if self.identifier_exists(identifier):
            raise Exception(f"Node {identifier} already exists")

        signing_private_key, signing_public_key = utils.ed25519.generate_ed25519_keys()

        node_id = self.db.insert({
            "identifier": identifier,
            "description": description,
            "signing_private_key": utils.ed25519.private_key_to_string(signing_private_key),
            "signing_public_key": utils.ed25519.public_key_to_string(signing_public_key),
            "creator": creator,
            "created_on": int(time.time()),
            "modified_on": int(time.time()),
        })

        return {
            "id": node_id,
            "identifier": identifier,
        }

    def list(self) -> list:
        nodes = self.db.all()
        results = []
        for node in nodes:
            results.append(self.to_dict(node))
        return results

    def get(self, identifier: str) -> dict:
        query = Query()
        node = self.db.get(query.identifier == identifier)
        if not node:
            raise Exception(f"Node {identifier} not found")
        return self.to_dict(node)

    def get_signing_private_key(self, identifier: str) -> dict:
        query = Query()
        node = self.db.get(query.identifier == identifier)
        if not node:
            raise Exception(f"Node {identifier} not found")
        return {
            "signing_private_key": node["signing_private_key"],
        }

    def update(self, identifier: str, description: str) -> dict:
        query = Query()
        result = self.db.update({
            "description": description,
            "modified_on": int(time.time()),
        }, query.identifier == identifier)

        if len(result) == 0:
            raise Exception(f"Node {identifier} not found")

        return {
            "identifier": identifier
        }

    def delete(self, identifier: str) -> dict:
        query = Query()
        result = self.db.remove(query.identifier == identifier)
        if len(result) == 0:
            raise Exception(f"Node {identifier} not found")
        return {
            "identifier": identifier
        }

    def reset_signing_keys(self, identifier: str) -> dict:
        signing_private_key, signing_public_key = utils.ed25519.generate_ed25519_keys()
        signing_public_key_str = utils.ed25519.public_key_to_string(signing_public_key)
        query = Query()
        result = self.db.update({
            "signing_private_key": utils.ed25519.private_key_to_string(signing_private_key),
            "signing_public_key": signing_public_key_str,
            "modified_on": int(time.time()),
        }, query.identifier == identifier)

        if len(result) == 0:
            raise Exception(f"Node {identifier} not found")
        return {
            "identifier": identifier,
            "signing_public_key": signing_public_key_str,
        }

    def identifier_exists(self, identifier: str) -> bool:
        query = Query()
        return self.db.contains(query.identifier == identifier)

    @staticmethod
    def to_dict(self):
        return {
            "identifier": self["identifier"],
            "description": self["description"],
            "signing_public_key": self["signing_public_key"],
            "creator": self["creator"],
            "created_on": self["created_on"],
            "modified_on": self["modified_on"],
        }
