#!/usr/bin/python2.7
from __future__ import print_function
from hepdata_retriever.retriever import Retriever
import os
import shutil
import errno
import sys
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

    if inspire_id == '':
        print('Warning: empty inspire_id', file=sys.stderr)
        continue

    # I don't know what's wrong with these submission, they hang every time
    if inspire_id in ['ins825040', 'ins1289225']:
        continue

    dest_path = data_dir + '/' + inspire_id[-2:] + '/'
    makedirs(dest_path)
    if os.path.exists(dest_path + inspire_id):
        continue

    try:
        retriever.get_record(inspire_id)
        shutil.move(temp_dir + '/' + inspire_id, dest_path)
        os.remove(temp_dir + '/' + inspire_id + '.zip')
    except KeyboardInterrupt:
        print('\nInterrupted.', file=sys.stderr)
        raise SystemExit(2)
    except:
        print('Ignoring %s.' % inspire_id, file=sys.stderr)

pbar.finish()
