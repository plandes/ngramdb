"""SQLite database.

"""
__author__ = 'plandes'

import logging
from pathlib import Path
from zensols.actioncli import (
    persisted,
    PersistedWork,
    StashFactory,
    DelegateStash,
)
from zensols.db import (
    Bean,
    BeanDbPersister,
    DbPersisterFactory,
)
import zensols.dbpg
from zensols.ngramdb import AppConfig

logger = logging.getLogger(__name__)


class NgramBean(Bean):
    def __init__(self, grams: str, yr: int, match_count: int,
                 page_count: int, volume_count: int, id: int):
        self.grams = grams
        self.yr = yr
        self.match_count = match_count
        self.page_count = page_count
        self.volume_count = volume_count
        self.id = id

    def get_attr_names(self):
        return 'grams yr match_count page_count volume_count id'.split()


class NgramPersister(BeanDbPersister):
    def __init__(self, lang: str, n_gram: str, prefix: str, *args, **kwargs):
        super(NgramPersister, self).__init__(
            *args, row_factory=NgramBean, **kwargs)
        self.lang = lang
        self.n_gram = n_gram
        self.prefix = prefix

    def get_by_grams(self, grams) -> list:
        return self.execute_by_name(
            self.prefix + '_select_by_ngram',
            params=(grams,),
            row_factory=self.row_factory)

    def get_match_count(self, grams=None, year_limit=None) -> int:
        entry_name = self.prefix + '_select_aggregate_match_count'
        params = []
        if grams is not None:
            entry_name = entry_name + '_by_grams'
            params.append(grams)
        if year_limit is not None:
            entry_name = entry_name + '_by_year'
            params.append(year_limit)
        res = self.execute_singleton_by_name(entry_name, params=params)
        if res is not None:
            return res[0]

    def get_match_pattern_count(self, grams) -> int:
        row = self.execute_singleton_by_name(
            'ngram_agg_select_aggregate_match_count_by_grams',
            params=(grams,))
        if row is not None:
            return row[0]

    def get_top_nth_count(self, n) -> int:
        return self.execute_singleton_by_name(
            'ngram_agg_top_n_count',
            row_factory='dict',
            params=(n,))

    def grams_exist(self, grams) -> bool:
        res = self.execute_singleton_by_name(
            self.prefix + '_select_entry_exists_by_id',
            params=(grams,))
        if res is not None:
            return res[0] > 0

    def get_grams(self) -> list:
        return self.execute_by_name(
            self.prefix + '_select_distinct_grams',
            map_fn=lambda x: x[0])


DbPersisterFactory.register(NgramPersister)


class NgramStash(DelegateStash):
    def __init__(self, config: AppConfig, persister: str, year_limit=None):
        super(NgramStash, self).__init__()
        fac = DbPersisterFactory(config)
        self.persister = fac.instance(persister)
        self.year_limit = year_limit
        data_dir = config.get_option(
            'data_dir', section=AppConfig.NGRAM_SECTION, expect=False)
        if data_dir is not None:
            cnf = config.populate(section=AppConfig.NGRAM_SECTION)
            prefix = self.persister.prefix
            fname = f'len_{prefix}_{cnf.lang}_{cnf.n_gram}ngram.dat'
            path = Path(data_dir, fname)
            path.parent.mkdir(parents=True, exist_ok=True)
            self._len = PersistedWork(path, self)

    def load(self, name: str) -> int:
        return self.persister.get_match_count(name, year_limit=self.year_limit)

    def exists(self, name: str) -> bool:
        return self.persister.grams_exist(name)

    def keys(self) -> iter:
        return self.persister.get_grams()

    @persisted('_len')
    def __len__(self):
        return self.persister.get_match_count(year_limit=self.year_limit)


StashFactory.register(NgramStash)
