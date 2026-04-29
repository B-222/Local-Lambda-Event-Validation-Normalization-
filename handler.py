"""
PL202 — Serverless Event Processing (Local Lambda Simulation)
Day 1 (45 min) — Individual Task
"""

from __future__ import annotations
from typing import Any, Dict, List, Optional
import re


ALLOWED_TYPES = {"USER_SIGNUP", "PAYMENT", "FILE_UPLOAD"}
ALLOWED_PLANS = {"free", "pro", "edu"}
ALLOWED_CURRENCIES = {"BHD", "USD", "EUR"}


def _err(*msgs: str) -> Dict[str, Any]:
    """Create a standard error response."""
    return {
        "status": "error",
        "message": "Event rejected",
        "data": None,
        "errors": list(msgs),
    }


def _ok(message: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """Create a standard ok response."""
    return {
        "status": "ok",
        "message": message,
        "data": data,
        "errors": [],
    }


def _is_email(value: str) -> bool:
    return bool(re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", value))


def handler(event: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Main Lambda-style handler."""
    # TODO 1: Validate event is a dict and has 'type' field
    if not isinstance(event, dict):
        return _err("Event must be a JSON object (dict), not a list or other type")

    if "type" not in event:
        return _err("Missing required field: type")

    # TODO 2: Ensure event['type'] is one of ALLOWED_TYPES
    event_type = event["type"]
    if event_type not in ALLOWED_TYPES:
        return _err(f"Unknown event type: '{event_type}'")

    # TODO 3 & 4: Route to the correct handler
    if event_type == "USER_SIGNUP":
        return handle_user_signup(event)
    elif event_type == "PAYMENT":
        return handle_payment(event)
    elif event_type == "FILE_UPLOAD":
        return handle_file_upload(event)


def handle_user_signup(event: Dict[str, Any]) -> Dict[str, Any]:
    """Process USER_SIGNUP events."""
    errors = []

    # TODO 5: Validate required fields and types
    if "user_id" not in event:
        errors.append("Missing required field: user_id")
    elif not isinstance(event["user_id"], int):
        errors.append("user_id must be an int")

    if "email" not in event:
        errors.append("Missing required field: email")
    elif not isinstance(event["email"], str):
        errors.append("email must be a string")

    if "plan" not in event:
        errors.append("Missing required field: plan")
    elif not isinstance(event["plan"], str):
        errors.append("plan must be a string")

    if errors:
        return _err(*errors)

    # TODO 6: Validate email format
    email = event["email"].lower()
    if not _is_email(email):
        errors.append(f"Invalid email format: '{event['email']}'")

    # TODO 7: Validate plan is allowed
    plan = event["plan"].lower()
    if plan not in ALLOWED_PLANS:
        errors.append(f"Invalid plan: '{event['plan']}'. Must be one of: free, pro, edu")

    if errors:
        return _err(*errors)

    # TODO 8: Build normalized output and return _ok
    data = {
        "user_id": event["user_id"],
        "email": email,
        "plan": plan,
        "welcome_email_subject": f"Welcome to the {plan} plan!",
    }
    return _ok("Signup processed", data)


def handle_payment(event: Dict[str, Any]) -> Dict[str, Any]:
    """Process PAYMENT events."""
    errors = []

    # TODO 9: Validate required fields and types
    if "payment_id" not in event:
        errors.append("Missing required field: payment_id")
    elif not isinstance(event["payment_id"], str):
        errors.append("payment_id must be a string")

    if "user_id" not in event:
        errors.append("Missing required field: user_id")
    elif not isinstance(event["user_id"], int):
        errors.append("user_id must be an int")

    if "amount" not in event:
        errors.append("Missing required field: amount")
    elif not isinstance(event["amount"], (int, float)):
        errors.append("amount must be a number")

    if "currency" not in event:
        errors.append("Missing required field: currency")
    elif not isinstance(event["currency"], str):
        errors.append("currency must be a string")

    if errors:
        return _err(*errors)

    # TODO 10: Validate amount > 0
    amount = float(event["amount"])
    if amount <= 0:
        errors.append(f"amount must be greater than 0, got {event['amount']}")

    # TODO 11: Validate currency
    currency = event["currency"].upper()
    if currency not in ALLOWED_CURRENCIES:
        errors.append(f"Invalid currency: '{event['currency']}'. Must be one of: BHD, USD, EUR")

    if errors:
        return _err(*errors)

    # TODO 12: Compute fee and net_amount
    amount = round(amount, 3)
    fee = round(0.02 * amount, 3)
    net_amount = round(amount - fee, 3)

    data = {
        "payment_id": event["payment_id"],
        "user_id": event["user_id"],
        "amount": amount,
        "currency": currency,
        "fee": fee,
        "net_amount": net_amount,
    }
    return _ok("Payment processed", data)


def handle_file_upload(event: Dict[str, Any]) -> Dict[str, Any]:
    """Process FILE_UPLOAD events."""
    errors = []

    # TODO 13: Validate required fields and types
    if "file_name" not in event:
        errors.append("Missing required field: file_name")
    elif not isinstance(event["file_name"], str):
        errors.append("file_name must be a string")

    if "size_bytes" not in event:
        errors.append("Missing required field: size_bytes")
    elif not isinstance(event["size_bytes"], int):
        errors.append("size_bytes must be an int")
    elif event["size_bytes"] < 0:
        errors.append("size_bytes must be >= 0")

    if "bucket" not in event:
        errors.append("Missing required field: bucket")
    elif not isinstance(event["bucket"], str):
        errors.append("bucket must be a string")

    if "uploader" not in event:
        errors.append("Missing required field: uploader")
    elif not isinstance(event["uploader"], str):
        errors.append("uploader must be a string")

    if errors:
        return _err(*errors)

    # TODO 14: Validate uploader email
    uploader = event["uploader"].lower()
    if not _is_email(uploader):
        errors.append(f"Invalid uploader email: '{event['uploader']}'")

    if errors:
        return _err(*errors)

    # Normalize
    file_name = event["file_name"].strip()
    bucket = event["bucket"].lower()
    size_bytes = event["size_bytes"]

    # TODO 15: Compute storage class
    if size_bytes < 1_000_000:
        storage_class = "STANDARD"
    elif size_bytes < 50_000_000:
        storage_class = "STANDARD_IA"
    else:
        storage_class = "GLACIER"

    data = {
        "file_name": file_name,
        "size_bytes": size_bytes,
        "bucket": bucket,
        "uploader": uploader,
        "storage_class": storage_class,
    }
    return _ok("Upload processed", data)
