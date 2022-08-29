from datetime import date, timedelta

import pytest
from freezegun import freeze_time
from sqlalchemy.ext.asyncio import AsyncSession

from database.crud import wordle as crud
from database.schemas import User, WordleGuess, WordleWord


@pytest.fixture
async def wordle_guesses(postgres: AsyncSession, user: User) -> list[WordleGuess]:
    """Fixture to generate some guesses"""
    guesses = []

    for guess in ["TEST", "WORDLE", "WORDS"]:
        guess = WordleGuess(user_id=user.user_id, guess=guess)
        postgres.add(guess)
        await postgres.commit()

        guesses.append(guess)

    return guesses


@pytest.mark.postgres
async def test_get_active_wordle_game_none(postgres: AsyncSession, user: User):
    """Test getting an active game when there is none"""
    result = await crud.get_active_wordle_game(postgres, user.user_id)
    assert not result


@pytest.mark.postgres
async def test_get_active_wordle_game(postgres: AsyncSession, wordle_guesses: list[WordleGuess]):
    """Test getting an active game when there is one"""
    result = await crud.get_active_wordle_game(postgres, wordle_guesses[0].user_id)
    assert result == wordle_guesses


@pytest.mark.postgres
async def test_get_daily_word_none(postgres: AsyncSession):
    """Test getting the daily word when the database is empty"""
    result = await crud.get_daily_word(postgres)
    assert result is None


@pytest.mark.postgres
@freeze_time("2022-07-30")
async def test_get_daily_word_not_today(postgres: AsyncSession):
    """Test getting the daily word when there is an entry, but not for today"""
    day = date.today() - timedelta(days=1)

    word = "testword"
    word_instance = WordleWord(word=word, day=day)
    postgres.add(word_instance)
    await postgres.commit()

    assert await crud.get_daily_word(postgres) is None


@pytest.mark.postgres
@freeze_time("2022-07-30")
async def test_get_daily_word_present(postgres: AsyncSession):
    """Test getting the daily word when there is one for today"""
    day = date.today()

    word = "testword"
    word_instance = WordleWord(word=word, day=day)
    postgres.add(word_instance)
    await postgres.commit()

    daily_word = await crud.get_daily_word(postgres)
    assert daily_word is not None
    assert daily_word.word == word


@pytest.mark.postgres
@freeze_time("2022-07-30")
async def test_set_daily_word_none_present(postgres: AsyncSession):
    """Test setting the daily word when there is none"""
    assert await crud.get_daily_word(postgres) is None
    word = "testword"
    await crud.set_daily_word(postgres, word)

    daily_word = await crud.get_daily_word(postgres)
    assert daily_word is not None
    assert daily_word.word == word


@pytest.mark.postgres
@freeze_time("2022-07-30")
async def test_set_daily_word_present(postgres: AsyncSession):
    """Test setting the daily word when there already is one"""
    word = "testword"
    await crud.set_daily_word(postgres, word)
    await crud.set_daily_word(postgres, "another word")

    daily_word = await crud.get_daily_word(postgres)
    assert daily_word is not None
    assert daily_word.word == word


@pytest.mark.postgres
@freeze_time("2022-07-30")
async def test_set_daily_word_force_overwrite(postgres: AsyncSession):
    """Test setting the daily word when there already is one, but "forced" is set to True"""
    word = "testword"
    await crud.set_daily_word(postgres, word)
    word = "anotherword"
    await crud.set_daily_word(postgres, word, forced=True)

    daily_word = await crud.get_daily_word(postgres)
    assert daily_word is not None
    assert daily_word.word == word


@pytest.mark.postgres
async def test_make_wordle_guess(postgres: AsyncSession, user: User):
    """Test making a guess in your current game"""
    test_user_id = user.user_id

    guess = "guess"
    await crud.make_wordle_guess(postgres, test_user_id, guess)
    wordle_guesses = await crud.get_active_wordle_game(postgres, test_user_id)
    assert list(map(lambda x: x.guess, wordle_guesses)) == [guess]

    other_guess = "otherguess"
    await crud.make_wordle_guess(postgres, test_user_id, other_guess)
    wordle_guesses = await crud.get_active_wordle_game(postgres, test_user_id)
    assert list(map(lambda x: x.guess, wordle_guesses)) == [guess, other_guess]


@pytest.mark.postgres
async def test_reset_wordle_games(postgres: AsyncSession, wordle_guesses: list[WordleGuess], user: User):
    """Test dropping the collection of active games"""
    test_user_id = user.user_id

    assert await crud.get_active_wordle_game(postgres, test_user_id)
    await crud.reset_wordle_games(postgres)
    assert not await crud.get_active_wordle_game(postgres, test_user_id)
