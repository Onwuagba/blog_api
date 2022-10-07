from celery import shared_task
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
import os
import requests
from rest_framework.response import Response

base_url = os.getenv('BASE_URL')

headers = {
    'Content-Type': 'application/json'
}

@shared_task()
def get_news():
    """
    get first 100 posts
    """
    path = 'newstories.json'
    url = base_url + path
    res = requests.get(url, headers=headers)
    all_posts = res.json()[:100]
    if all_posts:
        posts = posts_in_detail(all_posts)
    return Response(posts)

def posts_in_detail(all_posts):
    """
    return all posts in detail
    """
    posts_list = []
    for post_id in all_posts:
        path = f'/item/{post_id}.json'
        url = base_url + path
        res = requests.get(url, headers=headers)
        res_json = res.json()
        if 'kids' in res_json:
            res_json['kids'] = get_kids(res_json.get('kids'))
        posts_list.append(res_json)
    return posts_list

def get_kids(kids):
    """
    return all kids (comments) in posts
    """
    kid_list = []
    for kid_id in kids:
        path = f'/item/{kid_id}.json'
        url = base_url + path
        res = requests.get(url, headers=headers)
        res_json = res.json()
        kid_list.append(res_json)
    return kid_list