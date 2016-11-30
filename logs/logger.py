from os import listdir
from os.path import join as pathJoin
import csv
import random

MOVIES_RETURNED = 6
TAGS_RETURNED = 5


# uid | movIDsShown == 6 | depth | chosenID | tagIDs == 5 + 1 | tagVals == 5

class Logger:
    def __init__(self, path, on):
        self.on = on
        self.num = len(listdir(path))
        self.file = pathJoin(path, str(self.num) + ".txt")
        self.reset()

    def reset(self):
        # Depth
        self.shownNum = 0
        # uid
        self.uid = random.randint(0, 100000000)

    # Six movies, five tags
    def log(self, movIDsShown, chosenID, tagIDs, tagVals):
        if not self.on:
            return

        if len(movIDsShown) < MOVIES_RETURNED:
            print("Pass in correct data to logger: movies too short")

        if len(tagIDs) < TAGS_RETURNED or len(tagVals) < TAGS_RETURNED:
            print("Pass in correct data to logger: tags too short" +
                             str(tagIDs) + str(tagVals))

        movIDsShown = impute(movIDsShown, MOVIES_RETURNED + 1)
        tagIDs = impute(tagIDs, TAGS_RETURNED + 1) # to account for +1
        tagVals = impute(tagVals, TAGS_RETURNED + 1)

        with open(self.file, "a") as file:
            writer = csv.writer(file)
            writer.writerow([self.uid] + movIDsShown + [self.shownNum]
                            + [chosenID] + tagIDs + tagVals)

        self.shownNum += 1


def impute(lst, n):
    ret = [x for x in lst]
    for i in range(n - len(lst)):
        ret.append(-1)
    return ret

