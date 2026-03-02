import requests
from google.cloud import storage
from google.cloud.exceptions import GoogleCloudError

from utils.helper import png_to_svg
from utils.logger import logger
from utils.settings import settings


class GCSClient:
    def __init__(self):
        self.client = storage.Client()
        self.bucket = self.client.get_bucket(settings.BUCKET_NAME)

    def upload_image(self, url, name):
        logger.info(f"Uploading {url} to {name}")
        try:

            content = png_to_svg(url).encode("utf-8")
            blob = self.bucket.blob(f'category_images1/{name}.svg')
            blob.upload_from_string(content, content_type='image/svg+xml')

            logger.info(f"Successfully uploaded: {blob.public_url}")
            return blob.public_url
        except GoogleCloudError as e:
            logger.error(f"GCS Upload Error for {name}: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error uploading {name}: {e}")
            raise

gcs_client = GCSClient()