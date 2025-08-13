"""Finmail Ingest Function for Azure Functions."""

import json

import azure.functions as func

from finmail.models import EmailPayload


def main(req: func.HttpRequest) -> func.HttpResponse:  # noqa: D103
    try:
        data = req.get_json()
    except Exception:
        return func.HttpResponse("Bad JSON", status_code=400)

    try:
        payload = EmailPayload(**data)
    except Exception as e:
        return func.HttpResponse(f"Validation error: {e}", status_code=422)

    return func.HttpResponse(
        json.dumps({"ok": True, "subject": payload.subject}),
        mimetype="application/json",
        status_code=200,
    )
