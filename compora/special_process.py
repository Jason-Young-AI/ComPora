def special_process(string, language):
    if language == 'ug':
        string = special_process_uyghur(string)
    else:
        return string


def special_process_uyghur(string):
    def is_ug(char):
        if 1569 <= ord(char) and ord(char) <= 1791:
            return True
        return False
    chars = list(string)
    for index in range(len(chars)):
        if is_ug(chars[index]):
            continue
        else:
            chars[index] = chars[index].upper()
    string = ''.join(chars)
    return string
