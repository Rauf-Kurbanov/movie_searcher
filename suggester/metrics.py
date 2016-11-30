import numpy as np
import scipy.spatial.distance as dist
import pickle

import os

from sklearn.neighbors import NearestNeighbors


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
        self.model.fit(self.genome)

        with open('./tag-genome/pickled/precomp-knn-250.pickle', 'rb') as f:
            self.precomputedKNN = pickle.load(f)

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
        return np.array(indices_art2[0])

    # def movie_neighbours(self, i):
    #     clusters = self.precomputedKNN[1]
    #     return clusters[i]

    def N(self, i):
        return self.movie_neighbours(i)

    def Np(self, i, t, Ni):
        delta = 0.25
        return Ni[self.genome[Ni, t] > self.genome[i, t] + delta].size

    def Nn(self, i, t, Ni):
        delta = 0.25
        return Ni[self.genome[Ni, t] < self.genome[i, t] - delta].size

    @staticmethod
    def critiqueEntropyH(t, i, Nd, Ni):
        modNd = Nd + 1
        modN = len(Ni)
        return - modNd / modN * np.log(modNd / modN)

    def critiqueEntropy(self, t, i, Ni):
        res = 0
        lst = [self.Nn(i, t, Ni), self.Np(i, t, Ni)]
        lst.append(Ni.size - sum(lst))
        for Nd in lst:
            res += self.critiqueEntropyH(t, i, Nd, Ni)
        return res

    def tagSim(self, tA, tB):
        return dist.cosine(self.genome[:, tA], self.genome[:, tB])

    def softer_objective_function(self, S, i, Ni):
        return self.objective_function(S, i, Ni, filter3=False)

    def much_softer_objective_function(self, S, i, Ni):
        return self.objective_function(S, i, Ni, filter1=False, filter3=False)

    def much_much_softer_objective_function(self, S, i, Ni):
        return self.objective_function(S, i, Ni, filter1=False, filter2=False, filter3=False)

    def objective_function(self, S, i, Ni, filter1=True, filter2=True, filter3=True):
        cond1 = lambda t: self.popularity(t) >= 50 if filter1 else lambda x: True

        def cond2(t):
            if not filter2:
                return True

            for u in S:
                if t != u and self.tagSim(t, u) > 0.5:
                    return False
            return True

        cond3 = lambda t: self.critiqueEntropy(t, i, Ni) > 0.325 if filter3 else lambda x: True
        ts = [t for t in S if cond1(t) and cond3(t)]
        ts = [t for t in ts if cond2(t)]
        ts = np.array(ts)
        return np.sum([self.critiqueEntropy(t, i, Ni) * np.log(self.popularity(t)) for t in ts])
        # res = 0
        # for t in S:
        #     f = False
        #     pop_t = self.tags.TagPopularity[t] + 1
        #     if t < 50:
        #         continue
        #     c_entr_t = self.critiqueEntropy(t, i, Ni)
        #     if c_entr_t < 0.325:
        #         continue
        #     for i in S:
        #         if i == t:
        #             continue
        #         arr = self.tagSim(t, i)
        #         if arr > 0.5:
        #             f = True
        #             break
        #     if not f:
        #         res += c_entr_t * np.log(pop_t)
        # return res

    def critiqueDist(self, critiquedMovieId, retrievedMovieId, tagId, direction):
        ic, ir, t, d = critiquedMovieId, retrievedMovieId, tagId, direction
        return max(0, self.rel(t, ir) - self.rel(t, ic) * d)

    def linearSat(self, ic, ir, t, d):
        return self.critiqueDist(ic, ir, t, d)

    def diminishSat(self, ic, ir, t, d):
        return 1 - np.exp(-5 * self.critiqueDist(ic, ir, t, d))

    def critiqueFit(self, ic, ir, t, d):
        return self.linearSat(ic, ir, t, d) * self.articleCosSimi(ic, ir)