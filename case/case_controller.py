from case.case_service import CaseService
from flask import jsonify, Blueprint

case_blueprint = Blueprint('case_blueprint', __name__)
case_service = CaseService()


@case_blueprint.route('', methods=['GET'])
def get_cases():
    cases = case_service.get_cases()
    return cases


@case_blueprint.route('/case/<string:_id>', methods=['GET'])
def get_case_by_id(_id):
    case = case_service.get_case_by_id(_id)
    return case
