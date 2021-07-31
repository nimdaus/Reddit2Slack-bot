"""socialarr URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from ingest.views(
    ingest_view,
)

from analyze.views(
    analyze_view,
    subreddit_view,
    subreddit_subscribers_view,
    subreddit_wiki_view,
    submission_view,
    submission_detail_view,
    comment_view,
    comment_detail_view,
    redditor_view,
)

from relay.views(
    relay_view,
)

from report.views(
    report_view,
)

from update.views(
    report_view,
)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('analyze/', analyze_view),
    path('relay/', relay_view),
    path('report/', report_view),
    #
    path('ingest/', ingest_view),
    path('custom/', custom_view),
    path('feed/', feed_view),
    path('feed/<str>/<int>-<int>', feed_view), #how to do integer?
    

    path('subreddit/<str:pk>/', subreddit_view), #consider re_path for regex lookups re_path(r'^title/(?P<param>[a-zA-Z0-9-]+)/$', TitlePage.as_view(), name='title')
    path('subreddit_subscribers/<int:pk>/', subreddit_subscribers_view),
    path('subreddit_wiki/<int:pk>/', subreddit_wiki_view),
    path('submission/<int:pk>/', submission_view),
    path('submission_detail/<int:pk>/', submission_detail_view),
    path('comment/<int:pk>/', comment_view),
    path('comment_detail/<int:pk>/', comment_detail_view),
    path('redditor/<int:pk>/', redditor_view),
    #
    path('/', status_view),
    path('stopstart/', stopstart_view),
    path('reload/', reload_view),
    path('reset/', reset_view),
    path('restart/', restart_view),
    #
    path('something/', _view),
]
