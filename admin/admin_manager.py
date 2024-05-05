import bcrypt
import jwt
from password_generator import PasswordGenerator
from tinydb.table import Table
from tinydb import Query
from time import time


class AdminManager:

    def __init__(self, db: Table, jwt_signing_key: str, vertex_endpoint: str) -> None:
        self.db = db
        self.jwt_signing_key = jwt_signing_key
        self.vertex_endpoint = vertex_endpoint
        self.password_generator = PasswordGenerator()

    def init(self, username: str, password: str) -> dict:
        if len(self.db.all()) != 0:
            raise Exception("Not allowed")

        admin_id = self.db.insert({
            "username": username,
            "password": bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
            "creator": None,
            "created_on": int(time()),
            "modified_on": int(time()),
        })

        return {
            "id": admin_id,
            "username": username,
        }

    def get_token(self, username: str, password: str) -> dict:
        query = Query()
        admin = self.db.get(query.username == username)

        if not admin:
            raise Exception("Invalid username and password combination")

        if not bcrypt.checkpw(password.encode('utf-8'), admin["password"].encode('utf-8')):
            raise Exception("Invalid username and password combination")

        return {
            "token": jwt.encode({
                "sub": admin["username"],
                "type": "admin",
                "iat": int(time()),
                "iss": self.vertex_endpoint,
                "aud": self.vertex_endpoint
            }, algorithm="HS256", key=self.jwt_signing_key),
        }

    def get(self, username: str) -> dict:
        query = Query()
        admin = self.db.get(query.username == username)
        if not admin:
            raise Exception(f"Admin {username} not found")
        return self.to_dict(admin)

    def change_password(self, username: str, password: str) -> dict:
        query = Query()
        result = self.db.update({
            "password": bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
            "modified_on": int(time()),
        }, query.username == username)

        if len(result) == 0:
            raise Exception("User not found")

        return {
            "username": username
        }

    def add(self, username: str, creator: str) -> dict:
        password = self.password_generator.generate()

        if self.username_exists(username):
            raise Exception(f"Username {username} already exists")

        admin_id = self.db.insert({
            "username": username,
            "password": bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
            "creator": creator,
            "created_on": int(time()),
            "modified_on": int(time()),
        })

        return {
            "id": admin_id,
            "username": username
        }

    def delete(self, username: str) -> dict:
        query = Query()
        result = self.db.remove(query.username == username)
        if len(result) == 0:
            raise Exception(f"User {username} not found")
        return {
            "username": username
        }

    def reset_password(self, username: str) -> dict:
        password = self.password_generator.generate()
        return self.change_password(username, password)

    def list(self):
        admins = self.db.all()
        results = []
        for admin in admins:
            results.append(self.to_dict(admin))
        return results

    def username_exists(self, username: str) -> bool:
        query = Query()
        return self.db.contains(query.username == username)

    @staticmethod
    def to_dict(self) -> dict:
        return {
            "username": self["username"],
            "creator": self["creator"],
            "created_on": self["created_on"],
            "modified_on": self["modified_on"],
        }
