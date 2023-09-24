from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from database.engine import DBSession
from database.schemas import UforaCourse, UforaCourseAlias

__all__ = ["main"]


async def main():
    """Add the Ufora courses for the 2023-2024 academic year"""
    session: AsyncSession
    async with DBSession() as session:
        # # Remove Advanced Databases (which no longer exists)
        delete_stmt = delete(UforaCourse).where(UforaCourse.code == "E018441")
        await session.execute(delete_stmt)
        await session.commit()

        # Enable announcements for current courses
        select_stmt = select(UforaCourse).where(UforaCourse.compulsory & (UforaCourse.year == 5))
        second_master_courses: list[UforaCourse] = list((await session.execute(select_stmt)).scalars().all())

        for course in second_master_courses:
            course.log_announcements = True
            session.add(course)

        select_stmt = select(UforaCourse).where(UforaCourse.code == "C003711")
        comp_bio: UforaCourse = (await session.execute(select_stmt)).scalar_one()
        comp_bio.log_announcements = True
        session.add(comp_bio)

        await session.commit()

        # Fix IDs of courses
        select_stmt = select(UforaCourse).where(UforaCourse.code == "C004075")
        stage: UforaCourse = (await session.execute(select_stmt)).scalar_one()
        stage.course_id = 857878
        session.add(stage)

        select_stmt = select(UforaCourse).where(UforaCourse.code == "C002309A")
        thesis: UforaCourse = (await session.execute(select_stmt)).scalar_one()
        thesis.course_id = 828446
        session.add(thesis)

        await session.commit()

        # New elective courses
        bed_eco = UforaCourse(
            code="H001535", name="Bedrijfseconomie", year=6, compulsory=False, role_id=1155496199000952922
        )

        beg_eco = UforaCourse(
            code="D012144", name="Beginselen van economie", year=6, compulsory=False, role_id=1155495997024247948
        )

        big_data_tech = UforaCourse(
            code="E018240", name="Big Data Technology", year=6, compulsory=False, role_id=1155490114282201148
        )

        cloud_storage = UforaCourse(
            code="E017310", name="Cloud Storage and Computing", year=6, compulsory=False, role_id=1155490706849271841
        )

        criminologie = UforaCourse(
            code="B001623", name="Inleiding tot Criminologie", year=6, compulsory=False, role_id=1155486768477515936
        )

        data_quality = UforaCourse(
            code="E018700", name="Data Quality", year=6, compulsory=False, role_id=1155491028707586180
        )

        data_vis_ai = UforaCourse(
            code="E061370",
            name="Data Visualization for and with AI",
            year=6,
            compulsory=False,
            role_id=1155491854687686746,
        )

        db_design = UforaCourse(
            code="E018610", name="Database Design", year=6, compulsory=False, role_id=1155489846345875489
        )

        finance_markets = UforaCourse(
            code="F000093",
            name="Financiële Markten en Instellingen",
            year=6,
            compulsory=False,
            role_id=1155492815615299634,
        )

        game_theory = UforaCourse(
            code="E003710",
            name="Game Theory and Multiagent Systems",
            year=6,
            compulsory=False,
            role_id=1155488481666154506,
        )

        knowledge_graphs = UforaCourse(
            code="E018160", name="Knowledge Graphs", year=6, compulsory=False, role_id=1155491648323735592
        )

        natural_language_processing = UforaCourse(
            code="E061341", name="Natural Language Processing", year=6, compulsory=False, role_id=1155487540992823348
        )

        nosql = UforaCourse(
            code="E018130", name="NoSQL Databases", year=6, compulsory=False, role_id=1155491405955878973
        )

        secure_ss = UforaCourse(
            code="E017950", name="Secure Software and Systems", year=6, compulsory=False, role_id=1155492095281340467
        )

        session.add_all(
            [
                bed_eco,
                beg_eco,
                big_data_tech,
                cloud_storage,
                criminologie,
                data_quality,
                data_vis_ai,
                db_design,
                finance_markets,
                game_theory,
                knowledge_graphs,
                natural_language_processing,
                nosql,
                secure_ss,
            ]
        )

        await session.commit()

        # Aliases for new elective courses
        datakwaliteit = UforaCourseAlias(course_id=data_quality.course_id, alias="Datakwaliteit")
        devops = UforaCourseAlias(course_id=cloud_storage.course_id, alias="DevOps")
        nlp = UforaCourseAlias(course_id=natural_language_processing.course_id, alias="NLP")
        nlp_nl = UforaCourseAlias(course_id=natural_language_processing.course_id, alias="Natuurlijke Taalverwerking")

        session.add_all([datakwaliteit, devops, nlp, nlp_nl])

        await session.commit()
