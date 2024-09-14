from aiogram.types import Message

from .game_states import GameData, GameStates
from .get_user_mention import get_user_mention


async def process_remaining_players(message: Message, game_data: GameData) -> None:
    """Process the game state based on the remaining players and determine the outcome.

    This function checks the current number of spies and workers remaining in the game to decide
    whether the game should end or continue. It either declares the workers or spies as winners,
    or continues the game if conditions for a victory have not been met.

    Parameters
    ----------
    vote_msg : Message
        The message object used to send responses to the chat, providing updates on the game's status
        and announcing the winner if the game ends.

    game_data : GameData
        The current game state, which contains information about the remaining players, spies, and
        workers.
    """
    if len(game_data.spies) == 0:
        await game_data.state.clear()
        await message.answer(text="Работники выиграли!")
    elif len(game_data.order_dict) - len(game_data.spies) <= len(game_data.spies):
        await game_data.state.clear()
        spies_message = ""
        for spy in game_data.spies:
            spies_message += f"{get_user_mention(spy)} "
        response_message = (
            f"Ничья. Работники не смогли вычислить шпионов, а шпионы определить локацию\nШпионами были: {spies_message}"
        )
        await message.answer(text=response_message)
    else:
        await game_data.state.set_state(GameStates.game)
        await game_data.save()
        response_message = f"Продолжаем игру!\n\n{game_data.count_workers_and_spies}"
        await message.answer(text=response_message)
