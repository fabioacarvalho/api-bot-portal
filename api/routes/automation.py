from flask import Blueprint, jsonify, request
from flasgger import swag_from
from services.automation_service import AutomationService
from schemas.response_schema import automation_success_response

api = Blueprint("automation", __name__)
service = AutomationService()

@api.route("/start", methods=["POST"])
@swag_from(automation_success_response)
def start_automation():
    request_data = request.get_json()

    if not request_data or 'input_value' not in request_data:
        return jsonify({"error": "Missing 'input_value' in request body, please send NIS, Name or CPF"}), 400

    result = service.run(request_data['input_value'])
    return jsonify(result), 200