from django.db import models


class TimeStamp(models.Model):
    date_added = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ['-date_added', '-date_updated']


class Post(TimeStamp):
    GEEKS_CHOICES =(
        ("API", "internalAPI"),
        ("HR", "Hackerank"),
    )

    post_id = models.IntegerField(unique=True, null=False, blank=False)
    title = models.CharField(max_length=150, unique=True, null=False, blank=False, db_index=True)
    type = models.CharField(max_length=12, null=False, blank=False)
    url = models.URLField(max_length=150, unique=True, null=False, blank=False)
    score = models.IntegerField(null=False, blank=False, default='0')
    deleted = models.BooleanField(default=False)
    time = models.DateTimeField()
    descendant = models.IntegerField(null=True, blank=True) # number of comments per post
    author = models.CharField(max_length=50, null=False, blank=False)
    source = models.CharField(max_length=3, choices=GEEKS_CHOICES)
    
    class Meta:
        ordering = ['time']

    def __str__(self):
        return self.post_id
    
    def type_count(self, type):
        return self.filter(type=type).count()

    def author_posts(self, author):
        return self.filter(author=author)


class Comment(TimeStamp):
    comment_id = models.IntegerField(unique=True, null=False, blank=False)
    text = models.TextField(null=False, blank=False)
    type = models.CharField(max_length=12, null=False, blank=False)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comment_post')
    time = models.DateTimeField()
    author = models.CharField(max_length=150, null=False, blank=False, db_index=True)

    def __str__(self):
        return self.comment_id
