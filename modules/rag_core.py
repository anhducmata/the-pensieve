import openai
import logging

openai.api_key = 'your-api-key-here'

def increase_information_density(content):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": ("You are a data processing assistant. Your task is to "
                                "extract meaningful information from a scraped web page. "
                                "This information will serve as a knowledge base for further "
                                "customer inquiries. Be sure to include all possible relevant "
                                "information that could be queried by customers. The output "
                                "should be text-only (no lists) separated by paragraphs."),
                },
                {"role": "user", "content": content},
            ],
            temperature=0
        )
        return response.choices[0].message['content']
    except Exception as e:
        logging.error(f"Error in increase_information_density: {e}")
        return ""

def hierarchical_index_retrieval(documents):
    summaries = []
    for doc in documents:
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": ("Summarize the following document content to streamline "
                                    "identification of relevant information."),
                    },
                    {"role": "user", "content": doc},
                ],
                temperature=0
            )
            summaries.append(response.choices[0].message['content'])
        except Exception as e:
            logging.error(f"Error in hierarchical_index_retrieval for document: {e}")
    return summaries

def generate_hypothetical_qa_pairs(content):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": ("Analyze the provided text and create questions a customer could ask "
                                "a chatbot about the information in the text. Provide answers based strictly "
                                "on the information in the text. Use Q: for questions and A: for answers."),
                },
                {"role": "user", "content": content},
            ],
            temperature=0
        )
        return response.choices[0].message['content']
    except Exception as e:
        logging.error(f"Error in generate_hypothetical_qa_pairs: {e}")
        return ""

def deduplicate_information(chunks):
    unique_chunks = {}
    for chunk in chunks:
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": ("Identify and remove duplicated information in the following text. "
                                    "Provide a distilled version containing unique information."),
                    },
                    {"role": "user", "content": chunk},
                ],
                temperature=0
            )
            unique_chunk = response.choices[0].message['content']
            if unique_chunk not in unique_chunks:
                unique_chunks[unique_chunk] = 1
        except Exception as e:
            logging.error(f"Error in deduplicate_information for chunk: {e}")
    return list(unique_chunks.keys())

def test_chunking_strategies(documents):
    strategies = {
        "1000_char_200_overlap": [],
        "500_char_100_overlap": [],
        "paragraphs": [],
        "sentences": [],
        "hypothetical_questions": []
    }
    
    for doc in documents:
        # 1000 characters with 200 characters overlap
        for i in range(0, len(doc), 800):
            strategies["1000_char_200_overlap"].append(doc[i:i+1000])
        
        # 500 characters with 100 characters overlap
        for i in range(0, len(doc), 400):
            strategies["500_char_100_overlap"].append(doc[i:i+500])
        
        # Paragraphs split
        paragraphs = doc.split('\n\n')
        strategies["paragraphs"].extend(paragraphs)
        
        # Sentences split (using a simple sentence splitter for demonstration)
        sentences = doc.split('. ')
        strategies["sentences"].extend(sentences)
        
        # Hypothetical questions
        strategies["hypothetical_questions"].append(generate_hypothetical_qa_pairs(doc))
    
    return strategies

def optimize_search_query(conversation):
    try:
        system_prompt = ("You are examining a conversation between a customer and a chatbot. "
                         "A documentation lookup is necessary to respond to the customer. "
                         "Construct a search query to retrieve relevant documentation.")
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": conversation},
            ],
            temperature=0
        )
        return response.choices[0].message['content']
    except Exception as e:
        logging.error(f"Error in optimize_search_query: {e}")
        return ""

def generate_hypothetical_document(query):
    try:
        prompt = ('Please generate a 1000 character chunk of text that could be found on a website '
                  'to help answer the following query: {}'.format(query))
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "user", "content": prompt},
            ],
            temperature=0
        )
        return response.choices[0].message['content']
    except Exception as e:
        logging.error(f"Error in generate_hypothetical_document: {e}")
        return ""

def decide_rag_lookup(query):
    try:
        system_prompt = "Is a documentation lookup necessary to answer the user's question? Respond with True or False."
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query},
            ],
            temperature=0
        )
        return response.choices[0].message['content'].strip().lower() == "true"
    except Exception as e:
        logging.error(f"Error in decide_rag_lookup: {e}")
        return False

def rerank_results(results, query):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": "Rerank the following search results based on relevance to the query: {}".format(query),
                },
                {"role": "user", "content": "\n".join(results)},
            ],
            temperature=0
        )
        return response.choices[0].message['content']
    except Exception as e:
        logging.error(f"Error in rerank_results: {e}")
        return results

def compress_prompt(prompt):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": "Compress the following prompt to retain only the most important information.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0
        )
        return response.choices[0].message['content']
    except Exception as e:
        logging.error(f"Error in compress_prompt: {e}")
        return prompt

def score_retrieved_documents(documents, query):
    relevant_docs = []
    for doc in documents:
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": "Classify the following document as correct/relevant, ambiguous, or incorrect for the given query: {}".format(query),
                    },
                    {"role": "user", "content": doc},
                ],
                temperature=0
            )
            classification = response.choices[0].message['content'].strip().lower()
            if classification == "correct/relevant":
                relevant_docs.append(doc)
        except Exception as e:
            logging.error(f"Error in score_retrieved_documents for document: {e}")
    return relevant_docs

def chain_of_thought_prompting(documents):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": "Use chain-of-thought reasoning to process the following documents and extract relevant information.",
                },
                {"role": "user", "content": "\n".join(documents)},
            ],
            temperature=0
        )
        return response.choices[0].message['content']
    except Exception as e:
        logging.error(f"Error in chain_of_thought_prompting: {e}")
        return ""

def self_rag(query, context):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": "Determine if augmenting the following query with retrieved passages would be helpful.",
                },
                {"role": "user", "content": query},
                {"role": "system", "content": context},
            ],
            temperature=0
        )
        return response.choices[0].message['content']
    except Exception as e:
        logging.error(f"Error in self_rag: {e}")
        return ""

def fine_tune_ignore_irrelevant(contexts):
    relevant_contexts = []
    for context in contexts:
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": "Determine if the following context is relevant to the query.",
                    },
                    {"role": "user", "content": context},
                ],
                temperature=0
            )
            if response.choices[0].message['content'].strip().lower() == "relevant":
                relevant_contexts.append(context)
        except Exception as e:
            logging.error(f"Error in fine_tune_ignore_irrelevant for context: {e}")
    return relevant_contexts

def nli_robustness(query, context):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": "Determine if the retrieved context is relevant to the given query.",
                },
                {"role": "user", "content": "Query: {}\nContext: {}".format(query, context)},
            ],
            temperature=0
        )
        if response.choices[0].message['content'].strip().lower() == "relevant":
            return context
    except Exception as e:
        logging.error(f"Error in nli_robustness: {e}")
        return False
