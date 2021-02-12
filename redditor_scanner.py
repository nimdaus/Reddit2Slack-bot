from psaw import PushshiftAPI
import praw
from praw.exceptions import RedditAPIException
from prawcore.exceptions import PrawcoreException
import json
from datetime import datetime, timezone
import requests
import time
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from flask import Flask, request, Response
from slackeventsapi import SlackEventAdapter

def load_config():
    global reddit, query, subreddit_name, slack_token, slack_channel, config, signing_secret
    config = json.load(open('config.json'))
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
    signing_secret = config['slack']['signing_secret']
    return reddit, query, subreddit_name, slack_token, slack_channel, config, signing_secret



# need to make the actual hunter a function
# function needs username as input
def reddit_hunter(uredditor):
    user = reddit.redditor(f'{uredditor}')
    age_utc = time.time() - user.created_utc
    age = age_utc / 60 / 60 / 24 / 365.25
    verified_email = user.has_verified_email
    has_gold = user.is_gold
    submission_karma = user.link_karma
    comment_karma = user.comment_karma

    six_months_ago = time.time() - 15780000
    user_submissions_6 = api.search_submissions(after=six_months_ago, subreddit=f'{subreddit_name}', author=f"{uredditor}", filter=['created_utc', 'url', 'author', 'title', 'subreddit'])
    subreddit_submissions_6 = len(list(user_submissions_6))
    user_comments_6 = api.search_comments(after=six_months_ago, subreddit=f'{subreddit_name}', author=f"{uredditor}", filter=['created_utc', 'url', 'author', 'subreddit'])
    subreddit_comments_6 = len(list(user_comments_6))

    three_years_ago = time.time() - 94608000
    user_submissions_3 = api.search_submissions(after=three_years_ago, subreddit=f'{subreddit_name}', author=f"{uredditor}", filter=['created_utc', 'url', 'author', 'title', 'subreddit'])
    subreddit_submissions_3 = len(list(user_submissions_3))
    user_comments_3 = api.search_comments(after=three_years_ago, subreddit=f'{subreddit_name}', author=f"{uredditor}", filter=['created_utc', 'url', 'author', 'subreddit'])
    subreddit_comments_3 = len(list(user_comments_3))
    return uredditor, age, verified_email, has_gold, submission_karma, comment_karma, subreddit_submissions_6, subreddit_comments_6, subreddit_submissions_3, subreddit_comments_3

def slack_message(uredditor, age, verified_email, has_gold, submission_karma, comment_karma, subreddit_submissions_6, subreddit_comments_6, subreddit_submissions_3, subreddit_comments_3):
    print(f"Scan Complete!")
    client = WebClient(token=slack_token)
    message = json.load(open("redditor_template.json", "r"))
    message[0]["text"]["text"] = f"Redditor: *<https://reddit.com/u/{uredditor}|{uredditor}>*\nAccount Age: *{age}*\nEmail Verified: *{verified_email}*\nKarma: *{submission_karma}* Submission and *{comment_karma}* Comment\nPremium: {has_gold}"
    message[2]["text"]["text"] = f"*Activity in /r/{subreddit_name}:*\n6 Month Activity: {subreddit_submissions_6} Submissions and {subreddit_comments_6} Comments\n3 Year Activity: {subreddit_submissions_3} Submissions and {subreddit_comments_3} Comments"
    message[3]["text"]["text"] = f""
    client.chat_postMessage(channel = slack_channel, blocks = message)
    return

load_config()
app = Flask(__name__)
slack_event_adapter = SlackEventAdapter(signing_secret,'/slack/events', app)
api = PushshiftAPI(reddit)
analyzer = SentimentIntensityAnalyzer()

@slack_event_adapter.on("message")
def message(payload):
    event = payload.get("event", {})
    channel_id =  event.get("channel")
    user_id = event.get('user')
    uredditor = event.get('text')
    reddit_hunter(uredditor)

    if BOT_ID != user_id:
        slack_message(uredditor=uredditor, age=age, verified_email, has_gold, submission_karma, comment_karma, subreddit_submissions_6, subreddit_comments_6, subreddit_submissions_3, subreddit_comments_3)

@app.route('/target', methods=['POST'])
def target():
    data = requestt.form
    uredditor = data.get('text')
    return Response(), 200


# except RedditAPIException as e:
#     print(f"ErrorMSG - {e}\nWaiting 5 seconds and trying again")
#     heartbeat(good_state=False, info=f"{e}")
#     time.sleep(5)
#     continue
# except PrawcoreException as e:
#     print(f"ErrorMSG - {e}\nWaiting 5 seconds and trying again")
#     heartbeat(good_state=False, info=f"{e}")
#     time.sleep(5)
#     continue
# except SlackApiError as e:
#     print(f"ErrorMSG - {e}\nWaiting 5 seconds and trying again")
#     heartbeat(good_state=False, info=f"{e}")
#     time.sleep(5)
#     continue
# except Exception as e:
#     print(f"ErrorMSG - {e}\nWaiting 5 seconds and trying again")
#     heartbeat(good_state=False, info=f"{e}")
#     time.sleep(5)
#     quit()

if __name__ == "__main__":
    app.run(debug=True)

# for comment in reddit.redditor(f'{uredditor}').comments.new(limit=3):
#     compound_score = analyzer.polarity_scores(comment.body)["compound"]
#     print(comment.body[:140])
#     print(comment.score)
#     print(compound_score)
# for comment in reddit.redditor(f'{uredditor}').comments.top(limit=3):
#     compound_score = analyzer.polarity_scores(comment.body)["compound"]
#     print(comment.body[:140])
#     print(comment.score)
#     print(compound_score)
# for submission in reddit.redditor(f'{uredditor}').submissions.new(limit=3):
#     compound_score = analyzer.polarity_scores(submission.selftext)["compound"]
#     print(submission.title[:140])
#     print(submission.selftext[:140])
#     print(submission.score)
#     print(compound_score)
# for submission in reddit.redditor(f'{uredditor}').submissions.top(limit=3):
#     compound_score = analyzer.polarity_scores(submission.selftext)["compound"]
#     print(submission.title[:140])
#     print(submission.selftext[:140])
#     print(submission.score)
#     print(compound_score)