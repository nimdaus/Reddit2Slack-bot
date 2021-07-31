from django.db import models

# Create your models here.
class Subreddits(models.Model):
    subreddit_id = models.TextField(primary_key=True) #PK ##2gmzqe
    display_name = models.TextField() #
    description = models.TextField() #
    created_utc = models.FloatField() #

class Subreddits_Subscribers(models.Model):
    id = models.AutoField(primary_key=True) #PK
    subreddit_id = models.ForeignKey(Subreddits, on_delete=models.RESTRICT) #FK
    updated_utc = models.FloatField() #self-made
    subscribers = models.IntegerField() #

#lower priority
class Subreddits_Wikis(models.Model):
    id = models.AutoField(primary_key=True) #PK
    subreddit_id = models.ForeignKey(Subreddits, on_delete=models.RESTRICT) #FK
    updated_utc = models.FloatField()
    name = models.TextField()
    revision_date = models.FloatField()
    last_editor = models.TextField()
    content_md = models.TextField()

#lower priority
class Redditors(models.Model):
    redditor_id = models.TextField(primary_key=True) #PK  '''2gmzqe'''
    name = models.TextField()
    created_utc = models.FloatField() #
    has_verified_email = models.BooleanField()
    updated_utc = models.FloatField() #self-made
    comment_karma = models.IntegerField()
    link_karma = models.IntegerField()
    is_gold = models.BooleanField() # '''True/False?'''
    is_mod = models.BooleanField() # '''True/False?'''

class Submissions(models.Model):
    submission_id = models.TextField(primary_key=True) #PK '''2gmzqe'''
    subreddit_id = models.ForeignKey(Subreddits, on_delete=models.RESTRICT) #FK
    created_utc = models.FloatField()
    title = models.TextField() 
    author_id = models.ForeignKey(Redditors, on_delete=models.RESTRICT)
    self_text = models.TextField()
    link_flair_text = models.TextField()
    updated_utc = models.FloatField(blank=True, null=True)
    distinguished = models.BooleanField(blank=True, null=True) 
    edited = models.BooleanField()
    score = models.IntegerField(blank=True, null=True)
    upvote_ratio = models.DecimalField(blank=True, null=True)
    is_original_content = models.BooleanField()
    permalink = models.TextField()
    # Needs Poll_data

class Submissions_Detail(models.Model):
    id = models.AutoField(primary_key=True) #PK
    submission_id = models.ForeignKey(Submissions, on_delete=models.RESTRICT)
    polarity = models.FloatField()
    subjectivity = models.FloatField()
    neg = models.FloatField()
    neu = models.FloatField()
    pos = models.FloatField()
    compound = models.FloatField()
    overall = models.TextField()

class Comments(models.Model):
    comment_id = models.TextField(primary_key=True) #PK '''2gmzqe'''
    subreddit_id = models.ForeignKey(Subreddits, on_delete=models.RESTRICT) #FK
    submission_id = models.ForeignKey(Submissions, on_delete=models.RESTRICT) #FK
    parent_id = models.TextField(blank=True, null=True)
    created_utc = models.FloatField() #
    author_id = models.ForeignKey(Redditors, on_delete=models.RESTRICT)
    body = models.TextField() #
    is_submitter = models.BooleanField() # '''True/False?'''
    updated_utc = models.FloatField(blank=True, null=True)
    distinguished = models.BooleanField(blank=True, null=True)
    score = models.IntegerField(blank=True, null=True)
    permalink = models.TextField() #

class Comments_Detail(models.Model):
    id = models.AutoField(primary_key=True) #PK
    comment_id = models.ForeignKey(Comments, on_delete=models.RESTRICT)
    polarity = models.FloatField()
    subjectivity = models.FloatField()
    neg = models.FloatField()
    neu = models.FloatField()
    pos = models.FloatField()
    compound = models.FloatField()
    overall = models.TextField()

class Reddit_Config(models.Model):
    id = models.AutoField(primary_key=True) #PK
    name = models.TextField()
    client_id = models.TextField()
    client_secret = models.TextField() 
    username = models.TextField() 
    password = models.TextField() 
    user_agent = models.TextField()

    '''
    from django.contrib.auth.hashers import make_password
    password = make_password('somepass@123')
    '''

class Relay_Config(models.Model):
    type_choices = (
        ("Webhook"),
        ("Slack"),   
    )
    id = models.AutoField(primary_key=True) #PK
    name = models.TextField()
    type = models.CharField(choices=type_choices)
    url = models.URLField()
    channel = models.TextField()
    token = models.TextField()
