import numpy as np
import scipy.spatial.distance as dist
from sklearn.neighbors import NearestNeighbors
import itertools as itt


class Metrics:
    def __init__(self, tag_relevance, movies, tags, genome):

        self.tag_relevance = tag_relevance
        self.movies = movies
        self.tags = tags

        self.genome = genome

        n_tags = self.tags.shape[0]

        self.tag_weights = np.array([np.log(self.popularity(tagId)) / np.log(self.docFreq(tagId))
                                     for tagId in range(n_tags)])

        self.model = NearestNeighbors(algorithm="brute", metric=self.weightedCosSimi, n_neighbors=250)
        # nbrs_art2 = LSHForest(n_candidates = 500, n_neighbors = 250)
        self.model.fit(self.genome)

    def popularity(self, tag_id):
        return self.tags.TagPopularity[tag_id] + 1

    def docFreq(self, tag):
        byTag = self.genome[:, tag]
        specific = [x for x in byTag if x > 0.5]
        return len(specific) + 2

    def weightedCosSimi(self, u, v):
        """Not exactly like in the article"""
        return dist.cosine(u * self.tag_weights, v * self.tag_weights)

    def articleCosSimi(self, u, v):
        """Exactly like in the article"""
        w = self.tag_weights
        x = np.sum(w * u * v)
        y = np.sqrt(sum(w * u * u)) * np.sqrt(sum(w * v * v))
        return x / y

    def rel(self, tagId, movId):
        return self.genome[movId, tagId]

    def printNeigh(self, randMovNum):
        neighbors = self.movie_neighbours(randMovNum)
        for mid in neighbors:
            print(self.movies.loc[mid]["Title"])

    def movie_neighbours(self, i):
        _, indices_art2 = self.model.kneighbors(self.genome[i, :].reshape(1, -1))
        return indices_art2

    def N(self, i):
        return self.movie_neighbours(i)

    def Np(self, i, t, Ni):
        delta = 0.25
        return [j for j in Ni if self.rel(t, j) > self.rel(t, i) + delta]

    def Nn(self, i, t, Ni):
        delta = 0.25
        return [j for j in Ni if self.rel(t, j) < self.rel(t, i) - delta]

    def Nz(self, i, t, Ni):
        return [j for j in Ni if j not in self.Np(i, t, Ni) and j not in self.Nn(i, t, Ni)]

    @staticmethod
    def critiqueEntropyH(t, i, Nd, Ni):
        modNd = len(Nd) + 1
        modN = len(Ni)
        return - modNd / modN * np.log(modNd / modN)

    def critiqueEntropy(self, t, i):
        Ni = self.N(i)
        res = 0
        for Nd in [self.Nn(i, t, Ni), self.Nz(i, t, Ni), self.Np(i, t, Ni)]:
            res += self.critiqueEntropyH(t, i, Nd, Ni)
        return res

    def tagSim(self, tA, tB):
        relevanceA = self.genome[:, tA]
        relevanceB = self.genome[:, tB]
        return dist.cosine(relevanceA, relevanceB)

    def objective_function(self, S, i):
        """|S| == 5"""
        cond1 = lambda t: self.popularity(t) >= 50
        cond2 = lambda t: np.all(np.array([self.tagSim(t, u) < 0.5 for u in S if t != u]))
        cond3 = lambda t: self.critiqueEntropy(t) > 0.325
        ts = [t for t in S if cond1(t) and cond2(t) and cond3(t)]
        iss = list(itt.repeat(i, 6))
        return np.sum([self.critiqueEntropy(t, i) * np.log(self.popularity(t)) for t in ts])

    def critiqueDist(self, critiquedMovieId, retrievedMovieId, tagId, direction):
        ic, ir, t, d = critiquedMovieId, retrievedMovieId, tagId, direction
        return max(0, self.rel(t, ir) - self.rel(t, ic) * d)

    def linearSat(self, ic, ir, t, d):
        self.critiqueDist(ic, ir, t, d)

    def diminishSat(self, ic, ir, t, d):
        1 - np.exp(-5 * self.critiqueDist(ic, ir, t, d))