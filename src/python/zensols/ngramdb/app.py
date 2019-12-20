"""Creates an SQLite database of the one million english ngrams.

"""
__author__ = 'plandes'

import logging
import sys
from time import sleep
import itertools as it
import csv
from multiprocessing import Pool
from zensols.actioncli.time import time
from zensols.actioncli import (
    persisted,
    StashFactory,
)
from zensols.db import DbPersisterFactory
from zensols.ngramdb import Downloader, AppConfig

logger = logging.getLogger(__name__)


class PersisterContainer(object):
    SECTION = 'data'

    @property
    @persisted('_persister')
    def persister(self):
        fac = DbPersisterFactory(self.config)
        return fac.instance('ngram')


class Inserter(PersisterContainer):
    def __init__(self, paths, config, year_limit, batches):
        self.paths = paths
        self.config = config
        self.year_limit = year_limit
        self.batches = batches
        self.chunk_size = self.config.get_option_int('chunk_size', self.SECTION)

    def insert_files(self):
        n_files = 0
        for path in self.paths:
            logger.info(f'importing {path}')
            with open(path) as f:
                with time('imported {row_count} rows'):
                    row_count = self.insert_rows(f, self.batches)
            n_files += 1
        logger.info(f'imported {n_files} files from {path}')
        return n_files

    def insert_rows(self, f, batches):
        row_count = 0
        reader = csv.reader(f, delimiter='\t', quoting=csv.QUOTE_NONE)
        reader = iter(reader)
        for i in range(batches):
            logger.info(f'loading batch {i} with {self.chunk_size} rows')
            rows = []
            for row in it.islice(reader, self.chunk_size):
                yr = int(row[1])
                if self.year_limit is None or yr >= self.year_limit:
                    row[1] = yr
                    rows.append(row)
            if len(rows) == 0:
                break
            else:
                self.persister.insert_rows(rows, errors='ignore')
                row_count += len(rows)
                logger.info(f'added {len(rows)} rows')
            rows.clear()
        return row_count


class CreateDatabase(PersisterContainer):
    def __init__(self, config, year_limit=None):
        self.config = config
        self.n_workers = self.config.get_option_int(
            'n_workers', section=self.SECTION)
        if year_limit is None:
            self.year_limit = None
        else:
            self.year_limit = int(year_limit)

    @property
    def downloaded_files(self):
        return Downloader(self.config).get_downloaded()

    @classmethod
    def insert_file(cls, payload):
        inserter = Inserter(**payload)
        return inserter.insert_files()

    def load(self, clear=True, batches=sys.maxsize):
        logging.getLogger('zensols.dbpg').setLevel(level=logging.DEBUG)
        if clear:
            self.persister.conn_manager.drop()
            self.persister.conn_manager.create()
        # apparently postgres lets go of the connection before the DB is
        # dropped
        sleep(2)
        csv.field_size_limit(10 ** 9)
        n = self.n_workers
        paths = tuple(self.downloaded_files)
        path_sets = []
        for i in range(0, len(paths), n):
            payload = {'paths': paths[i:i + n],
                       'config': self.config,
                       'year_limit': self.year_limit,
                       'batches': batches}
            path_sets.append(payload)
        pool = Pool(self.n_workers)
        logger.info(f'starting {len(path_sets)} groups importing ' +
                    f'on/after {self.year_limit}')
        totals = pool.map(CreateDatabase.insert_file, path_sets)
        logger.info(f'completed inserting {sum(totals)} files')


class Query(object):
    def __init__(self, config, year_limit=None, stash_name='ngram'):
        self.config = config
        self.stash_name = stash_name
        self.year_limit = year_limit

    @property
    @persisted('_stash', cache_global=True)
    def stash(self):
        fac = StashFactory(self.config)
        if self.year_limit is None:
            inst = fac.instance(self.stash_name)
        else:
            inst = fac.instance(self.stash_name, year_limit=self.year_limit)
        return inst

    def probability(self, ngrams):
        stash = self.stash
        cnt = len(stash)
        return stash[ngrams] / cnt

    def __call__(self, ngrams):
        stash = self.stash
        return stash[ngrams]
