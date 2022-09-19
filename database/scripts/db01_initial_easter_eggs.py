from sqlalchemy.ext.asyncio import AsyncSession

from database.engine import DBSession
from database.schemas import EasterEgg

__all__ = ["main"]


async def main():
    """Add the initial easter egg responses"""
    session: AsyncSession
    async with DBSession() as session:
        # https://www.youtube.com/watch?v=Vd6hVYkkq88
        do_not_cite_deep_magic = EasterEgg(
            match=r"((don'?t)|(do not)) cite the deep magic to me,? witch",
            response="_I was there when it was written_",
            exact=True,
        )

        # https://www.youtube.com/watch?v=LrHTR22pIhw
        dormammu = EasterEgg(match=r"dormammu", response="_I've come to bargain_", exact=True)

        # https://youtu.be/rEq1Z0bjdwc?t=7
        hello_there = EasterEgg(match=r"hello there", response="_General Kenobi_", exact=True)

        # https://www.youtube.com/watch?v=_WZCvQ5J3pk
        hey = EasterEgg(
            match=r"hey,? ?(?:you)?",
            response="_You're finally awake!_",
            exact=True,
        )

        # https://www.youtube.com/watch?v=2z5ZDC1eQEA
        is_this_the_kk = EasterEgg(
            match=r"is (this|dis) (.*)", response="No, this is Patrick.", exact=False, startswith=True
        )

        # https://youtu.be/d6uckPRKvSg?t=4
        its_over_anakin = EasterEgg(
            match=r"it'?s over ", response="_I have the high ground_", exact=False, startswith=True
        )

        # https://www.youtube.com/watch?v=Vx5prDjKAcw
        perfectly_balanced = EasterEgg(match=r"perfectly balanced", response="_As all things should be_", exact=True)

        # ( ͡◉ ͜ʖ ͡◉)
        sixty_nine = EasterEgg(match=r"(^69$)|(^69 )|( 69 )|( 69$)", response="_Nice_", exact=False, startswith=False)

        # https://youtu.be/7mbLzkNFDs8?t=19
        what_did_it_cost = EasterEgg(match=r"what did it cost\??", response="_Everything_", exact=True)

        # https://youtu.be/EJfYh-JVbJA?t=10
        you_cant_defeat_me = EasterEgg(match=r"you can'?t defeat me", response="_I know, but he can_", exact=False)

        session.add_all(
            [
                do_not_cite_deep_magic,
                dormammu,
                hello_there,
                hey,
                is_this_the_kk,
                its_over_anakin,
                perfectly_balanced,
                sixty_nine,
                what_did_it_cost,
                you_cant_defeat_me,
            ]
        )
        await session.commit()
