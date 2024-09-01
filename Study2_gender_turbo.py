import pandas as pd
import csv
import json
import requests

# 读取WVS.dta文件
file_path = ('WVSUSGENDER200.dta')  # Stata数据文件的路径
df = pd.read_stata(file_path, columns=['sex', 'age', 'ethnic', 'education', 'income', 'chief', 'region'])

# API设置
url = "https://gpt-api.hkust-gz.edu.cn/v1/chat/completions"
headers = {
    "Content-Type": "application/json",
    "Authorization": "acb0f9d12f78421e81a921e55c5789bc4f64ba4f021949f087b6c48e7f16fcd2"
}

prompt_template = """Given a person, who is an American, with sex {sex}, age {age}, ethnic {ethnic}, the highest educational level {education}, household income level {income}, status whether is the chief wage earner in his house {chief} and region {region}, answer the following survey questions as a respondent would in a survey conducted in 2017:
Question 1: Think of score 1 as strongly agree, score 2 as agree, score 3 as disagree, score 4 as strongly disagree. What score comes closest to the way you feel the statement that "children suffer when a mother works for pay"? 
Question 2: Think of score 1 as strongly agree, score 2 as agree, score 3 as disagree, score 4 as strongly disagree. What score comes closest to the way you feel the statement that "men make better political leaders than women do"? 
Question 3: Think of score 1 as strongly agree, score 2 as agree, score 3 as disagree, score 4 as strongly disagree. What score comes closest to the way you feel the statement that "men make better business executives than women do"?
Question 4: Think of score 1 as strongly agree, score 2 as agree, score 3 as neither agree nor disagree, score 4 as disagree, score 5 as strongly disagree. What score comes closest to the way you feel the statement that "if a woman earns more money than her husband, it's almost certain to cause problems"?
"""

generated_dataset = []
max_records = 50  # 设置最大记录数为200

# 处理每一行数据
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

    # 发送请求
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

    # 打印data_content来检查内容
    print(data_content)

    # 解析回答
    q1_start = data_content.find('Question 1:')
    q2_start = data_content.find('Question 2:')
    q3_start = data_content.find('Question 3:')
    q4_start = data_content.find('Question 4:')
    if q1_start != -1 and q2_start != -1 and q3_start != -1 and q4_start != -1:
        answer_q1 = data_content[q1_start + len('Question 1:'):q2_start].strip()
        answer_q2 = data_content[q2_start + len('Question 2:'):q3_start].strip()
        answer_q3 = data_content[q3_start + len('Question 3:'):q4_start].strip()
        answer_q4 = data_content[q4_start + len('Question 4:'):].strip()
    else:
        print("Cannot find answers in response for row:", index)
        # 设置答案为None或空字符串
        answer_q1 = ''
        answer_q2 = ''
        answer_q3 = ''
        answer_q4 = ''

    # 添加到数据集
    generated_dataset.append([sex, age, ethnic, education, income, chief, region, answer_q1, answer_q2, answer_q3, answer_q4])


# 检查生成的记录数量
if len(generated_dataset) >= 200:
    generated_dataset = generated_dataset[:200]

# 将数据保存为CSV文件
csv_file = 'WVSUSGENDER001.csv'
with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(['sex', 'age', 'ethnic', 'education', 'income', 'chief', 'region', 'Answer to Question 1', 'Answer to Question 2', 'Answer to Question 3', 'Answer to Question 4'])
    writer.writerows(generated_dataset)

print(f"{len(generated_dataset)} records stored in {csv_file}")
