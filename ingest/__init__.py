"""Finmail Ingest Function for Azure Functions."""

import json

import azure.functions as func
from pydantic import ValidationError

from finmail.ingest import process_email
from finmail.models import EmailPayload


def main(req: func.HttpRequest) -> func.HttpResponse:  # noqa: D103
    try:
        data = req.get_json()
    except Exception:
        return func.HttpResponse("Bad JSON", status_code=400)

    try:
        payload = EmailPayload(**data)
    except ValidationError as e:
        return func.HttpResponse(f"Validation error: {e}", status_code=422)

    processed = process_email(payload)

    return func.HttpResponse(
        json.dumps({
            "ok": True,
            "subject": payload.subject,
            "processed": processed.model_dump(mode="json") if processed else "",
        }),
        mimetype="application/json",
        status_code=200,
    )
