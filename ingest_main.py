#===== Core Config =====
''' Sub text '''

import sys
import os
sys.path.insert(0, f'{os.path.realpath(__file__)}')
os.environ['DJANGO_SETTINGS_MODULE'] = 'socialarr.settings'
import django
django.setup()
from ingest.models import Subreddits, Subreddits_Subscribers, Subreddits_Wikis, Submissions, Comments, Redditors
import requests
import praw
from praw.exceptions import RedditAPIException
from prawcore.exceptions import PrawcoreException
from datetime import datetime, time

#===== Core Functions =====
''' Sub text '''

def load_config():
	global reddit, named_subreddit, named_user
	named_subreddit = os.environ['SUBREDDIT']
	named_user = os.environ['REDDITOR']
	reddit = praw.Reddit(
		client_id = os.environ['CLIENT_ID'],
		client_secret = os.environ['CLIENT_SECRET'],
		username = os.environ['USERNAME'],
		password = os.environ['PASSWORD'],
		user_agent = os.environ['USER_AGENT'])
	return reddit, named_subreddit, named_user

def save_redditor(target_user):
	Redditors.objects.create(
		redditor_id = target_user.id,
		name = target_user.name,
		created_utc = target_user.created_utc,
		has_verified_email = target_user.has_verified_email,
		updated_utc = time.time(),
		comment_karma = target_user.comment_karma,
		link_karma = target_user.link_karma,
		is_gold = target_user.is_gold,
		is_mod = target_user.is_mod
	)
	return

def save_subreddit(target_subreddit):
	Subreddits.objects.create(
		subreddit_id = target_subreddit.id,
		display_name = target_subreddit.display_name,
		description = target_subreddit.description,
		created_utc = target_subreddit.created_utc
	)
	return

def save_subscribers(target_subreddit):
	global link_subreddit
	if Subreddits.objects.get(pk=target_subreddit.ID) == True:
		link_subreddit = Subreddits.objects.get(pk=target_subreddit.ID)
		Subreddits_Subscribers.objects.create(
			subreddit_id = link_subreddit,
			updated_utc = time.time(),
			subscribers = target_subreddit.subscribers
		)
	else:
		return "error"
	return

def save_wiki(wiki, target_id):
	global link_subreddit
	if Subreddits.objects.get(pk=target_subreddit.ID) == True:
		link_subreddit = Subreddits.objects.get(pk=target_subreddit.ID)
		Subreddits_Wikis.objects.create(
			subreddit_id = link_subreddit,
			#reddit.subreddit(target_subreddit).ID, #THIS IS FOREIGN KEY AND NEEDS SPECIAL CARE
			updated_utc = time.time(),
			name = wiki.name,
			revision_date = wiki.revision_date,
			last_editor = wiki(f"{wiki.name}").revision_by,
			content_md = wiki.content_md
		)
	else:
		return "error"
	return

def save_submission(submission):
	global link_subreddit, link_author
	if Subreddits.objects.get(pk=target_subreddit.ID) == True:
		link_subreddit = Subreddits.objects.get(pk=target_subreddit.ID)
		if Redditors.objects.get(pk=submission.author.id) == True:
			link_author = Redditors.objects.get(pk=submission.author.id)
			Submissions.objects.create(
				ID = submission.id,
				Subreddit_id = link_subreddit,
				#submission.subreddit_id, #THIS IS FOREIGN KEY AND NEEDS SPECIAL CARE
				created_utc = comment.created_utc,
				title = submission.title,
				author_id = link_author,
				#submission.author.name, #THIS IS FOREIGN KEY AND NEEDS SPECIAL CARE
				self_text = submission.self_text,
				link = submission.link_flair_text,
				updated_utc = time.time(),
				distinguished = submission.distinguished,
				edited = submission.edited,
				score = submission.score,
				upvote_ratio = submission.upvote_ratio,
				is_original_content = submission.is_original_content,
				permalink = submission.permalink
			)
		else:
			# Should be celery task
			target_user = reddit.redditor(f"{submission.author.name}")
			save_redditor(target_user)
			save_submission(submission)
			return "error"
	else:
		return "error"
	return

def save_comment(comment):
	global link_subreddit, link_submission, link_author
	if Subreddits.objects.get(pk=target_subreddit.ID) == True:
		link_subreddit = Subreddits.objects.get(pk=target_subreddit.ID)
		if Submissions.objects.get(pk=comment.link_id) == True:
			link_submission = Submissions.objects.get(pk=comment.link_id)
			if Redditors.objects.get(pk=comment.author.id) == True:
				link_author = Redditors.objects.get(pk=comment.author.id)
				parent_comment = comment.parent_id
				if parent_comment.startswith("t3_") == true:
					parent_comment = link_submission
				else:
					parent_comment = parent_comment[3:]
				Comments.objects.create(
					comment_id = comment.id,
					subreddit_id = link_subreddit,
					# comment.subreddit_id, #THIS IS FOREIGN KEY AND NEEDS SPECIAL CARE
					submission_id = link_submission,
					# comment.link_id, #THIS IS FOREIGN KEY AND NEEDS SPECIAL CARE
					parent_id = comment.parent_id,
					created_utc = comment.created_utc,
					author_id = comment.author.id, #THIS IS FOREIGN KEY AND NEEDS SPECIAL CARE
					body = comment.body,
					is_submitter = comment.is_submiter,
					permalink = comment.permalink,
					updated_utc = time.time(),
					distinguished = comment.distinguished,
					score = comment.score
				)

			else:
				# Should be celery task
				target_user = reddit.redditor(f"{comment.author.name}")
				save_redditor(target_user)
				save_comment(comment)
				return "error"
		else:
			# Should be celery task
			submission = reddit.submission(f"{comment.link_id}")
			save_submission(submission)
			save_comment(comment)
			return "error"
	else:
		return "error"
	return

#===== Core App =====
''' Sub text '''
	
while True:
	try:
		load_config()

		if os.environ['INGEST_TYPE'] == "Comments":
			for comment in reddit.subreddit(f"{target_subreddit}").stream.comments(pause_after=1, skip_existing=True):
				if comment is None:
					continue
				save_comment(comment)

		elif os.environ['INGEST_TYPE'] == "Submissions":
			for submission in reddit.subreddit(f"{target_subreddit}").stream.submissions(pause_after=1, skip_existing=True):
				if submission is None:
					continue
				save_submission(submission)

		elif os.environ['INGEST_TYPE'] == "Subreddit":
			target_subreddit = reddit.subreddit(f"{named_subreddit}")
			save_subreddit(target_subreddit)
			save_subscribers(target_subreddit)
			for wiki in reddit.subreddit(f"{target_subreddit}").wiki:
				save_wiki(wiki, target_subreddit)

		elif os.environ['INGEST_TYPE'] == "Redditor":
			target_user = reddit.redditor(f"{named_user}")
			save_redditor(target_user)

		elif os.environ['INGEST_TYPE'] == "Self":
			"this"
			"grab PMs"
		else:
			print("Marvin has no purpose")
			continue

	except RedditAPIException as e:
		print(f"ErrorMSG - {e}\nWaiting 5 seconds and trying again")
		#heartbeat(good_state = False, info = f"{e}")
		time.sleep(5)
		continue
	except PrawcoreException as e:
		print(f"ErrorMSG - {e}\nWaiting 5 seconds and trying again")
		#heartbeat(good_state = False, info = f"{e}")
		time.sleep(5)
		continue
	except Exception as e:
		print(f"ErrorMSG - {e}\nWaiting 5 seconds and trying again")
		#heartbeat(good_state = False, info = f"{e}")
		time.sleep(5)
		quit()