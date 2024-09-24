import json
import requests
from prompts import worker_run_system_prompt_for_text
from anthropic import Anthropic
from dotenv import load_dotenv
import os

load_dotenv()

anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")

def chat_completion(messages, tools=[], model_name="claude-3-5-sonnet-20240620", temperature=0.1, max_tokens=8192):

    client = Anthropic(api_key=anthropic_api_key)

    print("calling claude")

    response = client.messages.create(
        model=model_name,
        messages=messages[1:],
        system=messages[0]["content"],
        temperature=temperature,
        max_tokens=max_tokens,
        tools=map(lambda tool: tool.get_schema(), tools),
        extra_headers={"anthropic-beta": "max-tokens-3-5-sonnet-2024-07-15"}
    )

    messages.append({"role": "assistant", "content": response.content})

    if response.stop_reason == "tool_use":
        print("tool_use happened!")
    
    response_data = response.content[0].text

    return response_data

if __name__ == "__main__":
    with open('data_text.json', 'r') as file:
        data = json.load(file)

    channel_name = data['channel_name']
    channel_details = data['channel_details']
    additional_context = data['additional_context']
    video_details = data['video_details']
    second_brain = data['second_brain']
    brand_compass_report = data['brand_compass_report']
    feedback_string = data['feedback_string']
    graph_input_string = data['graph_input_string']
    user_prompt = data['user_prompt']

    system_prompt = worker_run_system_prompt_for_text.format(
        channel_name=channel_name,
        channel_details=channel_details,
        additional_context=additional_context,
        video_details=video_details,
        second_brain=second_brain,
        brand_compass_report=brand_compass_report,
        feedback_string=feedback_string,
        graph_input_string=graph_input_string
    )

    messages = [
        {
            "role": "system",
            "content": system_prompt
        },
        {
            "role": "user",
            "content": user_prompt
        }
    ]

    response_data = chat_completion(messages)
    print(response_data)

    with open("response_data_text.txt", "w") as f:
        f.write(response_data)
