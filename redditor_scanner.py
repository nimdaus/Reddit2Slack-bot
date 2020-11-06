from psaw import PushshiftAPI
import datetime as dt
import praw
from praw.exceptions import RedditAPIException
from prawcore.exceptions import PrawcoreException
import json
from datetime import datetime, timezone
import requests
import time
from slack import WebClient

## FOR WHEN DOCKERIZED
#client_id = os.environ['client_id']
#client_secret = os.environ['client_secret']
#username = os.environ['username']
#password = os.environ['password']
#user_agent = os.environ['user_agent']
#uredditor = os.environ['uredditor']
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

api = PushshiftAPI()

'''
age of account
verified email?
reddit post vs comment karma
last 3 comments + score + sentiment
last 3 posts + score + sentiment
context line: I'm busy collecting info, more on this later.
'''
uredditor = "Diamond_Cut"

user = reddit.redditor(f'{uredditor}')
user.created_utc_format = datetime.fromtimestamp(user.created_utc, tz=timezone.utc).isoformat()
print(user.created_utc_format)
print(user.has_verified_email)
print(f"Post Karma: {user.link_karma}")
print(f"Link Karma: {user.comment_karma}")
for comment in reddit.redditor(f'{uredditor}').comments.new(limit=3):
    print(comment.body[:180])
for submission in reddit.redditor(f'{uredditor}').submissions.new(limit=3):
    print(submission.selftext[:180])

# start_epoch = int(dt.datetime(2020, 1, 1).timestamp())
# #after=start_epoch
# result = api.redditor_subreddit_activity(f'{uredditor}')
# print(result)