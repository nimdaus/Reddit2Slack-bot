import praw
from praw.exceptions import RedditAPIException
from prawcore.exceptions import PrawcoreException
import json
from datetime import datetime, timezone
import requests
import time
from slack import WebClient
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

#Load config and declare specific variables
config = json.load(open('config.json'))
analyzer = SentimentIntensityAnalyzer()

reddit = praw.Reddit(
    client_id=config['reddit']['client-id'],
    client_secret=config['reddit']['client-secret'],
    username=config['reddit']['username'],
    password=config['reddit']['password'],
    user_agent=config['reddit']['user_agent'])

query = config['reddit']['query']
subreddit_name = config['reddit']['subreddit']
slack_token = config['slack']['token']
slack_channel = config['slack']['channel']

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
                    sentiment_outcome = ":slightly_smiling_face: Seems *Positive*"
                    client = WebClient(token=slack_token)
                    client.chat_postMessage(
                    channel = slack_channel,
                    blocks = [
                        {
                            "type": "section",
                            "text": {
                                "type": "mrkdwn",
                                "text": f"*<{submission.url}|{submission.title}>* by <https://reddit.com/u/{submission.author.name}|{submission.author.name}> *|* *Posted*: <!date^{round(submission.created_utc)}^{{date_short_pretty}} {{time}}|{submission.created_utc_format}>"
                            }
                            },
                            {
                                "type": "divider"
                            },
                            {
                                "type": "section",
                                "text": {
                                    "type": "mrkdwn",
                                    "text": f"{submission.selftext}"
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
                elif compound_score < 0:
                    sentiment_outcome = ":dissappointed: Seems *Negative*"
                    client = WebClient(token=slack_token)
                    client.chat_postMessage(
                    channel = slack_channel,
                    blocks = [
                        {
                            "type": "section",
                            "text": {
                                "type": "mrkdwn",
                                "text": f"*<{submission.url}|{submission.title}>* by <https://reddit.com/u/{submission.author.name}|{submission.author.name}> *|* *Posted*: <!date^{round(submission.created_utc)}^{{date_short_pretty}} {{time}}|{submission.created_utc_format}>"
                            }
                            },
                            {
                                "type": "divider"
                            },
                            {
                                "type": "section",
                                "text": {
                                    "type": "mrkdwn",
                                    "text": f"{submission.selftext}"
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
                else:
                    sentiment_outcome = "¯\_(ツ)_/¯ Sorry I couldn't detect a substantial sentiment"
                    client = WebClient(token=slack_token)
                    client.chat_postMessage(
                    channel = slack_channel,
                    blocks = [
                        {
                            "type": "section",
                            "text": {
                                "type": "mrkdwn",
                                "text": f"*<{submission.url}|{submission.title}>* by <https://reddit.com/u/{submission.author.name}|{submission.author.name}> *|* *Posted*: <!date^{round(submission.created_utc)}^{{date_short_pretty}} {{time}}|{submission.created_utc_format}>"
                            }
                            },
                            {
                                "type": "divider"
                            },
                            {
                                "type": "section",
                                "text": {
                                    "type": "mrkdwn",
                                    "text": f"{submission.selftext}"
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
    except RedditAPIException as exception:
        print("error - waiting 5 seconds and trying again")
        time.sleep(5)
        continue
    except PrawcoreException as e:
        print("error - waiting 5 seconds and trying again")
        time.sleep(5)
        continue