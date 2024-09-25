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
            "📚 Правила игры:\n"
            "<blockquote><B>В этой игре вы можете оказаться где угодно:</B>\n"
            "• в школе 🏫\n"
            "• в полицейском участке 🚔\n"
            "• в пустыне Сахара 🏜\n"
            "• и даже на космической станции 🚀\n\n"
            "Где бы вы ни оказались, расслабляться нельзя: <B>рядом орудует шпион</B> 🤫.\n"
            "Тем не менее ему не известно, где вы, так что игрокам нужно задавать друг другу наводящие вопросы и "
            "прикладывать максимум усилий для того, чтобы не выдавая вашей локации <B>вычислить шпиона</B> по "
            "неточностям в ответах 🕵️.\n"
            "У шпионов другая задача — <B>выяснить локацию</B>, задавая вопросы о ней таким образом, чтобы остальные "
            "не вычислили его. Но ему стоит быть осторожным: лишь раскрыв себя, он может перейти к выбору, так что "
            "права на ошибку у него нет ❌.\n\n"
            f"<I>Минимальное количество игроков: {self.minimal_player_count}.\n"
            f"На 1 шпиона от {self.minimal_player_count-1} до {self.minimal_player_count*2-2} работников "
            "(на {self.minimal_player_count*2-1} работников 1 шпион, на {self.minimal_player_count*2} уже 2)</I>.\n\n"
            "❗️<B>Шпион побеждает</B>, угадав локацию работников (оставшиеся шпионы считаются проигравшими).\n"
            "Если шпион не угадал локацию — он покидает игру, ведь теперь его роль раскрыта.\n\n"
            "❗️Если в игре остается равное количество шпионов и работников - <B>объявляется ничья</B>.\n\n"
            "❗️<B>Работники одержат победу</B>, если выгонят всех шпионов.</blockquote>"
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
            "Для начала добавьте бота в чат, в котором вы хотите поиграть в шпиона. Пропишите команду /start_game. "
            "Бот присылает сообщение об регистрации в игру 🎮.\n\n"
            f"Если за {time} не наберется минимальное количество игроков ({self.minimal_player_count}) "
            "— игра отменяется ❌.\n"
            "Если же достаточное количество игроков набралось - начинается игровой процесс ✅.\n\n"
            "Просто следуйте сообщениям бота и наслаждайтесь игрой 😉!"
        )

    @property
    def commands(self) -> str:
        """Get formatted help on how to use bot`s commands."""
        return (
            "💻 Команды:\n\n"
            f"<blockquote>💬 /{self.start_game_command} — запустить набор в игру.\n\n"
            "💬 /vote — работник может прописать эту команду, если готов сказать кто является шпионом. "
            "Когда больше половины игроков напишут эту команду — голосование начнется!\n\n"
            "💬 /reveal — шпион может прописать эту команду, если он хочет раскрыть роль и угадать локацию.\n\n"
            "❗️Команды /vote и /reveal могут прописать как шпион, так и работник, но если команду /reveal "
            "пропишет сотрудник - он просто раскроет свою роль и выйдет из игры</blockquote>"
        )


settings = Settings()
