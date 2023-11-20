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

from ProfOrientationModule.serializers import ErrorSerializer, GroupAndQuestionSerializer, AnswersSerializer, ProgramWithSuplySerializer
from rest_framework.decorators import api_view

# Create your views here.
class GetGroupView(APIView):
    __access_token__ = os.environ['ACCESS_TOKEN_VK']
    __db_service__ = DBService(database="your_way_db", user="postgres", password="123zhz", host="localhost", port="5432")
    __classifier__ = BertClassifier(
                model_path='cointegrated/rubert-tiny',
                tokenizer_path='cointegrated/rubert-tiny',
                n_classes=41,
                epochs=60,
                max_len=512,
                model_save_path='./output/model.pt'
            )

    @swagger_auto_schema(
        responses={200: GroupAndQuestionSerializer, 406: ErrorSerializer, 404: ErrorSerializer, 500: ErrorSerializer},
        operation_description="This method define the education\'s group by data from VK page",
        manual_parameters=[
            openapi.Parameter(
                'id_vk',
                openapi.IN_QUERY,
                description="ID VK, from where will be defined edu group",
                type=openapi.TYPE_STRING,
            )
        ],
    )

    def get(self, request):
        #try:
        id_vk = request.GET.get('id_vk')

        #определим группу направлений
        self.__classifier__.load_model('./ProfOrientationModule/models/NNModule/trained_models/model_v0_4.pt')

        vk_service = VKService(self.__db_service__, self.__access_token__)

        try:
            prediction = self.__classifier__.predict(vk_service.get_fields(id_vk))
        except PageClosed as ex:
            return Response({'error':ex.txt}, status=status.HTTP_406_NOT_ACCEPTABLE)
        except PageFaked as ex:
            return Response({'error':ex.txt}, status=status.HTTP_404_NOT_FOUND)

        group = self.__db_service__.get_group(prediction)

        #определим вопросы по группе направлений
        questions_list = list()

        questions_tuple = self.__db_service__.get_questions(group)

        for tuple in questions_tuple:
            new_question = Question()
            new_question.question = tuple[0]
            new_question.program = tuple[1]
            questions_list.append(new_question)

        #формируем ответ
        result = GroupWithTest()
        result.group = group
        result.questions = questions_list

        return Response(GroupAndQuestionSerializer(result).data)
        #except:
            #return Response({'error':'Error on server'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
class PostProgramView(APIView):
    __access_token__ = os.environ['ACCESS_TOKEN_VK']
    __db_service__ = DBService(database="your_way_db", user="postgres", password="123zhz", host="localhost", port="5432")

    @swagger_auto_schema(
        operation_description="This method define the education\'s program by answers on test from edu/group method",
        responses={200: ProgramWithSuplySerializer, 500: ErrorSerializer},
        request_body=AnswersSerializer(many=True)
    )
    def post(self, request, *args, **kwargs):
        try:
            answers_list = json.loads(request.body)
            total_sums = dict()

            for answer in answers_list:
                if answer['program'] in total_sums:
                    total_sums[answer['program']] += answer['answer']
                else:
                    total_sums[answer['program']] = answer['answer']

            defined_program = max(total_sums, key=total_sums.get)

            professions = self.__db_service__.get_professions()
            subjects = self.__db_service__.get_subjects()

            result = ProgramWithSuply()
            result.professions = professions
            result.subjects = subjects
            result.edu_program = defined_program

            return Response(ProgramWithSuplySerializer(result).data)
        except:
            return Response({'error':'Error on server'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)