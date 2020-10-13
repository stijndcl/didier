from enum import Enum


class Ba1(Enum):
    Computergebruik = {"year": 1, "semester": 1, "id": 727820944478961685, "name": "Computergebruik"}
    Databanken = {"year": 1, "semester": 1, "id": 727823858660540466, "name": "Databanken"}
    Diwi = {"year": 1, "semester": 1, "id": 727824165989777478, "name": "Discrete Wiskunde"}
    Programmeren = {"year": 1, "semester": 1, "id": 727824450409594900, "name": "Programmeren"}
    RAF = {"year": 1, "semester": 1, "id": 727824527882715138, "name": "RAF"}
    AD1 = {"year": 1, "semester": 2, "id": 727828011407245322, "name": "AD 1"}
    Calculus = {"year": 1, "semester": 2, "id": 727827760566763601, "name": "Calculus"}
    LAM = {"year": 1, "semester": 2, "id": 727827533881409589, "name": "LAM"}
    OGProg = {"year": 1, "semester": 2, "id": 727827620548444160, "name": "Objectgericht Programmeren"}
    Scriptingtalen = {"year": 1, "semester": 2, "id": 727823849034350623, "name": "Scriptingtalen"}


class Ba2(Enum):
    AD2 = {"year": 2, "semester": 1, "id": 727877341539205190, "name": "AD 2"}
    CommNet = {"year": 2, "semester": 1, "id": 727879794892734531, "name": "Communicatienetwerken"}
    FuncProg = {"year": 2, "semester": 1, "id": 727879279622225920, "name": "Functioneel Programmeren"}
    StatProb = {"year": 2, "semester": 1, "id": 727879946458103880, "name": "Statistiek en Probabiliteit"}
    SysProg = {"year": 2, "semester": 1, "id": 727880036644028517, "name": "Systeemprogrammeren"}


years = [Ba1, Ba2]
