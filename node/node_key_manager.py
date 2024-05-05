import cryptography.hazmat.primitives.asymmetric.ed25519

from .node_manager import NodeManager
from .remote_node_manager import RemoteNodeManager
from utils.ed25519 import *


class NodeKeyManager:
    def __init__(self, node_manager: NodeManager, remote_node_manager: RemoteNodeManager, vertex_endpoint: str):
        self.vertex_endpoint = vertex_endpoint
        self.node_manager = node_manager
        self.remote_node_manager = remote_node_manager

    def get_signing_public_key(self, kid: str) ->\
            (str, str, cryptography.hazmat.primitives.asymmetric.ed25519.Ed25519PublicKey):
        components = kid.split("/")

        if len(components) != 2:
            raise Exception("Invalid key id")

        if components[0] == self.vertex_endpoint:
            return components[0], components[1], string_to_public_key(self.node_manager.get(components[1])["signing_public_key"])
        else:
            return components[0], components[1], string_to_public_key(
                self.remote_node_manager.get(components[0], components[1])["signing_public_key"])
