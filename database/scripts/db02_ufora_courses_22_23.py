from sqlalchemy.ext.asyncio import AsyncSession

from database.engine import DBSession
from database.schemas import UforaCourse, UforaCourseAlias

__all__ = ["main"]


async def main():
    """Add the Ufora courses for the 2022-2023 academic year

    Course id's are only used to fetch announcements, and I can only fetch announcements of courses I enroll in,
    so other courses can use an auto-generated id

    This will never clash as there will never be 650k regular courses
    """
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
        abc = UforaCourseAlias(course_id=automaten_berekenbaarheid_complexiteit.course_id, alias="ABC")
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
            course_id=parallelle_computersystemen.course_id, alias="Parallel Computer Systems"
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
        fundamenten_van_programmeertalen = UforaCourse(
            course_id=633639,
            code="C003241",
            name="Fundamenten van Programmeertalen",
            year=4,
            compulsory=True,
            role_id=1023298665416228876,
            overarching_role_id=1023293447387496570,
        )

        machine_learning = UforaCourse(
            course_id=630807,
            code="C003758",
            name="Machine Learning",
            year=4,
            compulsory=True,
            role_id=1023294041825235087,
            overarching_role_id=1023293447387496570,
        )

        parallelle_en_gedistribueerde = UforaCourse(
            course_id=633583,
            code="E017930",
            name="Parallelle en Gedistribueerde Softwaresystemen",
            year=4,
            compulsory=True,
            role_id=1023293978273136700,
            overarching_role_id=1023293447387496570,
            alternative_overarching_role_id=1023278462733127710,
        )

        discrete_algoritmen = UforaCourse(
            course_id=633675,
            code="C003349",
            name="Discrete Algoritmen",
            year=4,
            compulsory=True,
            role_id=1023299229277487145,
            overarching_role_id=1023293447387496570,
        )

        software_engineering_lab_3 = UforaCourse(
            course_id=631370,
            code="C004072",
            name="Software Engineering Lab 3",
            year=4,
            compulsory=True,
            role_id=1023299234008678550,
            overarching_role_id=1023293447387496570,
        )

        compilers = UforaCourse(
            course_id=633663,
            code="E018520",
            name="Compilers",
            year=4,
            compulsory=True,
            role_id=1023299237003399249,
            overarching_role_id=1023293447387496570,
        )

        datavisualisatie = UforaCourse(
            course_id=630803,
            code="C004041",
            name="Datavisualisatie",
            year=4,
            compulsory=True,
            role_id=1023299239243161671,
            overarching_role_id=1023293447387496570,
        )

        recht_van_intellectuele_eigendom = UforaCourse(
            course_id=633696,
            code="C000957",
            name="Recht van de Intellectuele Eigendom",
            year=4,
            compulsory=True,
            role_id=1023299241457745930,
            overarching_role_id=1023293447387496570,
        )

        """2nd Master CS"""
        computergrafiek = UforaCourse(
            code="C004073",
            name="Computergrafiek",
            year=5,
            compulsory=True,
            role_id=1023303199609860268,
            overarching_role_id=1023293447387496570,
        )

        big_data_science = UforaCourse(
            code="C004074",
            name="Big Data Science",
            year=5,
            compulsory=True,
            role_id=1023303190046851153,
            overarching_role_id=1023293447387496570,
        )

        bedrijfsstage = UforaCourse(
            code="C004075",
            name="Bedrijfsstage",
            year=5,
            compulsory=True,
            role_id=1023303201807679598,
            overarching_role_id=1023293447387496570,
        )

        masterproef = UforaCourse(
            code="C002309",
            name="Masterproef",
            year=5,
            compulsory=True,
            role_id=1023319264851144754,
            overarching_role_id=1023293447387496570,
            alternative_overarching_role_id=1023300434800164914,
        )

        """1st Master CSE"""
        design_of_multimedia_applications = UforaCourse(
            code="E017920",
            name="Design of Multimedia Applications",
            year=4,
            compulsory=True,
            role_id=1023300418635317259,
            overarching_role_id=1023278462733127710,
        )

        research_project = UforaCourse(
            code="E031710",
            name="Research Project",
            year=4,
            compulsory=True,
            role_id=1023300421776855160,
            overarching_role_id=1023278462733127710,
        )

        design_project = UforaCourse(
            code="E033710",
            name="Design Project",
            year=4,
            compulsory=True,
            role_id=1023300424561852537,
            overarching_role_id=1023278462733127710,
        )

        mobile_and_broadband_access_networks = UforaCourse(
            code="E012320",
            name="Mobile and Broadband Access Networks",
            year=4,
            compulsory=True,
            role_id=1023300427246223471,
            overarching_role_id=1023278462733127710,
        )

        information_theory = UforaCourse(
            code="E003600",
            name="Information Theory",
            year=4,
            compulsory=True,
            role_id=1023300429469204480,
            overarching_role_id=1023278462733127710,
        )

        queueing_analysis_and_simulation = UforaCourse(
            code="E011322",
            name="Queueing Analysis and Simulation",
            year=4,
            compulsory=True,
            role_id=1023300431696371793,
            overarching_role_id=1023278462733127710,
        )

        session.add_all(
            [
                fundamenten_van_programmeertalen,
                machine_learning,
                parallelle_en_gedistribueerde,
                discrete_algoritmen,
                software_engineering_lab_3,
                compilers,
                datavisualisatie,
                recht_van_intellectuele_eigendom,
                computergrafiek,
                big_data_science,
                bedrijfsstage,
                masterproef,
                design_of_multimedia_applications,
                research_project,
                design_project,
                mobile_and_broadband_access_networks,
                information_theory,
                queueing_analysis_and_simulation,
            ]
        )

        await session.commit()

        """Master aliases"""
        fundamenten = UforaCourseAlias(course_id=fundamenten_van_programmeertalen.course_id, alias="Fundamenten")
        ml = UforaCourseAlias(course_id=machine_learning.course_id, alias="ML")
        pds = UforaCourseAlias(course_id=parallelle_en_gedistribueerde.course_id, alias="PDS")
        parallel_and_distributed = UforaCourseAlias(
            course_id=parallelle_en_gedistribueerde.course_id, alias="Parallel and Distributed Software Systems"
        )
        da = UforaCourseAlias(course_id=discrete_algoritmen.course_id, alias="DA")
        discalg = UforaCourseAlias(course_id=discrete_algoritmen.course_id, alias="DiscAlg")
        sel3 = UforaCourseAlias(course_id=software_engineering_lab_3.course_id, alias="SEL3")
        selab3 = UforaCourseAlias(course_id=software_engineering_lab_3.course_id, alias="SELab3")
        dv = UforaCourseAlias(course_id=datavisualisatie.course_id, alias="DV")
        datavis = UforaCourseAlias(course_id=datavisualisatie.course_id, alias="DataVis")
        recht = UforaCourseAlias(course_id=recht_van_intellectuele_eigendom.course_id, alias="Recht")
        computer_graphics = UforaCourseAlias(course_id=computergrafiek.course_id, alias="Computer Graphics")
        stage = UforaCourseAlias(course_id=bedrijfsstage.course_id, alias="Stage")
        thesis = UforaCourseAlias(course_id=masterproef.course_id, alias="Thesis")

        session.add_all(
            [
                fundamenten,
                ml,
                pds,
                parallel_and_distributed,
                da,
                discalg,
                sel3,
                selab3,
                dv,
                datavis,
                recht,
                computer_graphics,
                stage,
                thesis,
            ]
        )

        await session.commit()

        """Elective master's courses"""
        aanbevelingssystemen = UforaCourse(
            course_id=635444,
            code="E018230",
            name="Aanbevelingssystemen",
            year=6,
            compulsory=False,
            role_id=1023303206572404817,
        )
        algoritmische_grafentheorie = UforaCourse(
            code="C000145", name="Algoritmische Grafentheorie", year=6, compulsory=False, role_id=1023304281094373436
        )
        artificial_intelligence = UforaCourse(
            code="E016330", name="Artificial Intelligence", year=6, compulsory=False, role_id=1023304874789703741
        )
        berekenbaarheid_en_complexiteit = UforaCourse(
            code="C000627",
            name="Berekenbaarheid en Complexiteit",
            year=6,
            compulsory=False,
            role_id=1023304692861784064,
        )
        capita_selecta_bio = UforaCourse(
            code="C004122",
            name="Capita Selecta in Bioinformatics",
            year=6,
            compulsory=False,
            role_id=1023305177727504444,
        )
        causal_machine_learning = UforaCourse(
            code="C004413", name="Causal Machine Learning", year=6, compulsory=False, role_id=1023304690491985961
        )
        computational_challenges = UforaCourse(
            code="C003711",
            name="Computational Challenges in Bioinformatics",
            year=6,
            compulsory=False,
            role_id=1023304283413811411,
        )
        computeralgebra = UforaCourse(
            code="C001026", name="Computeralgebra", year=6, compulsory=False, role_id=1023304697928495164
        )
        computervisie = UforaCourse(
            code="E736020", name="Computervisie", year=6, compulsory=False, role_id=1023304274945511575
        )
        context_and_nuance = UforaCourse(
            code="A005503",
            name="Context and Nuance: A Critical Reflection on Current Topics",
            year=6,
            compulsory=False,
            role_id=1023304898252648470,
        )
        deep_learning = UforaCourse(
            code="F000918", name="Deep Learning", year=6, compulsory=False, role_id=1023304893672464474
        )
        economie = UforaCourse(code="F000758", name="Economie", year=6, compulsory=False, role_id=1023305174506291290)
        geavanceerde_databanken = UforaCourse(
            code="E018441", name="Geavanceerde Databanken", year=6, compulsory=False, role_id=1023304259913134130
        )
        gevorderde_numerieke_methoden = UforaCourse(
            code="C004011", name="Gevorderde Numerieke Methoden", year=6, compulsory=False, role_id=1023304278410002482
        )
        gevorderd_wetenschappelijk_engels = UforaCourse(
            code="A003107",
            name="Gevorderd wetenschappelijk Engels",
            year=6,
            compulsory=False,
            role_id=1023305170987257898,
        )
        internet_of_things = UforaCourse(
            code="E019170", name="Internet of Things", year=6, compulsory=False, role_id=1023304695416111224
        )
        medical_imaging = UforaCourse(
            code="E010371", name="Medical Imaging", year=6, compulsory=False, role_id=1023304900555317399
        )
        robotica = UforaCourse(
            course_id=634368, code="E019370", name="Robotica", year=6, compulsory=False, role_id=1023303205360246904
        )
        software_hacking = UforaCourse(
            course_id=635436,
            code="E017941",
            name="Softwarehacking en -Protectie",
            year=6,
            compulsory=False,
            role_id=1023303203913211905,
        )
        spraakverwerking = UforaCourse(
            code="E010220", name="Spraakverwerking", year=6, compulsory=False, role_id=1023304686704533576
        )
        sustainable_computing = UforaCourse(
            code="E034500", name="Sustainable Computing", year=6, compulsory=False, role_id=1023304895421481081
        )

        session.add_all(
            [
                aanbevelingssystemen,
                algoritmische_grafentheorie,
                artificial_intelligence,
                berekenbaarheid_en_complexiteit,
                capita_selecta_bio,
                causal_machine_learning,
                computational_challenges,
                computeralgebra,
                computervisie,
                context_and_nuance,
                deep_learning,
                economie,
                geavanceerde_databanken,
                gevorderde_numerieke_methoden,
                gevorderd_wetenschappelijk_engels,
                internet_of_things,
                medical_imaging,
                robotica,
                software_hacking,
                spraakverwerking,
                sustainable_computing,
            ]
        )

        await session.commit()

        recommender_systems = UforaCourseAlias(course_id=aanbevelingssystemen.course_id, alias="Recommender Systems")
        cv = UforaCourseAlias(course_id=computervisie.course_id, alias="CV")
        comp_vis = UforaCourseAlias(course_id=computervisie.course_id, alias="CompVis")
        computer_vision = UforaCourseAlias(course_id=computervisie.course_id, alias="Computer Vision")
        context = UforaCourseAlias(course_id=context_and_nuance.course_id, alias="Context")
        eco = UforaCourseAlias(course_id=economie.course_id, alias="Eco")
        advanced_databases = UforaCourseAlias(course_id=geavanceerde_databanken.course_id, alias="Advanced Databases")
        advanced_academic_english = UforaCourseAlias(
            course_id=gevorderd_wetenschappelijk_engels.course_id, alias="Advanced Academic English"
        )
        iot = UforaCourseAlias(course_id=internet_of_things.course_id, alias="IoT")
        robotics = UforaCourseAlias(course_id=robotica.course_id, alias="Robotics")
        software_hacking_en = UforaCourseAlias(
            course_id=software_hacking.course_id, alias="Software Hacking and Protection"
        )
        speech_processing = UforaCourseAlias(course_id=spraakverwerking.course_id, alias="Speech Processing")

        session.add_all(
            [
                recommender_systems,
                cv,
                comp_vis,
                computer_vision,
                context,
                eco,
                advanced_databases,
                advanced_academic_english,
                iot,
                robotics,
                software_hacking_en,
                speech_processing,
            ]
        )

        await session.commit()
