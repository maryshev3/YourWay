# Create your models here.
class Question:
    question = ''
    edu_program = ''

class GroupWithTest:
    group = ''
    single_program = ''
    questions = list()

class ProgramWithSuply:
    edu_program = ''
    professions = list()
    subjects = list()