import logging

from aiogram import Bot, F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from core.settings import settings
from routers.start_game.keyboards import reg
from routers.start_game.states import GameStates

router = Router(name="start_game")
router.message.filter(
    F.chat.type.in_({"group", "supergroup"}),
)


@router.message(Command(settings.start_game_command))
async def registration_for_the_game(message: Message, state: FSMContext) -> None:
    """Start registration for the game.
    Give `settings.registration_time` min for registration.
    If there are less players than `settings.minimal_player_count` cancel the game,
    otherwise start the game process.

    Parameters
    ----------
    message : Message
        Message with command /{settings.start_game_command}
    """
    cur_state = await state.get_state()
    if cur_state == GameStates.game.state:
        await message.answer("Игра уже идет!")
    elif cur_state == GameStates.registration.state:
        await message.answer("Регистрация уже началась!")
    else:
        await state.set_state(GameStates.registration)
        await state.update_data(players=set())
        await message.answer(
            text="Началась регистрация на игру",
            reply_markup=reg,
        )


@router.callback_query(F.data == "reg")
async def register_user(callback: CallbackQuery, state: FSMContext) -> None:
    """Handle callback data "reg".

    Parameters
    ----------
    callback : CallbackQuery
        Callback with data "reg"
    """
    data = await state.get_data()
    players: set = data.get("players", set())
    user_id = callback.from_user.id
    if user_id not in players:
        players.add(user_id)
        await state.update_data(players=players)
        await callback.answer("Вы присоединились к игре! Для отмены нажмите кнопку 'Присоединиться' еще раз")
        logging.info(
            f"User {callback.from_user.username} - {callback.from_user.full_name} "
            f"- {callback.from_user.id} joined the game"
        )
    else:
        players.remove(user_id)
        await state.update_data(players=players)
        await callback.answer("Вы покинули игру!")
        logging.info(
            f"User {callback.from_user.username} - {callback.from_user.full_name} "
            f"- {callback.from_user.id} left the game"
        )


@router.callback_query(F.data == "rules")
async def show_rules(callback: CallbackQuery, bot: Bot) -> None:
    """Handle callback data "rules".

    Parameters
    ----------
    callback : CallbackQuery
        Callback with data "rules"
    """
    await callback.answer(
        text="Правила отправлены вам в лс",
        show_alert=True,
    )
    await bot.send_message(
        chat_id=callback.from_user.id,
        text=settings.game_rules,
    )
