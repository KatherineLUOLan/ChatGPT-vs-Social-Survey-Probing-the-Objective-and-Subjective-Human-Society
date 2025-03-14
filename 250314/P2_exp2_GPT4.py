import logging

# 日志配置
logging.basicConfig(
    filename="log_exp2_1.txt",
    level=logging.INFO,
    format="%(message)s",
    filemode='a'  
)

def log_print(*args, **kwargs):
    """自定义print函数，支持日志记录和终端输出"""
    message = " ".join(map(str, args))  
    print(message, **kwargs)  
    logging.info(message)  


import csv
import requests
import json
import time
import pandas as pd
from chardet import detect

url = "https://gpt-api.hkust-gz.edu.cn/v1/chat/completions"
headers = {
   "Content-Type": "application/json",
   "Authorization": "Bearer API"
}

file_path = "CGSS2017_1628.csv"
with open(file_path, "rb") as f:
    result = detect(f.read())
    file_encoding = result["encoding"]
    # print(f"Detected encoding: {file_encoding}")
columns=['a31', 'a2', 'a7a', 'a7b', 'a8a', 'a58', 'a18', 'isurban', 'index']
profile_df = pd.read_csv(file_path, encoding=file_encoding, usecols=columns)
# print(profile_df.head())

# agents profile
def generate_prompt_profile(row):
    age = 2017 - row['a31']
    gender = row['a2']
    highest_education = row['a7a']
    educated_status = row['a7b']
    income = row['a8a']
    work = row['a58']
    hukou = row['a18']
    isurban = "城市" if row['isurban']=="城" else "乡村"

    return (f"您是一位{age}岁的{gender}性，\n"
            f"您目前的最高教育程度为: {highest_education}且状态是{educated_status}，\n"
            f"您去年（2016年）全年的总收入为{income}元，\n"
            f"您的工作经历及状况是: {work}，\n"
            f"您目前的户口登记状况是{hukou}，并且您的居住地区是{isurban}。")


# Helper function to ask GPT to parse the response
def parse_answers_with_gpt(content):
    parsing_prompt = f"""这是用户收到的问题{prompt}，这是用户针对每个问题的的回答{content}，请提取每个回答中“答案：”部分所对应的答案数字，并以 JSON 格式返回。JSON 格式应如下：
    {{
        "Q1": "答案1",
        "Q2": "答案2",
        "Q3": "答案3",
        "Q4": "答案4"
    }}
"""

    data = {
        "model": "gpt-4",
        "messages": [{"role": "user", "content": parsing_prompt}],
        "temperature": 0
    }
    response = requests.post(url, headers=headers, data=json.dumps(data))
    if response.status_code == 200:
        try:
            parsed_data = response.json()
            gpt_output = parsed_data["choices"][0]["message"]["content"]
            # print("3333:", gpt_output)

            # 去掉 Markdown 格式
            gpt_output_cleaned = gpt_output.split("```json")[-1].strip("```").strip()
            print("解析agent回答：", gpt_output_cleaned)
            # log_print("解析agent回答：", gpt_output_cleaned)
            return gpt_output_cleaned

        except (KeyError, json.JSONDecodeError) as e:
            print(f"Error parsing GPT response: {e}")
            return None
    else:
        print("Failed to parse answers with GPT:", response.status_code)
        return None


csv_file = 'exp2_1_1628.csv'
if not pd.io.common.file_exists(csv_file):
    with open(csv_file, mode='w', newline='', encoding=file_encoding) as file:
        writer = csv.writer(file)
        writer.writerow(columns + ["Q1", "Q2", "Q3", "Q4"])  # 添加表头


# Generate records
while not profile_df.empty:
    row = profile_df.iloc[0]
    original_index = row['index']
    log_print(f"正在生成第{original_index}条记录...")

    prompt_profile = generate_prompt_profile(row)
    # print("0000 agent profile:", prompt_profile)
    prompt = f"""您是一位来自2017年的中国大陆的受访者，您具备的特征是: \n
        {prompt_profile}\n
        请回答：\n
        您在多大程度上同意下面的观点？\n
            1. 我国的收入差距太大了。\n
            2. 为了社会公平，人们的物质生活水平差异应该很小。\n
            3. 缩小高收入者和低收入者之间的差距是政府的责任。\n
            4. 我国的社会福利让人变得懒散。\n
        请给出您的答案，选项为[1, 2, 3, 4, 5]，您只能选择一个选项。1表示“非常同意”，2表示“同意”，3表示“说不上同意不同意”，4表示“不同意”，5表示“非常不同意”。\n
        如果你真的无法做出选择，请回答“8”，表示您“无法选择”。
        请在做出选择之前进行充分的思考，请一步一步地思考。
        您的理由和答案所表达的意思必须是匹配的。
        理由：
        答案：
    """
    # log_print("0000 prompt:", prompt)

    data = {
        "model": "gpt-4",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 1,
        "top_p": 1
    }

    response = requests.post(url, headers=headers, data=json.dumps(data))

    if response.status_code == 200:
        generated_data = response.json()
        data_content = generated_data['choices'][0]['message']['content']
        # print("agent思考过程：", data_content)
        log_print("agent思考过程：", data_content)

        # Parse answers with GPT
        parsed_response = parse_answers_with_gpt(data_content)
        if parsed_response:
            try:
                parsed_answers_json = json.loads(parsed_response)  # 解析为 JSON 对象
                # Collect answers into a list
                answers = [
                    parsed_answers_json.get("Q1"),
                    parsed_answers_json.get("Q2"),
                    parsed_answers_json.get("Q3"),
                    parsed_answers_json.get("Q4")
                ]

                # Validate answers
                if len(answers) == 4 and all(answer in ['1', '2', '3', '4', '5', '8'] for answer in answers):
                    with open(csv_file, mode='a', newline='', encoding='utf-8') as file:
                        writer = csv.writer(file)
                        writer.writerow(list(row) + answers)
                    log_print("Valid answers saved:", answers)

                    profile_df.drop(profile_df.index[0], inplace=True)
                    profile_df.to_csv(file_path, encoding=file_encoding, index=False)

                else:
                    print("Invalid or incomplete answers, skipping this response.")

            except json.JSONDecodeError as e:
                print(f"Error decoding GPT response: {e}")

        else:
            print("Parsing failed, skipping this response.")


    else:
        print("Failed to retrieve data:", response.status_code)


    time.sleep(1)  # Pause to respect API rate limits

