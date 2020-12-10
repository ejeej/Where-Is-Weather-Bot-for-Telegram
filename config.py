from enum import Enum


token = '1403912244:AAF3fDEByKRLwS9_rCvyS2RUR8gDf31fdMg'
db_file = 'db.vdb'
df_file = 'weather_data.csv'


class States(Enum):
    S_START = 0
    S_MONTH = 1
    S_DAY = 2
    S_TEMP = 3
    S_PREC_DAYS = 4
