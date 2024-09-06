from random import choice, shuffle

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, User

from core.settings import settings
from routers.game_process.keyboards import my_role
from routers.game_states import GameData, GameStates
from routers.helpers import get_str_players_list

router = Router(name="game_process")

router.message.filter(F.chat.type.in_({"group", "supergroup"}), GameStates.game)


@router.callback_query(F.data == "init_game")
async def init_game(callback: CallbackQuery, state: FSMContext) -> None:
    """Initializes the game by assigning spies and setting the turn order.

    This function is triggered when the "init_game" callback query is received.
    It sets the game state to active, assigns spies randomly, and determines the
    order in which players will take turns.

    Parameters
    ----------
    callback : CallbackQuery
        The callback query triggered when the game is initialized.
    state : FSMContext
        The current finite state machine context, used to manage game data.

    """
    game_data = await GameData.init(state=state)
    await game_data.state.set_state(GameStates.game)
    game_data.spies = set_spies(game_data)
    game_data.order_list = set_players_order(game_data)
    await game_data.save()
    await callback.message.answer(
        f"Участники:\n{get_str_players_list(game_data.players)}\nШпионов среди них: {len(game_data.spies)}",
        reply_markup=my_role,
    )


def set_players_order(game_data: GameData) -> list[User]:
    """Shuffles and returns the list of players to define the turn order.

    Parameters
    ----------
    game_data : GameData
        The current game data containing the list of players.

    Returns:
    -------
    list[User]
        A shuffled list of players representing the order in which they will take turns.
    """
    order: list[User] = list(game_data.players)
    shuffle(order)
    return order


def set_spies(game_data: GameData) -> set[User]:
    """Randomly selects spies from the list of players.

    The number of spies is determined by dividing the total number of players by the
    minimal player count setting.

    Parameters
    ----------
    game_data : GameData
        The current game data containing the list of players.

    Returns:
    -------
    set[User]
        A set of users who have been selected as spies.
    """
    count_of_spies: int = len(game_data.players) // settings.minimal_player_count
    players_list = list(game_data.players.copy())
    spies = set()
    for _ in range(count_of_spies):
        spy = choice(players_list)
        spies.add(spy)
        players_list.remove(spy)
    return spies


@router.callback_query(F.data == "my_role")
async def check_role(callback: CallbackQuery, state: FSMContext) -> None:
    """Informs the player of their role (spy or regular player) when they check their role.

    This function is triggered when the "my_role" callback query is received. It checks
    if the player is a spy or a regular player and sends a response accordingly.

    Parameters
    ----------
    callback : CallbackQuery
        The callback query triggered when a player requests to see their role.
    state : FSMContext
        The current finite state machine context, used to manage game data.
    """
    game_data = await GameData.init(state=state)
    if callback.from_user in game_data.spies:
        await callback.answer(
            text=(
                "Вы шпион"
                "\nЗадавайте вопросы осторожно и внимательно читайте ответы игроков, вам нужно вычислить локацию"
                "\nКак только будете уверенны в ответе пропишите команду /guess"
            ),
            show_alert=True,
        )
    else:
        await callback.answer(
            text=(
                "Вы сотрудник"
                "\nЗадавайте вопросы осторожно и внимательно читайте ответы игроков, вам нужно определить кто шпион"
                "\nКак только будете уверенны в ответе пропишите команду /vote"
            ),
            show_alert=True,
        )
