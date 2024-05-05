from flask import Flask
from utils.api import *

from messaging.outbox_manager import OutboxManager


class OutboxApi:
    def __init__(self, app: Flask, manager: OutboxManager):
        self.app = app
        self.manager = manager

    def register(self):
        @self.app.post("/api/v1/nodes/<node_identifier>/messaging/outboxes")
        @authenticate_actor
        def create_outbox(actor, node_identifier):
            return self.manager.create(
                node_identifier,
                required_param("identifier"),
                optional_param("description"),
                actor["address"]
            )

        @self.app.get("/api/v1/nodes/<node_identifier>/messaging/outboxes")
        @authenticate_actor
        def list_outboxes(actor, node_identifier):
            return self.manager.list(node_identifier, actor["address"])

        @self.app.get("/api/v1/nodes/<node_identifier>/messaging/outboxes/<identifier>")
        @authenticate_actor
        def get_outbox(actor, node_identifier, identifier: str):
            return self.manager.get(node_identifier, identifier, actor["address"])

        @self.app.put("/api/v1/nodes/<node_identifier>/messaging/outboxes/<identifier>")
        @authenticate_actor
        def update_outbox(actor, node_identifier, identifier):
            return self.manager.update(node_identifier, identifier, optional_param("description"), actor["address"])

        @self.app.delete("/api/v1/nodes/<node_identifier>/messaging/outboxes/<identifier>")
        @authenticate_actor
        def delete_outbox(actor, node_identifier, identifier):
            return self.manager.delete(node_identifier, identifier, actor["address"])
