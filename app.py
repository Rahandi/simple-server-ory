from flask import Flask, redirect, request

KRATOS_URL = "http://localhost:4433"

app = Flask(__name__)


@app.route('/registration', methods=['GET'])
def registration():
    args = request.args
    flowId = args.get('flow')

    if flowId:
        return flowId

    return redirect(KRATOS_URL + "/self-service/registration/api")

@app.route('/registration', methods=['POST'])
def registration_post():
    body = request.get_json()
    username = body.get('username')
    password = body.get('password')

    return username + password