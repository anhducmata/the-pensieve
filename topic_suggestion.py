import requests

# Replace with your ChatGPT API endpoint and secret key
API_ENDPOINT = "https://api.openai.com/v1/completions"
OPENAI_KEY = "YOUR_OPENAI_KEY"

# Keywords associated with different conversation topics (modify as needed)
conversation_topics = {
  "hobbies": ["favorite things", "like to do for fun", "passionate about"],
  "travel": ["travel destinations", "favorite places", "dream vacation"]
}

def get_chatgpt_suggestion(query):
  # Prepare request data
  data = {
      "model": "text-davinci-003",  # Choose a suitable ChatGPT model
      "prompt": f"Based on the user's query '{query}', what could be the potential conversation topic?",
      "max_tokens": 50,  # Limit the number of words in the response
      "n": 1,  # Generate only 1 response
      "stop": None,  # No specific stop sequence needed
      "temperature": 0.7,  # Control creativity vs informativeness (adjust as needed)
  }

  # Set headers with your OpenAI API key
  headers = {
      "Content-Type": "application/json",
      "Authorization": f"Bearer {OPENAI_KEY}"
  }

  # Send request to ChatGPT API
  response = requests.post(API_ENDPOINT, headers=headers, json=data)

  # Extract suggested topic from the response (assuming the first word)
  if response.status_code == 200:
    try:
      completion = response.json()["choices"][0]["text"].strip()
      suggested_topic = completion.split()[0].lower()  # Extract first word as the topic
      return suggested_topic
    except (IndexError, KeyError):
      pass  # Handle potential errors in parsing the response

  # Return None on errors or if no suggestion is found
  return None

def filter_topic(suggested_topic):
  # Check if the suggested topic matches any keyword list from conversation_topics
  for topic, keywords in conversation_topics.items():
    for keyword in keywords:
      if keyword in suggested_topic:
        return topic
  # No matching topic found based on keywords
  return None

def main():
  # Example usage
  user_query = "What are some fun things to do in your free time?"
  suggested_topic = get_chatgpt_suggestion(user_query)
  if suggested_topic:
    filtered_topic = filter_topic(suggested_topic)
    if filtered_topic:
      print(f"Potential conversation topic based on ChatGPT suggestion and filtering: {filtered_topic}")
    else:
      print(f"ChatGPT suggested '{suggested_topic}' but it doesn't match any conversation topics based on keywords.")
  else:
    print("ChatGPT failed to suggest a conversation topic.")

if __name__ == "__main__":
  main()
