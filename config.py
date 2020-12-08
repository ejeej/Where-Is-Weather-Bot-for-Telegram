from enum import Enum


token = '1403912244:AAF3fDEByKRLwS9_rCvyS2RUR8gDf31fdMg'
db_file = 'db.vdb'
df_file = 'weather_data.csv'


class States(Enum):
    S_START = 0
    S_MONTH = 1
    S_DAY = 2
    S_MIN_TEMP = 3
    S_MAX_TEMP = 4
    S_MIN_PREC_DAYS = 5
    S_MAX_PREC_DAYS = 6
