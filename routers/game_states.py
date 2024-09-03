from asyncio import Task
from dataclasses import dataclass, field
from typing import Optional, Set

from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import User

from core.settings import settings


class GameStates(StatesGroup):
    """Class for getting game state."""

    registration = State()
    game = State()


@dataclass
class GameData:
    state: FSMContext

    players: Set[User] = field(default_factory=set)
    registration_task: Optional[Task] = None
    spies: Set[User] = field(default_factory=set)
    order_list: list[User] = field(default_factory=list)
    cur_order_user_index: int = 0

    @classmethod
    async def init(cls, state: FSMContext) -> "GameData":
        """Asynchronous factory method to create and initialize GameData."""
        instance = cls(state=state)
        await instance.refresh()
        return instance

    async def save(self) -> None:
        """Saves the current state of the object back to the FSM state."""
        await self.state.update_data(self.__dict__)

    def is_players_enough(self) -> bool:
        """Returns True if the number of players is equal to or greater than the required minimum."""
        return len(self.players) >= settings.minimal_player_count

    async def refresh(self) -> None:
        """Refreshes the current object with the latest data from the FSM context state."""
        data = await self.state.get_data()
        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)
