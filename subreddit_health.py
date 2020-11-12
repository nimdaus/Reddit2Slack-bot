import praw
from praw.exceptions import RedditAPIException
from prawcore.exceptions import PrawcoreException
import json
from datetime import datetime, timezone, date
import datetime as dt
import requests
import time
from slack import WebClient
from psaw import PushshiftAPI
import pandas as pd
import csv

'''
todays subscribers
last X subscribers

get list of saved comments and submissions = mark as interacted

competitor mentions:
solarwinds, kaseya, connectwise

'''

from pandas.plotting import register_matplotlib_converters
from PIL import Image
import seaborn as sns
import matplotlib
import matplotlib.pyplot as plt

register_matplotlib_converters()

sns.set(style="ticks",
        rc={
            "figure.figsize": [12, 7],
            "text.color": "white",
            "axes.labelcolor": "white",
            "axes.edgecolor": "white",
            "xtick.color": "white",
            "ytick.color": "white",
            "axes.facecolor": "#222222",
            "figure.facecolor": "#222222"}
        )


## FOR WHEN DOCKERIZED
#client_id = os.environ['client_id']
#client_secret = os.environ['client_secret']
#username = os.environ['username']
#password = os.environ['password']
#user_agent = os.environ['user_agent']
#query = os.environ['query']
#subreddit = os.environ['subreddit']
#posts_from = os.environ['posts_from']
#sort_by = os.environ['sort_by']
#scan_count = os.environ['scan_count']
#slack_token = os.environ['slack_token']
#slack_channel = os.environ['slack_channel']

##I'd love to replace this with oauth2
# reddit = praw.Reddit(
#     client_id=client_id,
#     client_secret=client_secret,
#     username=username,
#     password=password,
#     user_agent=user_agent)

config = json.load(open('config.json'))
reddit = praw.Reddit(
    client_id=config['reddit']['client-id'],
    client_secret=config['reddit']['client-secret'],
    username=config['reddit']['username'],
    password=config['reddit']['password'],
    user_agent=config['reddit']['user_agent'])

api = PushshiftAPI(reddit)
subreddit_name = "msp"
start_year = 2019
start_month = 10
start_day = 31
start_epoch = int(dt.datetime(start_year,start_month,start_day).timestamp())
end_year = 2020
end_month = 10
end_day = 31
end_epoch = int(dt.datetime(end_year,end_month,end_day).timestamp())

# # #Today's Subscribers
# subscribers=[]
# row = [round(time.time()), subreddit_name, reddit.subreddit(subreddit_name).subscribers]
# subscribers.append(row)
# df = pd.DataFrame(subscribers)
# df.to_csv(f'{subreddit_name}-subscribers.csv', encoding='utf-8', index=False, mode='a', header=False)
# # needs csv detection
# # append mode mode='a', header=False
# # cut from DataFrame line columns=['checked_utc', 'subreddit', 'subscribers']

submissions_results = []
submissions = list(api.search_submissions(
  subreddit = subreddit_name,
  filter=['id', 'permalink', 'created_utc', 'author', 'title', 'selftext', 'score', 'score_ratio', 'num_comments'],
  after = start_epoch,
  before = end_epoch
))
print(len(submissions))
# for submission in submissions:
#   if submission is None:
#     print("No Submissions!")
#     break
#   else:
#     row = [submission.id, submission.permalink, datetime.fromtimestamp(submission.created_utc), submission.author, submission.title.encode('ascii', 'ignore').decode(), submission.selftext.encode('ascii', 'ignore').decode(), submission.score, submission.upvote_ratio, submission.num_comments]
#     submissions_results.append(row)
# df = pd.DataFrame(submissions_results, columns=['id', 'permalink', 'created_utc', 'author', 'title', 'selftext', 'score', 'score_ratio', 'num_comments'])
# df.to_csv(f'{subreddit_name}-{start_epoch}_to_{end_epoch}-submissions.csv', encoding='utf-8', index=False)
# submissions_df = pd.read_csv(f"{subreddit_name}-{start_epoch}_to_{end_epoch}-submissions.csv", parse_dates=["created_utc"], index_col=2)
# submissions_df['created_utc'] = pd.to_datetime(df['created_utc'],unit='s')
# # submissions_df.set_index('created_utc')
# # submissions_df['Date'] = submissions_df['Date'].dt.tz_localize('US/Eastern').dt.tz_convert('UTC')

comments_results = []
comments = list(api.search_comments(
  subreddit = subreddit_name,
  filter = ['id', 'permalink', 'created_utc', 'author', 'body', 'score'],
  after = start_epoch,
  before = end_epoch
))

print(len(comments))
# for comment in comments:
#   if comment is None:
#     print("No Comments!")
#     break
#   else:
#     row = [comment.id, comment.permalink, datetime.fromtimestamp(comment.created_utc), comment.author, comment.body.encode('ascii', 'ignore').decode(), comment.score]
#     comments_results.append(row)
# df = pd.DataFrame(comments_results, columns=['id', 'permalink', 'created_utc', 'author', 'body', 'score'])
# df.to_csv(f'{subreddit_name}-{start_epoch}_to_{end_epoch}-comments.csv', encoding='utf-8', index=False)
# comments_df = pd.read_csv(f"{subreddit_name}-{start_epoch}_to_{end_epoch}-comments.csv", parse_dates=["created_utc"], index_col=2)
# comments_df['created_utc'] = pd.to_datetime(df['created_utc'],unit='s')
# # comments_df.set_index('created_utc')
# # comments_df['Date'] = comments_df['Date'].dt.tz_localize('US/Eastern').dt.tz_convert('UTC')

