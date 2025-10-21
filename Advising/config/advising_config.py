# src/config/advising_config.py
from pydantic import BaseSettings


class AdvisingConfig(BaseSettings):
    """Cấu hình hệ thống cố vấn học tập (Advising System)."""

    SERVERDB: str
    USERNAME: str
    PASSWORD: str

    class Config:
        # Chỉ định file .env ở thư mục gốc
        env_file = ".env"
        env_file_encoding = "utf-8"

# Tạo instance để dùng trong toàn hệ thống
settings = AdvisingConfig()
