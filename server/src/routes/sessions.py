from flask import Blueprint, jsonify, request, g

from src.middleware.auth import require_auth
from src.services.session_service import (
    get_upcoming_sessions,
    get_completed_sessions,
    get_session_by_id,
    cancel_session_by_id,
    get_latest_feedback,
    save_feedback,
)

sessions_bp = Blueprint("sessions", __name__)


@sessions_bp.route("/", methods=["GET"])
@require_auth
def list_sessions():
    """
    Retrieve upcoming sessions for the authenticated user.

    This endpoint requires authentication and returns a list of
    upcoming sessions associated with the currently logged-in user.

    Returns:
        Response (JSON):
            - 200: A list of session objects.
    """
    sessions = get_upcoming_sessions(g.user.id)
    return jsonify([dict(s) for s in sessions]), 200


@sessions_bp.route("/completed", methods=["GET"])
@require_auth
def list_completed_sessions():
    sessions = get_completed_sessions(g.user.id)
    return jsonify([dict(s) for s in sessions])


@sessions_bp.route("/<session_id>", methods=["GET"])
@require_auth
def get_session(session_id):
    session = get_session_by_id(session_id, g.user.id)
    if not session:
        return jsonify({"error": "Session not found"}), 404
    return jsonify(dict(session))


@sessions_bp.route("/<session_id>/cancel", methods=["POST"])
@require_auth
def cancel_session_route(session_id):
    cancelled = cancel_session_by_id(session_id, g.user.id)
    if not cancelled:
        return jsonify({"error": "Session not found or cannot be cancelled"}), 404
    return jsonify({"status": "cancelled"})


@sessions_bp.route("/<session_id>/feedback", methods=["GET"])
@require_auth
def get_feedback(session_id):
    """
    Retrieve the most recent feedback for a given session.

    This endpoint returns the latest stored feedback for the specified
    session. If no feedback exists, it returns a null feedback response.

    Args:
        session_id (str): The ID of the session.

    Returns:
        Response (JSON):
            - 200: {"feedback": feedback_object or None}
    """
    feedback = get_latest_feedback(session_id)

    if not feedback:
        return jsonify({"feedback": None}), 200

    return jsonify({"feedback": dict(feedback)}), 200


@sessions_bp.route("/<session_id>/feedback", methods=["POST"])
@require_auth
def create_feedback(session_id):
    """
    Create and persist feedback for a completed session.

    Args:
        session_id (str): The ID of the session being reviewed.

    Request JSON Body:
        from_user_id (str): ID of the user submitting feedback
        from_user_name (str): Name of the user submitting feedback
        to_user_id (str, optional): ID of the user receiving feedback
        rating (int): Overall rating (1-5)
        communication (int): Communication score (1-5)
        preparedness (int): Preparedness score (1-5)
        technical_skill (int): Technical skill score (1-5)
        strengths (str, optional): Noted strengths
        improvements (str, optional): Suggested improvements
        notes (str, optional): Additional notes

    Returns:
        Response (JSON):
            - 201: {"feedback": created_feedback_object}
            - 400: {"error": "Missing required fields"}
    """
    data = request.get_json() or {}
    required = ["from_user_id", "from_user_name", "rating", "communication", "preparedness", "technical_skill"]
    missing = [k for k in required if data.get(k) in (None, "")]
    if missing:
        return jsonify({"error": f"Missing required fields: {', '.join(missing)}"}), 400

    feedback = save_feedback(
        session_id=session_id,
        from_user_id=str(data["from_user_id"]),
        from_user_name=str(data["from_user_name"]),
        to_user_id=str(data.get("to_user_id", "")),
        rating=int(data["rating"]),
        communication=int(data["communication"]),
        preparedness=int(data["preparedness"]),
        technical_skill=int(data["technical_skill"]),
        strengths=(data.get("strengths") or "").strip(),
        improvements=(data.get("improvements") or "").strip(),
        notes=(data.get("notes") or "").strip(),
    )
    return jsonify({"feedback": dict(feedback)}), 201
