from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    MAIN_URL:str = "https://api.alta.ge/v1/Products/v4?CategoryId={0}&Limit=200&Page={1}"
    PRODUCT_URL:str = "https://api.alta.ge/v1/Products/details?productId={0}"
    # DB_URL:str = "postgresql://postgres:123@localhost:5432/E-commerce"
    DB_URL:str ="postgresql://vipo_demo_user:PdVeSCiTeC5bWkLK0t1LLnwMDNhUXsDY@dpg-d6fdkki4d50c73eb0o2g-a.frankfurt-postgres.render.com/vipo_demo"
    BUCKET_NAME:str = "vipo-images"


    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

settings = Settings()