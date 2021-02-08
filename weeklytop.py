import praw
from praw.exceptions import RedditAPIException
from prawcore.exceptions import PrawcoreException
import json
from datetime import datetime, timezone
import requests
import time
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

def load_config():
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
    global reddit, query, subreddit_name, slack_token, slack_channel, config, scan_count, posts_from, sort_by
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
    scan_count = config['reddit']['scan_count']
    posts_from = config['reddit']['posts_from']
    sort_by = config['reddit']['sort_by']
    return reddit, query, subreddit_name, slack_token, slack_channel, config, scan_count, posts_from, sort_by

def slack_comment(text_1, text_2, text_3, divide):
    client = WebClient(token=slack_token)
    message = json.load(open("msg_template.json", "r"))
    if divide == False:
        message[1]["type"] = ""
    message[0]["text"]["text"] = text_1
    message[2]["text"]["text"] = text_2
    message[3]["elements"]["text"] = text_3
    client.chat_postMessage(channel = slack_channel, blocks = message)
    return

def heartbeat(good_state, info):
    if good_state == True:
        requests.get(f"https://hc-ping.com/{config['healthcheck']['uuid']}", timeout=10)
    else:
        requests.post(f"https://hc-ping.com/{config['healthcheck']['uuid']}/fail", data=info)
    return

while True:
    try:
        scan_count=0
        submissions_list = []
        load_config()
        for submission in reddit.subreddit(subreddit_name).top(f"{posts_from}"):
            if submission is None:
                text_1 = f"There are no more {sort_by} results in /r/{config['reddit']['subreddit']} this {posts_from}"
                slack_comment(text_1=text_1, text_2="", text_3="", divide=False)
                print("reseting and exiting")
                submissions_list.clear()
                heartbeat(good_state=True, info="Success")
                exit()
            else:
                submission_dict = {"submission_url": "", "submission_title": "", "submission_author_name": "", "submission_score": "", "submission_upvote_ratio": "", "submission_num_comments": "", "submission_created_utc": "", "submission_created_utc_format": ""}
                submission.created_utc_format = datetime.fromtimestamp(submission.created_utc, tz=timezone.utc).isoformat()
                print(f"Order: {len(submissions_list)} - Created: {submission.created_utc_format}, Title: {submission.title}, Upvotes: {submission.score}, Ratio: {submission.upvote_ratio}, Comments: {submission.num_comments}")
                submission_dict.update({"submission_url": f"{submission.url}", "submission_title": f"{submission.title}", "submission_author_name": f"{submission.author.name}", "submission_score": f"{submission.score}", "submission_upvote_ratio": f"{submission.upvote_ratio}", "submission_num_comments": f"{submission.num_comments}", "submission_created_utc": f"{round(submission.created_utc)}", "submission_created_utc_format": f"{submission.created_utc_format}"})
                submissions_list.append(submission_dict)
                text_1 = f"*<{submissions_list['submission_url']}|{submissions_list['submission_title']}>* by <https://reddit.com/u/{submissions_list['submission_author_name']}|{submissions_list['submission_author_name']}>\n*Upvotes*: {submissions_list['submission_score']} *|* *Upvote Ratio*: {submissions_list['submission_upvote_ratio']} *|* *Comments*: {submissions_list['submission_num_comments']} *|* *Posted*: <!date^{submissions_list['submission_created_utc']}^{{date_short_pretty}} {{time}}|{submissions_list['submission_created_utc_format']}>"
                slack_comment(text_1=text_1, text_2="", text_3="", divide=False)
                if len(submissions_list) == scan_count or len(submissions_list) == len(list(reddit.subreddit(subreddit_name).top(f"{posts_from}"))):
                    message = f"Below are this {posts_from}'s _Top {scan_count}_ *{sort_by}* posts in /r/{config['reddit']['subreddit']} :sports_medal:"
                    slack_comment(text_1=message, text_2="", text_3="", divide=True)
                    for i in range(len(submissions_list)):
                        message = f"*<{submissions_list[i]['submission_url']}|{submissions_list[i]['submission_title']}>* by <https://reddit.com/u/{submissions_list[i]['submission_author_name']}|{submissions_list[i]['submission_author_name']}>\n*Upvotes*: {submissions_list[i]['submission_score']} *|* *Upvote Ratio*: {submissions_list[i]['submission_upvote_ratio']} *|* *Comments*: {submissions_list[i]['submission_num_comments']} *|* *Posted*: <!date^{submissions_list[i]['submission_created_utc']}^{{date_short_pretty}} {{time}}|{submissions_list[i]['submission_created_utc_format']}>"
                        slack_comment(text_1=message, text_2="", text_3="")
                    heartbeat(good_state=True, info="Success")
                    print("reseting and exiting")
                    submissions_list.clear()
                    exit()
                else:
                    continue
    except RedditAPIException as e:
        print(f"ErrorMSG - {e}\nWaiting 5 seconds and trying again")
        heartbeat(good_state=False, info=f"{e}")
        time.sleep(5)
        continue
    except PrawcoreException as e:
        print(f"ErrorMSG - {e}\nWaiting 5 seconds and trying again")
        heartbeat(good_state=False, info=f"{e}")
        time.sleep(5)
        continue
    except SlackApiError as e:
        print(f"ErrorMSG - {e}\nWaiting 5 seconds and trying again")
        heartbeat(good_state=False, info=f"{e}")
        time.sleep(5)
        continue
    except Exception as e:
        print(f"ErrorMSG - {e}\nWaiting 5 seconds and trying again")
        heartbeat(good_state=False, info=f"{e}")
        time.sleep(5)
        quit()