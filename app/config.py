from pydantic import BaseSettings, EmailStr

class Settings(BaseSettings):
    linkedin_email: EmailStr
    linkedin_password: str
    redirect_url: str
    linkedin_home_url: str
    linkedin_login_url: str
    
    class Config:
        env_file = ".env"
        
        
settings = Settings()