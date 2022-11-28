import requests


class Keto:
  def __init__(self, read_url=None, write_url=None):
    if read_url is None or write_url is None:
      raise Exception("URL is required")
    self.READ_URL = read_url
    self.WRITE_URL = write_url

  def add_role(self, principal_id, role, project_id):
    response = requests.put(self.WRITE_URL + "/admin/relation-tuples", json={
      "namespace": "roles",
      "subject_id": principal_id,
      "object": project_id,
      "relation": role
    }).json()

    return response

  def add_permission(self, project_id, principal_id, resource_id, operation):
    response = requests.put(self.WRITE_URL + "/admin/relation-tuples", json={
      "namespace": "resources",
      "subject_id": principal_id,
      "object": project_id + "/" + resource_id,
      "relation": operation
    }).json()

    return response
  
  def add_role_permission(self, project_id, role, resource_id, operation):
    response = requests.put(self.WRITE_URL + "/admin/relation-tuples", json={
      "namespace": "resources",
      "object": project_id + "/" + resource_id,
      "relation": operation,
      "subject_set": {
        "namespace": "roles",
        "object": project_id,
        "relation": role
      }
    }).json()

    return response
  
  def add_child_permission(self, project_id, parent_resource, child_resource, operation):
    response = requests.put(self.WRITE_URL + "/admin/relation-tuples", json={
      "namespace": "resources",
      "object": project_id + "/" + child_resource,
      "relation": operation,
      "subject_set": {
        "namespace": "resources",
        "object": project_id + "/" + parent_resource,
        "relation": operation,
      }
    }).json()

    return response
  
  def check_permission(self, project_id, principal_id, resource, operation):
    response = requests.post(self.READ_URL + "/relation-tuples/check", json={
      "namespace": "resources",
      "subject_id": principal_id,
      "object": project_id + "/" + resource,
      "relation": operation
    }).json()

    return response.get('allowed', False)