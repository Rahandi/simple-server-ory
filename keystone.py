from keystoneauth1 import session
from keystoneauth1.identity import v3
from keystoneclient.v3 import client

class Keystone:
  def __init__(self, username, password) -> None:
    auth = v3.Password(auth_url="http://10.0.3.199/identity/v3", username=username, password=password, project_name="admin", user_domain_id="default", project_domain_id="default")
    sess = session.Session(auth=auth)
    self.keystone = client.Client(session=sess)

  def create_project(self, name, project_members=[], description="testing", domain='default', enabled=True):
    project = self.keystone.projects.create(name=name, description=description, domain=domain, enabled=enabled)

    # add user admin to project
    admin = self.keystone.users.find(name='admin')
    admin_role = self.keystone.roles.find(name='admin')
    self.keystone.roles.grant(role=admin_role, user=admin, project=project)

    project_member_role = self.keystone.roles.create(name=f'{name}_member', project=project)
    for member in project_members:
      user = self.keystone.users.find(name=member)
      self.keystone.roles.grant(role=project_member_role, user=user, project=project)

    return project
  
  def delete_project(self, name):
    project = self.keystone.projects.find(name=name)
    project.delete()
    return project
  
  def create_user(self, name, password, domain='default', enabled=True):
    user = self.keystone.users.create(name=name, password=password, domain=domain, enabled=enabled)
    return user
  
  def add_project_members(self, project, members):
    project_member_role = self.keystone.roles.find(name=f'{project}_member')
    for member in members:
      user = self.keystone.users.find(name=member)
      self.keystone.roles.grant(role=project_member_role, user=user, project=project)
    return project
  
  def remove_project_members(self, project, members):
    project_member_role = self.keystone.roles.find(name=f'{project}_member')
    for member in members:
      user = self.keystone.users.find(name=member)
      self.keystone.roles.revoke(role=project_member_role, user=user, project=project)
    return project