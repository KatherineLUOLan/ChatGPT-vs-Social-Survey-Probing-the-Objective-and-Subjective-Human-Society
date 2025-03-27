import logging

# 日志配置
logging.basicConfig(
    filename="log_exp1_qwen_3.txt",
    level=logging.INFO,
    format="%(message)s",
    filemode='a'  #追加模式，确保不会覆盖之前的日志
)

def log_print(*args, **kwargs):
    """自定义print函数，支持日志记录和终端输出"""
    message = " ".join(map(str, args))  # 将所有参数转为字符串并拼接
    print(message, **kwargs)  # 原始print
    logging.info(message)  # 同时记录到日志


import csv
import json
import time
import os
from openai import OpenAI

client = OpenAI(
    # 若没有配置环境变量，请用百炼API Key将下行替换为：api_key="sk-xxx",
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)



prompt_template = """您是一位来自2017年的中国大陆的受访者，请回答：\n
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


# Helper function to ask GPT to parse the response
def parse_answers_with_gpt(content):
    parsing_prompt = f"""这是用户收到的问题{prompt_template}，这是用户针对每个问题的的回答{content}，请提取每个回答中“答案：”部分所对应的答案数字，并以 JSON 格式返回。JSON 格式应如下：
    {{
        "Q1": "答案1",
        "Q2": "答案2",
        "Q3": "答案3",
        "Q4": "答案4"
    }}
"""

    try:
        completion = client.chat.completions.create(
            model="qwen-plus",
            messages=[{'role': 'user', 'content': parsing_prompt}],
            temperature=0
        )
        qwen_output = completion.choices[0].message.content
        # print("3333:", gpt_output)  # 调试输出

        # 去掉 Markdown 格式
        gpt_output_cleaned = qwen_output.strip("```json").strip("```").strip()
        log_print("解析 agent 回答：", gpt_output_cleaned)
        return gpt_output_cleaned
    except Exception as e:
        log_print(f"Error parsing QWEN response: {e}")
        return None


# Variables for record generation
total_records_needed = 200
generated_dataset = []

# Generate records
while len(generated_dataset) < total_records_needed:
    index = len(generated_dataset) + 1
    log_print(f"\n\nRespondent index: {index}...")
    prompt = prompt_template
    # print("0000:", prompt)


    try:
        completion = client.chat.completions.create(
            model="qwen-plus",  # 模型列表：https://help.aliyun.com/zh/model-studio/getting-started/models
            messages=[{'role': 'user', 'content': prompt_template}],
            temperature=1,
            top_p=1
        )
        # print(completion)
        data_content = completion.choices[0].message.content
        log_print("agent思考过程：", data_content)

        # Parse answers with GPT
        parsed_response = parse_answers_with_gpt(data_content)
        if parsed_response:
            try:
                # 转换 GPT 返回的 JSON 字符串为字典
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
                    generated_dataset.append(answers)
                    print("Valid answers:", answers)
                else:
                    log_print("Invalid or incomplete answers, skipping this response.")

            except json.JSONDecodeError as e:
                log_print(f"Error decoding QWEN response: {e}")
        else:
            log_print("Parsing failed, skipping this response.")


    except Exception as e:
        log_print(f"Failed to retrieve data: {e}")
        break

    time.sleep(1)  # Pause to respect API rate limits

# Write the records to a CSV file
csv_file = 'exp1_qwen_3.csv'

with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(["Q1", "Q2", "Q3", "Q4"])  # Add headers
    writer.writerows(generated_dataset)

log_print(f"{len(generated_dataset)} records stored in {csv_file}")


