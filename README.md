#HEPData Retriever

A tool to get HEPData records.

### Usage

```python

from hepdata_retriever.retriever import Retriever
__data_dir = os.path.abspath(os.path.dirname(__file__)) + '/data'
retriever = Retriever(__data_dir)
retriever.get_record('ins1404159')

```

### Getting all HEPData records and downloading them

**Please be considerate of the server!**


```python

from hepdata_retriever.retriever import Retriever
__data_dir = os.path.abspath(os.path.dirname(__file__)) + '/data'

retriever = Retriever(__data_dir)
inspire_ids = retriever.get_all_ids_in_current_system()

for index, inspire_id in enumerate(inspire_ids):
    retriever.get_record(inspire_id)

```
