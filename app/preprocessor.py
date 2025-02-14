'''
Author: Yaleesa Borgman
Date: 8-8-2019
predicter.py - handles predictions from imported models
'''

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import nltk
from nltk import word_tokenize
from nltk.corpus import stopwords

nltk.download('stopwords')
nltk.download('punkt')
stop_words = set(stopwords.words('english'))

class DataPreProcessor:
    def __init__(self, data):
        self.data = data
        self.dataframe = self.to_dataframe(self.data)
        self.transformed_df = self.transform_dataframe(self.dataframe)

    def to_dataframe(self, documents):
        '''
        make a dataframe from the list of dicts
        '''
        dataframe = pd.io.json.json_normalize(documents, sep='.')
        return dataframe

    def transform_dataframe(self, dataframe):
        '''
        transform the data from a multidimensional array to a 2d array, with ['label', 'text'] as columns
        '''

        dataframe = dataframe.astype(str)

        self.column_names = dataframe.columns.values
        return pd.melt(dataframe, value_vars=self.column_names, var_name='label', value_name='text',)

    def remove_categories(self, dataframe, list_of_cats):
        dataframe = dataframe.drop(list_of_cats ,axis=1)
        return dataframe


class DataCleaner:
    def remove_values(self, dataframe, value):
        '''
        The data has some 'unknown' values, as where the scrapetool didnt find any data for that category
        3997 rows contained an unknown value. introduction(2898), contract_type(1066), location(33)
        '''
        print(
        f'''---> removing missing values from the dataset
        ''')
        cleaned_df = dataframe[~dataframe.text.str.contains(value)]
        if cleaned_df[cleaned_df.text=='Unknown'].shape[0] == 0: print(f"   ---> all '{value}' removed")
        print(f'   ---> Removed {dataframe.shape[0] - cleaned_df.shape[0]} {value}\n')
        return cleaned_df

    def remove_not_null(self, dataframe):
        dataframe = dataframe[dataframe.notnull()]

    def unique(self, dataframe):
        dropped_df = dataframe.drop_duplicates()
        return dropped_df

    def lowercase(self, dataframe):
        dataframe['text'] = dataframe['text'].apply(lambda row:' '.join([w.lower() for w in word_tokenize(row)]) )
        return dataframe

    def remove_stopwords(self, dataframe):
        dataframe['text'] = dataframe['text'].apply(lambda row:' '.join([w for w in word_tokenize(row) if w not in stop_words]) )
        return dataframe

class xmlRemapper:
    def __init__(self):
        self.es = Elasticer()
    
        self.cleaner = DataCleaner()
        self.dataset_xml = 'sj-uk-vacancies-cleaned-4'
        self.exclude_xml = ['@language', 'DatePlaced', 'Id', 'companyLogo', 'country', 'topjob', 'HoursWeek', 'JobUrl', 'JobMinDaysPerWeek', 'JobParttime', 'JobCompanyBranch', 'JobCompanyProfile', 'JobRequirements.MinAge']
        self.include_xml = ['JobBranch', 'JobCategory', 'JobCompany', 'JobDescription','JobLocation.LocationRegion', 'JobProfession', 'Title','TitleDescription', 'functionTitle', 'postalCode', 'profession']
            
    def import_data(self):
        dataset = self.es.import_dataset(self.dataset_xml, self.include_xml)

        return dataset

    def remap(self, dataframe):
        rename_dict = {'Title': 'vacancy_title',
                        'functionTitle': 'vacancy_title',
                        'TitleDescription': 'introduction',
                        'JobCategory': 'contract_type',
                        'JobBranch': 'job_category',
                        'JobDescription': 'description',
                        'profession': 'job_category',
                        'JobLocation.LocationRegion': 'location',
                        'postalCode': 'location',
                        'JobCompany': 'company_name',
                        'JobProfession': 'job_category'}
        dataframe.rename(columns=rename_dict, inplace=True)
        return dataframe