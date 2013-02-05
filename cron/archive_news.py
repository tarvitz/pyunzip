#!/usr/bin/env python
import lib
from datetime import datetime, timedelta
from apps.news.models import News


def archive_news(news):
    for n in news:
        n.archive()


if __name__ == '__main__':
    #make an archives
    now = datetime.now()
    td = timedelta(days=365)
    older = now - td
    news = News.objects.filter(date__lt=older)
    archive_news(news)
