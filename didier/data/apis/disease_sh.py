from aiohttp import ClientSession

from didier.data.embeds.disease_sh import CovidData
from didier.utils.http.requests import ensure_get

__all__ = ["get_country_info", "get_global_info"]


async def get_country_info(http_session: ClientSession, country: str) -> CovidData:
    """Fetch the info for a given country for today and yesterday"""
    endpoint = f"https://disease.sh/v3/covid-19/countries/{country}"

    params = {"yesterday": 0, "strict": 1, "allowNull": 0}
    async with ensure_get(http_session, endpoint, params=params) as response:
        today = response

    params["yesterday"] = 1
    async with ensure_get(http_session, endpoint, params=params) as response:
        yesterday = response

    data = {"today": today, "yesterday": yesterday}
    return CovidData.model_validate(data)


async def get_global_info(http_session: ClientSession) -> CovidData:
    """Fetch the global info for today and yesterday"""
    endpoint = "https://disease.sh/v3/covid-19/all"

    params = {"yesterday": 0, "allowNull": 0}
    async with ensure_get(http_session, endpoint, params=params) as response:
        today = response

    params["yesterday"] = 1
    async with ensure_get(http_session, endpoint, params=params) as response:
        yesterday = response

    data = {"today": today, "yesterday": yesterday}
    return CovidData.model_validate(data)
