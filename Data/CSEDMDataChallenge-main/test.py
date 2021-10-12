import os
import pandas as pd
from ProgSnap2 import ProgSnap2Dataset

semester = 'S19'
BASE_PATH = os.path.join('data', 'Release', semester)
TRAIN_PATH = os.path.join(BASE_PATH, 'Train')
TEST_PATH = os.path.join(BASE_PATH, 'Test')
MAIN_PATH = os.path.join(BASE_PATH, r'Test\Data')

main = ProgSnap2Dataset(os.path.join(MAIN_PATH, 'MainTable'))
train_ps2 = ProgSnap2Dataset(os.path.join(TRAIN_PATH, 'Data'))
early_train = pd.read_csv(os.path.join(TRAIN_PATH, 'early.csv'))
print(early_train.head)
print(early_train["CorrectEventually"])
person_ids = (early_train["SubjectID"].unique())

print(len(person_ids))

single_person_ex = early_train[early_train["SubjectID"] == person_ids[0]]
problems = single_person_ex["ProblemID"].unique()
df = train_ps2.get_main_table()

print(df.columns)
for time in df["ServerTimestamp"]:
    print(time)
    print(type(time))







#print(early_train[""])
