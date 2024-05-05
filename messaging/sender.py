from messaging import OutboxManager


class Sender:
    def __init__(self, outbox_manager: OutboxManager):
        self.outbox_manager = outbox_manager

    def send(self, node_identifier: str, outbox_identifier: str, inbox_addresses: list[str], message: object):
        pass
