from aiogram.fsm.state import State, StatesGroup


class GameStates(StatesGroup):
    """Class for getting game state."""

    registration = State()
    game = State()
