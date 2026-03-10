from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    ALTA_CAT_URL:str = "https://api.alta.ge/v1/Products/v4?CategoryId={0}&Limit=200&Page={1}"
    ALTA_PRODUCT_URL:str = "https://api.alta.ge/v1/Products/details?productId={0}"
    DB_URL:str = "postgresql://postgres:postgres@localhost:5432/ecommerce"
    BUCKET_NAME:str = "vipo-images"
    GCS_KEY_PATH:str = "/home/user/Downloads/vipo-demo-eeed73f5c829.json"


    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

settings = Settings()