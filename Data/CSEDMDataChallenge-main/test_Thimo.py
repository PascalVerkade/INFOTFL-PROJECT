import os
import pandas as pd
from ProgSnap2 import ProgSnap2Dataset
import numpy as np
import scipy.stats



class Student:

    def __init__(self, problem_dic, student_id, student_skills_array, problem_attempts = {}, problem_scores = {}, student_w={}):
        self.student_id = student_id
        self.problems = problem_dic
        self.student_skills = student_skills_array
        
        self.student_weight = {}
        for ability in meta_problem_subjects:
            self.student_weight[ability] = 0
        
        self.problem_attempts = problem_attempts
        self.problem_scores = problem_scores

    def get_by_id_from_list(id_student, list_of_students):
        for x in list_of_students:
            if x.student_id == id_student:
                return x
        return None

semester = 'S19'
BASE_PATH = os.path.join('..', 'Release', semester)
TRAIN_PATH = os.path.join(BASE_PATH, 'Train')
TEST_PATH = os.path.join(BASE_PATH, 'Test')
MAIN_PATH = os.path.join(BASE_PATH, r'Train\Data')

main = ProgSnap2Dataset(os.path.join(MAIN_PATH, 'MainTable'))
train_ps2 = ProgSnap2Dataset(os.path.join(TRAIN_PATH, '..'))
early_train = pd.read_csv(os.path.join(TRAIN_PATH, 'early.csv'))
early_test = pd.read_csv(os.path.join(TRAIN_PATH, 'late.csv'))


META_PROBLEM_FILE = r"2nd CSEDM Data Challenge - Problem Prompts _ Concepts Used.xlsx"
META_PROBLEM_PATH = os.path.join(BASE_PATH, META_PROBLEM_FILE)

meta_problem = pd.read_excel(META_PROBLEM_PATH, engine='openpyxl')
meta_problem = meta_problem.fillna(0)
meta_problem = meta_problem.drop(["AssignmentID", 'Requirement'], axis=1)
meta_problem_subjects = meta_problem.drop(["ProblemID"], axis=1)

hierarchy = {
    'If/Else' : 3,
    'NestedIf': 3,
    'While': 4,
    'For': 4,
    'NestedFor': 4,
    'Math+-*/' : 2,
    'Math%' : 2,
    'LogicAndNotOr': 1,
    'LogicCompareNum' : 1,
    'LogicBoolean' : 1,
    'StringFormat' : 5,
    'StringConcat' : 5,
    'StringIndex' : 5,
    'StringLen' : 5,
    'StringEqual' : 6,
    'CharEqual' : 6,
    'ArrayIndex' : 5,
    'DefFunction' : 7
    }

concept_array = ['If/Else','NestedIf', 'While', 'For', 'NestedFor', 
                 'Math+-*/', 'Math%', 'LogicAndNotOr', 'LogicCompareNum', 
                 'LogicBoolean' , 'StringFormat', 'StringConcat', 'StringIndex',
                 'StringLen', 'StringEqual', 'CharEqual', 'ArrayIndex' , 'DefFunction'
                 
                 
                 ]
#for attempts per problem
main_table = main.get_main_table()
student_problem_codestate = main_table[['SubjectID', 'ProblemID', 'CodeStateID' ]]
problem_student_table = student_problem_codestate.groupby(["ProblemID", "SubjectID"])["CodeStateID"].unique().apply(list).to_dict()


#for avg attempts
    
def initialise_students(student_dataframe):
    person_ids = student_dataframe["SubjectID"].unique()
    subjects = meta_problem_subjects.iloc[0].to_numpy()
    student_list = []
    
    for person_id in person_ids:
        row_person = student_dataframe[student_dataframe["SubjectID"] == person_id]
        problems = dict(zip(row_person.ProblemID, row_person.Label))
        student_skills = np.zeros(len(subjects))
        problem_attempts = {}
        for (problem, stud_id) in problem_student_table:
            if person_id == stud_id:
                problem_attempts[problem] = len(problem_student_table[(problem, person_id)])
        new_student = Student(problem_dic=problems, student_id=person_id, student_skills_array=student_skills, problem_attempts=problem_attempts)
        student_list.append(new_student)
        
    return student_list

def get_meta_data(students):
    
    problem_ids_train = early_train["ProblemID"].unique().tolist()
    problem_ids_test = early_test["ProblemID"].unique().tolist()
    
    problem_ids = problem_ids_train + problem_ids_test

    aa = {}
    sd = {}
    pw = {}
    no_concepts = {}
    
   
    for problem_id in problem_ids:      
        no_concepts[problem_id] = meta_problem.loc[meta_problem['ProblemID'] == problem_id].drop(['ProblemID'], axis=1).to_numpy()
        attempts = []
        attempts_student = {}
        
       
        for x,y in problem_student_table:
            if x==problem_id:
                student = Student.get_by_id_from_list(y, students)
                attempts_student[student] = len(problem_student_table[(problem_id, y)])
                attempts = attempts + problem_student_table[(problem_id, y)]
            
        aa[problem_id] = len(attempts)/len(early_train["SubjectID"].unique())
          
        standaardafwijking = np.std(list(attempts_student.values()))
        sd[problem_id] = standaardafwijking
        
        z_scores = scipy.stats.zscore(list(attempts_student.values()))
        #reversing z-scores and mapping to distribution
        scores = scipy.stats.norm.cdf([0-x for x in z_scores])
        
        #adding problem scores to students
        student_scores = zip(attempts_student.keys(), scores)
        for student,score in student_scores:
            student.problem_scores[problem_id] = score
        
        pw[problem_id] = aa[problem_id] + len(no_concepts[problem_id])
                                              
    return aa, sd, pw, no_concepts

