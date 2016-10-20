from os.path import join as pathJoin
import pandas as pd
import numpy as np
import pickle
import random

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

    def getInitialRecs(self):
        return [self.getMovieByName("Fight Club (1999)"),
                self.getMovieByName("Hobbit: The Desolation of Smaug, The (2013)"),
                self.getMovieByName("Inception (2010)"),
                self.getMovieByName("Thor: The Dark World (2013)"),
                self.getMovieByName("Frozen (2013)"),
                self.getMovieByName("12 Angry Men (1957)")]

    def getMovieByName(self, name):
        return self.movies[self.movies.Title == name].Title.iloc[0]

    def getNextRecs(self, selectedMovie, tags):
        """Gets the selected movie :: string and new tag values :: ([name], [currentVals])
           and returns a new movies list"""
        return list(self.movies.Title.loc[12:12 + self.n_movies])

    # def getTopTags(self, movie_name):
    #     """ Returns ([tagNames], [tagVals]) for a movieName passed in
    #         tagVals are from 0 to 99"""
    #
    #     f = random.randint
    #     return (["Yuu", "Hoo", "Woo", "Zhoo", "Cloo", "Choo"],
    #             [f(0, 99), f(0, 99), f(0, 99), f(0, 99), f(0, 99), f(0, 99)])

    def movieTitleToNum(self, movie_name):
        movies = self.movies
        return np.argmax(movies.index.values[movies.Title == movie_name])

    def getTopTags(self, movie_name):
        mId = self.movieTitleToNum(movie_name)
        Ni = self.metrics.N(mId)
        tagIds = []
        for i in range(5):
            candidates = range(self.tags.shape[0])
            results = [self.metrics.objective_function(tagIds + [t], mId, Ni) for t in candidates if t not in tagIds]
            tagIds.append(np.argmax(results))

        tagNames = list(self.tags.loc[tagIds, ].Tag)
        print(tagIds)
        print(tagNames)
        return tagNames, tagIds