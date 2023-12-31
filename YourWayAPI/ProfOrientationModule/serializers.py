from rest_framework import serializers

class ProgramSerializer(serializers.Serializer):
   edu_program = serializers.CharField()

class QuestionsSerializer(serializers.Serializer):
   question = serializers.CharField()
   edu_program = serializers.CharField()

class AnswersSerializer(QuestionsSerializer):
   answer = serializers.IntegerField()

class GroupAndQuestionSerializer(serializers.Serializer):
   group = serializers.CharField()
   probability = serializers.DecimalField(max_digits=5, decimal_places=2)
   single_program = serializers.CharField()
   questions = QuestionsSerializer(many=True)

class GroupAndQuestionArraySerializer(QuestionsSerializer):
   answer = GroupAndQuestionSerializer(many=True)

class ProgramWithSuplySerializer(serializers.Serializer):
   edu_program = serializers.CharField()
   professions = serializers.ListField(child=serializers.CharField())
   subjects = serializers.ListField(child=serializers.CharField())

class ErrorSerializer(serializers.Serializer):
   error = serializers.CharField()

class PublicsSerializer(serializers.Serializer):
   name = serializers.CharField()

class SchoolsSerializer(serializers.Serializer):
   name = serializers.CharField()

class SchoolsAndPublicsSerializer(serializers.Serializer):
   schools = SchoolsSerializer(many=True)
   publics = PublicsSerializer(many=True) 

class AuthorizeSerializer(serializers.Serializer):
   silent_token = serializers.CharField()
   uuid = serializers.CharField()