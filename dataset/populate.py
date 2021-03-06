"""
Populates the dataset by traversing the Product Hunt API

Currently we fetch the following fields only:

Posts:
  - id
  - name
  - description
  - tagline
  - topics

Topics:
  - id
  - name
"""

import os
import json
import time
import logging
import sys
import inspect

# TODO: Fix this - https://gist.github.com/JungeAlexander/6ce0a5213f3af56d7369
current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from helpers.config import Config
from helpers.api import Api, ApiError, ApiRateLimitError

logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S')


class Populate:
    config = None
    api = None
    latest_post_id = None
    latest_post_cursor = None

    def __init__(self):
        self.config = Config().load()
        self.api = Api(self.config.get('API', 'developer_token'))
        self.load_stats()

    def reload_token(self, api_token):
        self.api = Api(api_token)

    @staticmethod
    def open_stats_file(mode="read"):
        dataset_directory_path = os.path.dirname(__file__)
        stats_file_path = os.path.join(dataset_directory_path, 'stats.json')
        stats_file = open(stats_file_path, "w+" if mode == "write" or not os.path.isfile(stats_file_path) else "r")
        return stats_file

    def load_stats(self):
        try:
            with self.open_stats_file() as stats_json:
                data = json.load(stats_json)
                if 'latest_post_id' in data:
                    self.latest_post_id = data['latest_post_id']
                    self.latest_post_cursor = data['latest_post_cursor']
        except json.JSONDecodeError:
            return

    def save_stats(self):
        with self.open_stats_file("write") as stats_json:
            json.dump(
                {
                    "latest_post_id": self.latest_post_id,
                    "latest_post_cursor": self.latest_post_cursor
                },
                stats_json
            )

    @staticmethod
    def format_post_data(post):
        topic_data = []
        for topic in post['topics']['edges']:
            topic_data.append({
                "id": topic['node']['id'],
                "name": topic['node']['name'],
            })
        post_data = {
            "id": post['id'],
            "name": post['name'],
            "description": post['description'],
            "tagline": post['tagline'],
            "topics": topic_data
        }
        return post_data

    def save_record(self, post):
        if 'id' not in post:
            return
        post_data = self.format_post_data(post)
        dataset_directory_path = os.path.dirname(__file__)
        post_file_path = os.path.join(dataset_directory_path, "posts/%s.json" % post['id'])
        if not os.path.isfile(post_file_path):
            with open(post_file_path, "w+") as pf:
                json.dump(post_data, pf)
        for topic_data in post_data['topics']:
            topic_file_path = os.path.join(dataset_directory_path, "topics/%s.json" % topic_data['id'])
            if not os.path.isfile(topic_file_path):
                with open(topic_file_path, "w+") as tf:
                    json.dump(topic_data, tf)

    def fetch_posts(self):
        cursor = ', before: "%s"' % self.latest_post_cursor if self.latest_post_cursor else ""
        query = """
        query {
          posts(order: NEWEST, last: 20%s) {
            pageInfo {
              hasPreviousPage
            },
            edges {
              node {
                id,
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
        """ % cursor
        posts = self.api.request(query)
        return posts

    def next_page(self):
        posts = self.fetch_posts()
        captured_cursor = False
        if 'data' not in posts:
            raise ApiError("API response is missing the data field")
        if 'errors' in posts:
            raise ApiRateLimitError(posts['errors'])
        # posts are ordered newest to orders, so we need the first cursor
        for post in posts['data']['posts']['edges']:
            if not captured_cursor:
                self.latest_post_cursor = post['cursor']
                self.latest_post_id = post['node']['id']
                captured_cursor = True
            self.save_record(post['node'])
        self.save_stats()
        return posts['data']['posts']['pageInfo']['hasPreviousPage']


populate = Populate()

while True:
    try:
        while populate.next_page():
            logging.info("Page processed! Latest post ID: %s" % populate.latest_post_id)
            time.sleep(3)
        break
    except ApiRateLimitError as e:
        logging.error("API rate limit exceeded - trying again in 1 minute - %s" % e)
        time.sleep(60)
