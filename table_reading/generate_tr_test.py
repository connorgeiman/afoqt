import pandas as pd
import numpy as np
import os
from fpdf import FPDF

NUM_Q = 40

correct_answers = []

# Create a folder to store the csvs and the generated test
folder_num = max([int(f.split("_")[1]) for f in os.listdir("table_reading/generated_tests") if f.startswith("test")] + [-1]) + 1
save_folder = f"table_reading/generated_tests/test_{folder_num}"
os.makedirs(save_folder, exist_ok=True)

question_number = 1

# Initialize your PDF document and set the page orientation to landscape
pdf = FPDF(orientation='L', unit='mm', format='letter')

# -- GENERATE TABLE --

# Generate table csvs
start_nums = range(0,101)
row_labels = range(-20, 21)
col_labels = range(-20, 21)
df = pd.DataFrame(index=row_labels, columns=col_labels)

start_num = np.random.choice(start_nums)

for y in range(41):
    for x in range(41):
        df.iloc[x,y] = start_num+x+y

# Save table to csv
csv_file = f"{save_folder}/table_{folder_num}.csv"
df.to_csv(csv_file, index=True)

# Add to PDF
pdf.add_page()
pdf.set_font('Arial', size=8)

# Define the column widths and heights for the table
col_widths = [(pdf.w-25.4) / (len(df.columns))] * len(df.columns)
row_height = pdf.font_size * 1.5

# Add the column names to the PDF document
pdf.cell(col_widths[df.columns.get_loc(0)], row_height, "", border=0)
for col in df.columns:
    pdf.set_font('Arial', 'B', size=9)
    pdf.cell(col_widths[df.columns.get_loc(col)], row_height, str(col), border=0, align="C")

pdf.ln(row_height)

# Add the table to the PDF document
for row_label, row in df.iterrows():
    pdf.set_font('Arial', 'B', size=9)
    pdf.cell(col_widths[0], row_height, str(row_label), border=0, align="C")
    pdf.set_font('Arial', size=8)        
    for col in df.columns:
        pdf.cell(col_widths[df.columns.get_loc(col)], row_height, str(row[col]), border=1, align="C")
    pdf.ln(row_height)

# -- GENERATE QUESTIONS --
# Create a new 8x40 table of questions and answers
row_labels = range(1, NUM_Q+1)
col_labels = ["X","Y"," ","A","B","C","D","E"]
question_df = pd.DataFrame(index=row_labels, columns=col_labels)

# Generate questions for each table
for q in range(1,NUM_Q+1):
    # read in the csv file as a DataFrame
    # df = pd.read_csv(csv_file, index_col=0, header=0)

    # generate a random index
    x = np.random.randint(0, 41)
    y = np.random.randint(0, 41)

    # extract the number at the random index
    number = df.iloc[y, x] # y is rows, x is columns
    x_label = df.columns[x]
    y_label = df.index[y]

    # Ask the question
    question_df.loc[q,"X"] = x_label
    question_df.loc[q,"Y"] = y_label

    # present the number to the user as a question with multiple choice options
    options = ["A", "B", "C", "D", "E"]
    correct_option = np.random.choice(options)
    options.remove(correct_option)
    incorrect_options = list(range(number-4,number)) + list(range(number+1,number+5))
    incorrect_options = np.random.choice(incorrect_options, size=len(options), replace=False)
    incorrect_options = [int(option) for option in incorrect_options]
    options_dict = {correct_option: number}
    for m, option in enumerate(options):
        options_dict[option] = incorrect_options[m]

    for option, number in sorted(options_dict.items()):
        question_df.loc[q,option] = number

    # Add correct answer to answer key
    correct_answers.append(f"{question_number}) {correct_option}")
    question_number += 1

question_df[" "] = question_df[" "].fillna("")

csv_file = f"{save_folder}/questions_{folder_num}.csv"
question_df.to_csv(csv_file, index=True)

# Add a page for the questions table
pdf.add_page(orientation='P')
pdf.set_font('Arial', size=12)

# Define the column widths and heights for the table
col_width = (pdf.w-25.4) / len(question_df.columns)
row_height = pdf.font_size * 1.4

# Add the column names to the PDF document
pdf.cell(col_widths[df.columns.get_loc(0)], row_height, "", border=0)
for col in question_df.columns:
    pdf.set_font('Arial', 'B', size=14)
    pdf.cell(col_width, row_height, str(col), border=0, align="C")

pdf.ln(row_height)

# Add the question table to the PDF document
for row_label, row in question_df.iterrows():
    pdf.set_font('Arial', 'B', size=11)
    pdf.cell(col_widths[0], row_height, str(row_label), border=0, align="R")
    pdf.set_font('Arial', size=11)        
    for col in question_df.columns:
        pdf.cell(col_width, row_height, str(row[col]), border=1, align="C")
    pdf.ln(row_height)

# -- ADD THE ANSWERS --

# Create page with answer key
pdf.add_page(orientation='P')
pdf.set_font('Arial', size=11)
pdf.cell(0, 10, txt="ANSWER KEY", ln=1, align="C")
for line in correct_answers:
    pdf.multi_cell(0, 5.9, line)

pdf.output(f"{save_folder}/table_reading_test_{folder_num}.pdf")