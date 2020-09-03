__all__ = ['Airtable']
from itertools import islice
import logging
import os
from time import sleep
from urllib.parse import ParseResult
from urllib.parse import parse_qs
from urllib.parse import unquote_plus
from urllib.parse import urlencode
from urllib.parse import urlparse
from urllib.parse import urlunparse

from .airtable import Airtable as OriginalAirtable

logger = logging.getLogger(__name__)


class Airtable(OriginalAirtable):
    def __init__(self, airtable_url_or_base_key, table_name=None, api_key=None, ignore_column='Status', sort=[], view=None, **kwargs):
        if isinstance(airtable_url_or_base_key, ParseResult):
            u = airtable_url_or_base_key
        elif airtable_url_or_base_key.startswith('airtable://'):
            u = urlparse(airtable_url_or_base_key)
        else:
            u = urlparse(f'airtable://{airtable_url_or_base_key}')

        if u.scheme != 'airtable':
            raise TypeError(f'{u.geturl()} is an unsupported Airtable URL.')

        if table_name is None:
            table_name = unquote_plus(u.path).lstrip('/')

        if not table_name:
            raise ValueError(f'Airtable table name not specified.')

        # This behavior was removed by gtalarico/airtable-python-wrapper in https://github.com/gtalarico/airtable-python-wrapper/commit/e742a9abc11112e0dc1b8ae9f097bd4a72ae30e1
        if api_key is None:
            api_key = os.environ['AIRTABLE_API_KEY']

        self._base_key = u.netloc

        super().__init__(self.base_id, table_name, api_key=api_key, **kwargs)

        q = parse_qs(u.query)
        self.view = q.get('view', [None])[0] or view
        self.sort = q.get('sort') or sort

        self.ignore_column = q.get('ignore_column', [None])[0] or ignore_column

        q = dict(view=self.view) if self.view else {}
        self._canonical_url = urlunparse((u.scheme, self.base_id, table_name, None, urlencode(q), None))

        logger.info(f'Connected to Airtable <{table_name}> on base <{self.base_id}> (view={self.view}, sort={self.sort}).')

    @property
    def base_id(self):
        return self._base_key

    @property
    def canonical_url(self):
        return self._canonical_url

    def iter_records(self, view=None, sort=[], ignore_column=None, **kwargs):
        view = view or self.view
        sort = sort or self.sort
        ignore_column = ignore_column or self.ignore_column

        for page in self.get_iter(view=view, sort=sort, **kwargs):
            for record in page:
                record_id, fields = record['id'], record.get('fields', {})
                if ignore_column and 'Ignore' in fields.get(ignore_column, []):
                    logger.debug(f'Ignore row {fields.get("ID", record_id)}.')
                    continue

                yield record_id, fields

    def batch_insert(self, records, typecast=False):
        # Almost the same as original except that it is a generator func
        inserted_records = []
        for chunk in self._chunk(records, self.MAX_RECORDS_PER_REQUEST):
            new_records = self._build_batch_record_objects(chunk)

            response = self._post(self.url_table, json_data={'records': new_records, 'typecast': typecast})

            yield from response['records']

            sleep(self.API_LIMIT)

        return inserted_records
    #end def

    def batch_update(self, records, typecast=True, destructive=False):
        request_func = self._put if destructive else self._patch

        for chunk in self._chunk(records, self.MAX_RECORDS_PER_REQUEST):
            new_records = [{'id': record_id, 'fields': fields} for record_id, fields in chunk]

            response = request_func(self.url_table, json_data={'records': new_records, 'typecast': typecast})

            yield from response['records']

            sleep(self.API_LIMIT)

    def get_all_as_dict(self, **kwargs):
        return dict(self.iter_records(**kwargs))

    def _chunk(self, iterable, chunk_size=128):
        it = iter(iterable)
        while True:
            chunk = tuple(islice(it, chunk_size))
            if not chunk:
                return

            yield chunk
