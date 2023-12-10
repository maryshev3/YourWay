import psycopg2

class DBService:
    __connection__ = None

    def __init__(self, database, user, password, host, port):
        self.__connection__ = psycopg2.connect(
            database = database,
            user = user,
            password = password,
            host = host,
            port = port
        )

    def get_professions(self, program):
        cursor = self.__connection__.cursor()

        cursor.execute("SELECT professions.professions FROM professions INNER JOIN programs ON professions.program_id = programs.program_id WHERE programs.program = \'" + program + "\';")

        result = cursor.fetchall()

        cursor.close()

        i = 0
        while i < len(result):
            result[i] = result[i][0]
            i += 1

        print(result)

        return result

    def get_subjects(self, program):
        cursor = self.__connection__.cursor()

        cursor.execute("SELECT subject FROM subjects INNER JOIN programs ON subjects.program_id = programs.program_id WHERE programs.program = \'" + program + "\';")

        result = cursor.fetchall()

        cursor.close()

        i = 0
        while i < len(result):
            result[i] = result[i][0]
            i += 1

        print(result)

        return result
    
    def is_popular_public(self, public_name):
        cursor = self.__connection__.cursor()

        cursor.execute("SELECT count(*) FROM popular_public WHERE popular_public.public = \'" + public_name + "\';")
        count = cursor.fetchone()[0]

        cursor.close()

        if count == 1:
            return True
        else:
            return False

    def create_popular_publics(self, public_list):
        cursor = self.__connection__.cursor()

        cursor.execute("DELETE FROM popular_publics;")
        self.__connection__.commit()

        for public in public_list:
            cursor.execute("INSERT INTO popular_public VALUES (\'" + public + "\');")

        self.__connection__.commit()
        cursor.close()

    def create_groups(self, groups):
        cursor = self.__connection__.cursor()

        for key in groups:
            cursor.execute("INSERT INTO groups (group_id, \"group\") VALUES (" + str(key) + ", " + str(groups[key]) + ") ON CONFLICT DO NOTHING;")

        self.__connection__.commit()
        cursor.close()

    def get_group(self, group_num):
        cursor = self.__connection__.cursor()

        cursor.execute("SELECT \"group\" FROM groups WHERE groups.group_id = " + str(group_num) + ";")

        group = cursor.fetchone()[0]

        cursor.close()

        return group

    def get_questions(self, group):
        cursor = self.__connection__.cursor()

        #cursor.execute("SELECT group_id FROM groups WHERE groups.group = " + str(group) + ";")
        #group_id = cursor.fetchone()[0]

        cursor.execute("SELECT questions, program FROM questions INNER JOIN programs ON questions.program_id = programs.program_id WHERE programs.group = " + str(group) + ";")
        questions = cursor.fetchall()
        print(questions)
        cursor.close()

        return questions
    
    def get_programs(self, group):
        cursor = self.__connection__.cursor()

        cursor.execute("SELECT program FROM programs WHERE programs.group = " + str(group) + ";")
        programs = cursor.fetchall()
        cursor.close()

        return programs

    def __del__(self):
        if self.__connection__:
            self.__connection__.close()