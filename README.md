#HEPData Retriever

A tool to get HEPData records.

### Usage

```python

__data_dir = 'Users/user/data/'
retriever = Retriever(__data_dir)
retriever.get_record('ins1404159')

```

### Getting all HEPData records and downloading them

**Please be considerate of the server!**


```python
__data_dir = 'Users/user/data/'

inspire_ids = self.retriever.get_all_ids_in_current_system()

retriever = Retriever(__data_dir)

for index, inspire_id in enumerate(inspire_ids):
    retriever.get_record(inspire_id)

```