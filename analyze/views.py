from django.shortcuts import render
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import render

from ingest.models import Subreddits, Subreddit_Subscribers, Subreddit_Wiki, Submissions, Comments, Redditor

# Create your views here.
def subreddit_view(request, pk,  *args, **kwargs):
    try:
        obj = Subreddits.objects.get(id=id)
    except Subreddits.DoesNotExist:
        raise Http404
    return render(request, "x.html", {"object":obj})

    ''' if "api" in request.path then return jsonresponse '''

def subreddit_subscribers_view(request, *args, **kwargs):
    return

def subreddit_wiki_view(request, *args, **kwargs):
    return

def submission_view(request, *args, **kwargs):
    return

def comment_view(request, *args, **kwargs):
    return

def redditor_view(request, *args, **kwargs):
    return

def search_view(request, *args, **kwargs):
    query - request.GET.get('q')
    qs = <model>.objects.filter(title_icontains=query[0])
    return

def sniper(request, *args, **kwargs):
    '''
    use batch of reddit accounts to downvote / upvote / gild

    '''
    return

def sherlock(request, *args, **kwargs):
    '''
    lookup redditor elsewhere
    
    '''
    return

def redditor_view(request, *args, **kwargs):
    return