from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from routers.helpers import GameData, GameStates, get_key, get_user_mention, process_remaining_players

reveal_process_router = Router(name="reveal_process")

reveal_process_router.message.filter(F.chat.type.in_({"group", "supergroup"}), GameStates.reveal)


@reveal_process_router.callback_query(F.data == "reveal_role")
async def init_reveal(callback: CallbackQuery, state: FSMContext) -> None:
    """Initializes the revealing process by setting the game state to reveal,
    sending the reveal user message, and start wait task.

    Parameters
    ----------
    callback : CallbackQuery
        The callback query containing the information to start the reveal process.
    state : FSMContext
        The state context used to manage the game state and data.
    """
    game_data = await GameData.init(state=state)
    player = callback.from_user
    player_num = get_key(game_data.order_dict, player)
    if player in game_data.spies:
        msg = f"{player_num}. {get_user_mention(player)} оказался шпионом!"
        await callback.message.answer(text=msg)

    else:
        msg = f"{player_num}. {get_user_mention(player)} был работником"
        await callback.message.answer(text=msg)
        await game_data.order_dict.pop(player_num)
        await process_remaining_players(message=callback.message, game_data=game_data)