student_list = initialise_students(early_train)
average_attempts, sd_average_attempts, problem_weights, problem_concepts = get_meta_data(student_list)


def update_model(student, problem):
    problem_row_name = meta_problem[meta_problem["ProblemID"] == problem]
    problem_row_name = problem_row_name.drop(['ProblemID'], axis=1)
    
    #to array
    #problem_row_name = problem_row_name.drop(["ProblemID"], axis=1).to_numpy()
    #problem_row = problem_row_name.flatten()
    
    #student_weight_old = student.student_weight
    #student.student_weight = student.student_weight + problem_weights[problem]
    
    for i, ability in enumerate(problem_row_name):
        if problem_row_name.iloc[0][ability] == 1:
            student_weight_old = student.student_weight[ability]
            student.student_weight[ability] = student.student_weight[ability] + problem_weights[problem]
            #score = (student.problem_attempts[problem] / (average_attempts[problem] + sd_average_attempts[problem] )) * student.problems[problem]
            score = student.problem_scores[problem] * student.problems[problem]
            #if student.problems[problem]:
            student.student_skills[i] = ((student.student_skills[i] * student_weight_old) + (score * problem_weights[problem])) / student.student_weight[ability]

def model_abilities(student):
    for problem in student.problems:
            update_model(student, problem)


print(student_list[120].student_skills)
for student in student_list:
    model_abilities(student)
print(student_list[120].student_skills)




main_table = main.get_main_table()
student_problem_codestate = main_table[['SubjectID', 'ProblemID', 'CodeStateID' ]]

test = student_problem_codestate.groupby(["ProblemID", "SubjectID"])["CodeStateID"].apply(list).to_dict()



 #calculate total concepts accross all problems
total_concepts = {}
for problem in meta_problem_subjects:
    total_concepts[problem] = sum(meta_problem_subjects[problem])
print(total_concepts)


def predict(student, problem):
    score_sum = 0
    
    abilities = []
    ability_locations = []
    
    total_hierarchy = 0
    for i, x in enumerate(problem):
        if x == 1:
            abilities.append(concept_array[i])
            ability_locations.append(i)
            total_hierarchy += hierarchy[concept_array[i]]
    
    ability_weights = {}
    for a in abilities:
        ability_weights[a] = hierarchy[a]/total_hierarchy
        #calculating weights
    
    for x in ability_locations:
        score_sum += student.student_skills[x] * ability_weights[concept_array[x]]
    
    return score_sum
        
print( predict(student_list[120], [1,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,1]) )







""""
problem_ids = early_train["ProblemID"].unique()

problem_Labels = early_train.groupby("ProblemID")["Label"].apply(list).to_dict()
problem_EC = early_train.groupby("ProblemID")["CorrectEventually"].apply(list).to_dict()
problem_averageattempts = early_train.groupby("ProblemID")["Attempts"].apply(list).to_dict()

problem_Labels_fraction_correct = {}
problem_EC_fraction_correct = {}
aa = {}
sd = {}
print(len(problem_ids))
for problem in problem_ids:
    boolean_list_EC = problem_EC[problem]
    boolean_list_labels = problem_Labels[problem]
    standaardafwijking = np.std(problem_averageattempts[problem])
    sd[problem] = standaardafwijking
    problem_averageattempts_problem = sum(problem_averageattempts[problem])/len(problem_averageattempts[problem])
    aa[problem] = np.round(problem_averageattempts_problem, 2)
    problem_Labels_fraction_correct[problem] = sum(problem_Labels[problem])/len(boolean_list_labels)
    problem_EC_fraction_correct[problem] = sum(problem_EC[problem])/len(boolean_list_EC)

print("68", sd)
print(problem_averageattempts[1])


print(problem_Labels_fraction_correct)
print(problem_EC_fraction_correct)
print(aa)

"""


""""
single_person_ex = early_train[early_train["SubjectID"] == person_ids[0]]
problems = single_person_ex["ProblemID"].unique()
df = train_ps2.get_main_table()

#print(df.columns)



subjects = list(df["SubjectID"])
for subject in subjects:
    personal_df = df[df["SubjectID"] == subject]
    personal_problemIDs = set(personal_df["ProblemID"])
    delivery_times = personal_df["ServerTimestamp"]
    problemid_deliverytimes = {}
    for pid in personal_problemIDs:
        print(type(personal_df[personal_df["ProblemID"] == pid]["ServerTimestamp"]))
        problemid_deliverytimes[pid] = personal_df[personal_df["ProblemID"] == pid]["ServerTimestamp"]
    break

print(problemid_deliverytimes)
    #print(x)
"""











#print(early_train[""])
