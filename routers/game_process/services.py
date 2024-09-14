from random import randint

from aiogram.types import CallbackQuery, Message, Update

from core.config import bot, dp
from routers.game_process.helpers import get_asnwerer, set_players_order, set_spies
from routers.game_process.keyboards import complete_msg
from routers.helpers import GameData, GameStates, get_user_mention


async def answer_turn(callback: CallbackQuery, game_data: GameData) -> None:
    """Send a message to the chat that the player whose current at the turn now answer a question to the next player.

    Parameters
    ----------
    callback : CallbackQuery
        callback with data 'finished'.
    game_data : GameData
        GameData object with current game state data.
    """
    await callback.message.answer(
        text=f"{game_data.cur_order_num}. {get_user_mention(game_data.order_dict[game_data.cur_order_num])} отвечает:",
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
    get_asnwerer(game_data)
    msg = (
        f"{game_data.cur_order_num}. {get_user_mention(game_data.order_dict[game_data.cur_order_num])} "
        "задает вопрос {answerer}:"
    )
    await callback.message.answer(
        text=msg,
        reply_markup=complete_msg,
    )


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
    game_data.order_dict = set_players_order(game_data)
    await game_data.save()


async def start_vote(message: Message) -> None:
    """Manually triggers the start of the voting process by simulating a callback query.

    This function creates a `CallbackQuery` object with the data `"start_vote"` and manually feeds
    this update to the bot. This simulates the start of the voting process, as if a player had pressed
    a button to begin voting.

    Parameters
    ----------
    message : Message
        The message object representing the user's message that triggers the vote.
    """
    callback_query = CallbackQuery(
        id="manual",
        from_user=message.from_user,
        chat_instance=str(message.chat.id),
        message=message,
        data="start_vote",
    )

    update = Update(update_id=randint(1, 9999), callback_query=callback_query)

    await dp.feed_update(bot=bot, update=update)


async def start_reveal(message: Message) -> None:
    """Manually triggers the reveal of a player's role by simulating a callback query.

    This function creates a `CallbackQuery` object with the data `"reveal_role"` and manually feeds
    this update to the bot. This simulates the reveal process, as if a player had pressed a button to
    reveal their role in the game.

    Parameters
    ----------
    message : Message
        The message object representing the player's request to reveal their role.
    """
    callback_query = CallbackQuery(
        id="manual",
        from_user=message.from_user,
        chat_instance=str(message.chat.id),
        message=message,
        data="reveal_role",
    )

    update = Update(update_id=randint(1, 9999), callback_query=callback_query)

    await dp.feed_update(bot=bot, update=update)
