from requests import get
from urllib.parse import urlencode
from bs4 import BeautifulSoup

# TODO add Football requests in here as well


def google_search(query):
    """
    Function to get Google search results
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36'
    }

    query = urlencode({"q": query})

    resp = get("https://www.google.com/search?{}&num=10&hl=en".format(query), headers=headers)
    print("got here")
    if resp.status_code != 200:
        return None, resp.status_code

    bs = BeautifulSoup(resp.text, "html.parser")

    def getContent(element):
        link = element.find('a', href=True)
        title = element.find('h3')
        return link, title

    divs = bs.find_all('div', attrs={'class': 'g'})
    print(divs)
    return list(getContent(d) for d in divs), 200
