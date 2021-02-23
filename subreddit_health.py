''' IMPLEMENTATION
todays subscribers
last X subscribers

comparison of upvotes / downvotes

competitor mentions:
datto, solarwinds, kaseya, connectwise

product mentions:
bcdr, backup; datto, veeam, kaseya, unitrends, solarwinds, acronis
rmm; datto, drmm, solarwinds, n-central, ncentral, kaseya, VSA, automate
psa; datto, autotask, connectwise, BMS, kaseya, 
networking; datto, openmesh, meraki, ubiquiti
'''

import praw
from praw.exceptions import RedditAPIException
from prawcore.exceptions import PrawcoreException
from psaw import PushshiftAPI
from datetime import datetime, timezone, date
import datetime as dt
import time
import requests
import json
import csv
import pandas as pd
from pandas.plotting import register_matplotlib_converters
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns
from PIL import Image
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

''' START CONFIGURATION '''


#start_year = os.environ['start_year']
#start_month = os.environ['start_month']
#start_day = os.environ['start_day']
#end_year = os.environ['end_year']
#end_month = os.environ['end_month']
#end_day = os.environ['end_day']
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
    user_agent=config['reddit']['user_agent']
    )

slack_token = config['slack']['token']
slack_channel = config['slack']['channel']
client = WebClient(token=slack_token)
register_matplotlib_converters()

api = PushshiftAPI(reddit)
subreddit_name = "msp"
start_year = 2020
start_month = 11
start_day = 9
start_epoch = int(dt.datetime(start_year,start_month,start_day).timestamp())
end_year = 2020
end_month = 11
end_day = 14
end_epoch = int(dt.datetime(end_year,end_month,end_day).timestamp())
''' END CONFIGURATION '''

''' START STYLING SETTINGS '''
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
''' END STYLING SETTINGS '''

''' START FUNCTION SPACE '''
def plot_submissions_and_comments_by_weekday(df, df2):
    """"Creates a vertical bar plot with the percentage of submissions and comments by weekday."""
    # Days of the week in English.
    labels = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

    # df['created_utc'] = pd.to_datetime(df['created_utc'],unit='s')
    # df2['created_utc'] = pd.to_datetime(df2['created_utc'],unit='s')

    # These will be used for calculating percentages.
    total = len(df)
    total2 = len(df2)

    # 0 to 6 (Monday to Sunday).
    submissions_weekdays = {i: 0 for i in range(0, 7)}
    comments_weekdays = {i: 0 for i in range(0, 7)}

    # We filter the DataFrames and set each weekday value equal to its number of records.
    for k, v in submissions_weekdays.items():
        submissions_weekdays[k] = len(df[df.index.weekday == k])

    for k, v in comments_weekdays.items():
        comments_weekdays[k] = len(df2[df2.index.weekday == k])

    # The first set of vertical bars have a little offset to the left.
    # This is so the next set of bars can fit in the same place.
    bars = plt.bar([i - 0.2 for i in submissions_weekdays.keys()], [(i / total) * 100 for i in submissions_weekdays.values()], 0.4, color="#1565c0", linewidth=0)

    # This loop creates small texts with the absolute values above each bar.
    for bar in bars:
        height = bar.get_height()
        real_value = int((height * total) / 100)

    plt.text(bar.get_x() + bar.get_width()/2.0, height, "{:,}".format(real_value), ha="center", va="bottom")

    # This set of bars have a little offset to the right so they can fit
    # with the previous ones.
    bars2 = plt.bar([i + 0.2 for i in comments_weekdays.keys()], [(i / total2) * 100 for i in comments_weekdays.values()], 0.4, color="#f9a825", linewidth=0)

    # This loop creates small texts with the absolute values above each bar (second set of bars).
    for bar2 in bars2:
        height2 = bar2.get_height()
        real_value2 = int((height2 * total2) / 100)

    plt.text(bar2.get_x() + bar2.get_width()/2.0, height2, "{:,}".format(real_value2), ha="center", va="bottom")

    # We remove the top and right spines.
    plt.gca().spines["top"].set_visible(False)
    plt.gca().spines["right"].set_visible(False)

    # For the xticks we use the previously defined English weekdays.
    plt.xticks(list(submissions_weekdays.keys()), labels)

    # We add final customizations.
    plt.xlabel("Day of the Week")
    plt.ylabel("Percentage")
    plt.title(f"/r/{subreddit_name}'s Submissions and Comments by Day between {start_year}/{start_month}/{start_day} to {end_year}/{end_month}/{end_day}")
    plt.legend(["Submissions", "Comments"])
    plt.tight_layout()
    plt.savefig(f"{subreddit_name}-submissionsandcommentsbyday_{start_year}-{start_month}-{start_day}-to-{end_year}-{end_month}-{end_day}.png", facecolor="#222222")

