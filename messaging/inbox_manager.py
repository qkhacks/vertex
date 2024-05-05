import time

from tinydb.table import Table
from tinydb import Query

from node import NodeManager


class InboxManager:
    def __init__(self, db: Table, node_manager: NodeManager):
        self.db = db
        self.node_manager = node_manager

    def create(self, node_identifier: str, identifier: str, description: str, creator_address: str) -> dict:
        if not self.node_manager.identifier_exists(node_identifier):
            raise Exception(f"Node {node_identifier} does not exist")
        if self.identifier_exists(identifier, node_identifier):
            raise Exception(f"Inbox {identifier} already exists on node {node_identifier}")

        inbox_id = self.db.insert({
            "node_identifier": node_identifier,
            "identifier": identifier,
            "description": description,
            "creator_address": creator_address,
            "created_on": int(time.time()),
            "modified_on": int(time.time()),
        })

        return {
            "id": inbox_id,
            "identifier": identifier,
        }

    def list(self, node_identifier: str, actor_address: str) -> list[dict]:
        query = Query()
        inboxes = self.db.search((query.creator_address == actor_address) &
                                 (query.node_identifier == node_identifier))
        results = []
        for inbox in inboxes:
            results.append(self.to_dict(inbox))
        return results

    def get(self, node_identifier: str, identifier: str, actor_address: str) -> dict:
        query = Query()
        inbox = self.db.get((query.node_identifier == node_identifier) &
                            (query.identifier == identifier) &
                            (query.creator_address == actor_address))
        if not inbox:
            raise Exception(f"Inbox {identifier} does not exist on node {node_identifier}")
        return self.to_dict(inbox)

    def update(self, node_identifier: str, identifier: str, description: str, actor_address: str) -> dict:
        query = Query()
        results = self.db.update({
            "description": description,
            "modified_on": int(time.time()),
        }, (query.node_identifier == node_identifier) &
           (query.identifier == identifier) &
           (query.creator_address == actor_address))

        if len(results) == 0:
            raise Exception(f"Inbox {identifier} does not exist on node {node_identifier}")

        return {
            "identifier": identifier,
        }

    def delete(self, node_identifier: str, identifier: str, actor_address) -> dict:
        query = Query()
        results = self.db.remove((query.node_identifier == node_identifier) &
                                 (query.identifier == identifier) &
                                 (query.creator_address == actor_address))
        if len(results) == 0:
            raise Exception(f"Inbox {identifier} does not exist on node {node_identifier}")
        return {
            "identifier": identifier,
        }

    def identifier_exists(self, identifier: str, node_identifier: str) -> bool:
        query = Query()
        return self.db.contains((query.identifier == identifier) & (query.node_identifier == node_identifier))

    @staticmethod
    def to_dict(self):
        return {
            "node_identifier": self["node_identifier"],
            "identifier": self["identifier"],
            "description": self["description"],
            "creator_address": self["creator_address"],
            "created_on": self["created_on"],
            "modified_on": self["modified_on"]
        }
