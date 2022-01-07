def filter_data_provider(filter_data, options_data):
    result_data = []
    for name in filter_data:
        for option in options_data:
            if isinstance(name, tuple):
                result_data.append((*name, *option))
            else:
                result_data.append((name, *option))
    return result_data
