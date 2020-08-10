# Python Airtable

[![PyPI version](https://img.shields.io/pypi/v/python-airtable.svg)](https://pypi.python.org/pypi/python-airtable/)
[![PyPI license](https://img.shields.io/pypi/l/python-airtable.svg)](https://pypi.python.org/pypi/python-airtable/)
[![PyPI pyversions](https://img.shields.io/pypi/pyversions/python-airtable.svg)](https://pypi.python.org/pypi/python-airtable/)
[![PyPI status](https://img.shields.io/pypi/status/python-airtable.svg)](https://pypi.python.org/pypi/python-airtable/)
[![PyPI download total](https://img.shields.io/pypi/dm/python-airtable.svg)](https://pypi.python.org/pypi/python-airtable/)
[![Documentation Status](https://readthedocs.org/projects/airtable-python-wrapper/badge/?version=latest)](http://airtable-python-wrapper.readthedocs.io/en/latest/?badge=latest)

This is a Python module for accessing Airtable largely based on the original [airtable-python-wrapper](https://github.com/gtalarico/airtable-python-wrapper/) by [Gui Talarico](https://github.com/gtalarico) with some modifications.

## Installing

```
pip install python-airtable
```

## Documentation

Thee original full documentation is available [here](http://airtable-python-wrapper.readthedocs.io/).

### Usage Example

```python
from airtable import Airtable

# We updated the signature of `Airtable` class to support `airtable://` scheme URLs along with `view` and `sort` supported within the URLs.
airtable = Airtable('airtable://app1234567890/table_name?view=My%20View&sort=ID')

for record_id, fields in airtable.iter_records():
    print(f'Record ID: {record_id}, Fields: {fields}')

# Now you can get all the Airtable records as a big dictionary with record ID as keys
airtable.get_all_as_dict()

airtable.insert({'Name': 'Brian'})

# We added `batch_insert` and support generators for the records arguments; chunking of records to 10 each is done automatically.
airtable.batch_insert([record1, record2, ...])
airtable.batch_update([(id1, record1), (id2, record2), ...))  # same for batch_update

airtable.search('Name', 'Tom')

airtable.update_by_field('Name', 'Tom', {'Phone': '1234-4445'})

airtable.delete_by_field('Name', 'Tom')
```