# def get_insights(df, df2):
#     """Totals and a couple of other things"""
#     # Get DataFrame totals.
#     total_submissions = len(df)
#     total_comments = len(df2)

#     # Get unique submitters and commenters.
#     submitters_set = set(df.groupby("author").count().index.tolist())
#     commenters_set = set(df2.groupby("author").count().index.tolist())

#     total_submitters = len(submitters_set)
#     total_commenters = len(commenters_set)
#     common_subers_comers = len(submitters_set.intersection(commenters_set))

# '''add support for how many!'''
# def get_most_common_submitters(df):
#     # Optional: Remove the [deleted] user.
#     # df.drop(df[df["author"] == "[deleted]"].index, inplace=True)
#     sub_counts_df = df["author"].value_counts()[0:20]
#     print(sub_counts_df)
# '''add support for how many!'''
# def get_most_common_commenters(df,how_many):
#     # Optional: Remove the [deleted] user.
#     # df.drop(df[df["author"] == "[deleted]"].index, inplace=True)
#     com_counts_df = df["author"].value_counts()[0:20]
#     print(com_counts_df)

def data_df_csv(reddit_type,list_to_df,remove_spaces,set_column_title):
    df = pd.DataFrame(list_to_df, columns=set_column_title)
    df[remove_spaces].replace(r'\s+|\\n', ' ', regex=True, inplace=True)
    df.to_csv(f'{subreddit_name}-{start_epoch}_to_{end_epoch}-{reddit_type}.csv', encoding='utf-8', index=False)
    return
''' END FUNCTION SPACE '''

''' START PROGRAM SPACE '''
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

for submission in submissions:
    if submission is None:
        print("No Submissions!")
    break
else:
    row = [submission.id, submission.permalink, datetime.fromtimestamp(submission.created_utc), submission.author, submission.title.encode('ascii', 'ignore').decode(), submission.selftext.encode('ascii', 'ignore').decode(), submission.score, submission.upvote_ratio, submission.num_comments]
    submissions_results.append(row)
# df = pd.DataFrame(submissions_results, columns=['id', 'permalink', 'created_utc', 'author', 'title', 'selftext', 'score', 'score_ratio', 'num_comments'])
# df['selftext'].replace(r'\s+|\\n', ' ', regex=True, inplace=True)
# df.to_csv(f'{subreddit_name}-{start_epoch}_to_{end_epoch}-submissions.csv', encoding='utf-8', index=False)
# submissions_df = pd.read_csv(f"{subreddit_name}-{start_epoch}_to_{end_epoch}-submissions.csv", parse_dates=["created_utc"], index_col=["created_utc"])
data_df_csv(reddit_type="submissions",list_to_df=submissions_results,remove_spaces='selftext',set_column_title=['id', 'permalink', 'created_utc', 'author', 'title', 'selftext', 'score', 'score_ratio', 'num_comments'])
submissions_df = pd.read_csv(f"{subreddit_name}-{start_epoch}_to_{end_epoch}-submissions.csv", parse_dates=["created_utc"], index_col=["created_utc"])


