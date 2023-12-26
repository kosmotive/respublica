def order_tuple_list(items):
    return sorted([tuple(item) for item in items], key = lambda item: str(item))
