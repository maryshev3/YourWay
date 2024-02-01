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

    def get_profiles(self, program_name):
        cursor = self.__connection__.cursor()

        cursor.execute(f"SELECT prof.name, prof.is_ochno, prof.is_zaochno, prof.is_ochzaoch FROM public.profiles as prof INNER JOIN public.programs as prog ON prof.program_id = prog.program_id WHERE prog.program = \'{program_name}\'")

        result = cursor.fetchall()

        cursor.close()

        return result
    
    def get_subjects_ege(self, program_name, profile_name):
        cursor = self.__connection__.cursor()

        cursor.execute(f'''
            SELECT
                ege.name as ege_name,
                ege_prof.is_required as ege_is_required
            FROM public.subjects_ege as ege
                INNER JOIN public.ege_profile as ege_prof ON ege.id = ege_prof.ege_id
                INNER JOIN public.profiles as prof ON ege_prof.profile_id = prof.id
                INNER JOIN public.programs as prog ON prog.program_id = prof.program_id
            WHERE prog.program = \'{program_name}\' AND ''' + ('prof.name is null' if profile_name is None else f'prof.name = \'{profile_name}\'')
        )

        result = cursor.fetchall()

        cursor.close()

        return result
    
    def get_subjects_spo(self, program_name, profile_name):
        cursor = self.__connection__.cursor()

        cursor.execute(f'''
            SELECT
                spo.name as spo_name
            FROM public.subjects_spo as spo
                INNER JOIN public.spo_profile as spo_prof ON spo.id = spo_prof.spo_id
                INNER JOIN public.profiles as prof ON spo_prof.profile_id = prof.id
                INNER JOIN public.programs as prog ON prog.program_id = prof.program_id
            WHERE prog.program = \'{program_name}\' AND ''' + ('prof.name is null' if profile_name is None else f'prof.name = \'{profile_name}\'')
        )

        result = cursor.fetchall()

        cursor.close()

        i = 0
        while i < len(result):
            result[i] = result[i][0]
            i += 1

        return result

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

    def get_group_name(self, group_num):
        cursor = self.__connection__.cursor()

        cursor.execute(f"SELECT name FROM groups_name WHERE groups_name.group = {group_num};")

        name = cursor.fetchone()[0]

        cursor.close()

        return name

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
        
    def is_in_agu(self, program):
        cursor = self.__connection__.cursor()

        cursor.execute("SELECT is_in_agu FROM programs WHERE programs.program = \'" + program + "\';")
        result = cursor.fetchone()[0]

        cursor.close()

        return result

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

        cursor.execute("SELECT questions, program, programs.is_in_agu FROM questions INNER JOIN programs ON questions.program_id = programs.program_id WHERE programs.group = " + str(group) + ";")
        questions = cursor.fetchall()
        print(questions)
        cursor.close()

        return questions
    
    def get_questions_in_agu(self, group):
        cursor = self.__connection__.cursor()

        cursor.execute("SELECT questions, program FROM questions INNER JOIN programs ON questions.program_id = programs.program_id WHERE programs.is_in_agu = true AND programs.group = " + str(group) + ";")
        questions = cursor.fetchall()
        print(questions)
        cursor.close()

        return questions
    
    def get_programs(self, group):
        cursor = self.__connection__.cursor()

        cursor.execute("SELECT program, is_in_agu FROM programs WHERE programs.group = " + str(group) + ";")
        programs = cursor.fetchall()
        cursor.close()

        return programs

    def __del__(self):
        if self.__connection__:
            self.__connection__.close()