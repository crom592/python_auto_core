import json
from functools import reduce
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q

SCHEMA_FILED_EXCEPT = ['page', 'count_per_page']

def readQuery(request, key):
    if '[]' in key:
        value = request.GET.get(key, '[]')
        if value == '[]':
            value = [-1]
        elif value.startswith('['):
            value = json.loads(value)
        else:
            value = request.GET.getlist(key)
        key = key.replace('[]', '')
        return Q(**{key:value})
    elif key.endswith('__not'):
        value = request.GET.get(key)
        key = key.replace('__not', '')
        return ~Q(**{key:value})
    else:
        value = request.GET.get(key)
        if value == 'true':
            value = True
        elif value == 'false':
            value = False
        return Q(**{key:value})

def applyOption(request, queryset):
    where__or = [Q()]
    where__and = [Q()]
    used_keys = []
    logic = request.GET.get('logic')
    if logic:
        keys = logic.split('__OR__')
        for key in keys:
            used_keys.append(key)
            where__or.append(readQuery(request, key))
    for key in request.GET:
        if key in SCHEMA_FILED_EXCEPT: 
            continue
        elif key in used_keys:
            continue
        else:
            where__and.append(readQuery(request, key))
    return queryset.filter(
        reduce(lambda x, y: x | y, where__or),
        reduce(lambda x, y: x & y, where__and)
    ).distinct()

def applyPagination(queryset, serializer_class, page, count):
    count = int(count)
    paginator = Paginator(queryset, count)
    try:
        items = paginator.page(page)
    except PageNotAnInteger:
        items = paginator.page(1)
    except EmptyPage:
        items = paginator.page(paginator.num_pages)
    output = serializer_class(items, many=True).data
    return {
        'total_page': paginator.num_pages,
        'total_count': queryset.count(),
        'items': output
    }
