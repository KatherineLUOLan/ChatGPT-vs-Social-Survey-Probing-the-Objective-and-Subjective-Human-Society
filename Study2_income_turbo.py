import pandas as pd
import csv
import json
import requests

file_path = ('.......dta') 
df = pd.read_stata(file_path, columns=['sex', 'age', 'ethnic', 'education', 'income', 'chief', 'region'])

# API
url = "https://gpt-api.hkust-gz.edu.cn/v1/chat/completions"
headers = {
    "Content-Type": "application/json",
    "Authorization": "Your API......"
}

prompt_template = """Given a person, who is an American, with sex {sex}, age {age}, ethnic {ethnic}, the highest educational level {education}, household income level {income}, status whether is the chief wage earner in his house {chief} and region{region}, answer the following survey questions as a respondent would in a survey conducted in 2017:
Question 1, think of a score of 1 as meaning that incomes should be made more equal, and a score of 10 meaning that there should be greater incentives for individual effort. What score (an integer) between 1 and 10 comes closest to the way you feel? 
Question 2, think of a score of 1 as meaning that government should take more responsibility to ensure that everyone is provided for, and a score of 10 meaning that people should take more responsibility to provide for themselves. What score (an integer) between 1 and 10 comes closest to the way you feel?
"""

generated_dataset = []
max_records = 50  

for index, row in df.iterrows():
    if index >= max_records:
        break

    sex = row['sex']
    age = row['age']
    ethnic = row['ethnic']
    education = row['education']
    income = row['income']
    chief = row['chief']
    region = row['region']
    prompt = prompt_template.format(sex=sex, age=age, ethnic=ethnic, education=education, income=income, chief=chief, region=region)

    data = {
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 1,
        "top_p": 1,
        "logprobs": 10
    }

    response = requests.post(url, headers=headers, data=json.dumps(data))
    generated_data = response.json()
    data_content = generated_data['choices'][0]['message']['content']

    print(data_content)

    q1_start = data_content.find('Question 1:')
    q2_start = data_content.find('Question 2:')
    if q1_start != -1 and q2_start != -1:
        answer_q1 = data_content[q1_start + len('Question 1:'):q2_start].strip()
        answer_q2 = data_content[q2_start + len('Question 2:'):].strip()
    else:
        print("Cannot find answers in response for row:", index)
        answer_q1 = ''
        answer_q2 = ''

    generated_dataset.append([sex, age, ethnic, education, income, chief, region, answer_q1, answer_q2])

if len(generated_dataset) >= 200:
    generated_dataset = generated_dataset[:200]

csv_file = '.......csv'
with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(['sex', 'age', 'ethnic', 'education', 'income', 'chief', 'region', 'Answer to Question 1', 'Answer to Question 2'])
    writer.writerows(generated_dataset)

print(f"{len(generated_dataset)} records stored in {csv_file}")
