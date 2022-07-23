from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Bank, NightlyData, User

__all__ = [
    "get_or_add",
]


async def get_or_add(session: AsyncSession, user_id: int, *, options: Optional[list] = None) -> User:
    """Get a user's profile

    If it doesn't exist yet, create it (along with all linked datastructures)
    """
    if options is None:
        options = []

    statement = select(User).where(User.user_id == user_id).options(*options)

    user: Optional[User] = (await session.execute(statement)).scalar_one_or_none()

    # User exists
    if user is not None:
        return user

    # Create new user
    user = User(user_id=user_id)
    session.add(user)
    await session.commit()

    # Add bank & nightly info
    bank = Bank(user_id=user_id)
    nightly_data = NightlyData(user_id=user_id)
    user.bank = bank
    user.nightly_data = nightly_data

    session.add(bank)
    session.add(nightly_data)
    session.add(user)

    await session.commit()
    await session.refresh(user)

    return user
