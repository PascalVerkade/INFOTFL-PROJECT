import os
import pandas as pd
from ProgSnap2 import ProgSnap2Dataset
import numpy as np
import scipy.stats
from sklearn.metrics import classification_report
import random



#class of the student including his ID, skill-values (array), attempts per problem (dict), label per problem (dict) and his student weights (dic)
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

    #get the student by id from a list of students
    def get_by_id_from_list(id_student, list_of_students):
        for x in list_of_students:
            if x.student_id == id_student:
                return x
        return None



#defining paths for retrieval of datasets
semester = 'S19'
BASE_PATH = os.path.join('data', 'Release', semester)
TRAIN_PATH = os.path.join(BASE_PATH, 'Train')
TEST_PATH = os.path.join(BASE_PATH, 'Test')
MAIN_PATH = os.path.join(BASE_PATH, r'Train\Data')
MAIN_PATH2 = os.path.join(BASE_PATH, r'test\Data')

#creating dataframes and reading actual files
main = ProgSnap2Dataset(os.path.join(MAIN_PATH, 'MainTable'))
main2 = ProgSnap2Dataset(os.path.join(MAIN_PATH2, 'MainTable'))
train_ps2 = ProgSnap2Dataset(os.path.join(TRAIN_PATH, '..'))
early_train = pd.read_csv(os.path.join(TRAIN_PATH, 'early.csv'))
early_test = pd.read_csv(os.path.join(TRAIN_PATH, 'late.csv'))

#getting full main tables in dataframe
main_table = main.get_main_table()
main_table2 = main2.get_main_table()
all_main = pd.concat([main_table, main_table2])

#getting unique codestates for each problem for each subject (to filter attempts)
#student_problem_codestate = main_table[['SubjectID', 'ProblemID', 'CodeStateID' ]]
student_problem_codestate = all_main[['SubjectID', 'ProblemID', 'CodeStateID' ]]

#editing dataframes for easier to handle format
del early_test['AssignmentID']
del early_train['AssignmentID']
del early_train['Attempts']
del early_train['CorrectEventually']
all_data = pd.concat([early_test, early_train])

#splitting randomly to test and training set on 75-25% (as was the original distribution):
test_data = all_data.sample(frac=0.25)
test_indices = list(test_data.index.values) 
train_data = all_data.drop(test_indices)

#call, read and create dataframe of meta-file of annotated problems
META_PROBLEM_FILE = r"2nd CSEDM Data Challenge - Problem Prompts _ Concepts Used.xlsx"
META_PROBLEM_PATH = os.path.join(BASE_PATH, META_PROBLEM_FILE)
meta_problem = pd.read_excel(META_PROBLEM_PATH, engine='openpyxl')
meta_problem = meta_problem.fillna(0)
meta_problem = meta_problem.drop(["AssignmentID", 'Requirement'], axis=1)
meta_problem_subjects = meta_problem.drop(["ProblemID"], axis=1)

#hardcoded hierarchy of programming concepts
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

#concepts in array (specific order!, used for indexing)
concept_array = ['If/Else','NestedIf', 'While', 'For', 'NestedFor', 
                 'Math+-*/', 'Math%', 'LogicAndNotOr', 'LogicCompareNum', 
                 'LogicBoolean' , 'StringFormat', 'StringConcat', 'StringIndex',
                 'StringLen', 'StringEqual', 'CharEqual', 'ArrayIndex' , 'DefFunction'
                 ]

#calculate total concepts for the given problems
total_concepts = {}
for problem in meta_problem_subjects:
    total_concepts[problem] = sum(meta_problem_subjects[problem])
    
#creating dataframe for unique attempts per problem
main_table = main.get_main_table()
student_problem_codestate = main_table[['SubjectID', 'ProblemID', 'CodeStateID' ]]
problem_student_table = student_problem_codestate.groupby(["ProblemID", "SubjectID"])["CodeStateID"].unique().apply(list).to_dict()


#initialise a list of students based on the complete dataframe
def initialise_students(student_dataframe):
    person_ids = student_dataframe["SubjectID"].unique()
    subjects = meta_problem_subjects.iloc[0].to_numpy()
    student_list = []
    
    #creating a student from all data available through the dataframe.
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


