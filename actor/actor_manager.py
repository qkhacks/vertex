import time

import bcrypt
import jwt
from tinydb.table import Table
from tinydb import Query

import utils.ed25519
from node import NodeManager


class ActorManager:

    def __init__(self, db: Table, node_manager: NodeManager, vertex_endpoint: str):
        self.db = db
        self.node_manager = node_manager
        self.vertex_endpoint = vertex_endpoint

    def sign_up(self, node_identifier: str, identifier: str, password: str, actor_type: str, display_name: str):
        if not self.node_manager.identifier_exists(node_identifier):
            raise Exception(f"Node {node_identifier} not found")

        if self.username_exists(node_identifier, identifier):
            raise Exception(f"Actor {identifier} already exists on node {node_identifier}")

        actor_id = self.db.insert({
            "node_identifier": node_identifier,
            "identifier": identifier,
            "password": bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8"),
            "type": actor_type,
            "display_name": display_name,
            "created_on": int(time.time()),
            "modified_on": int(time.time()),
        })

        return {
            "id": actor_id,
            "identifier": identifier,
        }

    def get_token(self, node_identifier: str, identifier: str, password: str,
                  audience_node_address: str = None) -> dict:
        node = self.node_manager.get_signing_private_key(node_identifier)
        query = Query()
        actor = self.db.get(
            (query.node_identifier == node_identifier) &
            (query.identifier == identifier)
        )

        if not actor:
            raise Exception("Invalid login credentials")

        if not bcrypt.checkpw(password.encode("utf-8"), actor["password"].encode("utf-8")):
            raise Exception("Invalid login credentials")

        issuer = "%s/%s" % (self.vertex_endpoint, node_identifier)
        if not audience_node_address:
            audience_node_address = issuer

        return {
            "token": jwt.encode({
                "sub": actor["identifier"],
                "type": "actor",
                "aud": audience_node_address,
                "iss": issuer,
                "iat": int(time.time()),
            }, headers={
                "kid": issuer
            }, key=utils.ed25519.string_to_private_key(node["signing_private_key"]), algorithm='EdDSA')
        }

    def get(self, node_identifier: str, identifier: str) -> dict:
        query = Query()
        actor = self.db.get((query.node_identifier == node_identifier) &
                            (query.identifier == identifier))

        if not actor:
            raise Exception(f"Actor {identifier} not found on node {node_identifier}")

        return self.to_dict(actor)

    def update(self, node_identifier: str, identifier: str, display_name: str):
        query = Query()
        results = self.db.update({
            "display_name": display_name,
            "modified_on": int(time.time()),
        }, (query.node_identifier == node_identifier) &
           (query.identifier == identifier))

        if len(results) == 0:
            raise Exception(f"Actor {identifier} not found on node {node_identifier}")

        return {
            "identifier": identifier,
        }

    def change_password(self, node_identifier: str, identifier: str, password: str) -> dict:
        query = Query()
        results = self.db.update({
            "password": bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()),
            "modified_on": int(time.time()),
        }, (query.node_identifier == node_identifier) &
           (query.identifier == identifier))

        if len(results) == 0:
            raise Exception(f"Actor {identifier} not found on node {node_identifier}")

        return {
            "identifier": identifier,
        }

    def delete(self, node_identifier: str, identifier: str) -> dict:
        query = Query()
        results = self.db.remove((query.node_identifier == node_identifier) &
                                 (query.identifier == identifier))

        if len(results) == 0:
            raise Exception(f"Actor {identifier} not found on node {node_identifier}")
        return {
            "identifier": identifier,
        }

    def username_exists(self, node_identifier: str, identifier: str) -> bool:
        query = Query()
        return self.db.contains((query.node_identifier == node_identifier) & (query.identifier == identifier))

    @staticmethod
    def to_dict(self) -> dict:
        return {
            "node_identifier": self["node_identifier"],
            "identifier": self["identifier"],
            "type": self["type"],
            "display_name": self["display_name"],
            "created_on": self["created_on"],
            "modified_on": self["modified_on"],
        }
