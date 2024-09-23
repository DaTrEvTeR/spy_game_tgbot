from pathlib import Path

from pydantic import ConfigDict
from pydantic_settings import BaseSettings

env_file = Path(__file__).parent.parent / ".env"


class Settings(BaseSettings):
    """Provides all project settings and takes some settings,
    such as "BOT_API_TOKEN", from .env.
    """

    bot_api_token: str

    minimal_player_count: int = 4
    start_game_command: str = "start_game"
    registration_time: int = 60  # Time for registration for game after command `start_game_command` in sec
    start_registration_msg: str = "Регистрация на игру!"
    vote_time: int = 60  # Time for vote for spy in sec

    model_config = ConfigDict(
        extra="ignore",
        env_file=env_file if env_file.exists() else None,
        env_file_encoding="utf-8",
    )

    @property
    def game_rules(self) -> str:
        """Get formatted game rules."""
        return (
            "В этой игре вы можете оказаться где угодно: в школе, в полицейском участке, "
            "в пустыне Сахаре или даже на космической станции.\n"
            "Где бы вы ни оказались, расслабляться нельзя, рядом орудует шпион.\n"
            "Игрокам нужно задавать друг другу наводящие вопросы и прикладывать максимум усилий для того, "
            "чтобы вычислить шпиона по неточностям в ответах.\n"
            "У шпионов будет другая задача — выяснить локацию, задавая вопросы о ней таким образом, "
            "чтобы остальные не вычислили его.\n"
            f"Минимальное количество игроков: {self.minimal_player_count}\n"
            f"На 1 шпиона от {self.minimal_player_count-1} до {self.minimal_player_count*2-2} игроков"
            f"(На {self.minimal_player_count*2-1} игроков 1 шпион, на {self.minimal_player_count*2} уже 2)\n"
            "Победа шпиона = угадывание слова"
            "(оставшиеся шпионы считаются проигравшими, а если шпион не угадал слово - он исключается из игры)\n"
            "Ничья = осталось равное количество шпионов и игроков\n"
            "Победа игроков - выгнали всех шпионов\n"
        )

    @property
    def how_use_bot(self) -> str:
        """Get formatted help on how to use the bot."""
        time_min = ""
        time_sec = ""
        if self.registration_time // 60 >= 1:
            time_min = f"{self.registration_time // 60} мин"
        if self.registration_time % 60 != 0:
            time_sec = f"{self.registration_time % 60} сек"
        time = f"{time_min} {time_sec}".strip()
        return (
            "Для начала добавьте бота в чат, в котором вы хотите поиграть в шпиона\n"
            f"Пропишите команду /{self.start_game_command}\n"
            f"На {time} бот присылает сообщение об регистрации в игру\n"
            f"Если не наберется минимальное количество игроков({self.minimal_player_count}) - игра отменяется\n"
            "Если набралось достаточное количество игроков начинается игровой процесс - "
            "просто следуйте сообщениям бота и наслаждайтесь игрой"
        )


settings = Settings()
