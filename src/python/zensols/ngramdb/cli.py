"""Command line entrance point to the application.

"""
__author__ = 'plandes'

import logging
from zensols.actioncli import OneConfPerActionOptionsCliEnv
from zensols.ngramdb import (
    AppConfig,
    Downloader,
    CreateDatabase,
    Query,
)

#logging.basicConfig(level=logging.DEBUG)


class Cli(object):
    def __init__(self, config, ngram=None, lang=None, grams=None, year=None):
        self.config = config.app_config
        if ngram is not None:
            self.config.n_gram = ngram
        if lang is not None:
            self.config.lang = lang
        self.grams = grams
        self.year = year

    def env(self):
        self.config.default_vars['file_n'] = 0
        for sec in 'data ngram_db'.split():
            for k, v in self.config.get_options(sec).items():
                print(f'{sec}.{k}={v}')

    def download(self):
        #logging.getLogger('zensols.ngramdb').setLevel(logging.INFO)
        dl = Downloader(self.config)
        dl.download()

    def load(self):
        #logging.getLogger('zensols.ngramdb').setLevel(logging.INFO)
        cd = CreateDatabase(self.config, year_limit=self.year)
        cd.load()

    def query(self):
        logging.getLogger('zensols.ngramdb').setLevel(logging.WARNING)
        query = Query(self.config, year_limit=self.year)
        n_occurs = query(self.grams)
        print(n_occurs)

    def probability(self):
        logging.getLogger('zensols.ngramdb').setLevel(logging.WARNING)
        query = Query(self.config, year_limit=self.year)
        proba = query.probability(self.grams)
        print(proba)


class ConfAppCommandLine(OneConfPerActionOptionsCliEnv):
    def __init__(self):
        ngram_op = ['-n', '--ngram', False,  # require argument
                    {'dest': 'ngram', 'metavar': 'INTEGER',
                     'default': '1',
                     'help': 'ngram corpus to download or use'}]
        lang_op = ['-l', '--lang', True,  # require argument
                   {'dest': 'lang', 'metavar': 'INTEGER',
                    'default': 'eng',
                    'help': 'lang corpus to download or use'}]
        grams_op = ['-g', '--grams', True,  # require argument
                    {'dest': 'grams', 'metavar': 'STRING',
                     'help': 'the token(s) used for the n_gram lookup'}]
        year_op = ['-y', '--year', False,  # require argument
                   {'dest': 'year', 'metavar': 'INTEGER',
                    'help': 'the year to limit queries (aggregates up to value)'}]
        cnf = {'executors':
               [{'name': 'exporter',
                 'executor': lambda params: Cli(**params),
                 'actions': [{'name': 'env',
                              'doc': 'get environment configuration',
                              'opts': [ngram_op, lang_op]},
                             {'name': 'download',
                              'doc': 'download the corpus',
                              'opts': [ngram_op, lang_op]},
                             {'name': 'load',
                              'doc': 'load the corpus in to the database',
                              'opts': [year_op, ngram_op, lang_op]},
                             {'name': 'query',
                              'doc': 'query the database for occurances',
                              'opts': [year_op, ngram_op, lang_op, grams_op]},
                             {'name': 'probability',
                              'doc': 'compute the probability of the occurances',
                              'opts': [ngram_op, lang_op, grams_op]}]}],
               'config_option': {'name': 'config',
                                 'expect': True,
                                 'opt': ['-c', '--config', False,
                                         {'dest': 'config',
                                          'metavar': 'FILE',
                                          'help': 'configuration file'}]},
               'whine': 1}
        super(ConfAppCommandLine, self).__init__(
            cnf, config_env_name='ngramdbrc', pkg_dist='zensols.ngramdb',
            config_type=AppConfig)

    # def _create_config(self, conf_file, default_vars):
    #     db_type = self.parsed_options.db_type
    #     del self.parsed_options.db_type
    #     return self.config_type(
    #         db_type, config_file=conf_file, default_vars=default_vars)


def main():
    cl = ConfAppCommandLine()
    cl.invoke()
