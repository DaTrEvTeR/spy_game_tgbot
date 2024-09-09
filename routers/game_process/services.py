from aiogram.types import CallbackQuery

from routers.game_process.helpers import get_asnwerer, set_players_order, set_spies
from routers.game_process.keyboards import complete_msg
from routers.game_states import GameData, GameStates
from routers.helpers import get_player_username_or_firstname


async def answer_turn(callback: CallbackQuery, game_data: GameData) -> None:
    """Send a message to the chat that the player whose current at the turn now answer a question to the next player.

    Parameters
    ----------
    callback : CallbackQuery
        callback with data 'finished'.
    game_data : GameData
        GameData object with current game state data.
    """
    cur_user_index = game_data.cur_order_user_index
    await callback.message.answer(
        text=f"{get_player_username_or_firstname(game_data.order_list[cur_user_index])} отвечает:",
        reply_markup=complete_msg,
    )
    await callback.answer()


async def question_turn(callback: CallbackQuery, game_data: GameData) -> None:
    """Send a message to the chat that the player whose current at the turn now asks a question to the next player.

    Parameters
    ----------
    callback : CallbackQuery
        callback with data 'finished'.
    game_data : GameData
        GameData object with current game state data.
    """
    cur_user_index = game_data.cur_order_user_index
    answerer = get_asnwerer(game_data)
    await callback.message.answer(
        text=f"{get_player_username_or_firstname(game_data.order_list[cur_user_index])} задает вопрос {answerer}:",
        reply_markup=complete_msg,
    )
    await callback.answer()


async def pass_turn(callback: CallbackQuery, game_data: GameData) -> None:
    """Advances the turn in the game and determines whether to proceed with
    a question or answer phase based on the current game state.

    Parameters
    ----------
    callback : CallbackQuery
        The callback query triggered by the user with data 'finished'.

    game_data : GameData
        GameData object with current game state data.
    """
    game_data.next_turn()
    await game_data.save()
    if game_data.is_question:
        await question_turn(callback, game_data)
    else:
        await answer_turn(callback, game_data)


async def setup_game_state(game_data: GameData) -> None:
    """Prepares the game by setting the game state, assigning spies, and
    determining the order of players before saving the game data.

    Parameters
    ----------
    game_data : GameData
        An instance of the GameData class that manages the current state
        and settings of the game, including players, roles, and order.
    """
    await game_data.state.set_state(GameStates.game)
    game_data.spies = set_spies(game_data)
    game_data.order_list = set_players_order(game_data)
    await game_data.save()
