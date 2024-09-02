import pandas as pd
import csv
import json
import requests
import openai

file_path = ('........dta') 
df = pd.read_stata(file_path, columns=['sex', 'age', 'ethnic', 'education', 'income', 'chief', 'region'])
columns = ['sex', 'age', 'ethnic', 'education', 'income', 'chief', 'region']

# API
url = "https://gpt-api.hkust-gz.edu.cn/v1/chat/completions"
headers = {
    "Content-Type": "application/json",
    "Authorization": "Your API......"
}

questions = [
    {
    "question_name":"income_first",
    "question_text":"Your characteristics are mentioned in this respondents: {{ respondents }}. Please answer the following question: think of a score of 1 as meaning that incomes should be made more equal, and a score of 10 meaning that there should be greater incentives for individual effort. What score (an integer) between 1 and 10 comes closest to the way you feel?",
    "question_options":[1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    },
    {
    "question_name":"income_second",
    "question_text":"Your characteristics are mentioned in this respondents: {{ respondents }}. Please answer the following question: think of a score of 1 as meaning that government should take more responsibility to ensure that everyone is provided for, and a score of 10 meaning that people should take more responsibility to provide for themselves. What score (an integer) between 1 and 10 comes closest to the way you feel?",
    "question_options":[1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    }
]


def create_agent_response(respondent, questions):
    attempts = 3
    responses = {}

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

    for question in questions:
        question_answered = False
        prompt = base_prompt

        for attempt in range(attempts):
            options_text = ', '.join(map(str, question['question_options']))
            prompt += f"""
                Question: {question['question_text']}
                Options: {options_text}
                Please provide your answer from the options and give a reason.
                Answer:
                Reason:
                """

            data = {
                "model": "gpt-3.5-turbo-0613",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 1,
                "top_p": 1,
                "logprobs": 10
            }

            response = requests.post(url, headers=headers, data=json.dumps(data))
            generated_data = response.json()
            response_text = generated_data['choices'][0]['message']['content'].strip()

            if "Answer:" in response_text and "Reason:" in response_text:
                answer_start = response_text.find("Answer:") + 7
                answer_end = response_text.find("Reason:")
                answer = response_text[answer_start:answer_end].strip()
                reason = response_text[answer_end + 7:].strip()

                try:
                    parsed_answer = int(answer)
                    if parsed_answer in question["question_options"]:
                        reason_key = question["question_name"] + "_reason"
                        answer_key = question["question_name"] + "_answer"
                        responses[reason_key] = reason
                        responses[answer_key] = parsed_answer
                        question_answered = True
                        break
                except ValueError:
                    continue

        if not question_answered:
            reason_key = question["question_name"] + "_reason"
            answer_key = question["question_name"] + "_answer"
            responses[reason_key] = "No reason provided"
            responses[answer_key] = "No answer provided"

    return responses

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

df = pd.DataFrame(generated_dataset)
df.to_csv('.......csv', index=False)

print("Data has been written to output.csv")
