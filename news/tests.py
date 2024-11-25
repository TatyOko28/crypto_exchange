from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from authentication.models import User
from .models import NewsArticle, NewsSource, NewsCategory
from datetime import datetime

class NewsArticleTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        self.source = NewsSource.objects.create(
            name='Test Source',
            url='https://test.com'
        )
        self.category = NewsCategory.objects.create(
            name='Cryptocurrency',
            slug='cryptocurrency'
        )
        self.article = NewsArticle.objects.create(
            title='Test Article',
            content='Test content',
            summary='Test summary',
            source=self.source,
            url='https://test.com/article',
            published_at=timezone.now()
        )
        self.article.categories.add(self.category)

    def test_get_news_list(self):
        url = reverse('news-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_get_news_detail(self):
        url = reverse('news-detail', kwargs={'slug': self.article.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Test Article')

    def test_news_category_filter(self):
        url = reverse('news-list')
        response = self.client.get(url, {'category': 'cryptocurrency'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_featured_news(self):
        self.article.is_featured = True
        self.article.save()
        url = reverse('news-featured')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

class NewsSourceTests(TestCase):
    def test_create_source(self):
        source = NewsSource.objects.create(
            name='Test Source',
            url='https://test.com'
        )
        self.assertEqual(str(source), 'Test Source')

class NewsCategoryTests(TestCase):
    def test_create_category(self):
        category = NewsCategory.objects.create(
            name='Test Category',
            slug='test-category'
        )
        self.assertEqual(str(category), 'Test Category')
