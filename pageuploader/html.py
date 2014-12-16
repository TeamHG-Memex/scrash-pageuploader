from base64 import urlsafe_b64encode

from twisted.internet.defer import inlineCallbacks, returnValue
from scrapy.exceptions import NotConfigured

from . import S3Pipeline


class UploadHtmlPipeline(S3Pipeline):
    def __init__(self, settings):
        self.uri = settings.get('S3_HTML_PATH')
        if not self.uri:
            raise NotConfigured('S3_HTML_PATH must be provided')
        super(UploadHtmlPipeline, self).__init__(settings)

    @inlineCallbacks
    def process_item(self, item, spider):
        if 'html' not in item:
            returnValue(item)
        html_utf8 = item['html'].encode('utf-8')
        key_name = self.key_name(item, spider)
        url = yield self.store(key_name, html_utf8)
        del item['html']
        item['html_url'] = url
        returnValue(item)

    def key_name(self, item, spider):
        filename = urlsafe_b64encode(item['url']) + '.html'
        return '%s/%s/%s/%s' % (
            self.root, spider.name, self.time_str, filename
        )
