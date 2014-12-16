import time
from urlparse import urlparse

import boto
from scrapy.exceptions import NotConfigured
from twisted.internet.threads import deferToThread


class S3Pipeline(object):

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings)

    def __init__(self, settings):
        self.time_str = time.strftime('%Y%m%d%H%M%S')
        self.root, self.bucket = self.get_root_and_bucket(self.uri, settings)

    def store(self, keyname, data):
        return deferToThread(self._store, keyname, data)

    def _store(self, keyname, data):
        key = self.bucket.new_key(keyname)
        key.set_contents_from_string(data)
        key.set_acl('public-read')
        key.close()
        url = key.generate_url(expires_in=0, query_auth=False)
        return url

    def get_root_and_bucket(self, uri, settings):
        u = urlparse(self.uri)
        bucketname = u.hostname
        access_key = u.username or settings['AWS_ACCESS_KEY_ID']
        secret_key = u.password or settings['AWS_SECRET_ACCESS_KEY']
        if not access_key or not secret_key:
            raise NotConfigured('No AWS_ACCESS_KEY_ID or '
                                'AWS_SECRET_ACCESS_KEY set in settings.py')
        conn = boto.connect_s3(access_key, secret_key)
        return u.path, conn.get_bucket(bucketname, validate=False)
