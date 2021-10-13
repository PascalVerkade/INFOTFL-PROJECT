import os
import pandas as pd
from ProgSnap2 import ProgSnap2Dataset
import numpy as np


class student:

    def __init__(self, problems):
        problems = problems



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

subjects = meta_problem.columns
subjects = subjects.drop("AssignmentID", "ProblemID")


person_ids = (early_train["SubjectID"].unique())


for person_id in person_ids:
    print(person_id)
    row_person = early_train[early_train["SubjectID"] == person_id]
    average_correct = sum(row_person["Label"] == True)/len(row_person["Label"])
    print(row_person["Label"] == True)
    break






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
