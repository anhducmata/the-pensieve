from transformers import AutoTokenizer, AutoModelForCausalLM

# Load pre-trained model and tokenizer
model_name = "EleutherAI/gpt-neo-2.7B"
model = AutoModelForCausalLM.from_pretrained(model_name)
tokenizer = AutoTokenizer.from_pretrained(model_name)

# Encode the input prompt
prompt = "Can you tell me about your professional background and current role?"
inputs = tokenizer(prompt, return_tensors="pt")

# Generate text
outputs = model.generate(inputs['input_ids'], max_length=100)
generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)

print(generated_text)
