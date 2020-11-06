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

query = config['reddit']['query']
subreddit_name = config['reddit']['subreddit']
slack_token = config['slack']['token']
slack_channel = config['slack']['channel']
scan_count = 3
posts_from = 'week'
sort_by = 'relevance'
#keep this
scan_length = scan_count

submissions_list = []

def basic_slack(message):
    client = WebClient(token=slack_token)
    client.chat_postMessage(
    channel = slack_channel,
    blocks = [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"{message}"
                }
        }
    ]
    )
    return

def prelude_slack(message):
    client = WebClient(token=slack_token)
    client.chat_postMessage(
    channel = slack_channel,
    blocks = [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"{message}"
                }
        },
        {
                "type": "divider"
        }
    ]
    )
    return

def submission_slack(submissions_list):
    client = WebClient(token=slack_token)
    client.chat_postMessage(
    channel = slack_channel,
    blocks = [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*<{submissions_list['submission_url']}|{submissions_list['submission_title']}>* by <https://reddit.com/u/{submissions_list['submission_author_name']}|{submissions_list['submission_author_name']}>\n*Upvotes*: {submissions_list['submission_score']} *|* *Upvote Ratio*: {submissions_list['submission_upvote_ratio']} *|* *Comments*: {submissions_list['submission_num_comments']} *|* *Posted*: <!date^{submissions_list['submission_created_utc']}^{{date_short_pretty}} {{time}}|{submissions_list['submission_created_utc_format']}>"
                }
            }
    ]
    )
    return

while True:
    try:
        for submission in reddit.subreddit(subreddit_name).search(query, sort=sort_by, time_filter=posts_from):
            if submission is None:
                message = f"There are no more {sort_by} results for *{config['reddit']['query']}* in /r/{config['reddit']['subreddit']} this {posts_from}"
                basic_slack(message)
                print("reseting and exiting")
                submissions_list.clear()
                exit()
            else:
                submission_dict = {"submission_url": "", "submission_title": "", "submission_author_name": "", "submission_score": "", "submission_upvote_ratio": "", "submission_num_comments": "", "submission_created_utc": "", "submission_created_utc_format": ""}
                submission.created_utc_format = datetime.fromtimestamp(submission.created_utc, tz=timezone.utc).isoformat()
                print(f"Order: {len(submissions_list)} - Created: {submission.created_utc_format}, Title: {submission.title}, Upvotes: {submission.score}, Ratio: {submission.upvote_ratio}, Comments: {submission.num_comments}")
                submission_dict.update({"submission_url": f"{submission.url}", "submission_title": f"{submission.title}", "submission_author_name": f"{submission.author.name}", "submission_score": f"{submission.score}", "submission_upvote_ratio": f"{submission.upvote_ratio}", "submission_num_comments": f"{submission.num_comments}", "submission_created_utc": f"{round(submission.created_utc)}", "submission_created_utc_format": f"{submission.created_utc_format}"})
                submissions_list.append(submission_dict)
                if len(submissions_list) == scan_length or len(submissions_list) == len(list(reddit.subreddit(subreddit_name).search(query, sort=sort_by, time_filter=posts_from))):
                    #needs posts from updated for variable
                    message = f"Below are this {posts_from}'s *{config['reddit']['query']}* _Top {scan_count}_ *{sort_by}* posts in /r/{config['reddit']['subreddit']} :sports_medal:" 
                    prelude_slack(message)
                    for i in range(len(submissions_list)):
                        submission_slack(submissions_list = submissions_list[i])
                    print("reseting and exiting")
                    submissions_list.clear()
                    exit()
                else:
                    continue
    except RedditAPIException as e:
        print("error - waiting 5 seconds and trying again")
        time.sleep(5)
        continue
    except PrawcoreException as e:
        print("error - waiting 5 seconds and trying again")
        time.sleep(5)
        continue
    except Exception as e:
        print("Generic Error")
        continue