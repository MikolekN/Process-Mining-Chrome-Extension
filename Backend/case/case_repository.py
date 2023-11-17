from pymongo import MongoClient


class CaseRepository:
    def __init__(self):
        # Connect to the MongoDB server
        client = MongoClient('localhost', 27017)

        # Access the database and collection
        db = client['chrome_test_v3']
        self.cases_collection = db['cases']

    def get_cases(self):
        cursor = self.cases_collection.find()
        return [case for case in cursor]

    def get_case_by_id(self, _id):
        case = self.cases_collection.find_one({'_id': _id})
        return case
