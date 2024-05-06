import os

from dotenv import *
from flask import Flask, request, jsonify, g
from tinydb import TinyDB
from huey import SqliteHuey

from health import *
from admin import *
from node import *
from actor import *
from messaging import *

load_dotenv()
jwt_signing_key = os.getenv("JWT_SIGNING_KEY")
vertex_endpoint = os.getenv("VERTEX_ENDPOINT")
data_path = os.getenv("DATA_PATH")
federation_protocol = os.getenv("FEDERATION_PROTOCOL")

if not os.path.exists(data_path):
    os.makedirs(data_path)

app = Flask(__name__)
huey = SqliteHuey("worker", filename= os.path.join(data_path, "huey.db"))
meta_db = TinyDB(os.path.join(data_path, 'meta.json'))

admin_manager = AdminManager(meta_db.table("admins"), jwt_signing_key, vertex_endpoint)
node_manager = NodeManager(meta_db.table("nodes"))
actor_manager = ActorManager(meta_db.table("actors"), node_manager, vertex_endpoint)
remote_node_manager = RemoteNodeManager(federation_protocol)
node_key_manager = NodeKeyManager(node_manager, remote_node_manager, vertex_endpoint)
outbox_manager = OutboxManager(meta_db.table("outboxes"), node_manager)
inbox_manager = InboxManager(meta_db.table("inboxes"), node_manager)

HealthAPI(app).register()
AdminAPI(app, admin_manager).register()
NodeApi(app, node_manager).register()
ActorApi(app, actor_manager).register()
OutboxApi(app, outbox_manager).register()
InboxApi(app, inbox_manager).register()


@app.before_request
def before_request():
    g.request_body = request.get_json(force=True, silent=True)
    g.jwt_signing_key = jwt_signing_key
    g.vertex_endpoint = vertex_endpoint
    g.node_key_manager = node_key_manager


@app.errorhandler(404)
def handle_404_error(e):
    return jsonify({
        "success": False,
        "message": str(e)
    }), 404


@app.errorhandler(Exception)
def handle_all_errors(e):
    return jsonify({
        "success": False,
        "message": str(e)
    }), 500


if __name__ == '__main__':
    app.run(host=os.getenv("HOST"), port=int(os.getenv("PORT")), debug=os.getenv("ENV") != "PROD")
