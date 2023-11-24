from rest_framework import serializers

class QuestionsSerializer(serializers.Serializer):
   question = serializers.CharField()
   edu_program = serializers.CharField()

class AnswersSerializer(QuestionsSerializer):
   answer = serializers.IntegerField()

class GroupAndQuestionSerializer(serializers.Serializer):
   group = serializers.IntegerField()
   single_program = serializers.CharField()
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

class PublicsSerializer(serializers.Serializer):
   name = serializers.CharField()

class SchoolsSerializer(serializers.Serializer):
   name = serializers.CharField()

class SchoolsAndPublicsSerializer(serializers.Serializer):
   schools = SchoolsSerializer(many=True)
   publics = PublicsSerializer(many=True) 