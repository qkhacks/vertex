from flask import Flask
from utils.api import *

from .inbox_manager import InboxManager


class InboxApi:
    def __init__(self, app: Flask, manager: InboxManager):
        self.app = app
        self.manager = manager

    def register(self):
        @self.app.post("/api/v1/nodes/<node_identifier>/messaging/inboxes")
        @authenticate_actor
        def create_inbox(actor, node_identifier):
            return self.manager.create(
                node_identifier,
                required_param("identifier"),
                optional_param("description"),
                actor["address"]
            )

        @self.app.get("/api/v1/nodes/<node_identifier>/messaging/inboxes")
        @authenticate_actor
        def list_inboxes(actor, node_identifier):
            return self.manager.list(node_identifier, actor["address"])

        @self.app.get("/api/v1/nodes/<node_identifier>/messaging/inboxes/<identifier>")
        @authenticate_actor
        def get_inbox(actor, node_identifier, identifier: str):
            return self.manager.get(node_identifier, identifier, actor["address"])

        @self.app.put("/api/v1/nodes/<node_identifier>/messaging/inboxes/<identifier>")
        @authenticate_actor
        def update_inbox(actor, node_identifier, identifier):
            return self.manager.update(node_identifier, identifier, optional_param("description"), actor["address"])

        @self.app.delete("/api/v1/nodes/<node_identifier>/messaging/inboxes/<identifier>")
        @authenticate_actor
        def delete_inbox(actor, node_identifier, identifier):
            return self.manager.delete(node_identifier, identifier, actor["address"])
