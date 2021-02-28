import requests


class Api:
    base_url = "https://api.producthunt.com"
    developer_token = ""

    def __init__(self, developer_token):
        self.developer_token = developer_token

    def request(self, query):
        response = requests.post(
            self.base_url + "/v2/api/graphql",
            json={"query": query},
            headers={"Authorization": "Bearer %s" % self.developer_token}
        )
        return response.json()
