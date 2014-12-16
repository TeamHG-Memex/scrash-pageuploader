Scrash Page Uploader
===

A set of [Scrapy](http://scrapy.org]) pipelines that provide easy way to store html and screenshots rendered by [Splash service](http://splash.readthedocs.org/). Each upload is non-blocking, so it won't slow down crawling process significantly.

**Note**: Only S3 storage is supported at the moment.

Pipelines
---
In order to store your HTML or PNG in S3 you must enable correspoding pipelines in `settings.py` (assuming you have package installed):

	ITEM_PIPELINES = {
		...
		'pageuploader.html.UploadHtmlPipeline': 700,
		... and/or ...
		'pageuploader.screenshots.UploadScreenshotsPipeline': 700,
		...
	}
	
Items
---
To support page/screenshot uploading you must define 4 additional fields in your items:

*Input fields* (will be deleted after upload):

- `html`: contains HTML string to store
- `screenshot`: contains PNG screenshot binary string to store

*Output fields* (will be populated with S3 urls):

- `html_url`: contains URL of stored HTML file
- `screenshot_url`: contains URL of stored PNG file
	
Configuring
---
If you have no S3 credentials set in Scrapy, you must set them in `settings.py`

	AWS_ACCESS_KEY_ID = '<my key id>'
	AWS_SECRET_ACCESS_KEY = '<my secret>'
	
Next, please set S3 bucket and path (expressed by single URI) where assets will be stored

	S3_HTML_PATH = 's3://bucket-name/prefix1/
	S3_SCREENSHOTS_PATH = 's3://bucket-name/prefix2/
	
**Note**: Please end URIs with trailing `/`

Tests
---
To run tests, you have to type it in console when you are in the project directory:

	tox
