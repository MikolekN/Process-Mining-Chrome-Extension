from bson import ObjectId

from case.case_repository import CaseRepository


class CaseService:
    def __init__(self):
        self.repository = CaseRepository()

    def get_cases(self):
        cases = self.repository.get_cases()
        return [{
            'caseEvents': [str(_id) for _id in case['caseEvents']],
            '_id': str(case['_id'])
        } for case in cases]

    def get_case_by_id(self, _id):
        case = self.repository.get_case_by_id(ObjectId(_id))
        return {
            'caseEvents': [str(_id) for _id in case['caseEvents']],
            '_id': str(case['_id'])
        }
