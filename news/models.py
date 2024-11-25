from django.db import models
from django.conf import settings

class NewsSource(models.Model):
    name = models.CharField(max_length=100)
    url = models.URLField()
    api_key = models.CharField(max_length=100, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class NewsCategory(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "News Categories"

    def __str__(self):
        return self.name

class NewsArticle(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    summary = models.TextField(blank=True)
    source = models.ForeignKey(
        NewsSource, 
        on_delete=models.CASCADE,
        related_name='articles'
    )
    news_category = models.ForeignKey(
        NewsCategory, 
        on_delete=models.SET_NULL,
        null=True,
        related_name='articles'
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='news_articles'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    published_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_featured = models.BooleanField(default=False)
    view_count = models.IntegerField(default=0)

    class Meta:
        ordering = ['-published_at']

    def __str__(self):
        return self.title
