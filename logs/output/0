from os import listdir
from os.path import join as pathJoin
import csv
import random

MOVIES_RETURNED = 6
TAGS_RETURNED = 5


# uid | movIDsShown == 6 | depth | chosenID | tagIDs == 5 | tagsPrev == 5 | tagsChanged == 5

class Logger:
    def __init__(self, path):
        self.num = len(listdir(path))
        self.file = pathJoin(path, str(self.num))
        # Depth
        self.shownNum = 0
        # uid
        self.uid = random.randint(0, 100000000)

    # Six movies, five tags
    def log(self, movIDsShown, chosenID, tagIDs, tagPrev, tagCur):
        if len(movIDsShown) != MOVIES_RETURNED:
            print("Pass in correct data to logger: movies too short")

        if len(tagIDs) != TAGS_RETURNED or len(tagPrev) != TAGS_RETURNED \
                or len(tagCur) != TAGS_RETURNED:
            print("Pass in correct data to logger: tags too short" +
                             str(tagIDs) + str(tagPrev) + str(tagCur))

        movIDsShown = impute(movIDsShown, MOVIES_RETURNED)
        tagIDs = impute(tagIDs, TAGS_RETURNED)
        tagPrev = impute(tagPrev, TAGS_RETURNED)
        tagCur = impute(tagCur, TAGS_RETURNED)

        with open(self.file, "a") as file:
            writer = csv.writer(file)
            writer.writerow([self.uid] + movIDsShown + [self.shownNum]
                            + [chosenID] + tagIDs + tagPrev + tagCur)

        self.shownNum += 1


def impute(lst, n):
    ret = [x for x in lst]
    for i in range(n - len(lst)):
        ret.append(-1)
    return ret

