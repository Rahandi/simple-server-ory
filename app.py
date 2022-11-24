from flask import Flask, redirect, request

KRATOS_URL = "http://localhost:4433"

app = Flask(__name__)


@app.route('/registration', methods=['GET'])
def registration():
    return redirect(KRATOS_URL + "/self-service/registration/browser")
