import asyncio

from aiogram.types import CallbackQuery, Message

from core.settings import settings
from routers.game_states import GameData, GameStates
from routers.helpers import get_user_mention
from routers.vote_process.helpers import (
    get_key,
    get_user_by_id,
    register_vote,
    send_confirmation_notification,
    show_results,
)
from routers.vote_process.keyboards import users


async def send_voting_message(callback: CallbackQuery, game_data: GameData) -> Message:
    """Sends a message with an inline keyboard for voting to the chat.

    Parameters
    ----------
    callback : CallbackQuery
        The callback query containing the information to send the message.
    game_data : GameData
        The game data object used to generate the voting keyboard.

    Returns:
    -------
    Message
        The message object sent to the chat with the voting options.
    """
    await callback.message.answer(text="Больше половины игроков готовы дать ответ. \nКто же является шпионом?")
    keyboard = users(game_data)
    return await callback.message.answer(text="Кого вы подозреваете в шпионаже?", reply_markup=keyboard)


async def run_wait_task(game_data: GameData) -> None:
    """Runs a task that waits for a specified time and cancels if the condition is met.

    Parameters
    ----------
    game_data : GameData
        The game data object that may be updated if the voting condition is met.
    """
    timer = asyncio.create_task(asyncio.sleep(settings.vote_time))
    game_data.vote_task = timer
    await game_data.save()

    try:
        await timer
        return  # noqa: TRY300
    except asyncio.CancelledError:
        return


async def process_vote(callback: CallbackQuery, game_data: GameData) -> None:
    """Processes a user's vote and updates the game data accordingly.

    Parameters
    ----------
    callback : CallbackQuery
        The callback query containing the user's vote information.
    game_data : GameData
        The game data object to update with the vote.
    """
    player = callback.from_user

    if player not in game_data.order_list:
        await callback.answer("Вы не в игре.")
        return

    if player in game_data.voted_players:
        await callback.answer("Вы уже проголосовали.")
        return

    await register_vote(callback=callback, game_data=game_data)
    await send_confirmation_notification(callback=callback)

    if len(game_data.voted_players) == len(game_data.order_list):
        game_data.vote_task.cancel()  # type: ignore


async def process_vote_results(vote_msg: Message, game_data: GameData) -> None:
    """Processes and displays the results of the vote.

    Parameters
    ----------
    vote_msg : Message
        The message where the voting results will be displayed.
    game_data : GameData
        The game data object containing the voting results and player information.
    """
    await vote_msg.edit_text(text="Голосование завершено")
    await show_results(vote_msg, game_data)

    if game_data.votes:
        max_vote_count = max(set(game_data.votes.values()))
        if max_vote_count > len(game_data.order_list) / 2:
            player_for_kick_id = get_key(votes=game_data.votes, count=max_vote_count)
            player_for_kick = await get_user_by_id(chat_id=vote_msg.chat.id, user_id=int(player_for_kick_id))
            response_message = f"Большинство игроков считает, что шпионом является {get_user_mention(player_for_kick)}"
            await vote_msg.answer(text=response_message)

            game_data.order_list.remove(player_for_kick)
            if player_for_kick in game_data.spies:
                response_message = f"{get_user_mention(player_for_kick)} был шпионом!"
                game_data.spies.remove(player_for_kick)
            else:
                response_message = f"{get_user_mention(player_for_kick)} был работником!"

            await vote_msg.answer(text=response_message)
        else:
            await vote_msg.answer(text="Мнения игроков сильно разошлись - никто не будет выгнан")
    else:
        await vote_msg.answer(text="Все игроки решили воздержаться")

    if len(game_data.spies) == 0:
        await game_data.state.clear()
        await vote_msg.answer(text="Работники выиграли!")
    elif len(game_data.order_list) - len(game_data.spies) <= len(game_data.spies):
        await game_data.state.clear()
        spies_message = ""
        for spy in game_data.spies:
            spies_message += f"{get_user_mention(spy)} "
        response_message = f"Работники проиграли!\nШпионами были: {spies_message}"
        await vote_msg.answer(text=response_message)
    else:
        await game_data.state.set_state(GameStates.game)
        await game_data.save()
        response_message = f"Продолжаем игру!\n\n{game_data.count_workers_and_spies}"
        await vote_msg.answer(text=response_message)
