import os
import json
from dotenv import load_dotenv
import functions_framework
from requests import request
from requests.auth import HTTPBasicAuth
from flask import Request, Response
from werkzeug.exceptions import BadRequest, HTTPException
from markupsafe import escape

load_dotenv()
MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
MAIL_SECRET = os.environ.get("MAIL_SECRET")

SHAPE_MSG = "improper JSON shape"
URL = "https://api.mailjet.com/v3.1/send"
FROM = {"name": "Weterynarz na dyżurze, Ania Ganowska - Vetblog", "email": "weterynarznadyzurze@gmail.com"}


def validate_emails(email_dict):
    REQUIRED_KEYS = ["email", "name"]
    keys = email_dict.keys()
    valid = all([k in keys for k in REQUIRED_KEYS])

    if not valid:
        raise BadRequest(SHAPE_MSG)


def validate_json_shape(request_json):
    REQUIRED_KEYS = ["subject", "message", "to"]
    json_keys = request_json.keys()
    valid = all([k in json_keys for k in REQUIRED_KEYS])
    if not valid:
        raise BadRequest(SHAPE_MSG)
    validate_emails(request_json["to"])
    return request_json


def validate_method(request: Request):
    if request.method != "POST":
        raise BadRequest()


def send_email(validated_json: dict):
    data = {
        "Messages": [
            {
                "From": {
                    "Email": FROM["email"],
                    "Name": FROM["name"],
                },
                "To": [
                    {
                        "Email": validated_json["to"]["email"],
                        "Name": validated_json["to"]["name"],
                    }
                ],
                "Subject": validated_json["subject"],
                "TextPart": validated_json["message"],
                "HTMLPart": escape(validated_json["message"]),
            }
        ]
    }
    auth = HTTPBasicAuth(MAIL_USERNAME, MAIL_SECRET)
    resp = request(auth=auth, method="POST", url=URL, data=json.dumps(data))

    return resp


@functions_framework.http
def send_mail(request: Request):
    """HTTP Cloud Function.
    Args:
        request (flask.Request): The request object.
        <https://flask.palletsprojects.com/en/1.1.x/api/#incoming-request-data>
    Returns:
        The response text, or any set of values that can be turned into a
        Response object using `make_response`
        <https://flask.palletsprojects.com/en/1.1.x/api/#flask.make_response>.
    """
    validate_method(request)

    request_json = request.get_json()

    validated_json = validate_json_shape(request_json)
    resp = send_email(validated_json)

    # breakpoint()
    if resp.status_code != 200:
        raise HTTPException(
            description=resp.content,
            response=Response(response=resp.content, status=resp.status_code),
        )

    return resp.json()
