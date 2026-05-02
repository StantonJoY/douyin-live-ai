import openai
from config import LLM_API_KEY,LLM_API_URL,LLM_MODEL
client = openai.OpenAI(
  api_key=LLM_API_KEY,
  base_url=LLM_API_URL
)

response = client.chat.completions.create(
  model=LLM_MODEL,
  messages=[
      {"role": "user", "content": "Hello, how are you?"}
  ]
)

print(response.choices[0].message.content)