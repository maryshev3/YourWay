from ProfOrientationModule.models_classes import Question


def TupleToQuestionsList(questions_tuple):
    questions_list = list()

    for tuple in questions_tuple:
        new_question = Question()
        new_question.question = tuple[0]
        new_question.edu_program = tuple[1]
        questions_list.append(new_question)

    return questions_list