"""Finmail Ingest Function for Azure Functions."""

import json

import azure.functions as func

from shared_code.finmail.core.google_client import google_sheets_client
from shared_code.finmail.ingest import process_email
from shared_code.finmail.models import EmailPayload, Transaction


def _get_response(
    transaction: Transaction | None, payload: EmailPayload
) -> func.HttpResponse:
    if transaction:
        return func.HttpResponse(
            json.dumps({
                "ok": True,
                "subject": payload.subject,
                "processed": transaction.model_dump(mode="json"),
            }),
            mimetype="application/json",
            status_code=200,
        )
    return func.HttpResponse(
        json.dumps({"ok": False, "subject": payload.subject, "processed": None}),
        mimetype="application/json",
        status_code=200,
    )


def main(req: func.HttpRequest) -> func.HttpResponse:  # noqa: D103
    try:
        data = req.get_json()
    except Exception:
        return func.HttpResponse("Bad JSON", status_code=400)

    try:
        payload = EmailPayload(**data)
    except Exception as e:
        return func.HttpResponse(f"Validation error: {e}", status_code=422)

    processed = process_email(
        payload=payload, google_sheets_client=google_sheets_client
    )

    return _get_response(transaction=processed, payload=payload)
