import argparse
import pandas as pd
import os
import numpy as np

# parse arguments
parser = argparse.ArgumentParser()
parser.add_argument(
    "-md",
    "--modulesdirectory",
    help="collects the module data for all files in directory",
)
parser.add_argument("-f", "--file", help="collects the module data for a single file")
parser.add_argument(
    "-pd",
    "--participantsdirectory",
    help="collects the data for each participant from a directory",
)
parser.add_argument(
    "-v", "--verbose", action="store_true", help="print logging messages"
)
args = parser.parse_args()

# establish paths, make directory
home_path = os.path.expanduser("~/")
ran_in_path = os.getcwd()
moduleSummaries_dir_path = os.path.join(ran_in_path, "moduleSummaries")
participantSummaries_dir_path = os.path.join(ran_in_path, "participantSummaries")
temptxt_path = os.path.join(moduleSummaries_dir_path, "temp.txt")

# correct the csv file from learning suite and put it in temp.txt
def fix_file(file_name):
    with open(file_name) as f:
        lines = f.readlines()
        lines[0] = lines[0].strip()
        lines[0] = f"{lines[0]},\n"
        del lines[1:6]
        fixed = "".join(lines)
        os.chdir(moduleSummaries_dir_path)
        with open("temp.txt", "w") as newf:
            newf.write(fixed)
        os.chdir(data_dir_path)


# create data summaries for each module
def get_module_info(file_name, data):
    float_hours = []
    for value in data.iloc[:, 7]:
        if not pd.isnull(value):
            float_hours.insert(0, value)
    string_hours = [str(x) for x in float_hours]
    comments = [str(x) for x in data.iloc[:, 9]]
    if file_name[0:38] == "Student Answers for Computing Bootcamp":
        new_file_name = f"{file_name[39:-4].replace(' ', '')}_Results.txt"
    elif file_name[-11:] == "_Module.csv":
        new_file_name = f"{file_name[:-11]}_Results.txt"
    else:
        new_file_name = f"{file_name[:-4]}_Results.txt"
    os.chdir(moduleSummaries_dir_path)
    with open(new_file_name, "w") as out:
        out.write(f"Time Spent\n{'-'*100}\n")
        out.write(f"  - Mean: {np.mean(float_hours)}\n")
        out.write(f"  - Median: {np.median(float_hours)}\n")
        out.write(f"  - Max: {max(float_hours)}\n")
        out.write(f"  - Min: {min(float_hours)}\n")
        out.write(f"  - Full Data: {', '.join(np.sort(string_hours))}\n\n")
        out.write(f"Comments\n{'-'*100}\n")
        for comment in comments:
            if comment.find("nan"):
                out.write((f"  - {comment}\n"))
    os.remove(temptxt_path)
    os.chdir(data_dir_path)


# read module data and organize data by student
def get_student_info(file_name, data):
    if file_name[0:38] == "Student Answers for Computing Bootcamp":
        module_name = file_name[39:-4].replace(" ", "")
    elif file_name[-11:] == "_Module.csv":
        module_name = file_name[:-11]
    else:
        module_name = file_name[:-4]
    student_list = data.iloc[:, 0]
    i = 0
    for student in student_list:
        if student not in student_modules:
            student_modules[student] = []
            student_hours[student] = []
        student_data = data.iloc[i, :]
        if student_data[6] == "A":
            student_modules[student].append(module_name)
        student_hours[student].append(student_data[7])
        i = i + 1


# create a textfile for each student from student data
def create_student_summaries():
    os.chdir(participantSummaries_dir_path)
    for student in student_modules:
        new_file_name = f'{student.replace(" ", "")}_Results.txt'
        total_time = 0
        for value in student_hours[student]:
            if not pd.isnull(value):
                total_time = total_time + value
        if total_time != 0:
            with open(new_file_name, "w") as out:
                out.write(
                    f"{student} completed {len(student_modules[student])} modules:\n"
                )
                for mod in student_modules[student]:
                    out.write(f"    {mod}\n")
                out.write(f"\nTotal hours spent: {total_time}")


# main()
if args.file:
    if not os.path.isdir(moduleSummaries_dir_path):
        os.mkdir(moduleSummaries_dir_path)
    fix_file(args.file)
    data = pd.read_csv("temp.txt")
    get_module_info(args.file, data)
elif args.modulesdirectory:
    if not os.path.isdir(moduleSummaries_dir_path):
        os.mkdir(moduleSummaries_dir_path)
    data_dir_path = os.path.join(ran_in_path, args.modulesdirectory)
    for file_name in os.listdir(data_dir_path):
        os.chdir(data_dir_path)
        fix_file(file_name)
        data = pd.read_csv(temptxt_path)
        get_module_info(file_name, data)
elif args.participantsdirectory:
    if not os.path.isdir(participantSummaries_dir_path):
        os.mkdir(participantSummaries_dir_path)
    data_dir_path = os.path.join(ran_in_path, args.participantsdirectory)
    student_modules = {}
    student_hours = {}
    for file_name in os.listdir(data_dir_path):
        os.chdir(data_dir_path)
        fix_file(file_name)
        data = pd.read_csv(temptxt_path)
        get_student_info(file_name, data)
    create_student_summaries()
else:
    print("No options were selected, use -h option for help")
