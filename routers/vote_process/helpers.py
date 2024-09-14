from typing import Any, Dict

from aiogram.types import CallbackQuery, Message

from routers.game_states import GameData, GameStates
from routers.helpers import get_user_mention


async def register_vote(callback: CallbackQuery, game_data: GameData) -> None:
    """Registers a vote from a user in the game data.

    Parameters
    ----------
    callback : CallbackQuery
        The callback query containing the user information and vote data.
    game_data : GameData
        The game data object to update with the vote.
    """
    game_data.voted_players.add(callback.from_user)

    if callback.data in game_data.votes:
        game_data.votes[callback.data] += 1
    else:
        game_data.votes[callback.data] = 1
    await game_data.save()


async def send_confirmation_notification(callback: CallbackQuery, game_data: GameData) -> None:
    """Sends a confirmation notification to the user who cast the vote.

    Parameters
    ----------
    callback : CallbackQuery
        The callback query containing the information about the vote.

    game_data : GameData
        The GameData object with turns order dict
    """
    callback_answer = f"Ваш голос за игрока {game_data.order_dict[int(callback.data)].first_name} учтен"
    await callback.answer(callback_answer)
    message_answer = (
        f"{get_key(game_data.order_dict, callback.from_user)}. {get_user_mention(callback.from_user)} " "сделал выбор"
    )
    await callback.message.answer(message_answer)


async def show_results(vote_msg: Message, game_data: GameData) -> None:
    """Shows the results of the voting process.

    Parameters
    ----------
    vote_msg : Message
        The message where the voting results will be sent.
    game_data : GameData
        The game data object containing the voting results.
    """
    vote_results: str = ""
    if game_data.votes:
        for player_num, count in game_data.votes.items():
            voted_for = game_data.order_dict[int(player_num)]
            vote_results += f"\n{player_num}. {get_user_mention(voted_for)}: {count}"
        await vote_msg.answer(f"Результаты голосования:\n{vote_results}")
    else:
        await vote_msg.answer("Никто не выбрал кандидата в шпионы")


def get_key(dictionary: Dict, value: Any) -> Any:  #  noqa: ANN401
    """Finds the player key with the specified value."""
    for player_id, votes_count in dictionary.items():
        if votes_count == value:
            return player_id
    return None


async def process_votes(vote_msg: Message, game_data: GameData) -> None:
    """Process the voting results and determine if a player should be removed from the game.

    This function processes the results of a vote among players. It checks if any player has received
    more than half of the total votes, and if so, the player is removed from the game. If the player
    was a spy, it notifies the group. If the vote results are inconclusive or no votes were cast,
    it also handles these cases by sending appropriate messages to the chat.

    Parameters
    ----------
    vote_msg : Message
        The message object representing the voting message in the chat.

    game_data : GameData
        The current game state object containing information about players, votes, and spies.
    """
    if game_data.votes:
        max_vote_count = max(set(game_data.votes.values()))
        if max_vote_count > len(game_data.order_dict) / 2:
            await kick_user(vote_msg, game_data, max_vote_count)
        else:
            await vote_msg.answer(text="Мнения игроков сильно разошлись - никто не будет выгнан")
    else:
        await vote_msg.answer(text="Все игроки решили воздержаться")


async def kick_user(vote_msg: Message, game_data: GameData, max_vote_count: int) -> None:
    """Kick the player who received the most votes from the game and notify the group.

    This function identifies the player who received the highest number of votes and removes them
    from the game. It then informs the group whether the removed player was a spy or a regular worker.
    The function uses the `game_data` to determine the player and sends a message with the results
    of the vote to the chat.

    Parameters
    ----------
    vote_msg : Message
        The message object representing the voting message in the chat.

    game_data : GameData
        The current state of the game, which contains information about the players, votes, and spies.

    max_vote_count : int
        The highest number of votes received by a player.
    """
    player_for_kick_id = get_key(dictionary=game_data.votes, value=max_vote_count)
    player_for_kick = game_data.order_dict[int(player_for_kick_id)]
    response_message = (
        f"Большинство игроков считает, что шпионом является {player_for_kick_id}. {get_user_mention(player_for_kick)}"
    )
    await vote_msg.answer(text=response_message)

    game_data.order_dict.pop(int(player_for_kick_id))
    if player_for_kick in game_data.spies:
        response_message = f"{player_for_kick_id}. {get_user_mention(player_for_kick)} был шпионом!"
        game_data.spies.remove(player_for_kick)
    else:
        response_message = f"{player_for_kick_id}. {get_user_mention(player_for_kick)} был работником!"

    await vote_msg.answer(text=response_message)


async def process_remaining_players(vote_msg: Message, game_data: GameData) -> None:
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
        await vote_msg.answer(text="Работники выиграли!")
    elif len(game_data.order_dict) - len(game_data.spies) <= len(game_data.spies):
        await game_data.state.clear()
        spies_message = ""
        for spy in game_data.spies:
            spies_message += f"{get_user_mention(spy)} "
        response_message = (
            f"Ничья. Работники не смогли вычислить шпионов, а шпионы определить локацию\nШпионами были: {spies_message}"
        )
        await vote_msg.answer(text=response_message)
    else:
        await game_data.state.set_state(GameStates.game)
        await game_data.save()
        response_message = f"Продолжаем игру!\n\n{game_data.count_workers_and_spies}"
        await vote_msg.answer(text=response_message)
