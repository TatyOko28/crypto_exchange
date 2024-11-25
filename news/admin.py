from django.contrib import admin
from .models import NewsArticle, NewsSource, NewsCategory

@admin.register(NewsSource)
class NewsSourceAdmin(admin.ModelAdmin):
    list_display = ('name', 'url', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('name', 'url')

@admin.register(NewsCategory)
class NewsCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)

@admin.register(NewsArticle)
class NewsArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'source', 'news_category', 'author', 'published_at', 'is_featured')
    list_filter = ('is_featured', 'source', 'news_category')
    search_fields = ('title', 'content', 'summary')
    date_hierarchy = 'published_at'
    raw_id_fields = ('author', 'source', 'news_category')
    readonly_fields = ('view_count',)
