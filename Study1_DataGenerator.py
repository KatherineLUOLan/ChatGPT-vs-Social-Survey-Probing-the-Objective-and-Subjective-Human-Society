#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Oct 29 23:34:25 2023

@author: luyu
"""

import csv
import requests
import json

url="https://gpt-api.hkust-gz.edu.cn/v1/chat/completions"
headers = {
   "Content-Type":"application/json",
   "Authorization": "f6e02092decc4a7fa1f6d2bc5b58132ae7a921e9265243259c41bea84742c571" 
    }
prompt_template="Your task is to generate a survey dataset representing the US population in 2020. The sample size is 20. The dataset should include 6 demographic variables for a respondent: ”””1.sex(male, female)”””,””” 2.age”””, “””3.ethnic group(White; Black or African American; American Indian and Alaska Native; Asian; Hispanic or Latino; Native Hawaiian and Other Pacific Islander; Some Other Race; Two or more races)”””, “””4.the highest educational level that you have attained (Less than 9th grade; 9th to 12th grade, no diploma; High school graduate; Some college, no degree; Associate's degree; Bachelor's degree; Graduate or professional degree)”””, “””5. Annual household income(Less than $10,000; $10,000 to $14,999; $15,000 to $24,999; $25,000 to $34,999; $35,000 to $49,999; $50,000 to $74,999; $75,000 to $99,999; $100,000 to $149,999; $150,000 to $199,999; $200,000 or more)”””, ””” 6. region(urban; rural)”””. Here is an example of one data record: [male; 25; White; Some college, no degree; $50,000 to $74,999; urban]. Choose your answers only from the options provided, and please keep your letter case consistent with the example. After generating, only show the data you generated without additional words.  The format must be a JSON string representing a multi-dimensional array. Also, make sure that it is an array of arrays with no objects, like in a spreadsheet. Remember, the records should closely reflect the actual population demographic distribution in 2020."
# Variables for record generation
total_records_needed = 200
records_per_request = 20
generated_dataset = []

# Generate records
while len(generated_dataset) < total_records_needed:
    # Update the prompt with any necessary dynamic content
    prompt = prompt_template
    data = {
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 1,
        "top_p":1,
        "max tokens": 1
    }

    # Send the request to the API
    response = requests.post(url, headers=headers, data=json.dumps(data))

    # Check if the response is successful
    if response.status_code == 200:
        generated_data = response.json()
        # Extract the content from the response
        data_content = generated_data['choices'][0]['message']['content']
        # Parse the JSON string to a Python object (list of lists)
        data_batch = json.loads(data_content)
        # Extend the generated dataset with the new data batch
        generated_dataset.extend(data_batch)
        # Break out of the loop if we have enough records
        if len(generated_dataset) >= total_records_needed:
            break
    else:
        print("Failed to retrieve data:", response.status_code)
        break

# Write the records to a CSV file
csv_file = '200_30.csv'
with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerows(generated_dataset)
print(f"{len(generated_dataset)} records stored in {csv_file}")