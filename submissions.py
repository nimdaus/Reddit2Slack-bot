import praw
from praw.exceptions import RedditAPIException
from prawcore.exceptions import PrawcoreException
import json
from datetime import datetime, timezone
import requests
import time
from slack import WebClient
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

def reddit_auth():
    reddit = praw.Reddit(
        client_id=config['reddit']['client-id'],
        client_secret=config['reddit']['client-secret'],
        username=config['reddit']['username'],
        password=config['reddit']['password'],
        user_agent=config['reddit']['user_agent'],
        query = config['reddit']['query'],
        subreddit_name = config['reddit']['subreddit'],
        slack_token = config['slack']['token'],
        slack_channel = config['slack']['channel'])
    return reddit

def submission_in_message(submission_in_list, sentiment_outcome):
    client = WebClient(token=slack_token)
    client.chat_postMessage(
    channel = slack_channel,
    blocks = [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*<{submission_in_list.url}|{submission_in_list.title}>* by <https://reddit.com/u/{submission_in_list.author.name}|{submission_in_list.author.name}> *|* *Posted*: <!date^{round(submission_in_list.created_utc)}^{{date_short_pretty}} {{time}}|{submission_in_list.created_utc_format}>"
            }
            },
            {
                "type": "divider"
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"{submission_in_list.selftext}"
                }
            },
            {
                "type": "context",
                "elements": [
                    {
                    "type": "mrkdwn",
                    "text": f"{sentiment_outcome}"
                    }
                ]
            }
        ]
    )
    return

#Load config and declare specific variables
config = json.load(open('config.json'))
reddit_auth(reddit)
analyzer = SentimentIntensityAnalyzer()

while True:
    try:
        for submission in reddit.subreddit(subreddit_name).stream.submissions(pause_after=1, skip_existing=True):
            if submission is None:
                continue
            normalized_title = submission.title.lower()
            if query in normalized_title:
                submission.created_utc_format = datetime.fromtimestamp(submission.created_utc, tz=timezone.utc).isoformat()
                print("Created: {}, Title: {}".format(submission.created_utc_format, submission.title))
                compound_score = analyzer.polarity.scores(submission.selftext)["compound"]
                if compound_score > 0.5:
                    sentiment = ":slightly_smiling_face: Seems *Positive*"
                    submission_in_message(submission_in_list=submission, sentiment_outcome=sentiment)
                elif compound_score < 0:
                    sentiment = ":dissappointed: Seems *Negative*"
                    submission_in_message(submission_in_list=submission, sentiment_outcome=sentiment)
                else:
                    sentiment = "¯\_(ツ)_/¯ Sorry I couldn't detect a substantial sentiment"
                    submission_in_message(submission_in_list=submission, sentiment_outcome=sentiment)
    except RedditAPIException as exception:
        print("error - waiting 5 seconds and trying again")
        time.sleep(5)
        continue
    except PrawcoreException as e:
        print("error - waiting 5 seconds and trying again")
        time.sleep(5)
        continue