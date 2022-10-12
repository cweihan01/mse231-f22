"""
CREATE A TWEET OBJECT that initialises the 4 fields, together with the prediction of user gender and the original user's gender (if any)
two lists, one for male posts, one for female posts
analyse the processed tweet data (.csv) that is passed in through command line, and plot graphs
"""

import csv
import gzip
import sys
from typing import Dict, List
import matplotlib.pyplot as plt
import numpy as np

# constant strings
MALE = "MALE"
FEMALE = "FEMALE"
NA = "NA"


class TweetAnalyser:
    def __init__(self, filename: str) -> None:
        self.filter_keyword = filename.removesuffix(".csv")

        print("Reading from gzip files...")
        self.male_name_frequencies = self.read_gender_file("male_names.tsv.gz")
        self.female_name_frequencies = self.read_gender_file("female_names.tsv.gz")
        print("Done reading gzip files")

        self.datetimes = self.populate_datetimes(filename)
        # remove first and last datetime as they are not a complete 10 minute interval
        self.datetimes = self.datetimes[1 : len(self.datetimes) - 1]

        # dicts map each unique datetime to the respective total number of tweets during that period
        self.male_tweets = dict.fromkeys(self.datetimes, 0)
        self.female_tweets = dict.fromkeys(self.datetimes, 0)

        # number of retweets that are male_retweet_male, female_retweet_male etc
        self.mrm = dict.fromkeys(self.datetimes, 0)
        self.frm = dict.fromkeys(self.datetimes, 0)
        self.frf = dict.fromkeys(self.datetimes, 0)
        self.mrf = dict.fromkeys(self.datetimes, 0)

        self.analyse_file(filename)

    def read_gender_file(self, filename: str) -> Dict[str, int]:
        """
        Reads from the male/female gender files.
        Returns a dictionary mapping each unique name to the total number of times
        that name appeared in the dataset.
        """
        if not filename.endswith(".tsv.gz"):
            print("file extension type must be '.tsv.gz'")
            sys.exit(1)

        try:
            with gzip.open(filename, "rt", encoding="UTF-8") as f:
                next(f)  # skip header row
                names = dict()
                for line in f:
                    name = line.split("\t")[0].lower()
                    count = int(line.split("\t")[1])
                    if name in names:
                        names[name] += count
                    else:
                        names[name] = count
            return names
        except FileNotFoundError:
            print(f"{filename} does not exist!")
            sys.exit(1)

    def populate_datetimes(self, filename: str) -> List[str]:
        """
        Reads the given file and populates the instance 'datetimes' list
        with each unique datetime.
        """
        try:
            with open(filename, "rt") as f:
                datetimes: List[str] = list()
                for line in csv.DictReader(f):
                    datetime = line["date"] + " " + line["time"]
                    if datetime not in datetimes:
                        datetimes.append(datetime)
            return datetimes
        except FileNotFoundError:
            print(f"{filename} does not exist!")
            sys.exit(1)

    def analyse_file(self, filename: str) -> None:
        """
        Reads the given file and predicts the gender of the user.
        Then creates a new Tweet object and adds the Tweet to the respective bin.
        """
        try:
            total_tweets_count = 0
            total_retweets_count = 0
            unclassified_tweets_count = 0
            unclassified_retweets_count = 0

            with open(filename, "rt") as f:
                for line in csv.DictReader(f):
                    total_tweets_count += 1
                    datetime = line["date"] + " " + line["time"]
                    name, original_poster = line["name"], line["original_poster"]

                    if datetime not in self.datetimes:
                        continue

                    # predict gender, and add to respective bin
                    gender = self.predict_gender(name)
                    if gender == MALE:
                        self.male_tweets[datetime] += 1
                    elif gender == FEMALE:
                        self.female_tweets[datetime] += 1
                    else:
                        unclassified_tweets_count += 1

                    if original_poster == NA:
                        continue

                    # predict gender of original poster, and store this retweet in
                    # the 4 instance variables
                    total_retweets_count += 1
                    original_poster_gender = self.predict_gender(original_poster)
                    if original_poster_gender == MALE:
                        if gender == MALE:
                            self.mrm[datetime] += 1
                        elif gender == FEMALE:
                            self.frm[datetime] += 1
                    elif original_poster_gender == FEMALE:
                        if gender == MALE:
                            self.mrf[datetime] += 1
                        elif gender == FEMALE:
                            self.frf[datetime] += 1
                    else:
                        unclassified_retweets_count += 1

                    # print predicted genders (for retweets) to console/file
                    # print("user's gender/name:", name, gender)
                    # print(
                    #     "original poster's gender/name:",
                    #     original_poster,
                    #     original_poster_gender,
                    # )
                    # print()
            self.unclassified_tweets_percentage = round(
                (unclassified_tweets_count / total_tweets_count) * 100, 2
            )
            self.unclassified_retweets_percentage = round(
                (unclassified_retweets_count / total_retweets_count) * 100, 2
            )
        except FileNotFoundError:
            print(f"{filename} does not exist!")

    def predict_gender(self, name: str) -> str:
        """
        Helper method for analyse_file().
        Predicts whether a given name is male or female.
        Returns True if male, False if female.
        """
        appears_in_male = name in self.male_name_frequencies
        appears_in_female = name in self.female_name_frequencies

        # name appears in one and only one dataset
        if appears_in_male and not appears_in_female:
            return MALE
        elif appears_in_female and not appears_in_male:
            return FEMALE

        # name appears in both datasets (eg. jules), compare frequency
        if appears_in_male and appears_in_female:
            male_frequency = self.male_name_frequencies[name]
            female_frequency = self.female_name_frequencies[name]
            if male_frequency > female_frequency:
                return MALE
            else:
                return FEMALE

        # return NA for those we cannot classify for now
        return NA

    def lev_distance(self, s1: str, s2: str) -> int:
        """
        Helper method for predict_gender().
        Uses a recursive method to calculate the Leveshtein distance between two strings.
        Source: https://blog.finxter.com/how-to-calculate-the-levenshtein-distance-in-python/
        Not used, too slow for large datasets.
        """
        if not s1:
            return len(s2)
        if not s2:
            return len(s1)
        return min(
            self.lev_distance(s1[1:], s2[1:]) + (s1[0] != s2[0]),
            self.lev_distance(s1[1:], s2) + 1,
            self.lev_distance(s1, s2[1:]) + 1,
        )

    def plot(self) -> None:
        """
        Plots the data onto a graph.
        """
        # x is datetime, y is volume of tweets per datetime
        x = self.datetimes
        male_tweets = self.male_tweets.values()
        female_tweets = self.female_tweets.values()
        print(f"{x=}")
        print(f"{male_tweets=} {female_tweets=}")

        # title/axis labels
        fig, ax = plt.subplots(constrained_layout=True)
        fig.set_size_inches(18.5, 10.5)
        fig.suptitle(f"Tweets with filter keyword = {self.filter_keyword}")
        ax.set_xlabel("Datetime", fontweight="bold", labelpad=10)
        ax.set_ylabel("Volume of tweets", fontweight="bold", labelpad=10)

        # plot main line
        ax.plot(x, male_tweets, label="Men", linewidth=3)
        ax.plot(x, female_tweets, label="Women", linewidth=3)

        # plot 4 retweet lines
        mrm = np.array(list(self.mrm.values()))
        frf = np.array(list(self.frm.values()))
        mrf = np.array(list(self.mrf.values()))
        frm = np.array(list(self.frf.values()))
        male_retweets = mrm + mrf
        female_retweets = frf + frm
        print(f"{mrm=}")
        print(f"{frf=}")
        print(f"{mrf=}")
        print(f"{frm=}")

        ax.plot(x, mrm, label="Men retweet Men", linewidth=2)
        ax.plot(x, frf, label="Women retweet Women", linewidth=2)
        ax.plot(x, mrf, label="Men retweet Women", linewidth=1)
        ax.plot(x, frm, label="Women retweet Men", linewidth=1)

        # calculate some stats and print to graph
        mrm_percentage = round(np.average(np.divide(mrm, male_retweets)) * 100, 2)
        frf_percentage = round(np.average(np.divide(frf, female_retweets)) * 100, 2)
        mrf_percentage = round(np.average(np.divide(mrf, male_retweets)) * 100, 2)
        frm_percentage = round(np.average(np.divide(frm, female_retweets)) * 100, 2)

        s1 = (
            f"Of {np.sum(male_retweets)} retweets by men, on average:\n"
            f"- {mrm_percentage}% of men retweeted men\n"
            f"- {mrf_percentage}% of men retweeted women\n"
        )
        s2 = (
            f"Of {np.sum(female_retweets)} retweets by women, on average:\n"
            f"- {frf_percentage}% of women retweeted women\n"
            f"- {frm_percentage}% of women retweeted men\n"
        )
        s3 = (
            f"Unclassified tweets: {self.unclassified_tweets_percentage}%\n"
            f"Unclassified retweets: {self.unclassified_retweets_percentage}%\n"
        )
        # put text at top left of graph
        fig.text(
            0.83,
            0.18,
            "\n".join([s1, s2, s3]),
            linespacing=1.5,
            wrap=True,
            bbox=dict(facecolor="none", edgecolor="black", boxstyle="round, pad=0.4"),
        )

        ax.legend(bbox_to_anchor=(1, 1))
        plt.setp(ax.get_xticklabels(), rotation=20, horizontalalignment="right")
        plt.show()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python tweet_analysis.py file1.csv")
        sys.exit(1)

    analyser = TweetAnalyser(sys.argv[1])
    analyser.plot()
