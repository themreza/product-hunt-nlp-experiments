from helpers.config import Config
from helpers.api import Api

config = Config().load()
developer_token = config.get('API', 'developer_token')

api = Api(developer_token)

posts = api.request("""
query {
  posts(order: NEWEST) {
    totalCount,
    edges {
      node {
        id
        name,
        description,
        tagline,
        topics {
          edges {
            node {
              id,
              name
            }
          }
        }
      },
      cursor
    }
  }
}
""")

print(posts)