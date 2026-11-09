
import ollama
import json


MODEL_NAME = "qwen2.5-coder:3b"


def generate_ai_response(prompt: str) -> dict:

    response = ollama.chat(
        model=MODEL_NAME,
        messages=[
            {
                "role": "system",
                "content": """
You are CodebaseGPT, an expert software engineer
and code reviewer.

Analyze repository information carefully.

Return valid JSON only.

Do not include markdown or explanations
outside the JSON.

Use exactly these keys:

{
    "project_overview": "string",
    "main_functionality": ["string"],
    "important_files": [
        {
            "file": "string",
            "purpose": "string"
        }
    ],
    "technologies": ["string"],
    "potential_issues": ["string"],
    "improvements": ["string"]
}

Rules:
1. Analyze only the provided repository information.
2. Do not invent files or features.
3. Identify actual issues only when supported by code.
4. If information is insufficient, mention it.
5. Keep explanations clear and concise.
6. Return valid JSON.
"""
            },
            {
                "role": "user",
                "content": prompt
            }
        ],

        format="json",

        options={
            "temperature": 0.2
        }
    )

    ai_response = response["message"]["content"]

    # Validate JSON response
    parsed_response = json.loads(ai_response)

    # Return formatted JSON string
    return parsed_response
