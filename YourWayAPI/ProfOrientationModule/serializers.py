from rest_framework import serializers

class ProgramSerializer(serializers.Serializer):
   edu_program = serializers.CharField()

class QuestionsSerializer(serializers.Serializer):
   question = serializers.CharField()
   edu_program = serializers.CharField()
   is_in_agu = serializers.BooleanField()

class AnswersSerializer(QuestionsSerializer):
   answer = serializers.IntegerField()

class GroupAndQuestionSerializer(serializers.Serializer):
   group = serializers.CharField()
   probability = serializers.DecimalField(max_digits=5, decimal_places=2)
   single_program = serializers.CharField()
   questions = QuestionsSerializer(many=True)

class GroupAndQuestionArraySerializer(QuestionsSerializer):
   answer = GroupAndQuestionSerializer(many=True)

class SubjectEgeSerializer(serializers.Serializer):
   subject = serializers.CharField()
   is_required = serializers.BooleanField()

class ProfileSerializer(serializers.Serializer):
   profile = serializers.CharField()
   subjects_ege = SubjectEgeSerializer(many=True)
   subjects_spo = serializers.ListField(child=serializers.CharField())
   is_ochno = serializers.BooleanField()
   is_zaochno = serializers.BooleanField()
   is_ochzaoch = serializers.BooleanField()

class ProgramWithSuplySerializer(serializers.Serializer):
   edu_program = serializers.CharField()
   professions = serializers.ListField(child=serializers.CharField())
   profiles = ProfileSerializer(many=True)

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