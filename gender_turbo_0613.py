import pandas as pd
import csv
import json
import requests
import openai

# 读取WVS.dta文件
file_path = ('........dta')  # Stata数据文件的路径
df = pd.read_stata(file_path, columns=['sex', 'age', 'ethnic', 'education', 'income', 'chief', 'region'])
# 定义列名
columns = ['sex', 'age', 'ethnic', 'education', 'income', 'chief', 'region']


# API设置
# 设置API
url = "https://gpt-api.hkust-gz.edu.cn/v1/chat/completions"
headers = {
    "Content-Type": "application/json",
    "Authorization":..........."
}


#定义问卷
questions = [
    {
    "question_name":"gender_first",
    "question_text":"Your characteristics are mentioned in this respondents: {{ respondents }}. Please answer the following question: How much do you agree with the statement that children suffer when a mother works for pay?",
    "question_options":["Strongly agree","Agree","Disagree","Strongly disagree"]
    },
    {
    "question_name":"gender_second",
    "question_text":"Your characteristics are mentioned in this respondents: {{ respondents }}. Please answer the following question: How much do you agree with the statement that men make better political leaders than women do?",
    "question_options":[ "Strongly agree","Agree","Disagree","Strongly disagree"]
    },
    {
    "question_name":"gender_third",
    "question_text":"Your characteristics are mentioned in this respondents: {{ respondents }}. Please answer the following question: How much do you agree with the statement that men make better business executives than women do?",
    "question_options":[ "Strongly agree","Agree","Disagree","Strongly disagree"]
    },
    {
    "question_name":"gender_fourth",
    "question_text":"Your characteristics are mentioned in this respondents: {{ respondents }}. Please answer the following question: How much do you agree with the statement that if a woman earns more money than her husband, it is almost certain to cause problems?",
    "question_options":[ "Strongly agree","Agree","Neither agree nor disagree","Disagree","Strongly disagree"]
    }
]


# 自定义代理方法
def create_agent_response(respondent, questions):
    # Define the number of maximum attempts for each question
    attempts = 3
    responses = {}  # Initialize the dictionary to store all responses

    # Construct a basic prompt with respondent characteristics
    base_prompt = f"""
    Based on the following respondent characteristics:
    - Sex: {respondent['sex']}
    - Age: {respondent['age']}
    - Ethnicity: {respondent['ethnic']}
    - Education: {respondent['education']}
    - Income: {respondent['income']}
    - Chief: {respondent['chief']}
    - Region: {respondent['region']}
    """

    # Loop through each question in the questionnaire
    for question in questions:
        question_answered = False  # Flag to track if a valid answer was provided
        prompt = base_prompt  # Start with the base prompt

        # Try to get a valid answer up to the maximum number of attempts
        for attempt in range(attempts):
            prompt += f"""
                Question: {question['question_text']}
                Options: {', '.join(question['question_options'])}
                Please provide your answer from the options and give a reason.
                Answer:
                Reason:
                """

            # Prepare the data for the POST request to the API
            data = {
                "model": "gpt-3.5-turbo-0613",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 1,
                "top_p": 1,
                "logprobs": 10
            }

            # Send the POST request to the API
            response = requests.post(url, headers=headers, data=json.dumps(data))
            generated_data = response.json()
            response_text = generated_data['choices'][0]['message']['content'].strip()

            # Parse the response to extract the answer and reason
            if "Answer:" in response_text and "Reason:" in response_text:
                answer_start = response_text.find("Answer:") + 7
                answer_end = response_text.find("Reason:")
                answer = response_text[answer_start:answer_end].strip()
                reason = response_text[answer_end + 7:].strip()

                # Check if the extracted answer is one of the expected options
                if answer in question["question_options"]:
                    reason_key = question["question_name"] + "_reason"
                    answer_key = question["question_name"] + "_answer"
                    responses[reason_key] = reason
                    responses[answer_key] = answer
                    question_answered = True  # Valid answer obtained
                    break  # Exit the loop early as we got a valid answer

        # If no valid answer was obtained after all attempts, record it as such
        if not question_answered:
            reason_key = question["question_name"] + "_reason"
            answer_key = question["question_name"] + "_answer"
            responses[reason_key] = "No reason provided"
            responses[answer_key] = "No answer provided"

    return responses  # Return the collected responses


def parse_response(response_text, questions):
    answers = {}
    response_parts = response_text.split('Answer:')

    for i, question in enumerate(questions):
        question_key = question["question_name"]
        reason_key = f"{question_key}_reason"
        answer_key = f"{question_key}_answer"

        if i + 1 < len(response_parts):
            part = response_parts[i + 1].strip()
            reason_end = part.find('Answer:')
            reason = part[:reason_end].strip()
            answer = part[reason_end + 7:].strip()

            # 确保答案是选项之一
            #if answer not in question["question_options"]:
            #    answer = "Invalid answer"

            answers[reason_key] = reason
            answers[answer_key] = answer
        else:
            answers[reason_key] = "No reason provided"
            answers[answer_key] = "No answer provided"
        print(answers)
    return answers

generated_dataset = []


for index, row in df.iterrows():
    respondent = {col: row[col] for col in columns}

    # 模拟代理回答
    answers = create_agent_response(respondent, questions)

    row_data = {
        "age": respondent.get("age"),
        "sex": respondent.get("sex"),
        "ethnic": respondent.get("ethnic"),
        "education": respondent.get("education"),
        "income": respondent.get("income"),
        "chief": respondent.get("chief"),
        "region": respondent.get("region")
    }
    row_data.update(answers)
    generated_dataset.append(row_data)

    print(f"Processed respondent index: {index}")

# 将提取的数据保存到DataFrame
df = pd.DataFrame(generated_dataset)

# Save to CSV
df.to_csv('...........csv', index=False)

print("Data has been written to output.csv")
