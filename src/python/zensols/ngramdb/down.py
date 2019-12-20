"""Download the corus files.

"""
__author__ = 'plandes'

import logging
import itertools as it
import urllib.request
import urllib.error

logger = logging.getLogger(__name__)


class Downloader(object):
    SECTION = 'data'

    def __init__(self, config):
        self.config = config

    def get_url(self, n):
        self.config.default_vars['file_n'] = n
        return self.config.get_option('url', self.SECTION)

    def get_path(self, n):
        self.config.default_vars['file_n'] = n
        return self.config.get_option_path('file_path', self.SECTION)

    def get_downloaded(self):
        dpath = self.get_path(0).parent
        return dpath.iterdir()

    def _download(self, n):
        path = self.get_path(n)
        url = self.get_url(n)
        if path.exists():
            logger.warning(f'{path} already exists--skipping')
        else:
            logger.info(f'downloading {url} -> {path}...')
            path.parent.mkdir(parents=True, exist_ok=True)
            try:
                urllib.request.urlretrieve(url, path)
            except urllib.error.HTTPError as e:
                if e.reason == 'Not Found':
                    return None
                else:
                    raise e
        return path

    def download(self):
        cnt = 0
        for n in it.count():
            path = self._download(n)
            if path is None:
                logger.info('downloaded {i} files')
                return cnt
            logger.info(f'downloaded {path}')
            cnt += 1
