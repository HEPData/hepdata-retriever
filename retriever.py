#!/usr/bin/python2.7
from hepdata_retriever.retriever import Retriever
import os
import errno
from progressbar import ProgressBar, Percentage, Bar, Widget

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

class Label(Widget):
    """Displays an updatable label."""
    def __init__(self, min_length=0, starting_text=''):
        self.min_length = min_length
        self.change_text(starting_text)

    def change_text(self, text):
        self.text = text.ljust(self.min_length)

    def update(self, pbar):
        return ' ' + self.text + ' '

class AlwaysUpdatingProgressBar(ProgressBar):
    def _need_update(self):
        return True

makedirs(temp_dir)
retriever = Retriever(temp_dir)
inspire_ids = retriever.get_all_ids_in_current_system()

submission_label = Label(min_length=10)
pbar = AlwaysUpdatingProgressBar(maxval=len(inspire_ids),
                   widgets=[
                       Percentage(),
                       submission_label,
                       Bar(marker='#', left='[', right=']')
                   ]).start()

for index, inspire_id in enumerate(inspire_ids):
    submission_label.change_text(inspire_id)
    pbar.update(index)

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

pbar.finish()
