from os.path import join as pathJoin
import pandas as pd
import numpy as np
import pickle

from suggester.metrics import Metrics

dataRootPath = "tag-genome"


class Suggester:
    def __init__(self):
        MovieID_TagID_Relevance = pathJoin(dataRootPath, "tag_relevance.dat")
        MovieID_Title_MoviePopularity = pathJoin(dataRootPath, "movies.dat")
        TagID_Tag_TagPopularity = pathJoin(dataRootPath, "tags.dat")

        self.tag_relevance = pd.read_csv(MovieID_TagID_Relevance, delimiter='\t', header=None,
                                         names=['MovieID', 'TagID', 'Relevance'])
        self.movies = pd.read_csv(MovieID_Title_MoviePopularity, delimiter='\t', header=None,
                                  names=['MovieID', 'Title', 'MoviePopularity'])
        self.tags = pd.read_csv(TagID_Tag_TagPopularity, delimiter='\t', header=None,
                                names=['TagID', 'Tag', 'TagPopularity'])

        with open(pathJoin(dataRootPath, 'pickled/genome.pickle'), 'rb') as f:
            self.genome = np.array(pickle.load(f))

        self.metrics = Metrics(self.tag_relevance, self.movies, self.tags, self.genome)
