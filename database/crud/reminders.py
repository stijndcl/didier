from typing import Optional

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from database.crud.users import get_or_add_user
from database.enums import ReminderCategory
from database.schemas import Reminder

__all__ = ["get_all_reminders_for_category", "toggle_reminder"]


async def get_all_reminders_for_category(session: AsyncSession, category: ReminderCategory) -> list[Reminder]:
    """Get a list of all Reminders for a given category"""
    statement = select(Reminder).where(Reminder.category == category)
    return (await session.execute(statement)).scalars().all()


async def toggle_reminder(session: AsyncSession, user_id: int, category: ReminderCategory) -> bool:
    """Switch a category on/off

    Returns the new value for the category
    """
    await get_or_add_user(session, user_id)

    select_statement = select(Reminder).where(Reminder.user_id == user_id).where(Reminder.category == category)
    reminder: Optional[Reminder] = (await session.execute(select_statement)).scalar_one_or_none()

    # No reminder set yet
    if reminder is None:
        reminder = Reminder(user_id=user_id, category=category)
        session.add(reminder)
        await session.commit()

        return True

    # Reminder found -> delete it
    delete_statement = delete(Reminder).where(Reminder.reminder_id == reminder.reminder_id)
    await session.execute(delete_statement)
    await session.commit()

    return False
