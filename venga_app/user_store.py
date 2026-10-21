import json
import os
from uuid import uuid4

from flask import current_app

from venga_app.models import User


def _get_file_path():
    os.makedirs(current_app.instance_path, exist_ok=True)
    return os.path.join(current_app.instance_path, "users.json")

def get_all():
    path = _get_file_path()

    if not os.path.exists(path):
        return []

    with open(path, "r", encoding="utf-8") as file:
        records = json.load(file)

    return [User(**record) for record in records]


def save_all(users):
    path = _get_file_path()
    temp_path = path + ".tmp"

    records = [
        {
            "id": user.id,
            "username": user.username,
            "display_name": user.display_name,
            "role": user.role,
            "password_hash": user.password_hash,
        }
        for user in users
    ]

    with open(temp_path, "w", encoding="utf-8") as file:
        json.dump(records, file, indent=4)

    os.replace(temp_path, path)


def get_by_id(user_id):
    return next(
        (user for user in get_all() if user.id == user_id),
        None,
    )


def get_by_username(username):
    username = username.strip().casefold()

    return next(
        (
            user for user in get_all()
            if user.username.casefold() == username
        ),
        None,
    )


def create_user(username, display_name, password):
    user = User(
        id=str(uuid4()),
        username=username.strip(),
        display_name=display_name.strip(),
        role="climber",
        password_hash="",
    )
    user.set_password(password)

    users = get_all()
    users.append(user)
    save_all(users)

    return user


def update_user_role(user_id, new_role):
    allowed_roles = {"climber", "setter"}

    if new_role not in allowed_roles:
        return False

    users = get_all()
    user = next(
        (user for user in users if user.id == user_id),
        None,
    )

    if user is None:
        return False

    user.role = new_role
    save_all(users)
    return True