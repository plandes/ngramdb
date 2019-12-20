"""Application configuration class.

"""
__author__ = 'plandes'

import os
from pathlib import Path
from zensols.actioncli import (
    Config,
    ExtendedInterpolationEnvConfig,
)


class AppConfig(ExtendedInterpolationEnvConfig):
    NGRAM_SECTION = 'ngram_db'
    # NGRAM_PERSISTER_SECTION = 'ngram_db_persister'
    # NGRAM_STASH = 'ngram'
    # NGRAM_STASH_SECTION = NGRAM_STASH + '_stash'

    def __init__(self, *args, **kwargs):
        if 'default_expect' not in kwargs:
            kwargs['default_expect'] = True
        if 'remove_vars' not in kwargs:
            kwargs['remove_vars'] = 'LANG USER user'.split()
        super(AppConfig, self).__init__(*args, **kwargs)

    @property
    def n_gram(self):
        self.get_option('n_gram', self.NGRAM_SECTION)

    @n_gram.setter
    def n_gram(self, n_gram):
        self.set_option('n_gram', n_gram, self.NGRAM_SECTION)

    @property
    def lang(self):
        self.get_option('lang', self.NGRAM_SECTION)

    @lang.setter
    def lang(self, lang):
        self.set_option('lang', lang, self.NGRAM_SECTION)

    @classmethod
    def instance(cls, db_type: str):
        return cls(db_type, Path('~/.ngramdbrc').expanduser(),
                   default_vars=os.environ)

    @property
    def app_config(self) -> Config:
        return self.get_app_config(self)

    @classmethod
    def get_app_config(cls, config: Config) -> Config:
        self = config
        db_sec = cls.NGRAM_SECTION
        db_type = self.get_option('db_type', db_sec)
        path = self.resource_filename(f'resources/ngramdb-{db_type}.conf')
        new_conf = self.derive_from_resource(
            str(path.absolute()),
            copy_sections=(db_sec, self.NGRAM_SECTION, 'default',))
        rc_dir = str(self.resource_filename('resources').absolute())
        new_conf.set_option('rc_dir', rc_dir, db_sec)
        return new_conf

    @classmethod
    def add_config(cls, config: Config):
        secs = 'ngram_db_persister ngram_agg_db_persister ngram_stash ngram_agg_stash'.split()
        nconf = cls(config.config_file)
        nconf = nconf.app_config
        nconf.copy_sections(config, secs)
