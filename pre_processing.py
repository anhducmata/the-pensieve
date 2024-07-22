import re
import autogen

llm_config = {
    "config_list": [{"model": "gpt-4o", "api_key": "sk-proj-AAAA"}],
}
self_agent_prompt = "A human admin. Interact with the planner to discuss the plan. Plan execution needs to be approved by this admin."
english_agent_prompt = "You are the English Agent. Your task is to correct any grammatical, spelling, or syntactical errors in the input. Ensure that the input is clear and correctly structured in English. Print the result"
emotion_agent_prompt =  """
You are the Relationship Emotion Agent. Your task is to analyze the user's input and determine the following:
1. The relationship between the user and the subjects mentioned.
2. The user's feelings about these subjects.
3. Any relevant context or background information that enriches the understanding of the user's emotions.

Format your response as follows:
Relationship: [Describe the relationship]
Feelings: [Describe the user's feelings]
Context: [Provide any additional context or background information]

Analyze the following input and provide a detailed response in the specified format:
"""

def pre_process_text(text, doEnrich=False):
  self_agent = autogen.UserProxyAgent(
    name="self_agent",
    human_input_mode="NEVER",
    code_execution_config=False,
    system_message=self_agent_prompt,
    default_auto_reply="Reply `TERMINATE` if the task is done.",
    llm_config=llm_config
  )

  english_agent = autogen.AssistantAgent(
    name="english_agent",
    system_message=english_agent_prompt,
    human_input_mode="NEVER",
    code_execution_config=False,
    llm_config=llm_config
  )

  emotion_agent = autogen.AssistantAgent(
    name="english_agent",
    system_message=emotion_agent_prompt,
    human_input_mode="NEVER",
    code_execution_config=False,
    llm_config=llm_config
  )

  if (doEnrich):
    agents = [self_agent, english_agent, emotion_agent]
  else:
    agents = [self_agent, english_agent]
  
  groupchat = autogen.GroupChat(
      agents=agents,
      messages=[],
      max_round=len(agents),
      speaker_selection_method="round_robin",
      allow_repeat_speaker=False,
    )
  manager = autogen.GroupChatManager(groupchat=groupchat, llm_config=llm_config)
  chat_result = self_agent.initiate_chat(
      manager, message=text
  )

  if (doEnrich):
    return f"""{text} - {chat_result.chat_history[-1]['content']}"""
  return chat_result.chat_history[-1]['content']
