import glob
import os
import json

from collections import defaultdict
import pandas as pd


class Dataframes:
    @staticmethod
    def get_post_file_paths():
        dataset_directory_path = os.path.dirname(__file__)
        post_file_pattern = os.path.join(dataset_directory_path, 'posts/*.json')
        post_file_paths = glob.glob(post_file_pattern)
        return post_file_paths

    @staticmethod
    def has_all_fields_filled(data, fields):
        return all((field in data and data[field]) for field in fields)

    def filter_dictionary_keys(self, data, keys):
        return {key: self.clean_data(data[key]) for key in keys}

    @staticmethod
    def save_as_dataframe_csv(dataframe, fields, index=False):
        dataset_directory_path = os.path.dirname(__file__)
        dataframe_path = os.path.join(dataset_directory_path, 'dataframes/%s.csv' % '_'.join(fields))
        dataframe.to_csv(dataframe_path, index=index)

    @staticmethod
    def clean_data(data):
        if type(data) is not list:
            return data
        cleaned_data = []
        for datum in data:
            cleaned_data.append(datum['name'])
        return cleaned_data

    def create_from_fields(self, fields):
        # Creates a dataset containing a pairing of the specified fields
        # Only posts that have values for all the fields are used
        # The dataset is saved as a CSV file with a filename reflecting the fields used
        post_file_paths = self.get_post_file_paths()
        dataframes = []
        for post_file_path in post_file_paths:
            with open(post_file_path, "r") as post_file:
                post = json.load(post_file)
                if self.has_all_fields_filled(post, fields):
                    filtered_dictionary = self.filter_dictionary_keys(post, fields)
                    dataframes.append(pd.DataFrame.from_dict(filtered_dictionary))
        dataframe = pd.concat(dataframes)
        self.save_as_dataframe_csv(dataframe, fields)
        # TODO: Remove - Test only
        # print(dataframe)
        # self.save_as_dataframe_csv(pd.DataFrame(dataframe.drop('description', axis=1).value_counts()), ['test'], index=True)


dataframes = Dataframes()

# Model 1 and 2
dataframes.create_from_fields(['description', 'topics'])

# TODO: Bugfix
# dataframes.create_from_fields(['name', 'tagline'])
