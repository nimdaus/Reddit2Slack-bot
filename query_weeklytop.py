import praw
from praw.exceptions import RedditAPIException
from prawcore.exceptions import PrawcoreException
import json
from datetime import datetime, timezone
import requests
import time
from slack import WebClient

#Load config and declare specific variables
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
posts_from = config['reddit']['posts_from']
sort_by = config['reddit']['sort_by']
counter = 0
submissions_list = []

while True:
    try:
        for submission in reddit.subreddit(subreddit_name).search(query, sort='relevance', time_filter='week'):
            if submission is None:
                #code for when there's < 3 topics with query

                #what if there's no top datto topic
                if counter = 0
                    client = WebClient(token=slack_token)
                    client.chat_postMessage(
                    channel = slack_channel,
                    blocks = [
                        {
                            "type": "section",
                            "text": {
                                "type": "mrkdwn",
                                "text": f"*Happy Friday!* There are no relevant results *{config['reddit']['query']} related* _Top 3 Posts_ in /r/{config['reddit']['subreddit']} :sports_medal:"
                                }
                        }
                
                #procedurally deal with 1/2/3 topics 
                continue

            submission_dict = {"submission_url": "", "submission_title": "", "submission_author_name": "", "submission_score": "", "submission_upvote_ratio": "", "submission_num_comments": "", "submission_created_utc": "", "submission_created_utc_format": ""}
            submission.created_utc_format = datetime.fromtimestamp(submission.created_utc, tz=timezone.utc).isoformat()
            print("Order: {} - Created: {}, Title: {}, Upvotes: {}, Ratio: {}, Comments: {}".format(counter, submission.created_utc_format, submission.title, submission.score, submission.upvote_ratio, submission.num_comments))
            counter += 1
            submission_dict.update({"submission_url": f"{submission.url}", "submission_title": f"{submission.title}", "submission_author_name": f"{submission.author.name}", "submission_score": f"{submission.score}", "submission_upvote_ratio": f"{submission.upvote_ratio}", "submission_num_comments": f"{submission.num_comments}", "submission_created_utc": f"{round(submission.created_utc)}", "submission_created_utc_format": f"{submission.created_utc_format}"})
            submissions_list.append(submission_dict)
            if counter > 2:
                client = WebClient(token=slack_token)
                client.chat_postMessage(
                channel = slack_channel,
                blocks = [
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"*Happy Friday!* Below are this week's *{config['reddit']['query']} related* _Top 3 Posts_ in /r/{config['reddit']['subreddit']} :sports_medal:"
                            }
                    },
                    {
                            "type": "divider"
                    },
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"*<{submissions_list[0]['submission_url']}|{submissions_list[0]['submission_title']}>* by <https://reddit.com/u/{submissions_list[0]['submission_author_name']}|{submissions_list[0]['submission_author_name']}>\n*Upvotes*: {submissions_list[0]['submission_score']} *|* *Upvote Ratio*: {submissions_list[0]['submission_upvote_ratio']} *|* *Comments*: {submissions_list[0]['submission_num_comments']} *|* *Posted*: <!date^{submissions_list[0]['submission_created_utc']}^{{date_short_pretty}} {{time}}|{submissions_list[0]['submission_created_utc_format']}>"
                            }
                        },
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"*<{submissions_list[1]['submission_url']}|{submissions_list[1]['submission_title']}>* by <https://reddit.com/u/{submissions_list[1]['submission_author_name']}|{submissions_list[1]['submission_author_name']}>\n*Upvotes*: {submissions_list[0]['submission_score']} *|* *Upvote Ratio*: {submissions_list[1]['submission_upvote_ratio']} *|* *Comments*: {submissions_list[1]['submission_num_comments']} *|* *Posted*: <!date^{submissions_list[1]['submission_created_utc']}^{{date_short_pretty}} {{time}}|{submissions_list[1]['submission_created_utc_format']}>"
                            }
                        },
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"*<{submissions_list[2]['submission_url']}|{submissions_list[2]['submission_title']}>* by <https://reddit.com/u/{submissions_list[2]['submission_author_name']}|{submissions_list[2]['submission_author_name']}>\n *Upvotes*: {submissions_list[2]['submission_score']} *|* *Upvote Ratio*: {submissions_list[2]['submission_upvote_ratio']} *|* *Comments*: {submissions_list[2]['submission_num_comments']} *|* *Posted*: <!date^{submissions_list[2]['submission_created_utc']}^{{date_short_pretty}} {{time}}|{submissions_list[2]['submission_created_utc_format']}>"
                            }
                        }
                    ]
                )
                print("reseting and sleeping until next week")
                counter = 0
                submissions_list.clear()
                time.sleep(604800)
    except RedditAPIException as exception:
        print("error - waiting 5 seconds and trying again")
        time.sleep(5)
        continue
    except PrawcoreException as e:
        print("error - waiting 5 seconds and trying again")
        time.sleep(5)
        continue