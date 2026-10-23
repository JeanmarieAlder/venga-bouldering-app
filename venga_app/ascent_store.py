import json
import os
from datetime import datetime, timezone
from uuid import uuid4

from flask import current_app


def _get_file_path():
    return os.path.join(current_app.instance_path, "ascents.json")


def get_all():
    path = _get_file_path()

    if not os.path.exists(path):
        return []

    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def save_all(ascents):
    path = _get_file_path()
    os.makedirs(os.path.dirname(path), exist_ok=True)

    temp_path = f"{path}.tmp"

    with open(temp_path, "w", encoding="utf-8") as file:
        json.dump(ascents, file, indent=2)

    os.replace(temp_path, path)


def get_for_user(user_id):
    return [
        ascent
        for ascent in get_all()
        if ascent.get("user_id") == str(user_id)
    ]


def get_for_user_and_boulder(user_id, boulder_id):
    return next(
        (
            ascent
            for ascent in get_all()
            if ascent.get("user_id") == str(user_id)
            and ascent.get("boulder_id") == str(boulder_id)
        ),
        None,
    )


def upsert_ascent(user_id, boulder_id, tries, personal_grade):
    """Create an ascent or update the climber's existing record."""
    ascents = get_all()
    user_id = str(user_id)
    boulder_id = str(boulder_id)
    now = datetime.now(timezone.utc).isoformat()

    existing = next(
        (
            ascent
            for ascent in ascents
            if ascent.get("user_id") == user_id
            and ascent.get("boulder_id") == boulder_id
        ),
        None,
    )

    if existing:
        existing["tries"] = tries
        existing["personal_grade"] = personal_grade
        existing["updated_at"] = now
    else:
        ascents.append({
            "id": str(uuid4()),
            "user_id": user_id,
            "boulder_id": boulder_id,
            "tries": tries,
            "personal_grade": personal_grade,
            "completed_at": now,
            "updated_at": now,
        })

    save_all(ascents)