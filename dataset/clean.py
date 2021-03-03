import os
import glob
import json
import logging

from langdetect import detect_langs, lang_detect_exception
from language_detector import detect_language


class Clean:
    @staticmethod
    def get_post_file_paths():
        dataset_directory_path = os.path.dirname(__file__)
        post_file_pattern = os.path.join(dataset_directory_path, 'posts/*.json')
        post_file_paths = glob.glob(post_file_pattern)
        return post_file_paths

    @staticmethod
    def identify_languages(text):
        # We use two different language detection libraries for maximum efficiency
        # Due to the low input word count, false-positives are expected
        languages = []
        if not text:
            return languages
        try:
            languages += [detect_language(text)]
            languages += list(map(lambda l: l.lang, detect_langs(text)))
        except lang_detect_exception.LangDetectException:
            # If we can't detect a language, then the post isn't fit for training
            pass
        return languages

    @staticmethod
    def append_to_file(file_name, data):
        dataset_directory_path = os.path.dirname(__file__)
        file_path = os.path.join(dataset_directory_path, file_name)
        with open(file_path, "a+") as json_file:
            json.dump(data, json_file)
            json_file.write('\n')

    @staticmethod
    def delete_post(post_id):
        dataset_directory_path = os.path.dirname(__file__)
        file_path = os.path.join(dataset_directory_path, 'posts/%s.json' % post_id)
        if os.path.exists(file_path):
            os.remove(file_path)
            logging.info('Deleted posts/%s.json' % post_id)

    def find_non_english_posts(self):
        post_file_paths = self.get_post_file_paths()
        for post_file_path in post_file_paths:
            with open(post_file_path, "r") as post_file:
                post = json.load(post_file)
                languages = []
                languages += self.identify_languages(post['description'])
                languages += self.identify_languages(post['tagline'])
                languages = list(set(languages))
                if 'en' not in languages and 'English' not in languages:
                    # Log the non-English posts before deleting
                    self.append_to_file('non_english_posts.json', {
                        'id': post['id'],
                        'languages': languages,
                        'description': post['description'],
                        'tagline': post['tagline']
                    })
                    # Remove the post from the dataset
                    self.delete_post(post['id'])


clean = Clean()
clean.find_non_english_posts()
