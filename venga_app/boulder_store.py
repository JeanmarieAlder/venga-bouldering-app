import os, json

from flask import current_app


def _get_file_path():
    os.makedirs(current_app.instance_path, exist_ok=True)
    return os.path.join(current_app.instance_path, "boulders.json")


def get_all():
    path = _get_file_path()

    if not os.path.exists(path):
        return []

    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def save_all(boulders):
    path = _get_file_path()
    temp_path = path + ".tmp"

    with open(temp_path, "w", encoding="utf-8") as file:
        json.dump(boulders, file, indent=4, ensure_ascii=False)

    # Replace the previous file only after writing succeeds.
    os.replace(temp_path, path)


def get_by_id(boulder_id):
    return next(
        (boulder for boulder in get_all()
         if boulder["id"] == boulder_id),
        None,
    )
