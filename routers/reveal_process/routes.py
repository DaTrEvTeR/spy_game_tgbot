from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from routers.helpers import GameData, GameStates, get_key, get_user_mention, process_remaining_players
from routers.reveal_process.keyboards import locations

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
        await callback.message.answer(text=f"{player_num}. {get_user_mention(player)} оказался шпионом!")
        game_data.reaveled_spy = callback.from_user
        await game_data.save()
        pos_locs = ""
        for num, loc in game_data.possible_locations.items():
            pos_locs += f"{num}. {loc}\n"
        await callback.message.answer(
            text=f"Список возможных локаций:\n\n{pos_locs}\n{get_user_mention(player)} выбирает:",
            reply_markup=locations(list(game_data.possible_locations.keys())),
        )

    else:
        msg = f"{player_num}. {get_user_mention(player)} был работником"
        await callback.message.answer(text=msg)
        game_data.order_dict.pop(player_num)
        await game_data.save()
        await process_remaining_players(message=callback.message, game_data=game_data)


@reveal_process_router.callback_query()
async def spy_answer(callback: CallbackQuery, state: FSMContext) -> None:
    """_summary_.

    Parameters
    ----------
    callback : CallbackQuery
        _description_
    state : FSMContext
        _description_
    """
    game_data = await GameData.init(state=state)

    if callback.from_user != game_data.reaveled_spy:
        return await callback.answer("Сейчас не ваш ход!")

    player_id = get_key(dictionary=game_data.order_dict, value=callback.from_user)
    if game_data.possible_locations[int(callback.data)] == game_data.game_loc:
        await callback.message.answer(
            text=(
                f"Шпион {get_user_mention(callback.from_user)} правильно отгадал локацию '{game_data.game_loc}'"
                "\n\nРаботники проиграли"
            )
        )
        await game_data.state.clear()
        return None
    await callback.message.answer(
        text=f"Шпион {get_user_mention(callback.from_user)} не отгадал локацию и исключается из игры"
    )
    game_data.order_dict.pop(int(player_id))
    game_data.spies.remove(callback.from_user)
    await process_remaining_players(callback.message, game_data)
    return None
