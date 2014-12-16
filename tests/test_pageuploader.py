#coding: utf-8
from mock import Mock
from twisted.trial.unittest import TestCase
from twisted.internet.defer import inlineCallbacks, returnValue
from scrapy import Item, Field
from scrapy.settings import Settings
from scrapy.exceptions import NotConfigured

from pageuploader.html import UploadHtmlPipeline
from pageuploader.screenshots import UploadScreenshotsPipeline


class TestItem(Item):
    url = Field()
    png = Field()
    screenshot_url = Field()
    html = Field()
    html_url = Field()


class SpiderMock(object):
    name = 'test-spider'


class PageUploaderTestCase(TestCase):

    def test_no_s3_html_path_given(self):
        settings = Settings({
            'AWS_ACCESS_KEY_ID': 'user',
            'AWS_SECRET_ACCESS_KEY': 'password',
        })
        self.assertRaises(NotConfigured, UploadHtmlPipeline, settings)

    def test_no_s3_credentials(self):
        settings = Settings({
            'S3_HTML_PATH': 's3://test/html',
            'S3_SCREENSHOTS_PATH': 's3://test/html'
        })
        self.assertRaises(NotConfigured, UploadHtmlPipeline, settings)

    @inlineCallbacks
    def test_html_uploaded_if_given(self):
        item = TestItem(url='http://example.com', html='data')
        yield self._test_pipeline_uploading(UploadHtmlPipeline, item)

    @inlineCallbacks
    def test_screenshot_uploaded_if_given(self):
        item = TestItem(url='http://example.com', png='data')
        yield self._test_pipeline_uploading(UploadScreenshotsPipeline, item)

    @inlineCallbacks
    def test_html_doesnt_uploaded_if_missing(self):
        item = TestItem(url='http://example.com', png='data')
        yield self._test_pipeline_uploading(UploadHtmlPipeline, item, False)

    @inlineCallbacks
    def test_screenshot_doesnt_uploaded_if_missing(self):
        item = TestItem(url='http://example.com', html='data')
        yield self._test_pipeline_uploading(UploadScreenshotsPipeline, item,
                                            False)

    @inlineCallbacks
    def test_item_populated_with_html_url(self):
        item = TestItem(url='http://example.com', html='data')
        new_item = yield self._test_pipeline_uploading(UploadHtmlPipeline,
                                                       item)
        self.assertEqual(new_item['html_url'], 'http://example.com')

    @inlineCallbacks
    def test_item_populated_with_png_url(self):
        item = TestItem(url='http://example.com', png='data')
        new_item = yield self._test_pipeline_uploading(
            UploadScreenshotsPipeline, item
        )
        self.assertEqual(new_item['screenshot_url'], 'http://example.com')

    @inlineCallbacks
    def _test_pipeline_uploading(self, cls, item, should_store=True):
        obj = cls(self.settings)
        obj.get_root_and_bucket = Mock(side_effect=[[None, None]])
        obj.store = Mock(side_effect=['http://example.com'])

        spider = SpiderMock()
        key_name = obj.key_name(item, spider)
        new_item = yield obj.process_item(item, spider)
        if should_store:
            obj.store.assert_called_once_with(key_name, 'data')
        else:
            self.assertEqual(obj.store.called, False)
        returnValue(new_item)

    @property
    def settings(self):
        return Settings({
            'S3_HTML_PATH': 's3://test/html',
            'S3_SCREENSHOTS_PATH': 's3://test/html',
            'AWS_ACCESS_KEY_ID': 'user',
            'AWS_SECRET_ACCESS_KEY': 'password',
        })
