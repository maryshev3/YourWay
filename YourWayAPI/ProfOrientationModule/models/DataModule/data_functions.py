def del_punctuation(str, delimeters):
    result_str = (str + '.')[:-1]

    for delimeter in delimeters:
        while delimeter in result_str:
            result_str = result_str.replace(delimeter, '')

    while '  ' in result_str:
        result_str = result_str.replace('  ', ' ')

    while result_str[0] == ' ':
        result_str = result_str[1:]

    while result_str[len(result_str) - 1] == ' ':
        result_str = result_str[:-1]

    return result_str

def clear(str_list, db_service):
    i = 0

    while i < len(str_list):
        if db_service.is_popular_public(str_list[i]):
            str_list.pop(i)
        else:
            i += 1

    return str_list