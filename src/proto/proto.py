import logging
from zensols.actioncli import ClassImporter
from zensols.ngramdb import AppConfig

logger = logging.getLogger(__name__)


def instance(name, info=(), debug=()):
    test_conf = AppConfig('test-resources/test.conf')
    conf = test_conf.app_config
    for l in debug:
        logging.getLogger(f'zensols.ngramdb.{l}').setLevel(logging.DEBUG)
    for l in info:
        logging.getLogger(f'zensols.ngramdb.{l}').setLevel(logging.INFO)
    return ClassImporter(name).instance(conf)


def tmp():
    app = instance('zensols.ngramdb.app.Query', debug='createdb'.split())
    app.query('The')


def main():
    logging.basicConfig(level=logging.WARNING)
    run = 1
    {1: tmp,
     }[run]()


main()
