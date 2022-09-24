from sqlalchemy.ext.asyncio import AsyncSession

from database.engine import DBSession
from database.schemas import UforaCourse, UforaCourseAlias

__all__ = ["main"]


async def main():
    """Add the Ufora courses for the 2022-2023 academic year"""
    session: AsyncSession
    async with DBSession() as session:
        """3rd Bachelor"""
        artificiele_intelligentie = UforaCourse(
            code="C003756",
            name="Artificiële Intelligentie",
            year=3,
            compulsory=True,
            role_id=891743671022673920,
            overarching_role_id=891743208248324196,
        )

        algoritmen_datastructuren_3 = UforaCourse(
            code="C003782",
            name="Algoritmen en Datastructuren 3",
            year=3,
            compulsory=True,
            role_id=891743791466307654,
            overarching_role_id=891743208248324196,
        )

        automaten_berekenbaarheid_complexiteit = UforaCourse(
            code="C003785",
            name="Automaten, Berekenbaarheid en Complexiteit",
            year=3,
            compulsory=True,
            role_id=891744082404200539,
            overarching_role_id=891743208248324196,
        )

        besturingssystemen = UforaCourse(
            code="E019010",
            name="Besturingssystemen",
            year=3,
            compulsory=True,
            role_id=891743898291032114,
            overarching_role_id=891743208248324196,
        )

        computationele_biologie = UforaCourse(
            code="C003789",
            name="Computationele Biologie",
            year=3,
            compulsory=True,
            role_id=891744050988847135,
            overarching_role_id=891743208248324196,
        )

        logisch_programmeren = UforaCourse(
            code="C003783",
            name="Logisch Programmeren",
            year=3,
            compulsory=True,
            role_id=891743966482034800,
            overarching_role_id=891743208248324196,
        )

        software_engineering_lab_2 = UforaCourse(
            code="C003784",
            name="Software Engineering Lab 2",
            year=3,
            compulsory=True,
            role_id=891744007300980737,
            overarching_role_id=891743208248324196,
        )

        modelleren_en_simuleren = UforaCourse(
            course_id=636139,
            code="C003786",
            name="Modelleren en Simuleren",
            year=3,
            compulsory=True,
            overarching_role_id=891744461405687808,
            log_announcements=True,
        )

        informatiebeveiliging = UforaCourse(
            code="E019400",
            name="Informatiebeveiliging",
            year=3,
            compulsory=True,
            role_id=1023333190678626314,
            overarching_role_id=891744461405687808,
            alternative_overarching_role_id=1023278462733127710,
        )

        parallelle_computersystemen = UforaCourse(
            code="E034140",
            name="Parallelle Computersystemen",
            year=3,
            compulsory=True,
            role_id=1023300295918358691,
            overarching_role_id=891744461405687808,
            alternative_overarching_role_id=1023278462733127710,
        )

        inleiding_tot_elektrotechniek = UforaCourse(
            code="C003806",
            name="Inleiding tot de Elektrotechniek",
            year=3,
            compulsory=True,
            overarching_role_id=891744390035415111,
        )

        inleiding_tot_telecommunicatie = UforaCourse(
            code="C003787",
            name="Inleiding tot de Telecommunicatie",
            year=3,
            compulsory=True,
            overarching_role_id=891744390035415111,
        )

        wiskundige_modellering = UforaCourse(
            code="C003788",
            name="Wiskundige Modellering in de Ingenieurswetenschappen",
            year=3,
            compulsory=True,
            overarching_role_id=891744390035415111,
        )

        session.add_all(
            [
                artificiele_intelligentie,
                algoritmen_datastructuren_3,
                automaten_berekenbaarheid_complexiteit,
                besturingssystemen,
                computationele_biologie,
                logisch_programmeren,
                software_engineering_lab_2,
                modelleren_en_simuleren,
                informatiebeveiliging,
                parallelle_computersystemen,
                inleiding_tot_elektrotechniek,
                inleiding_tot_telecommunicatie,
                wiskundige_modellering,
            ]
        )
        await session.commit()

        """Aliases"""
        ai = UforaCourseAlias(course_id=artificiele_intelligentie.course_id, alias="AI")
        ad3 = UforaCourseAlias(course_id=algoritmen_datastructuren_3.course_id, alias="AD3")
        abc = (UforaCourseAlias(course_id=automaten_berekenbaarheid_complexiteit.course_id, alias="ABC"),)
        bs = UforaCourseAlias(course_id=besturingssystemen.course_id, alias="BS")
        compbio = UforaCourseAlias(course_id=computationele_biologie.course_id, alias="Compbio")
        logprog = UforaCourseAlias(course_id=logisch_programmeren.course_id, alias="LogProg")
        prolog = UforaCourseAlias(course_id=logisch_programmeren.course_id, alias="Prolog")
        sel2 = UforaCourseAlias(course_id=software_engineering_lab_2.course_id, alias="SEL2")
        selab2 = UforaCourseAlias(course_id=software_engineering_lab_2.course_id, alias="SELab2")
        modsim = UforaCourseAlias(course_id=modelleren_en_simuleren.course_id, alias="ModSim")
        infosec = UforaCourseAlias(course_id=informatiebeveiliging.course_id, alias="InfoSec")
        information_security = UforaCourseAlias(course_id=informatiebeveiliging.course_id, alias="Information Security")
        pcs = UforaCourseAlias(course_id=parallelle_computersystemen.course_id, alias="PCS")
        parallel_computer_systems = UforaCourseAlias(
            parallelle_computersystemen.course_id, alias="Parallel Computer Systems"
        )
        elektro = UforaCourseAlias(course_id=inleiding_tot_elektrotechniek.course_id, alias="Elektro")
        elektrotechniek = UforaCourseAlias(course_id=inleiding_tot_elektrotechniek.course_id, alias="Elektrotechniek")
        telecom = UforaCourseAlias(course_id=inleiding_tot_telecommunicatie.course_id, alias="Telecom")
        wimo = UforaCourseAlias(course_id=wiskundige_modellering.course_id, alias="WiMo")

        session.add_all(
            [
                ai,
                ad3,
                abc,
                bs,
                compbio,
                logprog,
                prolog,
                sel2,
                selab2,
                modsim,
                infosec,
                information_security,
                pcs,
                parallel_computer_systems,
                elektro,
                elektrotechniek,
                telecom,
                wimo,
            ]
        )

        await session.commit()

        """1st Master CS"""
