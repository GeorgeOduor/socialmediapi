from django.db import models


# Create your models here.

class SocialMediaDataset(models.Model):
    Account = models.CharField(max_length=15, null=True)
    Month = models.CharField(max_length=15, null=True)
    Date = models.CharField(max_length=15, null=True)
    Day = models.CharField(max_length=15, null=True)
    Post = models.TextField(max_length=1000, null=True)
    Format = models.CharField(max_length=50, null=True)
    Impressions = models.IntegerField(null=True)
    ClickThroughrate = models.DecimalField(max_digits=50, decimal_places=20, null=True)
    Retweets_Shares = models.IntegerField(null=True)
    Likes = models.IntegerField(null=True)
    Mediaviews = models.IntegerField(null=True)
    Linkclicks = models.IntegerField(null=True)
    Detailexpands = models.IntegerField(null=True)
    Hashtagclicks = models.IntegerField(null=True)
    Userprofileclicks = models.IntegerField(null=True)
    Mediaengagements = models.IntegerField(null=True)
    Totalengagement = models.IntegerField(null=True)
    Engagements = models.IntegerField(null=True)
    Follows = models.IntegerField(null=True)
    Replies = models.IntegerField(null=True)
    Fballclicks = models.IntegerField(null=True)
    Time = models.IntegerField(null=True)
    Totalengagement2 = models.IntegerField(null=True)
    PostLength = models.IntegerField(null=True)
    Hashtags = models.IntegerField(null=True)
    With_hash = models.IntegerField(null=True)
    Mentions = models.IntegerField(null=True)
    With_mentions = models.IntegerField(null=True)
    Quater = models.CharField(max_length=2, null=True)
    Word_count = models.IntegerField(null=True)

    def __str__(self):
        return str(self.Post)
