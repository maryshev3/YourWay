from rest_framework import serializers

class QuestionsSerializer(serializers.Serializer):
   question = serializers.CharField()
   edu_program = serializers.CharField()

class AnswersSerializer(QuestionsSerializer):
   answer = serializers.IntegerField()

class GroupAndQuestionSerializer(serializers.Serializer):
   group = serializers.IntegerField()
   questions = QuestionsSerializer(many=True)

class ProfessionsSerializer(serializers.Serializer):
   profession = serializers.CharField()

class SubjectsSerializer(serializers.Serializer):
   subject = serializers.CharField()

class ProgramWithSuplySerializer(serializers.Serializer):
   edu_program = serializers.CharField()
   professions = ProfessionsSerializer(many=True)
   subjects = SubjectsSerializer(many=True)

class ErrorSerializer(serializers.Serializer):
   error = serializers.CharField()