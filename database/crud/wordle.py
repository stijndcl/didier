import datetime
from typing import Optional

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from database.schemas import WordleGuess, WordleWord

__all__ = [
    "get_active_wordle_game",
    "make_wordle_guess",
    "set_daily_word",
    "reset_wordle_games",
]


async def get_active_wordle_game(session: AsyncSession, user_id: int) -> list[WordleGuess]:
    """Find a player's active game"""
    statement = select(WordleGuess).where(WordleGuess.user_id == user_id)
    guesses = (await session.execute(statement)).scalars().all()
    return guesses


async def make_wordle_guess(session: AsyncSession, user_id: int, guess: str):
    """Make a guess in your current game"""
    guess_instance = WordleGuess(user_id=user_id, guess=guess)
    session.add(guess_instance)
    await session.commit()


async def get_daily_word(session: AsyncSession) -> Optional[WordleWord]:
    """Get the word of today"""
    statement = select(WordleWord).where(WordleWord.day == datetime.date.today())
    row = (await session.execute(statement)).scalar_one_or_none()

    if row is None:
        return None

    return row


async def set_daily_word(session: AsyncSession, word: str, *, forced: bool = False) -> str:
    """Set the word of today

    This does NOT overwrite the existing word if there is one, so that it can safely run
    on startup every time.

    In order to always overwrite the current word, set the "forced"-kwarg to True.

    Returns the word that was chosen. If one already existed, return that instead.
    """
    current_word = await get_daily_word(session)

    if current_word is None:
        current_word = WordleWord(word=word, day=datetime.date.today())
        session.add(current_word)
        await session.commit()

        # Remove all active games
        await reset_wordle_games(session)
    elif forced:
        current_word.word = word
        current_word.day = datetime.date.today()
        session.add(current_word)
        await session.commit()

        # Remove all active games
        await reset_wordle_games(session)

    return current_word.word


async def reset_wordle_games(session: AsyncSession):
    """Reset all active games"""
    statement = delete(WordleGuess)
    await session.execute(statement)
