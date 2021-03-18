def decouple(obj, query:str):
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