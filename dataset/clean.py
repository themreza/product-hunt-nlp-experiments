import os
import glob
import json
import logging
import re

from langdetect import detect_langs, lang_detect_exception
from language_detector import detect_language


class Clean:
    link_regex = r'^(http:\/\/www\.|https:\/\/www\.|http:\/\/|https:\/\/)?[a-z0-9]+([\-\.]{1}[a-z0-9]+)*\.[a-z]{2,5}(:[0-9]{1,5})?(\/.*)?$'

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

    def non_english_posts(self):
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

    def delete_invalid_post_files(self):
        post_file_paths = self.get_post_file_paths()
        for post_file_path in post_file_paths:
            with open(post_file_path, "r") as post_file:
                try:
                    json.load(post_file)
                except json.decoder.JSONDecodeError:
                    print("Deleting invalid JSON file %s" % post_file_path)
                    os.remove(post_file_path)

    def homogeneous_posts(self):
        post_file_paths = self.get_post_file_paths()
        for post_file_path in post_file_paths:
            with open(post_file_path, "r") as post_file:
                post = json.load(post_file)
                post_content = []
                if post['name']:
                    post_content.append(post['name'])
                if post['description']:
                    post_content.append(post['description'])
                if post['tagline']:
                    post_content.append(post['tagline'])
                if len(list(set(post_content))) <= 1:
                    # A valid post must have at least 2 out of 3 unique and valid fields
                    self.append_to_file('homogeneous_posts.json', {
                        'id': post['id'],
                        'name': post['name'],
                        'description': post['description'],
                        'tagline': post['tagline']
                    })
                    # Remove the post from the dataset
                    self.delete_post(post['id'])

    @staticmethod
    def get(dictionary, key, default=None):
        if key not in dictionary or not dictionary[key]:
            return default
        return dictionary[key]

    @staticmethod
    def tuple_in_string(tuple, string):
        return any(s in string for s in tuple)

    @staticmethod
    def remove_unicode_characters(string):
        return string.encode('ascii', 'ignore').decode()

    def remove_links(self, string):
        return re.sub(self.link_regex, '', string)

    def sanitize_field(self, dictionary, key):
        if self.get(dictionary, key):
            sanitized_tokens = []
            # Tokenize strings to process each phrase
            for token in dictionary[key].split():
                token = self.remove_unicode_characters(token)
                token = self.remove_links(token)
                sanitized_tokens.append(token)
            # Put the array of tokens back together
            dictionary[key] = ' '.join(sanitized_tokens)
            # Remove duplicate whitespaces and trim the ends
            dictionary[key] = re.sub(' +', ' ', dictionary[key]).strip()

    @staticmethod
    def save_post(post_id, data):
        dataset_directory_path = os.path.dirname(__file__)
        post_file_path = os.path.join(dataset_directory_path, 'posts/%s.json' % post_id)
        if os.path.exists(post_file_path):
            with open(post_file_path, 'w') as post_file:
                json.dump(data, post_file)

    def sanitize_posts(self):
        post_file_paths = self.get_post_file_paths()
        for post_file_path in post_file_paths:
            with open(post_file_path, "r") as post_file:
                post = json.load(post_file)
                self.sanitize_field(post, 'name')
                self.sanitize_field(post, 'description')
                self.sanitize_field(post, 'tagline')
                self.save_post(post['id'], post)


clean = Clean()

clean.delete_invalid_post_files()

# Takes a while to finish
# clean.non_english_posts()

clean.sanitize_posts()

# We run this last to take into account posts that had fields cleared during the sanitation
clean.homogeneous_posts()
