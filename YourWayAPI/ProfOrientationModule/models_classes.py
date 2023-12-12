# Create your models here.
class Question:
    question = ''
    edu_program = ''

class GroupWithTest:
    group = list()
    probability = 0.0
    single_program = ''
    questions = list()

class ProgramWithSuply:
    edu_program = ''
    professions = list()
    subjects = list()