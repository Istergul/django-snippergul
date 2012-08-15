def enumerate_lim(elements):
    last_index = len(elements) - 1
    for i, e in enumerate(elements):
        first = i == 0
        last = i == last_index
        yield i, e, first, last
