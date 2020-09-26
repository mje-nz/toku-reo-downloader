from attr import attrs, attrib
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import textwrap
import dateutil.parser

BASE_URL = "http://www.tokureo.maori.nz/"


def get_page(path):
    response = requests.get(BASE_URL + path)
    return BeautifulSoup(response.content, from_encoding="utf8", features="html.parser")


@attrs(auto_attribs=True)
class Episode:
    season_number: int
    episode_number: int
    episode_page: str
    title: str
    _soup: BeautifulSoup = attrib(None, repr=False)

    @property
    def soup(self):
        if self._soup is None:
            self._soup = get_page(self.episode_page)
        return self._soup

    @property
    def description(self):
        return self.soup.select("div.maincol p")[0].text

    @property
    def video_url(self):
        return self.soup.select("div.streaming a.download")[0]["href"]

    @property
    def date(self):
        return dateutil.parser.parse(self.soup.select("span.date")[0].text.strip("- "))

    @property
    def nfo(self):
        return textwrap.dedent(
            f"""
            <?xml version="1.0" encoding="UTF-8" standalone="yes" ?>
            <episodedetails>
                <title>{self.title}</title>
                <plot>
                    {self.description}
                </plot>
                <uniqueid type="" default="true">
                    tokureo-s{self.season_number}e{self.episode_number}
                </uniqueid>
                <aired>{self.date.date().isoformat()}</aired>
            </episodedetails>
            """
        )


@attrs(auto_attribs=True)
class Season:
    season_number: int
    season_page: str
    _soup: BeautifulSoup = attrib(None, repr=False)

    @property
    def soup(self):
        if self._soup is None:
            self._soup = get_page(self.season_page)
        return self._soup

    @property
    def episodes(self):
        episode_links = [a for a in self.soup.select("a") if a.select("span.episode")]
        episode_pages = [urljoin(self.season_page, a["href"]) for a in episode_links]
        episode_numbers = [int(list(a.stripped_strings)[0]) for a in episode_links]
        episode_titles = [list(a.stripped_strings)[-1] for a in episode_links]
        return [Episode(self.season_number, n, p, t)
                for n, p, t in zip(episode_numbers, episode_pages, episode_titles)]


def get_seasons():
    soup = get_page("index.html")
    season_links = soup.select("ul.seriesPick a")
    season_pages = [a["href"] for a in season_links]
    return [Season(i + 1, page) for i, page in enumerate(season_pages)]


def generate_tvshow_nfo():
    return textwrap.dedent(
        """
        <?xml version="1.0" encoding="UTF-8" standalone="yes" ?>
        <tvshow>
            <title>Tōku Reo</title>
            <uniqueid type="" default="true">tokureo</uniqueid>
        </tvshow>
        """
    )