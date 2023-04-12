from celery import shared_task
import os
import requests
from mainapp.models import Post, Comment
from datetime import datetime, timezone
import pytz

base_url = os.getenv("BASE_URL")

headers = {"Content-Type": "application/json"}


@shared_task()
def get_news():
    """
    Get latest 100 from Hackerank if no news in Post DB else pull latest news
    """
    limit = None if Post.objects.exists() else 100
    return get_hackernews(limit)


def get_hackernews(limit):
    """
    Return list of post_ids from Hackernews
    """
    path = "newstories.json"
    url = base_url + path
    try:
        res = requests.get(url, headers=headers)
        if res.status_code == 200:
            all_posts = res.json()[:limit] if limit else res.json()
            news_source = "HR"
            news_response = posts_in_detail(all_posts, news_source)
        else:
            news_response = res.text
    except Exception as ex:
        return str(ex)
    return news_response


def get_latest_time():
    """
    Get the latest time from db to prevent entering old news
    """
    utc = pytz.UTC
    try:
        latest_local_date = Post.objects.latest("time")
        latest_local_date = latest_local_date.time
        return latest_local_date
    except Exception:
        date_str = "1000-01-01 00:01:00"  # set to an arbitrary date to allow for new entries in DB
        latest_local_date = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
        return utc.localize(latest_local_date)


def posts_in_detail(all_posts, source):
    """
    save posts to db
    ** receives list of post_ids as all_posts
    """
    posts_list = []
    for post_id in all_posts:
        path = f"item/{post_id}.json"
        url = base_url + path
        try:
            res = requests.get(url, headers=headers)
            if res.status_code == 200:
                res_json = res.json()
                res_time = datetime.fromtimestamp(res_json.get("time"), timezone.utc)
                if get_latest_time() < res_time:
                    post_obj = Post(
                        post_id=res_json.get("id"),
                        title=res_json.get("title"),
                        type=res_json.get("type"),
                        text=res_json.get("text"),
                        url=res_json.get("url"),
                        score=res_json.get("score"),
                        deleted=res_json.get("deleted", False),
                        time=res_time,
                        descendant=res_json.get("descendants"),
                        author=res_json.get("by"),
                        source=source,
                    )
                    posts_list.append(post_obj)
                    if "kids" in res_json:
                        comment(res_json.get("kids"), post_obj, nested_comment=None)
                else:
                    break
        except Exception as e:
            print("Exception in posts_in_detail", e)
    if posts_list:
        try:
            Post.objects.bulk_create(posts_list)
        except Exception as e:
            return {"response": f"Error saving to db in post method {str(e)}"}
    return {"response": "Post saved successfully"}


def comment(kids, post_obj, nested_comment):
    """
    return all comments in posts
    """
    error = ""
    for kid_id in kids:
        path = f"item/{kid_id}.json"
        url = base_url + path
        try:
            res = requests.get(url, headers=headers)
            if res.status_code == 200:
                res_json = res.json()
                res_time = datetime.fromtimestamp(
                    res_json.get("time"),
                    timezone.utc)
                comment_obj = Comment(
                    comment_id=res_json.get("id"),
                    text=res_json.get("text"),
                    type=res_json.get("type"),
                    post=post_obj,
                    nested_comment=nested_comment,
                    time=res_time,
                    author=res_json.get("by"),
                )
                comment_obj.save()

                # recursive - for comments within comments
                if "kids" in res_json:
                    comment(res_json.get("kids"), post_obj, comment_obj)
        except Exception as e:
            error = str(e)

    if error:
        return error
    return "comment saved successfully"
