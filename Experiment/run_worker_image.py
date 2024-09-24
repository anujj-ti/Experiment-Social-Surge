import json
import requests
from prompts import worker_run_system_prompt_for_image
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
    with open('data/data_image.json', 'r') as file:
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

    system_prompt = worker_run_system_prompt_for_image.format(
        channel_name=channel_name,
        channel_details=channel_details,
        additional_context=additional_context,
        video_details=video_details,
        second_brain=second_brain,
        brand_compass_report=brand_compass_report,
        graph_input_string=graph_input_string,
        feedback_string=feedback_string,
        user_prompt=user_prompt,
    )
    messages = [
        {
            "role": "system",
            "content": system_prompt
        },
        {
            "role": "user",
            "content": "Generate a crisp image description for the designer tool"
        },
        {
            "role": "assistant",
            "content": "Image description for the designer tool is as follows:"
        }
    ]

    response_data = chat_completion(messages, max_tokens=4096)

    image_description = None
    chain_of_thoughts = None

    try:
        response_dict = json.loads(response_data)
        image_description = response_dict.get("image_description", "No description found")
        chain_of_thoughts = response_dict.get("chain_of_thoughts", "No chain of thoughts found")
    except json.JSONDecodeError:
        print("Failed to decode JSON")

    # Now you can access the variables here
    if image_description is not None:
        print("Image Description:", image_description)

    if chain_of_thoughts is not None:
        print("Chain of Thoughts:", chain_of_thoughts)



    with open("response/response_data_image.txt", "w") as f:
        f.write(response_data)