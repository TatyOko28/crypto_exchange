from django.shortcuts import render
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from .models import NewsArticle, NewsSource, NewsCategory
from .serializers import NewsArticleSerializer, NewsSourceSerializer, NewsCategorySerializer
from .tasks import fetch_latest_news
from rest_framework.permissions import IsAuthenticated

class NewsArticleViewSet(viewsets.ModelViewSet):
    queryset = NewsArticle.objects.all()
    serializer_class = NewsArticleSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['category']

    def get_queryset(self):
        queryset = NewsArticle.objects.all()
        category = self.request.query_params.get('category', None)
        if category:
            queryset = queryset.filter(categories__slug=category)
        
        source = self.request.query_params.get('source', None)
        if source:
            queryset = queryset.filter(source__name=source)
        
        return queryset

    @action(detail=False)
    def featured(self, request):
        featured = self.get_queryset().filter(is_featured=True)
        serializer = self.get_serializer(featured, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def latest(self, request):
        latest_news = NewsArticle.objects.filter(
            published_at__lte=timezone.now()
        )[:10]
        serializer = self.get_serializer(latest_news, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.view_count += 1
        instance.save()
        return super().retrieve(request, *args, **kwargs)

class NewsCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = NewsCategory.objects.all()
    serializer_class = NewsCategorySerializer
    lookup_field = 'slug'
