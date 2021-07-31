from django.shortcuts import render
from django.http import Http404, HttpResponse
import re
from ingest.models import *
from datetime import datetime
import time

#===== WebApp =====
''' Sub text '''
def specific_view(request, name):
	'''
	/feed/subreddit/mmddyyyy-mmddyyyy
	/subreddit/subreddit/mmddyyyy-mmddyyyy
	/submission/subreddit/mmddyyyy-mmddyyyy
	/comment/subreddit/mmddyyyy-mmddyyyy

	HOW TO HANDLE SUBREDDIT ID? 

	'''
	target_subreddit = Subreddits.objects.get(display_name=name)
	if "feed" in request.path:
		before = re(request.path)
		before_dt = datetime.strptime(f'{before}', '%d/%m/%Y').timestamp()
		after = re(request.path)
		after_dt = datetime.strptime(f'{after}', '%d/%m/%Y').timestamp()
		qs_subreddits = Subreddits.objects.get(subreddit_id=pk, created_utc__range=(before_dt, after_dt))
		for subreddit in qs_subreddits:
			qs_submissions = Submissions.objects.select_related('Redditors').get(subreddit_id=pk, created_utc__range=(before_dt, after_dt)) #__gte "greater than or equal to" __lte "less than or equal to" __range=(x,y)
			for submission in qs_submissions:
				qs_comments = Comments.objects.select_related('Redditors').get(subreddit_id=pk, created_utc__range=(before_dt, after_dt))

	elif "subreddit" in request.path:
		before = re(request.path)
		before_dt = datetime.strptime(f'{before}', '%d/%m/%Y').timestamp()
		after = re(request.path)
		after_dt = datetime.strptime(f'{after}', '%d/%m/%Y').timestamp()
		qs = Subreddits.objects.select_related('Subreddits_Subscribers').get(subreddit_id=pk, updated_utc__range=(before_dt, after_dt))
	elif "submission" in request.path:
		before = re(request.path)
		before_dt = datetime.strptime(f'{before}', '%d/%m/%Y').timestamp()
		after = re(request.path)
		after_dt = datetime.strptime(f'{after}', '%d/%m/%Y').timestamp()
		qs = Submissions.objects.select_related('Redditors').get(subreddit_id=pk, created_utc__range=(before_dt, after_dt))
	elif "comment" in request.path:
		before = re(request.path)
		before_dt = datetime.strptime(f'{before}', '%d/%m/%Y').timestamp()
		after = re(request.path)
		after_dt = datetime.strptime(f'{after}', '%d/%m/%Y').timestamp()
		qs = Comments.objects.select_related('Redditors').get(subreddit_id=pk, created_utc__range=(before_dt, after_dt))
	else:
		return HttpResponse(status=404) #swap with raise Http404("does not exist or whatever")
	return render(request, 'view.html', qs)
	## need to handle the different qs objects; maybe a list of them LOL

def custom_view(request, pk):
	'''
	/feed/id
	/subreddit/id
	/submission/id
	/comment/id
	'''
	if "feed" in request.path:
		qs_subreddits = Subreddits.objects.get(subreddit_id=pk)
		for subreddit in qs_subreddits:
			qs_submissions = Submissions.objects.select_related('Redditors').get(subreddit_id=pk)
			for submission in qs_submissions:
				qs_comments = Comments.objects.select_related('Redditors').get(subreddit_id=pk)

	elif "subreddit" in request.path:
		qs = Subreddits.objects.select_related('Subreddits_Subscribers').get(subreddit_id=pk)
	elif "submission" in request.path:
		qs = Submissions.objects.select_related('Redditors').get(subreddit_id=pk)
	elif "comment" in request.path:
		qs = Comments.objects.select_related('Redditors').get(subreddit_id=pk)
	else:
		return HttpResponse(status=404) #swap with raise Http404("does not exist or whatever")
	return render(request, 'view.html', qs)
	## need to handle the different qs objects; maybe a list of them LOL

def feed_view(pk):
	before_dt = time.time() - 259200
	after_dt = time.time()
	qs_subreddits = Subreddits.objects.get(subreddit_id=pk, created_utc__range=(before_dt, after_dt))
	for subreddit in qs_subreddits:
		qs_submissions = Submissions.objects.select_related('Redditors').get(subreddit_id=pk, created_utc__range=(before_dt, after_dt)) #__gte "greater than or equal to" __lte "less than or equal to" __range=(x,y)
		for submission in qs_submissions:
			qs_comments = Comments.objects.select_related('Redditors').get(subreddit_id=pk, created_utc__range=(before_dt, after_dt))
	return


