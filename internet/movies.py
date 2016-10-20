import requests
from urllib.parse import quote


def imdb_descr_and_poster_from_title(title):
    try:
        description_request = 'http://www.omdbapi.com/?t={movie_title}&y=&plot=full&r=json'
        url = description_request.format(movie_title=quote(title))
        r = requests.get(url)
        res = r.json()

        pic = requests.get(res['Poster']).content
        return res['Plot'], pic
    except (KeyError, requests.exceptions.MissingSchema):
        print("No such thing, I guess")
        err_file = open("internet/img.png", "rb")
        data = err_file.read()
        err_file.close()
        return "Error", data


