import requests
import os
import json
from openai import OpenAI

client = OpenAI()

SYSTEMVAL = os.getenv("SYSTEM_PROMPT","Null")

def extractJsonText(text):
    stack, json_objects = [], []
    start = 0
    in_string = False
    escape = False
    for i, char in enumerate(text):
        if char == '\\' and not escape:
            escape = True
            continue
        if char == '"' and not escape:
            in_string = not in_string
        escape = False
        if not in_string:
            if char == '{':
                if not stack:
                    start = i
                stack.append(char)
            elif char == '}':
                stack.pop()
                if not stack:
                    try:
                        json_object = json.loads(text[start:i + 1])
                        json_objects.append(json_object)
                    except json.JSONDecodeError:
                        print("ther was an error with the json")
                        continue

    return json_objects


def getCommand(endpoint):
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": [{"type": "text", "text": SYSTEMVAL}]},
            {"role": "user", "content": [{"type": "text", "text": endpoint}]},
        ],
        temperature=1,
        max_tokens=2048,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        response_format={"type": "text"},
    )
    return response

def lambda_handeler(event, context):
    websites = ['google.com','gmail.com']
    jsonList = dict()
    for web in websites:
        data = getCommand(web)
        rawJason = data.choices[0].message.content
        jsonData = extractJsonText(rawJason)
        print("------------------------------------------"+web)
        jsonList[web]=jsonData
        for js in jsonData:
            print(js.get('commands',"+++++++++++++++++++++++++++++++++++++++++"))
    return {
        'statusCode': 200,
        'body': json.dumps(jsonList)
    }
