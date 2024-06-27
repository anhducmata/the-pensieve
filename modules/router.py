import openai

def call_llm(prompt: str, api_key: str) -> str:
    openai.api_key = api_key
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=50
    )
    return response.choices[0].text.strip()

def needs_rag_lookup(query: str, api_key: str) -> bool:
    prompt = f"Does the following query require a lookup in an external knowledge base? Answer 'yes' or 'no'. Query: '{query}'"
    decision = call_llm(prompt, api_key).lower()
    return decision == "yes"