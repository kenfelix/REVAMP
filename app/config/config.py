from pydantic import BaseSettings, EmailStr


class Settings(BaseSettings):
    linkedin_email: EmailStr
    linkedin_password: str
    linkedin_home_url: str
    linkedin_login_url: str
    rabbitmq_username: str
    rabbitmq_password: str
    rabbitmq_vhost: str
    mongodb_uri: str

    class Config:
        env_file = ".env"


settings = Settings()
