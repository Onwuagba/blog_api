from celery import shared_task
import os
import requests
from rest_framework.response import Response
from mainapp.models import Post, Comment
from datetime import datetime, timezone
import pytz

base_url = os.getenv('BASE_URL')

headers = {
    'Content-Type': 'application/json'
}

@shared_task()
def get_news():
    print('CELERY: get_news')
    """
    Get latest 100 from Hackerank if no news in Post DB else pull latest news
    """
    if Post.objects.exists():
        print('something in post')
        limit = None
        res = get_hackernews(limit)
    else:
        print('nothing in posts')
        limit = 100
        res = get_hackernews(limit)
    print("response in main", res)
    return res


def get_hackernews(limit):
    """
    Return list of post_ids from Hackernew
    """
    print ("celery entered top100")
    path = 'newstories.json'    
    url = base_url + path
    try:
        res = requests.get(url, headers=headers)
        if res.status_code == 200:
            if limit:
                all_posts = res.json()[:10]
            else:
                all_posts = res.json()
            news_source = "HR"
            news_response = posts_in_detail(all_posts, news_source)
        else:
            news_response = res.text
    except Exception as e:
        return str(e)
    return news_response


def get_latest_time():
    """
    Get the latest time from db to prevent entering old news
    """
    print ("celery entered latest time")
    utc=pytz.UTC
    try:
        latest_local_date = Post.objects.latest('time')
        latest_local_date = latest_local_date.time
        return latest_local_date
    except Exception:
        date_str = '1000-01-01 00:01:00' # set to an arbitrary date to allow for new entries in DB
        latest_local_date = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
        return utc.localize(latest_local_date)


def posts_in_detail(all_posts, source):
    """
    save posts to db
    ** receives list of post_ids as all_posts
    """
    print ("celery entered posts_in_detail")
    posts_list = []
    for post_id in all_posts:
        print("all posts", all_posts)
        path = f'item/{post_id}.json'
        url = base_url + path
        try:
            res = requests.get(url, headers=headers)
            if res.status_code==200:
                res_json = res.json()
                res_time = datetime.fromtimestamp(res_json.get('time'), timezone.utc)
                if get_latest_time() < res_time:
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
                        comment(res_json.get('kids'), post_obj, nested_comment=None)
                else:
                    break
        except Exception as e:
            print("Exception in posts_in_detail",str(e))

    if posts_list:
        print("posts for insert:", posts_list)
        try:
            Post.objects.bulk_create(posts_list)
        except Exception as e:
            return {"response":f"Error saving to db in post method {str(e)}"}
    return {"response":f"Post saved successfully"}


def comment(kids, post_obj, nested_comment):
    """
    return all comments in posts
    """
    print ("celery entered get_kids")
    kid_list = []
    for kid_id in kids:
        path = f'item/{kid_id}.json'
        url = base_url + path
        try:
            res = requests.get(url, headers=headers)
            if res.status_code == 200:
                res_json = res.json()
                res_time = datetime.fromtimestamp(res_json.get('time'), timezone.utc)
                comment_obj = Comment(
                                comment_id=res_json.get('id'),
                                text=res_json.get('text'),
                                type=res_json.get('type'),
                                post=post_obj,
                                nested_comment=nested_comment,
                                time=res_time,
                                author=res_json.get('by')
                            )
                kid_list.append(comment_obj)

                # recursive - for comments within comments
                if 'kids' in res_json:
                    comment(res_json.get('kids'), post_obj, comment_obj)
        except Exception as e:
            print("Exception in comment method",str(e))
    
    
    if kid_list:
        print("posts for insert in comment:", kid_list)
        try:
            Comment.objects.bulk_create(kid_list)
        except Exception as e:
            print("Error saving to db in comment method",str(e))
    return kid_list