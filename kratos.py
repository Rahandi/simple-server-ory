from typing import NamedTuple

import ory_kratos_client
import requests


class KratosResponse:
  messages : list
  token : str
  action_url : str
  csrf_token : str
  principal_id : str

  def __init__(self):
    self.messages = []
    self.token = ""
    self.action_url = ""
    self.csrf_token = ""
    self.principal_id = ""


class Kratos:
  def __init__(self, url=None):
    if url is None:
      raise Exception("URL is required")

    self.URL = url

  def register(self, username, password):
    response = requests.get(self.URL + "/self-service/registration/api").json()
    initResponse = self._parse_kratos_responses(response)
    response = requests.post(initResponse.action_url, json={
      "csrf_token": initResponse.csrf_token,
      "method": "password",
      "password": password,
      "traits": {
          "username": username
      }
    }).json()
    registerResponse = self._parse_kratos_responses(response)
    if len(registerResponse.messages) > 0:
      return {"messages": registerResponse.messages}

    return {
      "principal_id": registerResponse.principal_id,
      "token": registerResponse.token
    }

  def login(self, username, password):
    response = requests.get(self.URL + "/self-service/login/api").json()
    initResponse = self._parse_kratos_responses(response)
    response = requests.post(initResponse.action_url, json={
      "identifier": username,
      "method": "password",
      "password": password
    }).json()
    loginResponse = self._parse_kratos_responses(response)
    if len(loginResponse.messages) > 0:
      return {"messages": loginResponse.messages}

    return {
      "principal_id": loginResponse.principal_id,
      "token": loginResponse.token
    }
  
  def whoami(self, token):
    response = requests.get(self.URL + "/sessions/whoami", headers={"X-Session-Token": token}).json()
    responseParsed = self._parse_kratos_responses(response)

    return {
      "principal_id": responseParsed.principal_id,
    }

  def _parse_kratos_responses(self, response) -> KratosResponse:
    kratosResponse = KratosResponse()

    kratosResponse.action_url = response.get("ui", {}).get("action", "")
    kratosResponse.token = response.get("session_token", "")

    # temporary use username as principal_id
    # kratosResponse.principal_id = response.get("identity", {}).get("id", "")
    kratosResponse.principal_id = response.get("identity", {}).get("traits", {}).get("username", "")

    generalMessages = response.get("ui", {}).get("messages", [])
    for message in generalMessages:
      kratosResponse.messages.append(message.get("text", ""))

    nodes = response.get("ui", {}).get("nodes", [])
    for node in nodes:
      if node.get("type") == "input":
        messages = node.get("messages", [])
        for message in messages:
          kratosResponse.messages.append(message.get("text", ""))
        if node.get("attributes", {}).get("name") == "csrf_token":
          kratosResponse.csrf_token = node.get("attributes", {}).get("value", "")

    return kratosResponse
