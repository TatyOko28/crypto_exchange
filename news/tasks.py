from celery import shared_task
import requests
from django.utils import timezone
from .models import NewsArticle, NewsSource

@shared_task
def fetch_latest_news():
    """Tâche pour récupérer les dernières actualités crypto"""
    sources = NewsSource.objects.filter(is_active=True)
    
    for source in sources:
        try:
            if source.api_key:
                # Si la source nécessite une clé API
                headers = {'Authorization': f'Bearer {source.api_key}'}
            else:
                headers = {}
                
            response = requests.get(source.url, headers=headers)
            data = response.json()
            
            # Traitement des données selon la source
            if 'articles' in data:  # Format standard
                articles = data['articles']
                for article in articles:
                    NewsArticle.objects.get_or_create(
                        title=article.get('title'),
                        defaults={
                            'content': article.get('content', ''),
                            'summary': article.get('description', '')[:200],
                            'source': source,
                            'url': article.get('url', ''),
                            'image_url': article.get('urlToImage', ''),
                            'published_at': article.get('publishedAt', timezone.now())
                        }
                    )
                    
        except Exception as e:
            print(f"Error fetching news from {source.name}: {str(e)}")

@shared_task
def clean_old_news():
    """Tâche pour nettoyer les anciennes actualités"""
    # Supprimer les actualités de plus de 30 jours
    thirty_days_ago = timezone.now() - timezone.timedelta(days=30)
    NewsArticle.objects.filter(published_at__lt=thirty_days_ago).delete()

@shared_task
def update_featured_news():
    """Tâche pour mettre à jour les actualités en vedette"""
    # Sélectionner les actualités les plus vues des dernières 24h
    last_24h = timezone.now() - timezone.timedelta(hours=24)
    top_news = NewsArticle.objects.filter(
        published_at__gte=last_24h
    ).order_by('-view_count')[:5]
    
    # Mettre à jour le statut "featured"
    NewsArticle.objects.all().update(is_featured=False)
    for news in top_news:
        news.is_featured = True
        news.save()
    