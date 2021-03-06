from os.path import join as pathJoin
from random import randint
from math import floor

import pandas as pd
import numpy as np
import pickle
import json
import itertools as itt

from logs.logger import Logger
from suggester.metrics import Metrics

dataRootPath = "tag-genome"

MOVIES_RETURNED = 6
TAGS_RETURNED = 5

# Sets logging on and off
logger = Logger("logs/output", False)


class Suggester:
    def __init__(self):
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

        with open(pathJoin(dataRootPath, "json/allFilmsToTags.json")) as f:
            self.precompTags = json.loads(f.read())

    def getInitialRecs(self):
        ret = [self._getMovieByName("Fight Club (1999)"),
               self._getMovieByName("Hobbit: The Desolation of Smaug, The (2013)"),
               self._getMovieByName("Inception (2010)"),
               self._getMovieByName("Thor: The Dark World (2013)"),
               self._getMovieByName("Frozen (2013)"),
               self._getMovieByName("12 Angry Men (1957)")]
        return ret

    @staticmethod
    def resetLogger(completely=False):
        logger.reset(completely)

    def _getMovieByName(self, name):
        return self.movies[self.movies.Title == name].Title.iloc[0]

    def getNextRecs(self, selectedMovieName, tags):
        """Gets the selected movie :: string and new tag values :: ([name], [currentVals])
           and returns a new movies list :: string """
        print("getNextRecs")
        print(tags)
        selectedMovie = self._movieTitleToNum(selectedMovieName)
        tagNames, tagValues = tags

        prev_tag_values = [int(self.genome[selectedMovie, self._tagNameToID(tId)] * 100) for tId in tagNames]

        print("##############################")
        print(tagNames)
        print(prev_tag_values)
        print(tagValues)
        print("##############################")

        abso = lambda p, c: abs(p - c)

        directions = [abso(p, c) if p < c else 0 if p == c else -abso(p, c)
                      for (p, c) in zip(prev_tag_values, tagValues)]

        tids = [self._tagNameToID(name) for name in tagNames]
        tagAndDir = [td for td in zip(tids, directions) if td[1] != 0]

        def norm(mId):
            return -np.sum([self.metrics.critiqueFit(selectedMovie, mId, tag, d)
                            for tag, d in tagAndDir])

        candidates = self.metrics.movie_neighbours(selectedMovie)
        # candidates = range(self.movies.shape[0])
        # for tag, d in tagAndDir:
        # print(sorted([self.metrics.critiqueDist(selectedMovie, c, tag, d) for c in candidates])[-5])
        # print(sorted([self.metrics.articleCosSimi(selectedMovie, c) for c in candidates])[-5])

        candidates = sorted(candidates, key=norm)[:MOVIES_RETURNED]
        # print([norm(x) for x in candidates][:MOVIES_RETURNED])
        ret = list(self.movies.loc[candidates].Title)
        ##################################
        logger.log([self._movieTitleToID(x) for x in ret],
                   self._movieTitleToID(selectedMovieName),
                   [self._tagNameToID(x) for x in tagNames],
                   tagValues)
        ##################################
        print(ret)
        return ret

    def _movieTitleToID(self, movie_name):
        return self.movies[self.movies.Title == movie_name].MovieID.iloc[0]

    def _tagNameToID(self, tag_name):
        return self.tags[self.tags.Tag == tag_name].TagID.iloc[0]

    def getTagNames(self):
        return self.tags.Tag

    def getTagMetric(self, tag, curr_movie):
        mId = self._movieTitleToNum(curr_movie)
        tId = self._tagNameToID(tag)
        return int(self.genome[mId, tId] * 100)

    def getMovieNames(self):
        return self.movies.Title

    def _movieTitleToNum(self, movie_name):
        movies = self.movies
        return np.argmax(movies.index.values[movies.Title == movie_name])
        # return np.where(movies.index.values[movies.Title == movie_name] == 1)[0][0]

    def _topTagsGreedy(self, mId, Ni, obj_function):
        tagIds = []
        for i in range(TAGS_RETURNED):
            candidates = range(self.tags.shape[0])
            results = [obj_function(tagIds + [t], mId, Ni) for t in candidates if t not in tagIds]
            tagIds.append(np.argmax(results))
        return tagIds

    def getTopTags(self, movie_name):
        if movie_name in self.precompTags:
            tagNames, _ = self.precompTags[movie_name]

            tagIds = [self._tagNameToID(name) for name in tagNames]
            if 0 in tagIds:
                values = np.array(tagIds)
                where_zero = np.where(values == 0)[0]
                for i in where_zero:
                    r = randint(0, self.tags.shape[0])
                    while r in tagIds:
                        r = randint(self.tags.shape[0])
                    tagIds[i] = r

            tagNames = list(self.tags.loc[tagIds].Tag)
            tagValues = [self.getTagMetric(x, movie_name) for x in tagNames]
            return tagNames, tagValues

            # mId = self._movieTitleToNum(movie_name)
            # Ni = self.metrics.N(mId)
            #
            # print("Using softer objective function")
            # tagIds = self._topTagsGreedy(mId, Ni, self.metrics.softer_objective_function)
            #
            # # For now I's assuming tag zero in missing tag, not "007"
            # # if 0 in tagIds:
            # #     print("Couldnt find all tags")
            # #     print("Number of missing tags: {}", tagIds.count(0))
            # #     print("Using softer objective function")
            # #     tagIds = self._topTagsGreedy(mId, Ni, self.metrics.softer_objective_function)
            #
            # # if 0 in tagIds:
            # #     print("Using much softer objective function")
            # #     tagIds = self._topTagsGreedy(mId, Ni, self.metrics.much_softer_objective_function)
            # #
            # # if 0 in tagIds:
            # #     print("Using very much softer objective function")
            # #     tagIds = self._topTagsGreedy(mId, Ni, self.metrics.much_much_softer_objective_function)
            #
            # if 0 in tagIds:
            #     print("Inserting random tags instead of missing ones")
            #     values = np.array(tagIds)
            #     where_zero = np.where(values == 0)[0]
            #     for i in where_zero:
            #         r = randint(0, self.tags.shape[0])
            #         print("R = {}", r)
            #         while r in tagIds:
            #             r = randint(self.tags.shape[0])
            #         tagIds[i] = r
            #
            # tagNames = list(self.tags.loc[tagIds, ].Tag)
            # tagValues = [self.genome[mId, tId] * 100 for tId in tagIds]
            #
            # # self.prev_tag_values = tagValues
            # print("Top tags")
            # print("Tag names: {}".format(tagNames))
            # print("Tag values: {}".format(tagValues))
            #
            # return tagNames, tagValues
