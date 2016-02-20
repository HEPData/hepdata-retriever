#!/usr/bin/python2.7
from hepdata_retriever.retriever import Retriever
import os
import errno

data_dir  = '/hepdata/data/'
temp_dir = '/hepdata/tmp/'

def makedirs(dirs):
    try:
        os.makedirs(dirs)
    except OSError as err:
        if err.errno == errno.EEXIST:
            return
        else:
            raise err

makedirs(temp_dir)
retriever = Retriever(temp_dir)
inspire_ids = retriever.get_all_ids_in_current_system()

for index, inspire_id in enumerate(inspire_ids):
    path = data_dir + '/' + inspire_id[-2:] + '/' + inspire_id
    if os.path.exists(path):
        continue

    makedirs(path)
    try:
        retriever.get_record(inspire_id)
    except KeyboardInterrupt:
        print('Interrupted.')
        break
    except:
        print('Ignoring %s.' % inspire_id)
