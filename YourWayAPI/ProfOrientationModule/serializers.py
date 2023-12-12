from rest_framework import serializers

class QuestionsSerializer(serializers.Serializer):
   question = serializers.CharField()
   edu_program = serializers.CharField()

class AnswersSerializer(QuestionsSerializer):
   answer = serializers.IntegerField()

class GroupAndQuestionSerializer(serializers.Serializer):
   group = serializers.CharField()
   single_program = serializers.CharField()
   questions = QuestionsSerializer(many=True)

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