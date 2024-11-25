from rest_framework import serializers
from .models import NewsArticle, NewsSource, NewsCategory

class NewsCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsCategory
        fields = ['id', 'name', 'slug', 'description']

class NewsSourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsSource
        fields = ['id', 'name', 'url', 'is_active']

class NewsArticleSerializer(serializers.ModelSerializer):
    source = NewsSourceSerializer(read_only=True)
    category = NewsCategorySerializer(read_only=True)
    author_name = serializers.CharField(source='author.username', read_only=True)

    class Meta:
        model = NewsArticle
        fields = [
            'id', 
            'title',
            'content',
            'summary',
            'source',
            'category',
            'author_name',
            'published_at',
            'is_featured',
            'view_count'
        ] 