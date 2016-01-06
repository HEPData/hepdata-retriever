import os
import unittest
from hepdata_retriever.retriever import Retriever

__author__ = 'eamonnmaguire'


class RetrieverTest(unittest.TestCase):

    def setUp(self):
        self.base_dir = os.path.dirname(os.path.realpath(__file__))

        __data_dir = os.path.join(self.base_dir, 'data')
        if not os.path.exists(__data_dir):
            os.mkdir(__data_dir)

        self.retriever = Retriever(__data_dir)

    def test_download(self):
        records = ['ins1404159', 'ins1396140']

        for record in records:
            self.retriever.get_record(record)
            self.assertTrue(
                os.path.exists(os.path.join(self.base_dir, 'data', record)))

    def test_get_all_current_ids(self):
        inspire_ids = self.retriever.get_all_ids_in_current_system()
        print 'We have {0} records to retrieve'.format(len(inspire_ids))
        self.assertTrue(len(inspire_ids) > 0)


if __name__ == '__main__':
    unittest.main()
