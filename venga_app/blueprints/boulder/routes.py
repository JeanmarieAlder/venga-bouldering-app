from datetime import datetime, timezone
from uuid import uuid4

from flask import jsonify, request

from venga_app.boulder_store import (
    get_all,
    get_by_id,
    save_all,
)

from venga_app.permissions import setter_required

from . import boulder_bp


@boulder_bp.route("/test", methods=["GET"])
def index():
    return jsonify({
        "status": "ok",
        "message": "Venga API is running.",
    })


# GET /api/boulders
@boulder_bp.route("/", methods=["GET"])
def list_boulders():
    boulders = get_all()

    include_archived = (
        request.args.get("include_archived", "false").lower()
        == "true"
    )

    if not include_archived:
        boulders = [
            boulder for boulder in boulders
            if boulder.get("active", True)
        ]

    return jsonify(boulders), 200


# GET /api/boulders/<id>
@boulder_bp.route("/<boulder_id>", methods=["GET"])
def get_boulder(boulder_id):
    boulder = get_by_id(boulder_id)

    if boulder is None:
        return jsonify({"error": "Boulder not found"}), 404

    return jsonify(boulder), 200


# POST /api/boulders
@boulder_bp.route("/", methods=["POST"])
@setter_required
def create_boulder():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "A JSON object is required"}), 400

    required_fields = ["name", "grade", "color", "setter"]
    missing = [
        field for field in required_fields
        if not isinstance(data.get(field), str)
        or not data[field].strip()
    ]

    if missing:
        return jsonify({
            "error": "Missing or invalid required fields",
            "fields": missing,
        }), 400

    boulders = get_all()

    boulder = {
    "id": str(uuid4()),
    "name": data["name"].strip(),
    "grade": data["grade"].strip(),
    "color": data["color"].strip(),
    "setter": data["setter"].strip(),
    "active": True,
    "archived_at": None,
    "created_at": datetime.now(timezone.utc).isoformat(),
    }

    boulders.append(boulder)
    save_all(boulders)

    return jsonify(boulder), 201


# PATCH /api/boulders/<id>
@boulder_bp.route("/<boulder_id>", methods=["PATCH"])
@setter_required
def update_boulder(boulder_id):
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "A JSON object is required"}), 400

    boulders = get_all()

    for boulder in boulders:
        if boulder["id"] == boulder_id:
            allowed_fields = ["name", "grade", "color", "setter"]

            if not data:
                return jsonify({"error": "No fields provided"}), 400

            invalid = set(data.keys()) - set(allowed_fields)

            if invalid:
                return jsonify({
                    "error": "Fields cannot be updated",
                    "fields": sorted(invalid),
                }), 400

            for field, value in data.items():
                if not isinstance(value, str) or not value.strip():
                    return jsonify({
                        "error": f"{field} must be a non-empty string"
                    }), 400

                boulder[field] = value.strip()

            save_all(boulders)
            return jsonify(boulder), 200

    return jsonify({"error": "Boulder not found"}), 404


# DELETE /api/boulders/<id>
@boulder_bp.route("/<boulder_id>", methods=["DELETE"])
@setter_required
def delete_boulder(boulder_id):
    boulders = get_all()

    for boulder in boulders:
        if boulder["id"] == boulder_id:
            if not boulder.get("active", True):
                return jsonify({
                    "error": "Boulder is already archived"
                }), 409

            boulder["active"] = False
            boulder["archived_at"] = (
                datetime.now(timezone.utc).isoformat()
            )

            save_all(boulders)
            return jsonify(boulder), 200

    return jsonify({"error": "Boulder not found"}), 404


# POST restore boulder (set back active to true)
@boulder_bp.route(
    "/<boulder_id>/restore",
    methods=["POST"],
)
@setter_required
def restore_boulder(boulder_id):
    boulders = get_all()

    for boulder in boulders:
        if boulder["id"] == boulder_id:
            if boulder.get("active", True):
                return jsonify({
                    "error": "Boulder is already active"
                }), 409

            boulder["active"] = True
            boulder["archived_at"] = None

            save_all(boulders)
            return jsonify(boulder), 200