import re

def preprocess_text(text):
  """
  This function preprocesses a given text entry for your Reminis bot.

  Args:
      text (str): A string containing a diary entry.

  Returns:
      list: A list of preprocessed words (tokens).
  """
  # 1. Lowercase conversion
  text = text.lower()

  # 2. Remove punctuation
  text = re.sub(r'[^\w\s]', '', text)

  # 3. Remove stop words (optional)
  stopwords = ['stop', 'the', 'to', 'and', 'a', 'in', 'it', 'is', 'I', 'that', 'had', 'on', 'for', 'were', 'was']
  tokens = text.split()
  tokens = [word for word in tokens if word not in stopwords]

  # 4. Tokenization (word-based)
  return tokens


def preprocess_data(entries):
  # Loop through entries, preprocess each entry using the preprocess_text function
  # Store the preprocessed entries in a new list
  preprocessed_entries = []
  for entry in entries:
    preprocessed_entries.append(preprocess_text(entry))
  return preprocessed_entries
