from .admin_manager import AdminManager
from flask import Flask
from utils.api import *


class AdminAPI:
    def __init__(self, app: Flask, manager: AdminManager):
        self.app = app
        self.manager = manager

    def register(self):
        @self.app.post("/api/v1/admins/init")
        def init_admin():
            return self.manager.init(
                required_param("username"),
                required_param("password")
            )

        @self.app.post("/api/v1/admins/token")
        def get_admin_token():
            return self.manager.get_token(
                required_param("username"),
                required_param("password")
            )

        @self.app.get("/api/v1/admins/current")
        @authenticate_admin
        def get_current_admin_details(admin):
            return self.manager.get(admin["username"])

        @self.app.put("/api/v1/admins/current/password")
        @authenticate_admin
        def change_current_admin_password(admin):
            return self.manager.change_password(
                admin["username"],
                required_param("password"),
            )

        @self.app.post("/api/v1/admins")
        @authenticate_admin
        def add_admin(admin):
            return self.manager.add(required_param("username"), admin["username"])

        @self.app.get("/api/v1/admins")
        @authenticate_admin
        def list_admins(_):
            return self.manager.list()

        @self.app.get("/api/v1/admins/<username>")
        @authenticate_admin
        def get_admin_details(_, username):
            return self.manager.get(username)

        @self.app.delete("/api/v1/admins/<username>")
        @authenticate_admin
        def delete_admin(_, username):
            return self.manager.delete(username)

        @self.app.put("/api/v1/admins/<username>/password")
        @authenticate_admin
        def reset_admin_password(_, username):
            return self.manager.reset_password(username)
