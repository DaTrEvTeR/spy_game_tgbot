from aiogram.types import CallbackQuery

from routers.helpers import GameData, get_key, get_user_mention, process_remaining_players
from routers.reveal_process.keyboards import locations


async def process_spy_answer(callback: CallbackQuery, game_data: GameData) -> None:
    """Processes the spy's answer and checks whether they guessed the game's location correctly.

    If the spy guesses correctly, it announces their victory and clears the game state. If the spy guesses incorrectly,
    it removes the spy from the game and continues with the remaining players.

    Parameters
    ----------
    callback : CallbackQuery
        The callback query object from aiogram that contains information about the interaction.
    game_data : GameData
        The GameData object that holds all the current game-related data, including players, locations, and game state.
    """
    player_order_num = get_key(dictionary=game_data.order_dict, value=callback.from_user)
    if game_data.possible_locations[int(callback.data)] == game_data.game_loc:
        await callback.message.answer(
            text=(
                f"Шпион {get_user_mention(callback.from_user)} правильно отгадал локацию '{game_data.game_loc}'"
                "\n\nРаботники проиграли"
            )
        )
        await game_data.state.clear()
        return

    await callback.message.answer(
        text=f"Шпион {get_user_mention(callback.from_user)} не отгадал локацию и исключается из игры"
    )
    game_data.order_dict.pop(int(player_order_num))
    game_data.spies.remove(callback.from_user)
    await game_data.save()
    await process_remaining_players(callback.message, game_data)


async def process_reveal_command(callback: CallbackQuery, game_data: GameData) -> None:
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
