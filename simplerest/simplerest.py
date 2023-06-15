from falcon_cors import CORS
import falcon
import requests
import io
import json


class Elements():
    def on_get(self, req, resp):
        try:
            resp.media = jsontoshow
            return
        except KeyError:
            resp.status = falcon.HTTP_NOT_FOUND


with open('/datafiles/data.json') as f:
    jsontoshow = json.load(f)

elements = Elements()
cors = CORS(allow_all_origins=True, allow_methods_list=['GET'])
api = falcon.API(middleware=[cors.middleware])

api.add_route('/elements', elements)
