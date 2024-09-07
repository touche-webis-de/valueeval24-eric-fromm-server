from typing import List, Dict
import requests
import json
import sys
import os

import logging
import pandas as pd

from tqdm import tqdm
from tira.third_party_integrations import is_running_as_inference_server, get_input_directory_and_output_directory


url = 'https://llm.srv.webis.de/api/generate'

prompt_template = "Assess if the text relates to VALUE. Return only a JSON object with the attribute \"attained\" set to true if the text does relate, false if not. The text is as follows: TEXT"
values = {
    "Self-direction: thought": "SELF-DIRECTION-THOUGHT: Freedom to cultivate one’s own ideas and abilities",
    "Self-direction: action": "SELF-DIRECTION-ACTION: Freedom to determine one’s own actions",
    "Stimulation": "STIMULATION: Excitement, novelty, and change",
    "Hedonism": "HEDONISM: Pleasure and sensuous gratification",
    "Achievement": "ACHIEVEMENT: Success according to social standards",
    "Power: dominance": "POWER-DOMINANCE: Power through exercising control over people",
    "Power: resources": "POWER-RESOURCES: Power through control of material and social resources",
    "Face": "FACE: Security and power through maintaining one’s public image and avoiding humiliation",
    "Security: personal": "SECURITY-PERSONAL: Safety in one’s immediate environment",
    "Security: societal": "SECURITY-SOCIETAL: Safety and stability in the wider society",
    "Tradition": "TRADITION: Maintaining and preserving cultural, family, or religious traditions",
    "Conformity: rules": "CONFORMITY-RULES: Compliance with rules, laws, and formal obligations",
    "Conformity: interpersonal": "CONFORMITY-INTERPERSONAL: Avoidance of upsetting or harming other people",
    "Humility": "HUMILITY: Recognizing one’s insignificance in the larger scheme of things",
    "Benevolence: dependability": "BENEVOLENCE-DEPENDABILITY: Being a reliable and trustworthy member of the in-group",
    "Benevolence: caring": "BENEVOLENCE–CARING:Devotion to the welfare of in-group members",
    "Universalism: concern": "UNIVERSALISM-CONCERN: Commitment to equality, justice, and protection for all people",
    "Universalism: nature": "UNIVERSALISM-NATURE: Preservation of the natural environment",
    "Universalism: tolerance": "UNIVERSALISM-TOLERANCE: Acceptance and understanding of those who are different from oneself",
}


class NetworkError(Exception):
    pass


def query_text(text, progress) -> Dict[str, int]:
    if not text.endswith('.'):
        text += '.'
    base_prompt = prompt_template.replace("TEXT", text)
    result = {}
    for key, value in values.items():
        prompt = base_prompt.replace("VALUE", value)

        try:
            reply = requests.post(url, json={"model": "default", "prompt": prompt, "stream": False, "keep_alive": "1h"})
            reply_body = reply.json()
        except Exception as e:
            raise NetworkError(str(e))

        response_text: str = reply_body['response']
        delimiter = response_text.index('}')
        try:
            response = json.loads(response_text[:delimiter + 1])
        except json.JSONDecodeError:
            if is_running_as_inference_server():
                logging.error(f"Unable to parse response for {key}:\n{reply_body['response']}")
            else:
                progress.write(f"Unable to parse response for {key}:\n{reply_body['response']}")
            result[key] = 0
            continue

        result[key] = 1 if response['attained'] else 0
    return result


def predict(input_data: List[str]) -> List:
    with tqdm(input_data, desc="Sentences") as progress:
        responses = [query_text(text, progress) for text in progress]
    return responses


if __name__ == "__main__" and not is_running_as_inference_server():
    input_directory, output_dir = get_input_directory_and_output_directory('./dataset', default_output='./output')
    output_file = os.path.join(output_dir, "run.tsv")

    dataset = pd.read_csv(os.path.join(input_directory, "sentences.tsv"), sep='\t', header=0, index_col=None)

    prediction = predict(dataset['Text'].tolist())
    dataset = pd.concat([dataset.drop(['Text'], axis=1), pd.Series(prediction).apply(pd.Series)], axis=1)

    dataset.to_csv(output_file, sep='\t', header=True, index=False)
