from base64 import urlsafe_b64encode

from scrapy.exceptions import NotConfigured
from twisted.internet.defer import inlineCallbacks, returnValue

from . import S3Pipeline


class UploadScreenshotsPipeline(S3Pipeline):

    def __init__(self, settings):
        self.uri = settings.get('S3_SCREENSHOTS_PATH')
        if not self.uri:
            raise NotConfigured('S3_SCREENSHOTS_PATH must be provided')
        super(UploadScreenshotsPipeline, self).__init__(settings)

    @inlineCallbacks
    def process_item(self, item, spider):
        png = item.get('screenshot')
        if png is None:
            returnValue(item)

        key_name = self.key_name(item, spider)
        url = yield self.store(key_name, png)
        del item['screenshot']
        item['screenshot_url'] = url
        returnValue(item)

    def key_name(self, item, spider):
        return '%s/%s/%s/%s' % (
            self.root, spider.name, self.time_str,
            urlsafe_b64encode(item['url']) + '.png'
        )
