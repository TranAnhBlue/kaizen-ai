from pydantic_settings import BaseSettings, SettingsConfigDict
class Settings(BaseSettings):
    ai_service_token: str
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')
settings = Settings()
