import os


class Settings:
    notifier_ui_url: str = os.getenv("NOTIFIER_UI_URL", "http://notifier-ui:8000")


settings = Settings()
