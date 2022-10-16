def paginate_items(itemsBatchSize, page, items):
    start = (page - 1) * itemsBatchSize
    end = start + itemsBatchSize
    paginatedItems = items[start:end]
    return paginatedItems