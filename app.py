from flask import Flask, redirect, request

from keto import Keto
from kratos import Kratos

KRATOS_URL = "http://localhost:4433"
KETO_READ_URL = "http://localhost:4466"
KETO_WRITE_URL = "http://localhost:4467"

app = Flask(__name__)
kratos = Kratos(KRATOS_URL)
keto = Keto(KETO_READ_URL, KETO_WRITE_URL)

PROJECT_ID = "project1"

PROJECT_RESOURCES = [
  "roles",
  "permissions",
  "compute",
]

@app.route('/init', methods=['GET'])
def init_get():
  keto.add_role_permission(PROJECT_ID, 'admin', '', 'create')
  keto.add_role_permission(PROJECT_ID, 'admin', '', 'read')
  keto.add_role_permission(PROJECT_ID, 'admin', '', 'update')
  keto.add_role_permission(PROJECT_ID, 'admin', '', 'delete')

  for resource in PROJECT_RESOURCES:
    keto.add_child_permission(PROJECT_ID, '', resource, 'create')
    keto.add_child_permission(PROJECT_ID, '', resource, 'read')
    keto.add_child_permission(PROJECT_ID, '', resource, 'update')
    keto.add_child_permission(PROJECT_ID, '', resource, 'delete')

  return 'ok'

@app.route('/register', methods=['POST'])
def registration_post():
  body = request.get_json()
  username = body.get('username')
  password = body.get('password')

  registered = kratos.register(username, password)
  if 'messages' in registered:
    return registered

  if username == 'admin':
    keto.add_role(registered['principal_id'], 'admin', PROJECT_ID)
  else:
    keto.add_role(registered['principal_id'], 'user', PROJECT_ID)

  return registered

@app.route('/login', methods=['POST'])
def login_post():
  body = request.get_json()
  username = body.get('username')
  password = body.get('password')

  return kratos.login(username, password)

@app.route('/add_role', methods=['POST'])
def add_role_post():
  if not check_permission(request.headers.get('Authorization'), 'roles', 'create'):
    return 'Unauthorized', 401

  body = request.get_json()
  principal_id = body.get('principal_id')
  role = body.get('role')

  return keto.add_role(principal_id, role, PROJECT_ID)

@app.route('/add_permission', methods=['POST'])
def add_permission_post():
  if not check_permission(request.headers.get('Authorization'), 'permissions', 'create'):
    return 'Unauthorized', 401

  body = request.get_json()
  principal_id = body.get('principal_id')
  resource_id = body.get('resource_id')
  operation = body.get('operation')

  return keto.add_permission(PROJECT_ID, principal_id, resource_id, operation)

@app.route('/resources/<resource>', methods=['GET'])
def resources_get(resource):
  operation = request.headers.get('operation')
  if not check_permission(request.headers.get('Authorization'), resource, operation):
    return 'Unauthorized', 401

  return f"access to {resource} is allowed"

def check_permission(authorization, object, operation):
  principal_id = kratos.whoami(authorization).get('principal_id')
  return keto.check_permission(PROJECT_ID, principal_id, object, operation)