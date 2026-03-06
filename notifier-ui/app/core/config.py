import os


class Settings:
    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql://notifier_user:notifier_pass@localhost:5432/notifier_db",
    )
    provider_sim_url: str = os.getenv("PROVIDER_SIM_URL", "http://provider-sim:8000")
    callback_url: str = os.getenv(
        "CALLBACK_URL",
        "http://notifier-ui:8000/api/provider-callback",
    )
    static_dir: str = os.getenv("STATIC_DIR", "static")


settings = Settings()
