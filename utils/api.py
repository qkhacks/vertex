from flask import g, request
from functools import wraps
import jwt


def required_param(key: str, data_type=str):
    if not g.request_body:
        raise Exception("Request body is missing")
    if key not in g.request_body:
        raise Exception(f"{key} is required")
    val = g.request_body[key]
    if not isinstance(val, data_type):
        raise Exception(f"Invalid data type for value of {key}")
    return val


def optional_param(key: str, data_type=str):
    if not g.request_body:
        return None
    if key not in g.request_body:
        return None
    val = g.request_body[key]
    if not isinstance(val, data_type):
        raise Exception(f"Invalid data type for value of {key}")
    return val


def page():
    return request.args.get("page", 0, int)


def size():
    return request.args.get("size", 50, int)


def authenticate_admin(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]

        if not token:
            raise Exception("Invalid access token")

        try:
            data = jwt.decode(token, g.jwt_signing_key, algorithms=['HS256'], issuer=g.vertex_endpoint,
                              audience=g.vertex_endpoint)
            if data["type"] != "admin":
                raise Exception("Invalid access token")
            current_admin = {
                "username": data["sub"]
            }
        except Exception as _:
            raise Exception("Invalid access token")

        return f(current_admin, *args, **kwargs)

    return decorated


def authenticate_actor(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]

        if not token:
            raise Exception("Invalid access token")

        try:
            kid = jwt.get_unverified_header(token)["kid"]
            issuer_vertex_endpoint, issuer_node_identifier, issuer_signing_public_key = g.node_key_manager.get_signing_public_key(
                kid)

            data = jwt.decode(token,
                              issuer_signing_public_key,
                              algorithms=['EdDSA'],
                              issuer="%s/%s" % (issuer_vertex_endpoint, issuer_node_identifier),
                              audience="%s/%s" % (g.vertex_endpoint, kwargs.get("node_identifier")))
            if data["type"] != "actor":
                raise Exception("Invalid access token")
            current_actor = {
                "identifier": data["sub"],
                "vertex_endpoint": issuer_vertex_endpoint,
                "node_identifier": issuer_node_identifier,
                "node_address": "%s/%s" % (issuer_vertex_endpoint, issuer_node_identifier),
                "address": "%s/%s/%s" % (g.vertex_endpoint, issuer_node_identifier, data["sub"])
            }
        except Exception as _:
            raise Exception("Invalid access token")

        return f(current_actor, *args, **kwargs)

    return decorated


def check_local_vertex(actor_vertex_endpoint: str) -> bool:
    return g.vertex_endpoint == actor_vertex_endpoint


def check_node_is_home(actor, node_identifier: str) -> bool:
    return check_local_vertex(actor["vertex_endpoint"]) and actor["node_identifier"] == node_identifier
