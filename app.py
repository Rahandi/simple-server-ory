from flask import Flask, redirect, request

from datastore import DataStore
from keto import Keto
from keystone import Keystone
from kratos import Kratos

import base64

KRATOS_URL = "http://localhost:4433"
KETO_READ_URL = "http://localhost:4466"
KETO_WRITE_URL = "http://localhost:4467"

app = Flask(__name__)
datastore = DataStore()

kratos = Kratos(KRATOS_URL)
keto = Keto(KETO_READ_URL, KETO_WRITE_URL)


PROJECT_ID = "project"

PROJECT_RESOURCES = [
  "roles",
  "permissions",
  "compute",
]

def permission_check(project, object, operation):
  principal = kratos.whoami(request.headers.get('Authorization')).get('principal_id')
  allowed = keto.check_permission(project, principal, object, operation)
  data = {
    'principal': datastore.get_user(principal),
    'allowed': allowed
  }

  return data

@app.route('/register', methods=['POST'])
def registration_post():
  body = request.get_json()
  username = body.get('username')
  password = body.get('password')

  registered = kratos.register(username, password)
  if 'messages' in registered:
    return registered

  keystone_passwd = None
  if username == 'admin':
    keystone_passwd = 'adminpw'
  else:
    keystone = Keystone('admin', 'adminpw')
    keystone_password = base64.b64encode(f'{username}{password}'.encode('utf-8')).decode('utf-8')
    keystone.create_user(username, keystone_password)

  datastore.create_tables()
  datastore.add_user(username, password, keystone_passwd)

  return registered

@app.route('/login', methods=['POST'])
def login_post():
  body = request.get_json()
  username = body.get('username')
  password = body.get('password')

  return kratos.login(username, password)

@app.route('/create_project', methods=['POST'])
def create_project_post():
  check = permission_check('project', '', 'create')
  if check.get('principal') != 'admin':
    return 'Unauthorized', 401

  keystone = Keystone('admin', 'adminpw')

  body = request.get_json()
  project_name = body.get('project_name')
  project_admin = body.get('project_admin')
  project_members = body.get('project_members')
  project_members.append(project_admin)

  project = keystone.create_project(project_name, project_members)
  project = project.name
  
  keto.add_role('admin', 'admin', project)
  keto.add_role(project_admin, 'admin', project)
  for member in project_members:
    keto.add_role(member, 'user', project)

  keto.add_role_permission(project, 'admin', '', 'create')
  keto.add_role_permission(project, 'admin', '', 'read')
  keto.add_role_permission(project, 'admin', '', 'update')
  keto.add_role_permission(project, 'admin', '', 'delete')

  keto.add_role_permission(project, 'user', '', 'read')

  for resource in PROJECT_RESOURCES:
    keto.add_child_permission(project, '', resource, 'create')
    keto.add_child_permission(project, '', resource, 'read')
    keto.add_child_permission(project, '', resource, 'update')
    keto.add_child_permission(project, '', resource, 'delete')

  return 'ok'

@app.route('/<project>/delete', methods=['DELETE'])
def delete_project_post(project):
  check = permission_check(project, '', 'delete')
  if not check['allowed']:
    return 'Unauthorized', 401
  
  principal = check.get('principal')
  keystone = Keystone(principal[1], principal[3])
  project = keystone.delete_project(project)
  return 'ok'

@app.route('/<project>/members/add', methods=['POST'])
def add_project_member_post(project):
  check = permission_check(project, 'roles', 'create')
  if not check['allowed']:
    return 'Unauthorized', 401
  
  principal = check.get('principal')
  body = request.get_json()
  role = body.get('role')
  members = body.get('members')

  keystone = Keystone(principal[1], principal[3])
  keystone.add_project_member(project, members)

  for member in members:
    keto.add_role(member, role, project)
    keto.add_child_permission(project, 'roles', member, 'create')
    keto.add_child_permission(project, 'roles', member, 'read')
    keto.add_child_permission(project, 'roles', member, 'update')
    keto.add_child_permission(project, 'roles', member, 'delete')

  return 'ok'

@app.route('/<project>/members/remove', methods=['POST'])
def remove_project_member_post(project):
  check = permission_check(project, 'roles', 'delete')
  if not check['allowed']:
    return 'Unauthorized', 401
  
  principal = check.get('principal')
  keystone = Keystone(principal[1], principal[3])
  members = request.get_json().get('members')
  keystone.remove_project_member(project, members)

  for member in members:
    keto.remove_role(member, 'admin', project)
    keto.remove_role(member, 'user', project)

  return 'ok'

# @app.route('/<project>/add_role', methods=['POST'])
# def add_role_post(project):
#   check = permission_check(project, 'roles', 'delete')
#   if not check['allowed']:
#     return 'Unauthorized', 401

#   body = request.get_json()
#   principal_id = body.get('principal_id')
#   role = body.get('role')

#   return keto.add_role(principal_id, role, PROJECT_ID)

# @app.route('/add_permission', methods=['POST'])
# def add_permission_post():
#   if not check_permission(request.headers.get('Authorization'), 'permissions', 'create'):
#     return 'Unauthorized', 401

#   body = request.get_json()
#   principal_id = body.get('principal_id')
#   resource_id = body.get('resource_id')
#   operation = body.get('operation')

#   return keto.add_permission(PROJECT_ID, principal_id, resource_id, operation)

# @app.route('/resources/<resource>', methods=['GET'])
# def resources_get(resource):
#   operation = request.headers.get('operation')
#   if not check_permission(request.headers.get('Authorization'), resource, operation):
#     return 'Unauthorized', 401

#   return f"access to {resource} is allowed"