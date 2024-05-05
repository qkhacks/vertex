from .actor_manager import ActorManager
from flask import Flask
from utils.api import *


class ActorApi:
    def __init__(self, app: Flask, actor_manager: ActorManager):
        self.app = app
        self.actor_manager = actor_manager

    def register(self):
        @self.app.post('/api/v1/nodes/<node_identifier>/actors/signup')
        def actor_sign_up(node_identifier: str):
            return self.actor_manager.sign_up(
                node_identifier,
                required_param("identifier"),
                required_param("password"),
                required_param("type"),
                required_param("display_name")
            )

        @self.app.post('/api/v1/nodes/<node_identifier>/actors/token')
        def get_actor_token(node_identifier: str):
            return self.actor_manager.get_token(
                node_identifier,
                required_param("identifier"),
                required_param("password")
            )

        @self.app.get("/api/v1/nodes/<node_identifier>/actors/current")
        @authenticate_actor
        def get_actor(actor, node_identifier: str):
            check_node_is_home(actor, node_identifier)
            return self.actor_manager.get(actor["node_identifier"], actor["identifier"])

        @self.app.put("/api/v1/nodes/<node_identifier>/actors/current")
        @authenticate_actor
        def update_actor(actor, node_identifier: str):
            check_node_is_home(actor, node_identifier)
            return self.actor_manager.update(actor["node_identifier"],
                                             actor["identifier"],
                                             required_param("display_name"))

        @self.app.delete("/api/v1/nodes/<node_identifier>/actors/current/password")
        @authenticate_actor
        def change_actor_password(actor, node_identifier: str):
            check_node_is_home(actor, node_identifier)
            return self.actor_manager.change_password(actor["node_identifier"],
                                                      actor["identifier"],
                                                      required_param("password"))

        @self.app.delete("/api/v1/nodes/<node_identifier>/actors/current")
        @authenticate_actor
        def delete_actor(actor, node_identifier: str):
            check_node_is_home(actor, node_identifier)
            return self.actor_manager.delete(actor["node_identifier"], actor["identifier"])
