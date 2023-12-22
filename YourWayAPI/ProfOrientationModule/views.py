import json
import os
from django.shortcuts import render
from rest_framework.response import Response
import coreapi
import coreschema
from rest_framework import schemas
from rest_framework.views import APIView
from django.http import HttpResponse
from rest_framework.schemas.openapi import AutoSchema
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status

from ProfOrientationModule.models.DBModule.DBService import DBService
from ProfOrientationModule.models.VKService import PageClosed, PageFaked, VKService
from ProfOrientationModule.models.NNModule.bert_classifier import BertClassifier

from ProfOrientationModule.models_classes import GroupWithTest, ProgramWithSuply, Question

from ProfOrientationModule.serializers import AuthorizeSerializer, ErrorSerializer, GroupAndQuestionArraySerializer, GroupAndQuestionSerializer, AnswersSerializer, ProgramSerializer, ProgramWithSuplySerializer, SchoolsAndPublicsSerializer
from rest_framework.decorators import api_view

from ProfOrientationModule.models.DataModule.data_functions import del_punctuation

import configparser

from ProfOrientationModule.models.JsonToUserFields import JsonToUserFields
from ProfOrientationModule.models.TupleToQuestionsList import TupleToQuestionsList

class PostGroupView(APIView):
    __access_token__ = os.environ['ACCESS_TOKEN_VK']
    __db_service__ = None
    __classifier__ = None

    def __prepare__(self):
        config = configparser.ConfigParser()

        config.read('./ProfOrientationModule/config.ini')

        self.__db_service__ = DBService(
                database = config["DataBaseSettings"]["db_name"],
                user = config["DataBaseSettings"]["db_user"],
                password = config["DataBaseSettings"]["db_password"],
                host = config["DataBaseSettings"]["db_host"],
                port = config["DataBaseSettings"]["db_port"]
            )
        
        self.__classifier__ = BertClassifier(
                model_path='cointegrated/rubert-tiny',
                tokenizer_path='cointegrated/rubert-tiny',
                n_classes=41,
                epochs=60,
                max_len=512,
                model_save_path='./output/model.pt'
            )

    @swagger_auto_schema(
        responses={200: GroupAndQuestionSerializer(many=True), 406: ErrorSerializer, 404: ErrorSerializer, 500: ErrorSerializer, 501: ErrorSerializer},
        operation_description="This method define the education\'s group by data from VK page",
        manual_parameters=[
            openapi.Parameter(
                'id_vk',
                openapi.IN_QUERY,
                description="ID VK, from where will be defined edu group",
                type=openapi.TYPE_STRING,
            )
        ],
        request_body=SchoolsAndPublicsSerializer
    )

    
    def post(self, request):
        self.__prepare__()

        id_vk = request.GET.get('id_vk')

        user_fields = ''

        try:
            user_fields = JsonToUserFields(json.loads(request.body))
        except:
            if id_vk == None:
                return Response({'error':'incorrect body of request'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                vk_service = VKService(self.__db_service__, self.__access_token__)

                try:
                    user_fields = vk_service.get_fields(id_vk)
                except PageClosed as ex:
                    return Response({'error':ex.txt}, status=status.HTTP_406_NOT_ACCEPTABLE)
                except PageFaked as ex:
                    return Response({'error':ex.txt}, status=status.HTTP_404_NOT_FOUND)

        #определим группу направлений
        self.__classifier__.load_model('./ProfOrientationModule/models/NNModule/trained_models/model_v0.5.pt')

        prediction_tuple = self.__classifier__.predict(user_fields)

        #group_list = [self.__db_service__.get_group(p['label'] for p in prediction_tuple['probabilities'])]

        def get_prob(element):
            element[1]["probability"]

        #print(prediction_tuple["probabilities"])
        groups_list = sorted(prediction_tuple["probabilities"], key=lambda g: g['probability'], reverse = True)[:3]

        print(groups_list)

        probabilities_list = [group['probability'] for group in groups_list]
        real_group_list = [self.__db_service__.get_group(group['label']) for group in groups_list]
        group_name_list = [str(group) + '. ' + self.__db_service__.get_group_name(group) for group in real_group_list]

        #определим вопросы по группе направлений
        questions_list = [TupleToQuestionsList(self.__db_service__.get_questions(group)) for group in real_group_list]

        #Проверяем, несколько ли направлений
        single_program = 'None'
        programs_list = [self.__db_service__.get_programs(group) for group in real_group_list]
        if len(programs_list) == 1:
            single_program = programs_list[0][0]

        # is_fully = True
        # if single_program == 'None':
        #     #Проверим, есть ли все вопросы для группы направлений (должны быть для всех направлений подготовки)

        #     for program in programs_list:
        #         is_contain = False
        #         for question in questions_list:
        #             if question.edu_program == program[0]:
        #                 is_contain = True
        #                 break
        #         if not is_contain:
        #             is_fully = False
        #             break


        #формируем ответ
        result_array = list()

        for i in range(0, 3):
            result = GroupWithTest()
            result.single_program = single_program
            result.probability = probabilities_list[i]
            result.group = group_name_list[i]
            #if is_fully:
            result.questions = questions_list[i]

            result_array.append(result)

        return Response(GroupAndQuestionSerializer(result_array, many=True).data)
    
class PostProgramView(APIView):
    __db_service__ = None

    def __prepare__(self):
        config = configparser.ConfigParser()

        config.read('./ProfOrientationModule/config.ini')

        self.__db_service__ = DBService(
                database = config["DataBaseSettings"]["db_name"],
                user = config["DataBaseSettings"]["db_user"],
                password = config["DataBaseSettings"]["db_password"],
                host = config["DataBaseSettings"]["db_host"],
                port = config["DataBaseSettings"]["db_port"]
            )

    @swagger_auto_schema(
        operation_description="This method define the education\'s program by answers on test from edu/group method",
        responses={200: ProgramWithSuplySerializer, 500: ErrorSerializer},
        request_body=AnswersSerializer(many=True)
    )
    def post(self, request, *args, **kwargs):
        self.__prepare__()

        try:
            answers_list = json.loads(request.body)
            total_sums = dict()

            for answer in answers_list:
                if answer['edu_program'] in total_sums:
                    total_sums[answer['edu_program']] += answer['answer']
                else:
                    total_sums[answer['edu_program']] = answer['answer']

            defined_program = max(total_sums, key=total_sums.get)

            professions = self.__db_service__.get_professions(defined_program)
            subjects = self.__db_service__.get_subjects(defined_program)

            result = ProgramWithSuply()
            result.professions = professions
            result.subjects = subjects
            result.edu_program = defined_program

            return Response(ProgramWithSuplySerializer(result).data)
        except:
            return Response({'error':'Error on server'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class PostSuplyByProgramView(APIView):
    __db_service__ = None

    def __prepare__(self):
        config = configparser.ConfigParser()

        config.read('./ProfOrientationModule/config.ini')

        self.__db_service__ = DBService(
                database = config["DataBaseSettings"]["db_name"],
                user = config["DataBaseSettings"]["db_user"],
                password = config["DataBaseSettings"]["db_password"],
                host = config["DataBaseSettings"]["db_host"],
                port = config["DataBaseSettings"]["db_port"]
            )

    @swagger_auto_schema(
        operation_description="This method define the education\'s program by answers on test from edu/group method",
        responses={200: ProgramWithSuplySerializer, 500: ErrorSerializer},
        request_body=ProgramSerializer
    )
    def post(self, request, *args, **kwargs):
        self.__prepare__()

        program = json.loads(request.body)['edu_program']

        professions = self.__db_service__.get_professions(program)
        subjects = self.__db_service__.get_subjects(program)

        if len(professions) == 0 or len(subjects) == 0:
            return Response({'error':'Not found professions or subjects for this program'}, status=status.HTTP_404_NOT_FOUND)

        result = ProgramWithSuply()
        result.professions = professions
        result.subjects = subjects
        result.edu_program = program

        return Response(ProgramWithSuplySerializer(result).data)

class PostAuthorizeVK(APIView):
    __db_service__ = None
    __access_token__ = os.environ['ACCESS_TOKEN_VK_AUTH']

    def __prepare__(self):
        config = configparser.ConfigParser()

        config.read('./ProfOrientationModule/config.ini')

        self.__db_service__ = DBService(
                database = config["DataBaseSettings"]["db_name"],
                user = config["DataBaseSettings"]["db_user"],
                password = config["DataBaseSettings"]["db_password"],
                host = config["DataBaseSettings"]["db_host"],
                port = config["DataBaseSettings"]["db_port"]
            )

    @swagger_auto_schema(
        operation_description="This method defined for authorization in VK",
        request_body=AuthorizeSerializer
    )
    def post(self, request):
        silent_token = json.loads(request.body)['silent_token']
        uuid = json.loads(request.body)['uuid']

        vk_service = VKService(self.__db_service__, self.__access_token__)

        return Response(vk_service.authorize(silent_token, uuid))