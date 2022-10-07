from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
import os
import requests
from rest_framework.response import Response
from mainapp.models import Post, Comment
from datetime import datetime, timezone

base_url = os.getenv('BASE_URL')

headers = {
    'Content-Type': 'application/json'
}


class TopNewsView(APIView):
    permission_classes = (AllowAny, )

    def get(self, *args):
        """
        get first 100 posts
        """
        path = 'newstories.json'
        url = base_url + path
        try:
            res = requests.get(url, headers=headers)
            if res.status_code == 200:
                all_posts = res.json()[:20]
                if all_posts:
                    source = 'HR'
                    posts = self.posts_in_detail(all_posts, source)
                news_response = posts
            else:
                news_response = res.text
        except Exception as e:
            return Response(str(e))
        return Response(news_response)

    def posts_in_detail(self, all_posts, source):
        """
        save and return detail of posts
        ** receives list of post_ids as all_posts
        """
        posts_list = []
        for post_id in all_posts:
            path = f'item/{post_id}.json'
            url = base_url + path
            try:
                res = requests.get(url, headers=headers)
                if res.status_code==200:
                    print(res.text)
                    res_json = res.json()
                    res_time = datetime.fromtimestamp(res_json.get('time'), timezone.utc)
                    post_obj = Post(
                            post_id=res_json.get('id'),
                            title=res_json.get('title'),
                            type=res_json.get('type'),
                            text=res_json.get('text'),
                            url=res_json.get('url'),
                            score=res_json.get('score'),
                            deleted=res_json.get('deleted', False),
                            time=res_time,
                            descendant=res_json.get('descendants'),
                            author=res_json.get('by'),
                            source=source
                        )
                    posts_list.append(post_obj)
                    if 'kids' in res_json:
                        res_json['kids'] = self.get_kids(res_json.get('kids'), post_obj)
                        posts_list.append(res_json)
            except Exception as e:
                print(str(e))

        if posts_list:
            Comment.objects.bulk_create(posts_list)
            return "saved succesfully", True
        return posts_list


    def get_kids(self, kids, post):
        """
        return all kids (comments) in posts
        """
        kid_list = []
        error = []
        for kid_id in kids:
            path = f'item/{kid_id}.json'
            url = base_url + path
            try:
                res = requests.get(url, headers=headers)
                if res.status_code == 200:
                    res_json = res.json()
                    res_time = datetime.fromtimestamp(res_json.get('time'), timezone.utc)
                    comment_obj = Comment(
                                    comment_id=res_json['id'],
                                    text=res_json['text'],
                                    type=res_json['type'],
                                    post=post,
                                    time=res_time,
                                    author=res_json['by']
                                )
                    kid_list.append(comment_obj)

                    # recursive - for comments within comments
                    if 'kids' in res_json:
                        import pdb
                        pdb.set_trace()
                        self.get_kids(res_json.get('kids'), comment_obj)
            except Exception as e:
                error.append(str(e))
        
        
        if kid_list:
            Comment.objects.bulk_create(kid_list)
            return "saved succesfully", True
        return error