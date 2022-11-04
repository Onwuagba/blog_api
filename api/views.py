from django.shortcuts import render
from rest_framework.generics import ListAPIView
from rest_framework.views import APIView
from rest_framework.permissions import  IsAuthenticatedOrReadOnly, AllowAny
from rest_framework.response import Response
from api.serializers import PostSerializer, PostDetailSerializer, CommentSerializer
from rest_framework import status, filters
from django.http import JsonResponse
from mainapp.models import Post, Comment
import json, random
from datetime import datetime
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.exceptions import ValidationError
from urllib.parse import urlparse
from django.core.validators import URLValidator

# Create your views here.

class PostListView(ListAPIView):
    permission_classes = (IsAuthenticatedOrReadOnly,)
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['source','deleted','type','author']
    search_fields = ["title", "author", "text"]
    ordering_fields = ['time', 'date_added']

    
    def delete_obj(self, source):
        try:
            queryset = Post.objects.filter(source=source)
        except Exception as e:
            raise ValidationError(str(e))
        return queryset

    def get(self, *args):
        try:
            queryset = self.filter_queryset(self.get_queryset())
            page = self.paginate_queryset(queryset)
            if page:
                serializer = self.serializer_class(page,  many=True)
                query_response = self.get_paginated_response(serializer.data)
                res = query_response.data
                re_status = 'success'
                res_status = status.HTTP_200_OK
            else:
                res = "No data matching query"
                re_status = 'failed'
                res_status = status.HTTP_400_BAD_REQUEST
        except Exception as e:
            res = e.args[0]
            re_status = 'failed'
            res_status = status.HTTP_400_BAD_REQUEST
            
        return Response({
                'message':res,
                'status':re_status,
            }, status=res_status)
    
    
    def post(self, request):

        def validate_url(url):
            if url:
                try:
                    validator = URLValidator()
                    validator(url) 
                except:
                    url = 'http://' + url

            return url

        def get_object(request):
            data = request.data
            data['url'] = validate_url(data.get('url'))
            data['source'] = 'API'
            data['post_id'] = random.randint(0,99999999)
            data['time'] = datetime.now()
            return data

        serializer = self.serializer_class(data=get_object(request))
        try:
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                res = 'Post saved successful.'
                re_status = 'success'
                res_status = status.HTTP_201_CREATED
            else:
                res = serializer.errors
                re_status = 'failed'
                res_status = status.HTTP_400_BAD_REQUEST
        except Exception as e:
            res = e.args[0]
            re_status = 'failed'
            res_status = status.HTTP_400_BAD_REQUEST
        
        return Response({
                'message':res,
                'status':re_status,
            }, status=res_status)
    
    def delete(self, request, **kwargs):

        try:
            news_source = 'API'
            news_obj = self.delete_obj(news_source)
            news_obj.delete()
            res = 'All internal posts have been deleted successfully'
            re_status = 'success'
            res_status = status.HTTP_200_OK
        except Exception as e:
            res = e.args[0]
            re_status = 'failed'
            res_status = status.HTTP_400_BAD_REQUEST

        return JsonResponse({
            'message':res,
            'status':re_status,
            }, status=res_status)

            
class PostDetailView(APIView):
    """
    Retrieve, update and delete post instance
    """
    permission_classes = (IsAuthenticatedOrReadOnly,)
    serializer_class = PostDetailSerializer

    def get_object(self, id, source=None):
        try:
            if source:
                return Post.objects.get(post_id=id, source=source)
            else:
                return Post.objects.get(post_id=id) # used for get method
        except:
            raise ValidationError("Invalid post id")
    

    def get(self, request, **kwargs):
        id = kwargs.get('id')
        try:
            queryset = self.get_object(id)
            if queryset:
                serializer = self.serializer_class(queryset)
                res={'comment_count':queryset.comment_count()}
                res.update(serializer.data)
                re_status = 'success'
                res_status = status.HTTP_200_OK
            else:
                res = "No data matching query"
                re_status = 'failed'
                res_status = status.HTTP_400_BAD_REQUEST
        except Exception as e:
            res = e.args[0]
            re_status = 'failed'
            res_status = status.HTTP_400_BAD_REQUEST
            
        return Response({
                'message':res,
                'status':re_status,
            }, status=res_status)


    def patch(self, request, **kwargs):
        id = kwargs.get('id')

        try:
            news_source="API"
            news_obj = self.get_object(id, news_source)
            serializer = self.serializer_class(news_obj, data=request.data, partial=True)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                res = 'Post updated successfully'
                re_status = 'success'
                res_status = status.HTTP_200_OK
            else:
                res = serializer.errors
                re_status = 'failed'
                res_status = status.HTTP_400_BAD_REQUEST
        except Exception as e:
            res = e.args[0]
            re_status = 'failed'
            res_status = status.HTTP_400_BAD_REQUEST

        return JsonResponse({
            'message':res,
            'status':re_status,
            }, status=res_status)


    def delete(self, request, **kwargs):
        id = kwargs.get('id')

        try:
            news_source="API"
            news_obj = self.get_object(id, news_source)
            news_obj.delete()
            res = 'Post deleted successfully'
            re_status = 'success'
            res_status = status.HTTP_200_OK
        except Exception as e:
            res = e.args[0]
            re_status = 'failed'
            res_status = status.HTTP_400_BAD_REQUEST

        return JsonResponse({
            'message':res,
            'status':re_status,
            }, status=res_status)

class CommentDetailView(ListAPIView):
    permission_classes = (AllowAny,)
    serializer_class = CommentSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['type','author']
    search_fields = ["title", "author", "text"]
    ordering_fields = ['time', 'date_added']

    def get_queryset(self, id):
        try:
            # return only parent comment
            return Comment.objects.filter(post=id, nested_comment=None)
        except:
            raise ValidationError("Invalid post id")

    def get(self, request, **kwargs):
        id = kwargs.get('id')

        try:
            queryset = self.filter_queryset(self.get_queryset(id))
            page = self.paginate_queryset(queryset)
            if page:
                serializer = self.serializer_class(page,  many=True)
                query_response = self.get_paginated_response(serializer.data)
                res = query_response.data
                re_status = 'success'
                res_status = status.HTTP_200_OK
            else:
                res = "No data matching query"
                re_status = 'failed'
                res_status = status.HTTP_400_BAD_REQUEST
        except Exception as e:
            res = e.args[0]
            re_status = 'failed'
            res_status = status.HTTP_400_BAD_REQUEST
            
        return Response({
                'message':res,
                'status':re_status,
            }, status=res_status)