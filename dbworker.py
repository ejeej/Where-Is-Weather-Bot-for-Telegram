import os

from vedis import Vedis

import config


def reset_user(uid):
    with Vedis(config.db_file) as db:
        db[uid] = str({})
    for mf in [
        '%s-df_filtered_week.csv' % str(uid),
        '%s-df_filtered_tmpr.csv' % str(uid),
        '%s-df_filtered_final.csv' % str(uid),
        '%s-map.png' % str(uid)
    ]:
        if os.path.exists(mf):
            os.remove(mf)

def get_param(uid, param):
    with Vedis(config.db_file) as db:
        usr_dict = eval(db[uid].decode())
        if not usr_dict:
            db[uid] = str({})
            usr_dict = {}
        value = usr_dict.get(param)
        try:
            value = int(value)
        except ValueError:
            pass
        except TypeError:
            pass
        return value

def set_param(uid, param, value):
    with Vedis(config.db_file) as db:
        usr_dict = eval(db[uid].decode())
        usr_dict.update({param: str(value)})
        db[uid] = str(usr_dict)

def get_user_info(uid):
    with Vedis(config.db_file) as db:
        return db[uid].decode()
