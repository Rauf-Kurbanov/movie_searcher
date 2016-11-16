from os import listdir
from os.path import join as pathJoin
import csv
import random


# uid | movIDsShown | depth | chosenID | tagIDs | tagShifts

class Logger:
    def __init__(self, path):
        self.num = len(listdir(path))
        self.file = pathJoin(path, str(self.num))
        # Depth
        self.shownNum = 0
        # uid
        self.uid = random.randint(0, 100000000)

    # Six movies, five tags
    def log(self, movIDsShown, chosenID, tagIDs, tagShifts):
        if len(movIDsShown) != 6 or len(tagIDs) != 5 or len(tagShifts) != 5:
            raise ValueError("Pass in correct data to logger")

        with open(self.file, "a") as file:
            writer = csv.writer(file)
            writer.writerow([self.uid] + movIDsShown + [self.shownNum]
                            + [chosenID] + tagIDs + tagShifts)
            
        self.shownNum += 1
