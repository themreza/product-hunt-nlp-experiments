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
import helpers.api as Api


class Populate():
    latest_post_id = None
    latest_post_cursor = None

    def __init__(self):
        self.load_stats()

    @staticmethod
    def get_posts_directory_path():
        dataset_directory_path = os.path.dirname(__file__)
        posts_directory_path = os.path.join(dataset_directory_path, 'posts')
        return posts_directory_path

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


populate = Populate()
