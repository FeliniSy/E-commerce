from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # apis for technics
    ALTA_CAT_URL:str = "https://api.alta.ge/v1/Products/v4?CategoryId={0}&Limit=200&Page={1}"
    ALTA_PRODUCT_URL:str = "https://api.alta.ge/v1/Products/details?productId={0}"

    #apis for furniture
    FURNITURE_CAT_API: str = "https://koncept.ge/collections.json?limit=100"
    FURNITURE_PROD_API: str = "https://koncept.ge/collections/{0}/products.json?limit=250&page={1}"

    #apis for biblus
    BIBLUSI_API:str = "https://apiv1.biblusi.ge/api/book?page={0}"
    BIBLUSI_CAT_API:str = "https://apiv1.biblusi.ge/api/category"
    BIBLUSI_PROD_API:str = "https://apiv1.biblusi.ge/api/book/{0}?author=1&category=1&rate=1"

    # DB URL
    DB_URL:str = "postgresql://user:password@10.217.143.178:5432/products_db"

    #GCS CLIENT
    BUCKET_NAME:str = "vipo-images"
    GCS_KEY_PATH:str = "/home/user/Downloads/vipo-demo-eeed73f5c829.json"


    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

settings = Settings()