comments_results = []
comments = list(api.search_comments(
    subreddit = subreddit_name,
    filter = ['id', 'permalink', 'created_utc', 'author', 'body', 'score'],
    after = start_epoch,
    before = end_epoch
))

for comment in comments:
    if comment is None:
        print("No Comments!")
    break
else:
    row = [comment.id, comment.permalink, datetime.fromtimestamp(comment.created_utc), comment.author, comment.body.encode('ascii', 'ignore').decode(), comment.score]
    comments_results.append(row)
# df = pd.DataFrame(comments_results, columns=['id', 'permalink', 'created_utc', 'author', 'body', 'score'])
# df['body'].replace(r'\s+|\\n', ' ', regex=True, inplace=True) 
# df.to_csv(f'{subreddit_name}-{start_epoch}_to_{end_epoch}-comments.csv', encoding='utf-8', index=False)
# 
data_df_csv(reddit_type="comments",list_to_df=comments_results,remove_spaces='body',set_column_title=['id', 'permalink', 'created_utc', 'author', 'body', 'score'])
comments_df = pd.read_csv(f"{subreddit_name}-{start_epoch}_to_{end_epoch}-comments.csv", parse_dates=["created_utc"], index_col=["created_utc"])

# df.df["selftext"].str.lower().split().explode().value_counts()  
# labels = ["datto", "connectwise", "solarwinds", "kaseya", "veeam", "acronis", "ubiquity", "meraki"]

'''function list'''
how_many=3
'''cloned out the function because of crunch'''
# Get DataFrame totals.
total_submissions = len(submissions_df)
total_comments = len(comments_df)
# Get unique submitters and commenters.
submitters_set = set(submissions_df.groupby("author").count().index.tolist())
commenters_set = set(comments_df.groupby("author").count().index.tolist())
total_submitters = len(submitters_set)
total_commenters = len(commenters_set)
common_subers_comers = len(submitters_set.intersection(commenters_set))

sub_counts_df = submissions_df["author"].value_counts()[0:3]

com_counts_df = comments_df["author"].value_counts()[0:3]

'''Manually entered subscriber counts'''
subscribers_now = reddit.subreddit(subreddit_name).subscribers
subscribers_then = 87421

client.chat_postMessage(
channel = slack_channel,
blocks = [
    {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": f"*/r/{subreddit_name}'s After Action Report for period {start_year}/{start_month}/{start_day} to {end_year}/{end_month}/{end_day}*"
            }
    },
    {
        "type": "divider"
    },
    {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": f"This week we saw *{total_submissions}* Submissions by *{total_submitters}* Submitters\n_Alongside that..._ We saw *{total_comments}* Comments from *{total_commenters}* Commenters\n**Of whom *{common_subers_comers}* both commented and submitted"
        }
    },
    {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": f"Subscribers went from from *{subscribers_then:,}* to *{subscribers_now:,}*\nThis represents a *{(((subscribers_now - subscribers_then) / subscribers_then)):.2%}* change"
        }
    },
    {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": f"By count, the *Top 3 Submitters* were:\n{sub_counts_df.to_string()}\n\nBy count, the *Top 3 Commenters* were:\n{com_counts_df.to_string()}"
        }
    }
  ]
)
plot_submissions_and_comments_by_weekday(df=submissions_df, df2=comments_df)
'''insert slack message'''
try:
    response = client.files_upload(    
        file=f"./{subreddit_name}-submissionsandcommentsbyday_{start_year}-{start_month}-{start_day}-to-{end_year}-{end_month}-{end_day}.png",
        initial_comment=f"*Time analysis of /r/{subreddit_name}'s activity*",
        channels=f'{slack_channel}'
    )
except SlackApiError as e:
    # You will get a SlackApiError if "ok" is False
    assert e.response["ok"] is False
    assert e.response["error"]  # str like 'invalid_auth', 'channel_not_found'
    print(f"Got an error: {e.response['error']}")
''' END PROGRAM SPACE '''