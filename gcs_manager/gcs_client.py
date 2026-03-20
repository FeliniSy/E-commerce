from google.cloud import storage
from google.cloud.exceptions import GoogleCloudError

from utils.helper import png_to_svg
from utils.logger import logger
from utils.settings import settings


class GCSClient:
    def __init__(self):
        self._client = storage.Client.from_service_account_json(settings.GCS_KEY_PATH)
        self._bucket = None
        self._credentials_available = True
        self._upload_cache = {}

    def _connect(self):
        if self._bucket is None and self._credentials_available:
            try:
                self._bucket = self._client.get_bucket(settings.BUCKET_NAME)
            except GoogleCloudError as e:
                logger.warning(f"GCS access error: {e}. Image uploads will be skipped.")
                self._credentials_available = False
                self._client = None
                self._bucket = None

    def upload_image(self, url, name):
        if name in self._upload_cache:
            logger.info(f"Using cached URL for {name}")
            return self._upload_cache[name]

        logger.info(f"Uploading {url} to {name}")
        self._connect()

        if not self._credentials_available or self._client is None:
            logger.warning(f"Skipping GCS upload for {name} - credentials not available")
            return None

        try:
            content = png_to_svg(url).encode("utf-8")
            blob = self._bucket.blob(f'category_images1/{name}.svg')
            blob.upload_from_string(content, content_type='image/svg+xml')

            logger.info(f"Successfully uploaded: {blob.public_url}")
            self._upload_cache[name] = blob.public_url
            return blob.public_url
        except GoogleCloudError as e:
            logger.error(f"GCS Upload Error for {name}: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error uploading {name}: {e}")
            raise

gcs_client = GCSClient()