from ProfOrientationModule.models.DataModule.data_functions import del_punctuation


def JsonToUserFields(JsonRequest):
    user_fields = ''

    if 'schools' in JsonRequest:
        if len(JsonRequest['schools']) != 0:
            for school in JsonRequest['schools']:
                user_fields = user_fields + ' ' + del_punctuation(school['name'].lower(), './\\!@#$%^&*()-+_?;\"\':`|<>[]') + ' '

            user_fields = del_punctuation(user_fields, './\\!@#$%^&*()-+_?;\"\':`|<>[]')
    try:
        for public in JsonRequest['publics']:
            user_fields = user_fields + ' ' + del_punctuation(public['name'].lower(), './\\!@#$%^&*()-+_?;\"\':`|<>[]') + ' '
    except:
        raise Exception("not correct body")

    user_fields = del_punctuation(user_fields, './\\!@#$%^&*()-+_?;\"\':`|<>[]')

    return user_fields