# def plot_submissions_and_comments_by_weekday(df, df2):
#   """Creates a vertical bar plot with the percentage of
#   submissions and comments by weekday.
#   Parameters
#   ----------
#   df : pandas.DataFrame
#       The submissions DataFrame.
#   df2 : pandas.DataFrame
#       The comments DataFrame.
#   """

#   # Days of the week in English.
#   labels = ["Monday", "Tuesday", "Wednesday",
#             "Thursday", "Friday", "Saturday", "Sunday"]

#   # These will be used for calculating percentages.
#   total = len(df)
#   total2 = len(df2)

#   # 0 to 6 (Monday to Sunday).
#   submissions_weekdays = {i: 0 for i in range(0, 7)}
#   comments_weekdays = {i: 0 for i in range(0, 7)}

#   # We filter the DataFrames and set each weekday value equal to its number of records.
#   for k, v in submissions_weekdays.items():
#       submissions_weekdays[k] = len(df[df.index.weekday == k])

#   for k, v in comments_weekdays.items():
#       comments_weekdays[k] = len(df2[df2.index.weekday == k])

#   # The first set of vertical bars have a little offset to the left.
#   # This is so the next set of bars can fit in the same place.
#   bars = plt.bar([i - 0.2 for i in submissions_weekdays.keys()], [(i / total) * 100 for i in submissions_weekdays.values()], 0.4, color="#1565c0", linewidth=0)

#   # This loop creates small texts with the absolute values above each bar.
#   for bar in bars:
#       height = bar.get_height()
#       real_value = int((height * total) / 100)

#       plt.text(bar.get_x() + bar.get_width()/2.0, height,
#                 "{:,}".format(real_value), ha="center", va="bottom")

#   # This set of bars have a little offset to the right so they can fit
#   # with the previous ones.
#   bars2 = plt.bar([i + 0.2 for i in comments_weekdays.keys()], [(i / total2) * 100 for i in comments_weekdays.values()], 0.4, color="#f9a825", linewidth=0)

#   # This loop creates small texts with the absolute values above each bar (second set of bars).
#   for bar2 in bars2:
#       height2 = bar2.get_height()
#       real_value2 = int((height2 * total2) / 100)

#       plt.text(bar2.get_x() + bar2.get_width()/2.0, height2,
#                 "{:,}".format(real_value2), ha="center", va="bottom")

#   # We remove the top and right spines.
#   plt.gca().spines["top"].set_visible(False)
#   plt.gca().spines["right"].set_visible(False)

#   # For the xticks we use the previously defined English weekdays.
#   plt.xticks(list(submissions_weekdays.keys()), labels)

#   # We add final customizations.
#   plt.xlabel("Day of the Week")
#   plt.ylabel("Percentage")
#   plt.title(f"/r/{subreddit_name}'s Submissions and Comments by Day between {start_year}/{start_month}/{start_day} to {end_year}/{end_month}/{end_day}")
#   plt.legend(["Submissions", "Comments"])
#   plt.tight_layout()
#   plt.savefig(f"{subreddit_name}-submissionsandcommentsbyday_{start_year}-{start_month}-{start_day}-to-{end_year}-{end_month}-{end_day}.png", facecolor="#222222")

# def get_insights(df, df2):
#   """Prints several interesting insights.
#   Parameters
#   ----------
#   df : pandas.DataFrame
#       The submissions DataFrame.
#   df2 : pandas.DataFrame
#       The comments DataFrame.
#   """

#   # Get DataFrame totals.
#   print("Total submissions:", len(df))
#   print("Total comments:", len(df2))

#   # Get unique submitters and commenters.
#   submitters_set = set(df.groupby("author").count().index.tolist())
#   commenters_set = set(df2.groupby("author").count().index.tolist())

#   print("Total Submitters:", len(submitters_set))
#   print("Total Commenters:", len(commenters_set))

#   print("Common Submitters and Commenters:", len(submitters_set.intersection(commenters_set)))

#   print("Not common submitters:", len(submitters_set.difference(commenters_set)))
#   print("Not common commenters:", len(commenters_set.difference(submitters_set)))

#   print("\Submissions stats:\n")
#   resampled_submissions = df.resample("D").count()
#   print("Most submissions on:", resampled_submissions.idxmax()["author"])
#   print("Least submissions on:", resampled_submissions.idxmin()["author"])
#   print(resampled_submissions.describe())

#   print("\nComments stats:\n")
#   resampled_comments = df2.resample("D").count()
#   print("Most comments on:", resampled_comments.idxmax()["author"])
#   print("Least comments on:", resampled_comments.idxmin()["author"])
#   print(resampled_comments.describe())

# def get_most_common_submitters(df):
#   """Prints the 20 most frequent submitters.
#   Parameters
#   ----------
#   df : pandas.DataFrame
#       The submissions DataFrame.
#   """

#   # Optional: Remove the [deleted] user.
#   df.drop(df[df["author"] == "[deleted]"].index, inplace=True)

#   df = df["author"].value_counts()[0:20]
#   print(df)


# def get_most_common_commenters(df):
#   """Prints the 20 most frequent commenters.
#   Parameters
#   ----------
#   df : pandas.DataFrame
#       The comments DataFrame.
#   """

#   # Optional: Remove the [deleted] user.
#   df.drop(df[df["author"] == "[deleted]"].index, inplace=True)

#   df = df["author"].value_counts()[0:20]
#   print(df)

# get_insights(df=submissions_df, df2=comments_df)
# plot_submissions_and_comments_by_weekday(df=submissions_df, df2=comments_df)
# # get_most_common_submitters(df=submissions_df)
# # get_most_common_commenters(df=comments_df)