from math import ceil
from django.core.paginator import Paginator, Page, InvalidPage, EmptyPage
from django.http import HttpRequest

class WindowNotValid(Exception):
    pass

class Paginate(object):
    def __init__(self, page, window=2):
        if isinstance(page, dict):
            self.num_pages = int(ceil(float(page['count'])/page['onpage']))
            self.current = page['page']
        else:
            self.num_pages = page.paginator.num_pages
            self.current = page.number
        current_revert = self.num_pages - self.current
        self.window = self.window_validate(window)
        self.start = self.current - self.window if self.current > self.window else 1
        self.end = self.current + self.window if current_revert > self.window else self.num_pages

    def window_validate(self, window):
        try:
            window = int(window)
        except ValueError:
            raise WindowNotValid('That window is not an integer')
        if window < 0:
            raise WindowNotValid('That window is less than 0')
        return window

    def _get_pages(self):
        if not hasattr(self, '_pages'):
            pages = [{'current': i == self.current, 'number': i} for i in range(self.start, self.end+1)]
            self._pages = pages
        return self._pages
    pages = property(_get_pages)

    def prev(self):
        return self.current - 1 if self.current > 1 else None

    def next(self):
        return self.current + 1 if self.current < self.num_pages else None

    def first(self):
        return 1 if self.start > 1 else None

    def last(self):
        return self.num_pages if self.end < self.num_pages else None

    def dots_left(self):
        pre_start = self.start - 1
        return pre_start if self.start > 1 and pre_start > 1 else None

    def dots_right(self):
        post_end = self.end + 1
        return post_end if self.end < self.num_pages and post_end < self.num_pages else None

    def wind_left(self):
        return start-2 if self.start > 1 else None

    def wind_right(self):
        return self.end - self.current if self.end < self.num_pages else None

    def serialize(self):
        return {"num_pages": self.num_pages,
                "window": self.window,
                "start": self.start,
                "end": self.end,
                "pages": self.pages,
                "next": self.next(),
                "prev": self.prev(),
                "last": self.last(),
                "dots_left": self.dots_left(),
                "dots_right": self.dots_right(),
                "wind_left": self.wind_left(),
                "wind_right": self.wind_right()}


def pager(queryset, request, onpage=10, window=3, page_get_param='page'):
    if isinstance(request, HttpRequest):
        if request.GET.has_key(page_get_param) and request.GET[page_get_param].isdigit():
            page = int(request.GET[page_get_param])
        else:
            page = 1
    else:
        page = request if isinstance(request, int) and request > 0 else 1
    paginator = Paginator(queryset, onpage)
    try:
        objects = paginator.page(page)
    except (EmptyPage, InvalidPage):
        objects = paginator.page(paginator.num_pages)
    paginate = Paginate(objects, window=window)
    return objects, paginate