#calculate and create dictionaris for the metadata: For each problem: Average attempts, standard deviation, weight and amount of concepts. Also adds score for problem to the student objects
def get_meta_data(students):
    
    problem_ids_train = early_train["ProblemID"].unique().tolist()
    problem_ids_test = early_test["ProblemID"].unique().tolist()
    
    problem_ids = problem_ids_train + problem_ids_test

    aa = {}
    sd = {}
    pw = {}
    no_concepts = {}
    
    #loop through the problems
    for problem_id in problem_ids:      
        no_concepts[problem_id] = meta_problem.loc[meta_problem['ProblemID'] == problem_id].drop(['ProblemID'], axis=1).to_numpy()
        attempts = []
        attempts_student = {}
        
        #loop through students for average attempts and standard deviation.
        for x,y in problem_student_table:
            if x==problem_id:
                student = Student.get_by_id_from_list(y, students)
                attempts_student[student] = len(problem_student_table[(problem_id, y)])
                attempts = attempts + problem_student_table[(problem_id, y)]
            
        aa[problem_id] = len(attempts)/len(early_train["SubjectID"].unique())
        sd[problem_id] = np.std(list(attempts_student.values()))
        
        z_scores = scipy.stats.zscore(list(attempts_student.values()))
        #reversing z-scores and mapping to distribution
        scores = scipy.stats.norm.cdf([0-x for x in z_scores])
        
        # loop throughs students and adding problem scores for each problem.
        student_scores = zip(attempts_student.keys(), scores)
        for student,score in student_scores:
            student.problem_scores[problem_id] = score
        
        #calculating problem weights
        pw[problem_id] = aa[problem_id] + len(no_concepts[problem_id])
                                              
    return aa, sd, pw, no_concepts


#updating a student model given a student and a problem
def update_model(student, problem):
    problem_row_name = meta_problem[meta_problem["ProblemID"] == problem]
    problem_row_name = problem_row_name.drop(['ProblemID'], axis=1)
        
    #check all concepts, and only update those that are part of problem and calculate necessary items
    for i, ability in enumerate(problem_row_name):
        if problem_row_name.iloc[0][ability] == 1:
            student_weight_old = student.student_weight[ability]
            student.student_weight[ability] = student.student_weight[ability] + problem_weights[problem]
            score = student.problem_scores[problem] * student.problems[problem]
            student.student_skills[i] = ((student.student_skills[i] * student_weight_old) + (score * problem_weights[problem])) / student.student_weight[ability]


#generic method to call update for list of student and the problems the student has made.
def model_abilities(student):
    #get the problem list of this student basd on the 75% training set.
    training = train_data[train_data["SubjectID"] == student.student_id]
    problem_dict = dict(zip(training.ProblemID, training.Label))
    #for each problem, update the model
    for problem in problem_dict:
        update_model(student, problem)


#method to predict a score/struggle probability of a single studnt on a single problem
def predict(student, problem):
    score_sum = 0
    
    abilities = []
    ability_locations = []
    
    total_hierarchy = 0
   
    #check hierarcy and abilities
    for i, x in enumerate(problem):
        if x == 1:
            #if student.student_skills[i] != 0:
            abilities.append(concept_array[i])
            ability_locations.append(i)
            total_hierarchy += hierarchy[concept_array[i]]
    
    #calculate ability weights
    ability_weights = {}
    for a in abilities:
        ability_weights[a] = hierarchy[a]/total_hierarchy

    #calculate parts of weighted sum (struggle probability) for each ability.
    for x in ability_locations:
        score_sum += student.student_skills[x] * ability_weights[concept_array[x]]
    
    return score_sum


#wrapper-method to call predict on a set of students and a set of problems
def predict_sets(students, problems):
    d=[]
    for problem in problems:
        for student in students:
            
            d.append(
                {'student': student.student_id,
                 'problem': problem,
                 'score': predict(student, problem) 
                 }
            )    
    frame = pd.DataFrame(d)
    return frame
    


#-----------Section to call all methods to initailize full student model---------------
student_list = initialise_students(all_data)
average_attempts, sd_average_attempts, problem_weights, problem_concepts = get_meta_data(student_list)

#call to model the abilities of a studnt
for student in student_list:
    model_abilities(student)

#print single instance of student model (for insight purposes and to check that it worked)
print(random.choice(student_list).student_skills)


              
#---------Section for evaluation---------------------------                                         
actual_y = []
predicted_y = []
complete = []
#for all data entries, get students, problems with accompanying concepts and annotated labels.
for row in all_data.sample(frac=0.25).itertuples():
    
    student = Student.get_by_id_from_list(getattr(row, 'SubjectID'), student_list)
    problem = getattr(row, 'ProblemID')
    true_label = getattr(row, 'Label')
    #getting concepts through some data shuffling:
    temp = meta_problem.loc[meta_problem['ProblemID'] == problem]
    del temp['ProblemID']
    [concepts] = temp.to_numpy()
    
    
    #start predicting and adding data to dictionary (for final dataframe)
    predict_label = True
    if predict(student, concepts) < 0.25: predict_label=False
        
    complete.append(
        {'student': student,
         'problem': concepts,
         'true_y': true_label,
         'predicted_y': predict_label            
            }
    )
    
#final datamanipulations of dataframe to create classfiication report
frame_complete = pd.DataFrame(complete)
actual_y = frame_complete['true_y'].to_numpy()
predicted_y = frame_complete['predicted_y'].to_numpy()
print(classification_report(actual_y, predicted_y))

