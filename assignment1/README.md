# MSE231_F22 ASSIGNMENT 1 - TWEET ANALYSIS 

## SPECIFICATIONS
- https://mse231.github.io/assignment1.html
- https://github.com/mse231/mse231_f22

### REFERENCES
- personal Twitter developer portal: https://developer.twitter.com/en/portal/projects/1578992483542761473/apps
- Tweet object api: https://developer.twitter.com/en/docs/twitter-api/data-dictionary/object-model/tweet
- plt text api: https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.text.html
- plt legend api: https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.legend.html

#### TWEET ANALYSIS
- https://twitter.com/i/web/status/<tweet_id>
- sample retweet [object](archives/retweet_sample.jsonc) corresponds to [this tweet](https://twitter.com/i/web/status/1579477321878482944)

<hr>

## PROJECT STRUCTURE
- `creds.txt` file containing all user keys needed to use Twitter's API <b>(DO NOT MODIFY)</b>
  - <i>file is excluded from github repo</i>
- `tweet_stream.py` uses Twitter's streaming API and the Tweepy python wrapper to scrape real-time Tweets; includes various flags to specify output or to filter certain tweets (specified below in commands)
- `parse_tweets.py` reads a stream of raw tweets from stdin, processes them and saves the processed data to a (new) csv file specified by the user
- `tweet_analysis.py` reads from the processed csv file to predict users' (and original posters') genders, then plot a graph

### SUBFOLDERS
- `archives` contains some files used to visualise processed data
- `graphs` contains the graphs generated from `tweet_analysis.py`
- `ssa_names` contains the baby names data separated by gender from SSA; `.tsv` files are the unzipped original files while `.txt` files contain processed data

### TWEET COLLECTION LOG
- <i>record of each .gz file in the format: `filename.gz` (keyword) - date time duration</i>
- `netflix.gz` (netflix) - 09/10/22 1535 ~1min
- `inflation.gz` (inflation) - 09/10/22 1631-1748 ~1h17min
- `tweets0.gz` (NIL) - 10/10/22 1002-1044 ~42min
- `space.gz` (space) - 10/10/22 1049 ~50s
- `politics.gz` (politics) - 10/10/22 2222-2325 ~1h3min
- `climate.gz` (climate) - 12/10/22 1159-1501 ~3h1min

<hr>

## COMMANDS
1. `python tweet_stream.py --keyfile creds.txt --gzip KEYWORD.gz --filter KEYWORD`
   - sample 1% of real-time tweets using the provided credentials (until Ctrl-C is entered)
   - gzip the output to the given file
   - filters only the tweets containing the given keyword(s)
2. `7z e -so KEYWORD.gz | python parse_tweets.py KEYWORD.csv`
   - pipe each Tweet object into stdin for python file, and output processed tweet data to given csv file
   - `7z e -so KEYWORD.gz` extract .gz file using 7zip and print to stdout
3. `python tweet_analysis.py KEYWORD.csv`
   - uses the processed csv data to predict users' (and original posters') genders
   - plots multiple lines of tweet volume against time using predicted genders

<hr>

## GRAPHS
![graph with keyword politics](graphs/politics.png)

![graph with keyword climate](graphs/climate.png)

> Note that trends observed may not accurately reflect real world tweet volume, as the graph excludes the tweets of users whose gender we are unable to classify

<hr>

## ANALYSIS

### GENDER PREDICTION
- from `parse_tweets.py`, users' usernames are processed, where non-alphabetic characters are removed and the most probable first name is added to the csv file
- in `tweet_analysis.py`, first names are classified based on their frequency in the SSA datasets
- names that cannot be classified are not reflected in the graphs (~30-45% of tweets)
