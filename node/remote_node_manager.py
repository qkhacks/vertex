import requests


class RemoteNodeManager:
    def __init__(self, federation_protocol: str):
        self.federation_protocol = federation_protocol

    def get(self, vertex_endpoint: str, identifier: str) -> dict:
        response = requests.get("%s://%s/api/v1/nodes/%s", (self.federation_protocol, vertex_endpoint, identifier)).json()
        return {
            "identifier": identifier,
            "signing_public_key": response["signing_public_key"],
            "description": response["description"],
            "creator": response["creator"],
            "created_on": response["created_on"],
            "modified_on": response["modified_on"]
        }
