from flask import Flask


class HealthAPI:
    def __init__(self, app: Flask):
        self.app = app

    def register(self):
        @self.app.get('/health')
        def health():
            return {
                'status': 'ok',
            }