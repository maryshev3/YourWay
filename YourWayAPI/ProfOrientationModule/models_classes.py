# Create your models here.
class Question:
    question = ''
    edu_program = ''
    is_in_agu = False

class GroupWithTest:
    group = list()
    probability = 0.0
    single_program = ''
    questions = list()

class ProgramWithSuply:
    edu_program = ''
    is_in_agu = False
    professions = list()
    profiles = list()

class SubjectEge:
    subject = ''
    is_required = False

class Profile:
    profile = ''
    subjects_ege = list()
    subjects_spo = list()
    is_ochno = False
    is_zaochno = False
    is_ochzaoch = False