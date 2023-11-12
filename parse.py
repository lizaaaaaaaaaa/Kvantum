import feedparser
from urllib.parse import quote

def get_post(search) -> dict:
    post_dict = {}

    encoded_search = quote(search)

    url = f"https://habr.com/ru/rss/search/?q={encoded_search}&order_by=relevance&amp;target_type=posts&amp;hl=ru&amp;fl=ru&amp;fl=ru"

    feed = feedparser.parse(url)

    for entry in feed.entries:
        post_dict[entry.title] = entry.link
    
    return post_dict


