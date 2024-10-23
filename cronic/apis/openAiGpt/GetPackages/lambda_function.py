import requests
import os
import json
from openai import OpenAI

client = OpenAI()

SYSTEMVAL = "Generate a VAPT (Vulnerability Assessment and Penetration Testing) report utilizing the MITRE ATT&CK framework. The report should include information based on the input of outputs from Kali Linux commands and various security tools. Follow the provided JSON structure for the report. # Steps 1. **Project Information**: Gather key project information such as client name, assessment date, and other relevant details. 2. **Executive Summary**: Provide a brief overview of the VAPT process, testing dates, and a summary of issues found, categorized by severity. 3. **Objectives**: List the main objectives of the VAPT process. 4. **Methodology**: Describe the methodology used, including stages and tools used. 5. **Scope of Testing**: Clearly define the scope of the test, including the target and areas tested. 6. **Findings and Analysis**: Summarize and provide detailed analysis of vulnerabilities found during testing. 7. **Risk Assessment**: Outline recommendations for actions based on the severity of risks identified. 8. **Recommendations**: Offer solutions and recommendations for identified issues. 9. **Conclusion**: Present a conclusion summarizing the findings and the impact of vulnerabilities. 10. **Appendix**: List the tools used and provide references for further information. # Output Format - The output should be in JSON format as defined below: ```json {  \"project_info \": {  \"client_name \":  \"[Client Company] \",  \"assessment_date \":  \"[Date] \",  \"report_date \":  \"[Date] \",  \"project_name \":  \"Website VAPT Report \" },  \"executive_summary \": {  \"description \":  \"[Brief description of the VAPT process] \",  \"testing_date \":  \"[Start and End Date] \",  \"total_issues_found \": {  \"total \":  \"[Number] \",  \"critical \":  \"[Number] \",  \"high \":  \"[Number] \",  \"medium \":  \"[Number] \",  \"low \":  \"[Number] \" } },  \"objectives \": [  \"[Objective 1] \",  \"[Objective 2] \",  \"[Objective 3] \" ],  \"methodology \": {  \"description \":  \"[Methodology description] \",  \"stages \": [  \"[Stage 1: Reconnaissance] \",  \"[Stage 2: Vulnerability Scanning] \",  \"[Stage 3: Exploitation] \",  \"[Stage 4: Reporting] \" ],  \"tools_used \": [  \"[Tool 1] \",  \"[Tool 2] \",  \"[Tool 3] \",  \"[Tool 4] \" ] },  \"scope_of_testing \": {  \"target \":  \"[Website URL] \",  \"tested_areas \": [  \"[Area 1] \",  \"[Area 2] \",  \"[Area 3] \",  \"[Area 4] \" ],  \"out_of_scope \": [  \"[Out-of-scope 1] \",  \"[Out-of-scope 2] \" ] },  \"findings_and_analysis \": {  \"vulnerability_summary \": [ {  \"severity \":  \"[Critical] \",  \"vulnerability \":  \"[Vulnerability Name] \",  \"count \":  \"[Number] \" }, {  \"severity \":  \"[High] \",  \"vulnerability \":  \"[Vulnerability Name] \",  \"count \":  \"[Number] \" }, {  \"severity \":  \"[Medium] \",  \"vulnerability \":  \"[Vulnerability Name] \",  \"count \":  \"[Number] \" }, {  \"severity \":  \"[Low] \",  \"vulnerability \":  \"[Vulnerability Name] \",  \"count \":  \"[Number] \" } ],  \"detailed_findings \": [ {  \"id \":  \"[Finding ID] \",  \"vulnerability_name \":  \"[Vulnerability Name] \",  \"severity \":  \"[Severity] \",  \"description \":  \"[Vulnerability description] \",  \"affected_url \":  \"[Affected URL] \",  \"proof_of_concept \":  \"[Proof of Concept] \",  \"impact \":  \"[Impact of vulnerability] \",  \"recommendation \":  \"[Recommendation] \" } ] },  \"risk_assessment \": [ {  \"severity \":  \"[Severity] \",  \"action_required \":  \"[Action required based on severity] \" } ],  \"recommendations \": [ {  \"issue \":  \"[Issue] \",  \"recommendation \":  \"[Recommendation] \" } ],  \"conclusion \": {  \"summary \":  \"[Conclusion summary] \" },  \"appendix \": {  \"tools_used \": [  \"[Tool 1] \",  \"[Tool 2] \",  \"[Tool 3] \" ],  \"references \": [  \"[Reference 1] \",  \"[Reference 2] \" ] } } ``` # Notes - Ensure that all placeholders are replaced with specific, accurate data based on your findings and the output from your tools. - Use clear, concise language tailored to a professional audience. - Ensure consistency and accuracy throughout the report, especially in categorizing and scoring vulnerabilities. - Identify the current stage by understanding the tools used and only include till that stage and only the tools used"


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
    data = event.get("body", "")
    data = getCommand(data)
    print(data)
    rawJason = data.choices[0].message.content
    jsonData = extractJsonText(rawJason)
    print("------------------------------------------")
    return {
        'statusCode': 200,
        'body': json.dumps(jsonData)
        }
