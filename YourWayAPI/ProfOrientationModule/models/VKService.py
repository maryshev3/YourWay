from django.shortcuts import redirect
import requests
import json
import os
from ProfOrientationModule.models.DataModule.data_functions import clear, del_punctuation

class PageClosed(Exception):
    def __init__(self, text):
        self.txt = text

class PageFaked(Exception):
    def __init__(self, text):
        self.txt = text

class VKService:
    __db_service__ = None
    __access_token__ = None
    __vk_api_version__ = '5.131'
    
    def __init__(self, db_service, access_token):
        self.__db_service__ = db_service
        self.__access_token__ = access_token

    def __send_request__(self, method_name, payload):
        payload['access_token'] = self.__access_token__
        payload['v'] = self.__vk_api_version__

        request = requests.get('https://api.vk.com/method/' + method_name, params=payload)

        return json.loads(request.text)

    def get_fields(self, id_vk):
        schools_dict = self.__send_request__('users.get', {'user_id': id_vk, 'fields': 'schools,connections'})
        print(schools_dict)

        if len(schools_dict['response']) == 0:
            raise PageFaked('Page is not exist.')

        if schools_dict['response'][0]['is_closed']:
            raise PageClosed('Page is closed. To use service it must be opened')

        groups_dict = self.__send_request__('users.getSubscriptions', {'user_id': int(schools_dict['response'][0]['id']), 'extended': 1})

        print(groups_dict)

        #Формируем списки
        schools_list = list()

        if 'schools' in schools_dict['response'][0]:
            if len(schools_dict['response'][0]['schools']) != 0:
                for i in schools_dict['response'][0]['schools']:
                    schools_list.append(del_punctuation(i['name'].lower(), './\\!@#$%^&*()-+_?;\"\':`|<>[]'))

        groups_list = list()

        if 'items' in groups_dict['response']:
            for i in groups_dict['response']['items']:
                try:
                    groups_list.append(del_punctuation(i['name'].lower(), './\\!@#$%^&*()-+_?;\"\':`|<>[]'))
                except:
                    continue

        #Очищаем список групп от самых популярных
        groups_list = clear(groups_list, self.__db_service__)

        schools_list.extend(groups_list)
        
        return ' '.join(schools_list)