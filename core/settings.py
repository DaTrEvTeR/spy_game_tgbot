from pathlib import Path

from pydantic import ConfigDict
from pydantic_settings import BaseSettings

env_file = Path(__file__).parent.parent / ".env"


class Settings(BaseSettings):
    """Provides all project settings and takes some settings,
    such as "BOT_API_TOKEN", from .env.
    """

    bot_api_token: str

    minimal_player_count: int = 2
    start_game_command: str = "start_game"
    registration_time: int = 60  # Time for registration for game after command `start_game_command` in sec

    model_config = ConfigDict(
        extra="ignore",
        env_file=env_file if env_file.exists() else None,
        env_file_encoding="utf-8",
    )

    @property
    def game_rules(self) -> str:
        return (
            "В этой игре вы можете оказаться где угодно: в школе, в полицейском участке, "
            "в пустыне Сахаре или даже на космической станции.\n"
            "Где бы вы ни оказались, расслабляться нельзя, рядом орудует шпион.\n"
            "Игрокам нужно задавать друг другу наводящие вопросы и прикладывать максимум усилий для того, "
            "чтобы вычислить шпиона по неточностям в ответах.\n"
            "У шпионов будет другая задача — выяснить локацию, задавая вопросы о ней таким образом, "
            "чтобы остальные не вычислили его.\n"
            f"Минимальное количество игроков: {self.minimal_player_count}"
        )

    @property
    def how_use_bot(self) -> str:
        return (
            "Для начала добавьте бота в чат, в котором вы хотите поиграть в шпиона\n"
            f"Пропишите команду /{self.start_game_command}\n"
            f"На {settings.registration_time // 60} мин бот присылает сообщение об регистрации в игру\n"
            f"Если не наберется минимальное количество игроков({self.minimal_player_count}) - игра отменяется\n"
            "Если набралось достаточное количество игроков начинается игровой процесс - "
            "просто следуйте сообщениям бота и наслаждайтесь игрой"
        )


settings = Settings()
