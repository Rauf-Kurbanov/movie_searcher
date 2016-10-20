import requests
from urllib.parse import quote


class Movies:

    @staticmethod
    def imdb_id_from_title(title):
        """ return IMDB id for search string

            Args::
                title (str): the movie title search string

            Returns:
                str. IMDB id, e.g., 'tt0095016'
                None. If no match was found

        """
        pattern = 'http://www.imdb.com/xml/find?json=1&nr=1&tt=on&q={movie_title}'
        url = pattern.format(movie_title=quote(title))
        r = requests.get(url)
        res = r.json()
        # sections in descending order or preference
        for section in ['popular','exact','substring']:
            key = 'title_' + section
            if key in res:
                return res[key][0]['id']