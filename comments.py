import praw
from praw.exceptions import RedditAPIException
from prawcore.exceptions import PrawcoreException
import json
from datetime import datetime, timezone
import requests
import time
from slack import WebClient
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
#import os

def slack_comment():
    print(f"Comment on: *<https://reddit.com{comment.permalink}|{comment.submission.title}>* by <https://reddit.com/u/{comment.author.name}|{comment.author.name}>\n*Posted*: <!date^{round(comment.created_utc)}^{{date_short_pretty}} {{time}}|{comment.created_utc_format}>")
    # client = WebClient(token=slack_token)
    # client.chat_postMessage(
    # channel = slack_channel,
    # blocks = [
    #     {
    #         "type": "section",
    #         "text": {
    #             "type": "mrkdwn",
    #             "text": f"Comment on: *<https://reddit.com{comment.permalink}|{comment.submission.title}>* by <https://reddit.com/u/{comment.author.name}|{comment.author.name}>\n*Posted*: <!date^{round(comment.created_utc)}^{{date_short_pretty}} {{time}}|{comment.created_utc_format}>"
    #         }
    #         },
    #         {
    #             "type": "divider"
    #         },
    #         {
    #             "type": "section",
    #             "text": {
    #                 "type": "mrkdwn",
    #                 "text": f"{comment.body_short}..."
    #             }
    #         },
    #         {
    #             "type": "context",
    #             "elements": [
    #                 {
    #                 "type": "mrkdwn",
    #                 "text": f"{sentiment_outcome}"
    #                 }
    #             ]
    #         }
    #     ]
    # )
    return

def heartbeat():
    try:
        requests.get("https://hc-ping.com/42bb23fb-68fb-4b7a-b933-fda65e30e5fe", timeout=10)
    except requests.RequestException as e:
        # Log ping failure here...
        print("Ping failed: %s" % e)

config = json.load(open('config.json'))
analyzer = SentimentIntensityAnalyzer()

## FOR WHEN DOCKERIZED
#os.environ['client-id']
#os.environ['client-secret']
#os.environ['username']
#os.environ['password']
#os.environ['user-agent']
#os.environ['query']
#os.environ['subreddit']
#os.environ['token']
#os.environ['channel']

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
        for comment in reddit.subreddit(subreddit_name).stream.comments(pause_after=1, skip_existing=True):
            if comment is None:
                continue
            normalized_body = comment.body.lower()
            if query in normalized_body:
                comment.created_utc_format = datetime.fromtimestamp(comment.created_utc, tz=timezone.utc).isoformat()
                comment.body_short = comment.body[:280]
                print("Created: {}, Comment of: {}. Excerpt: {}... Upvotes: {}, Link: reddit.com{}".format(comment.created_utc_format, comment.submission.title, comment.body_short, comment.score, comment.permalink))
                compound_score = analyzer.polarity_scores(comment.body)["compound"]
                if compound_score > 0.5:
                    sentiment_outcome = ":slightly_smiling_face: Seems Positive"
                    slack_comment()
                elif compound_score < 0:
                    sentiment_outcome = ":disappointed: Seems *Negative*"
                    slack_comment()
                else:
                    sentiment_outcome = "¯\_(ツ)_/¯ Sorry I couldn't detect a substantial sentiment"
                    slack_comment()
    except RedditAPIException as exception:
        print("error - waiting 5 seconds and trying again")
        time.sleep(5)
        continue
    except PrawcoreException as e:
        print("error - waiting 5 seconds and trying again")
        time.sleep(5)
        continue
    