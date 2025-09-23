from data_processing import cParserCV
from data_processing import save_bronze_data, load_bronze_data

from main_class.file_Applicant import Applicant
from main_class.file_Scholarship import Scholarship
from main_class.file_MasterScholarship import MasterScholarship
from main_class.file_PhDScholarship import PhDScholarship
from main_class.file_ExchangeProgram import ExchangeProgram

import os

cur_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(cur_dir)

# cParserCV usage example:
# nguyen_CV = cParserCV("D:\Git\ScholarshipRouting\CV.pdf")
# print(nguyen_CV.parse())

# save_bronze_data usage example:
# url = "https://docs.google.com/spreadsheets/d/1DcJkKtmH4zrepZ_ofmIrz0yfJLEt2rNqGFRPJN529p0/gviz/tq?tqx=out:csv&sheet=Master%20Scholarship"
# save_bronze_data(url, path=os.path.join(parent_dir, "data/1_bronze"))

# load_bronze_data usage example:
# df = load_bronze_data(path=os.path.join(parent_dir, "data/1_bronze"), type="parquet")
# print(df.info())
