import os
import functools

from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.template.loader import get_template
from django.utils import simplejson

get_static = lambda url: os.path.join(settings.STATIC_URL, url)

def history():
    def history_decor(view):
        @functools.wraps(view)
        def _view(request, *args, **kwargs):
            data = view(request, *args, **kwargs)
            context = data["context"]
            tmpl = data["template"]
            tmpl_hist = data['template_hist'] if data.has_key("template_hist") else tmpl
            if data.has_key("media"):
                media = {
                    "js": [get_static(u) for u in data['media']['js']],
                    "css": [get_static(u) for u in data['media']['css']],
                }
            else:
                media = None
            state = data['state'] if data.has_key("state") else None
            title = data['title'] if data.has_key('title') else ""
            options = data['options'] if data.has_key("options") else None
            if request.META.has_key('HTTP_X_HISTORY'):
                response = get_template(tmpl_hist).render(RequestContext(request, context))
                json = simplejson.dumps({'response': response,
                                         'options': options,
                                         'media': media,
                                         'title': title,
                                         'state': state})
                return HttpResponse(json, mimetype="application/json")
            else:
                context_instance = RequestContext(request, {"media_dynamic": media,
                                                            "title": title,
                                                            "state": state})
                return render_to_response(tmpl, context, context_instance=context_instance)
        return _view
    return history_decor

def media_classes(request):
    return {
        'js_dynamic_class': settings.JS_DYNAMIC_CLASS,
        'css_dynamic_class': settings.CSS_DYNAMIC_CLASS,
    }
