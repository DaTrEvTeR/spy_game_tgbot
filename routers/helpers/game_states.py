from asyncio import Task
from dataclasses import dataclass, field
from typing import Optional, Set

from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import User

from core.settings import settings

from .get_str_players_list import get_str_players_list


class GameStates(StatesGroup):
    """Class for getting game state."""

    registration = State()
    game = State()
    vote = State()
    reveal = State()


@dataclass
class GameData:
    """Class that represents all game data.

    Usage
    -------
    To create a GameData object with data from the current state, use the class method `init`:
        game_data = await GameData.init(state=state)
    To update the data, use the object method `refresh`:
        await game_data.refresh()
    To save data from the object to the state, use the `save` method:
        await game_data.save()
    """

    state: FSMContext

    players: Set[User] = field(default_factory=set)
    registration_task: Optional[Task] = None
    spies: Set[User] = field(default_factory=set)
    order_dict: dict[int, User] = field(default_factory=dict)
    cur_order_num: int = 1
    is_question: bool = True
    ready_to_vote: set[User] = field(default_factory=set)
    vote_task: Optional[Task] = None
    voted_players: set[User] = field(default_factory=set)
    votes: dict[str, int] = field(default_factory=dict)
    # possible_locations:

    @classmethod
    async def init(cls, state: FSMContext) -> "GameData":
        """Initializes a new instance of the GameData class and refreshes its state.

        This method creates a new GameData instance, setting its state to the provided FSMContext,
        and then calls `refresh()` to ensure the object's data is up to date.

        Parameters
        ----------
        state : FSMContext
            The FSMContext used to track the current state of the game.

        Returns:
        -------
        GameData
            A new instance of GameData with its state initialized and refreshed.
        """
        instance = cls(state=state)
        await instance.refresh()
        return instance

    @property
    def count_workers_and_spies(self) -> str:
        return f"Работники:\n{get_str_players_list(self.order_dict)}\nШпионов среди них: {len(self.spies)}"

    async def save(self) -> None:
        """Saves the current state of the object back to the FSM state."""
        await self.state.update_data(self.__dict__)

    def is_players_enough(self) -> bool:
        """Checks if the current number of players is sufficient to start the game.

        This method compares the number of players in the `self.players` list with the minimum
        required player count defined in the `settings.minimal_player_count` setting.


        Returns:
        -------
        bool
            True if the number of players is greater than or equal to the minimum required,
            False otherwise.
        """
        return len(self.players) >= settings.minimal_player_count

    async def refresh(self) -> None:
        """Refreshes the current object with the latest data from the FSM context state."""
        data = await self.state.get_data()
        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def next_turn(self) -> int:
        """Advances to the next player's turn, alternating between a question and non-question turn.

        If the current turn involves a question (`self.is_question` is True), the player index
        (`self.cur_order_user_index`) is advanced to the next player in the `order_list`. If the
        current player is the last in the list, the index wraps around to the first player.

        After updating the player index, the question turn flag (`self.is_question`) is toggled.


        Returns:
        -------
        int
            The updated index of the current player in the `order_list`.
        """
        if self.is_question:
            if self.cur_order_num != max(self.order_dict):
                self.cur_order_num = self.find_next()
            else:
                self.cur_order_num = min(self.order_dict)
        self.is_question = not self.is_question
        return self.cur_order_num

    def find_next(self) -> int:
        """Find the next key in the `order_dict` based on the current order number.

        This function returns the next key in `self.order_dict` after `self.cur_order_num`.
        If `self.cur_order_num` is the highest key in the dictionary, the smallest key
        is returned. If `self.cur_order_num` is not found in `self.order_dict`, the function
        returns 0.

        Returns:
        -------
        int
            The next key after `self.cur_order_num` in `self.order_dict`, or the smallest
            key in `self.order_dict` if `self.cur_order_num` is the largest. Returns `None`
            if `self.cur_order_num` is not found in `self.order_dict`.
        """
        if self.cur_order_num < max(self.order_dict):
            is_cur = False
            for i in self.order_dict:
                if is_cur:
                    return i
                if i == self.cur_order_num:
                    is_cur = True
            return 0
        return min(self.order_dict)
