"""
Takes a stream of tweets as input (via stdin) and writes in tsv format to stdout.
4 fields required: date, time rounded to nearest 15-minute, user's name, name of original poster (else NA)
Usage:
    <raw tweets stdout> | python parse_tweets.py keyword.csv
    7z e -so keyword.gz | python parse_tweets.py keyword.csv
"""

import sys
import re
import csv
import json
from typing import List


def main():
    if len(sys.argv) != 2 or not sys.argv[1].endswith(".csv"):
        print("Usage: <raw tweets stdout> | python parse_tweets.py filename.csv")
        sys.exit(1)

    filename = sys.argv[1]
    tweets = []

    # stream parsing of raw tweet data
    for line in sys.stdin:
        tweet: dict = json.loads(line)

        try:
            # get date & time info
            data: dict = tweet["data"]
            created_at: List[str] = data["created_at"].split("T")
            date = created_at[0]
            time = created_at[1][:5]
            time = time[:4] + "0"  # round down to nearest 10 minute interval

            # get user info and original user (if retweeted)
            users: List[dict] = tweet["includes"]["users"]
            name = parse_name(users[0]["name"])
            original_poster = "NA"  # assume tweet is not a retweet first
        except KeyError:
            # occasional errors when retrieving tweets, "data" field is replaced by "error" field
            continue

        # if tweet is a retweet, save original name (unless it's a self-retweet)
        try:
            if data["referenced_tweets"][0]["type"] == "retweeted":
                original_poster = parse_name(users[1]["name"])
        except (KeyError, IndexError):
            # referenced_tweets does not exist, or user retweeted their own tweet
            pass

        if name != "NA":
            tweets.append([date, time, name, original_poster])
            # print(date, time, name, original_poster)

    save_as_csv(filename, tweets)


def parse_name(name: str) -> str:
    """
    Takes a name and removes all non-alphabetical characters.
    Returns a single lowercase word that best represents the name based on
    length (longer than 2 characters) and is non-empty.
    Returns "NA" if name is empty after parsing.
    """
    regex = re.compile("[^a-zA-Z]")
    for token in name.split():
        token = regex.sub("", token)
        if token != "" and len(token) >= 3:
            return token.lower()
    return "NA"


def save_as_csv(filename: str, tweets: List[List[str]]) -> None:
    """
    Saves the processed tweet data into a new csv file.
    Csv file has 4 fields: date, time, name, original_name.
    """
    with open(filename, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["date", "time", "name", "original_poster"])
        for tweet in tweets:
            writer.writerow(tweet)


if __name__ == "__main__":
    main()
