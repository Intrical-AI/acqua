from collections import defaultdict


def decouple(obj, query: str):
    # recursive bounce
    cast_query = query.split('.')
    if len(cast_query) == 1 and cast_query[0] == '':
        yield obj
    else:
        inner = cast_query[0]
        rebuilt = '.'.join(cast_query[1:])
        if inner.endswith('[]'):
            inner = inner[:-2]
            for items in getattr(obj, inner):
                yield from decouple(items, rebuilt)
        else:
            yield from decouple(getattr(obj, inner), rebuilt)


def rec_dd():
    return defaultdict(rec_dd)


def nested_get(dic, keys):
    for key in keys:
        dic = dic.get(key, None)
        if dic is None:
            return None
    return dic
