import os
import pandas as pd
from ProgSnap2 import ProgSnap2Dataset
import numpy as np


class Student:

    def __init__(self, problem_dic, student_id, student_skills_array):
        self.student_id = student_id
        self.problems = problem_dic
        self.student_skills = student_skills_array




semester = 'S19'
BASE_PATH = os.path.join('data', 'Release', semester)
TRAIN_PATH = os.path.join(BASE_PATH, 'Train')
TEST_PATH = os.path.join(BASE_PATH, 'Test')
MAIN_PATH = os.path.join(BASE_PATH, r'Test\Data')

main = ProgSnap2Dataset(os.path.join(MAIN_PATH, 'MainTable'))
train_ps2 = ProgSnap2Dataset(os.path.join(TRAIN_PATH, 'Data'))
early_train = pd.read_csv(os.path.join(TRAIN_PATH, 'early.csv'))

META_PROBLEM_PATH = r"C:\Users\Thimo\Documents\School Documenten\ToL\CSEDMDataChallenge-main\data\Release\S19"
META_PROBLEM_FILE = r"\2nd CSEDM Data Challenge - Problem Prompts & Concepts Used.xlsx"


meta_problem = pd.read_excel(META_PROBLEM_PATH + META_PROBLEM_FILE)
meta_problem = meta_problem.fillna(0)
meta_problem = meta_problem.drop(["AssignmentID", 'Requirement'], axis=1)



subjects = meta_problem.columns
subjects = subjects.drop("ProblemID")


person_ids = (early_train["SubjectID"].unique())
student_list = []
for person_id in person_ids:
    row_person = early_train[early_train["SubjectID"] == person_id]
    average_correct = sum(row_person["Label"] == True)/len(row_person["Label"])
    problems = dict(zip(row_person.ProblemID, row_person.Label))
    student_skills = np.zeros(len(subjects))
    new_student = Student(problem_dic=problems, student_id=person_id, student_skills_array=student_skills)
    student_list.append(new_student)

for student in student_list:
    for problem in student.problems:
        problem_row = meta_problem[meta_problem["ProblemID"] == problem]
        problem_row = problem_row.drop(["ProblemID"], axis=1).to_numpy()
        problem_row = problem_row.flatten()
        if student.problems[problem]:
            student.student_skills += problem_row

for student in student_list:
    print(student.student_skills)

for problem in student.problems:
    problem_row = meta_problem[meta_problem["ProblemID"] == problem]
    problem_row = problem_row.drop(["ProblemID"], axis=1).to_numpy().flatten()
    relevant_skills = problem_row == 1


    #indices =
    break

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
