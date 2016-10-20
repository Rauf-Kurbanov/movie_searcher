from os.path import join as pathJoin
import pandas as pd
import numpy as np
import pickle
import itertools as itt

from suggester.metrics import Metrics

dataRootPath = "tag-genome"


class Suggester:
    def __init__(self, n_movies):
        movieID_tagID_relevance = pathJoin(dataRootPath, "tag_relevance.dat")
        movieID_title_movie_popularity = pathJoin(dataRootPath, "movies.dat")
        tagID_tag_tag_popularity = pathJoin(dataRootPath, "tags.dat")

        self.tag_relevance = pd.read_csv(movieID_tagID_relevance, delimiter='\t', header=None,
                                         names=['MovieID', 'TagID', 'Relevance'])
        self.movies = pd.read_csv(movieID_title_movie_popularity, delimiter='\t', header=None,
                                  names=['MovieID', 'Title', 'MoviePopularity'])
        self.tags = pd.read_csv(tagID_tag_tag_popularity, delimiter='\t', header=None,
                                names=['TagID', 'Tag', 'TagPopularity'])

        with open(pathJoin(dataRootPath, 'pickled/genome.pickle'), 'rb') as f:
            self.genome = np.array(pickle.load(f))

        self.metrics = Metrics(self.tag_relevance, self.movies, self.tags, self.genome)
        self.n_movies = n_movies

        # self.prev_tag_values = np.repeat(0.5, self.tags.shape[0])
        self.prev_tag_values = list(itt.repeat(0.5, self.tags.shape[0]))
        self.curr_movie = self._movieTitleToNum("Fight Club (1999)")

    def getInitialRecs(self):
        return [self._getMovieByName("Fight Club (1999)"),
                self._getMovieByName("Hobbit: The Desolation of Smaug, The (2013)"),
                self._getMovieByName("Inception (2010)"),
                self._getMovieByName("Thor: The Dark World (2013)"),
                self._getMovieByName("Frozen (2013)"),
                self._getMovieByName("12 Angry Men (1957)")]

    def _getMovieByName(self, name):
        return self.movies[self.movies.Title == name].Title.iloc[0]

    def getNextRecs(self, selectedMovie, tags):
        """Gets the selected movie :: string and new tag values :: ([name], [currentVals])
           and returns a new movies list"""
        tagNames, tagValues = tags
        directions = [1 if p < c else 0 if p == c else -1
                      for (p, c) in zip(self.prev_tag_values, tagValues)]
        tagAndDir = [td for td in enumerate(directions) if td[1] != 0]

        def norm(mId):
            return np.product([self.metrics.critiqueFit(selectedMovie, mId, tag, d)
                               for tag, d in tagAndDir])

        candidates = self.metrics.movie_neighbours(selectedMovie)
        for tag, d in tagAndDir:
            candidates = [c for c in candidates if self.metrics.critiqueDist(selectedMovie, c, tag, d) > 0]

        candidates = sorted(candidates, key=norm)[:5]
        self.curr_movie = selectedMovie
        return list(self.movies.loc[candidates].Title)

    def _movieTitleToNum(self, movie_name):
        movies = self.movies
        return np.argmax(movies.index.values[movies.Title == movie_name])

    def getTopTags(self, movie_name):
        mId = self._movieTitleToNum(movie_name)
        Ni = self.metrics.N(mId)
        tagIds = []
        for i in range(5):
            candidates = range(self.tags.shape[0])
            results = [self.metrics.objective_function(tagIds + [t], mId, Ni) for t in candidates if t not in tagIds]
            tagIds.append(np.argmax(results))

        tagNames = list(self.tags.loc[tagIds, ].Tag)
        tagValues = [self.genome[mId, tid] * 100 for tid in tagIds]

        self.prev_tag_values = tagValues
        return tagNames, tagValues
