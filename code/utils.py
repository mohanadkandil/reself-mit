def create_gpt_input(df):
  df['journal_id'] = df['userId'] + '_' + df['dailyReflection.journalId']
  input = df[['journal_id', 'dailyReflection.text0', 'dailyReflection.text1', 'dailyReflection.text2', 'dailyReflection.text3', 'dailyReflection.text4']].copy()
  input.rename(columns={'dailyReflection.text0': 'paraphrase_0', 'dailyReflection.text1': 'paraphrase_1', 'dailyReflection.text2': 'paraphrase_2', 'dailyReflection.text3': 'paraphrase_3', 'dailyReflection.text4': 'paraphrase_4'}, inplace=True)
  return input

#working version
import requests
import pandas as pd
import json
from tqdm import tqdm

# Claude API call function
def call_claude(prompt, api_key):
    headers = {
        'x-api-key': api_key,
        'anthropic-version': '2023-06-01',
        'content-type': 'application/json'
    }
    payload = {
        "model": "claude-3-opus-20240229",
        "max_tokens": 4096,
        "temperature": 0.5,
        "messages": [{"role": "user", "content": prompt}]
    }

    response = requests.post('https://api.anthropic.com/v1/messages', headers=headers, json=payload)

    try:
        data = response.json()
    except Exception as e:
        raise RuntimeError(f"Failed to decode JSON: {e}\nRaw response: {response.text}")

    # Check structure
    if "content" not in data or not isinstance(data["content"], list):
        raise RuntimeError(f"Unexpected response format:\n{json.dumps(data, indent=2)}")

    return data["content"][0]["text"]




