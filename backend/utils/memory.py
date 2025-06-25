from langchain.memory import ConversationBufferMemory
from langchain.memory.chat_message_histories import ChatMessageHistory

# memory = ConversationBufferMemory(
#     return_messages=True,
#     chat_memory=ChatMessageHistory()
# ) 
# utils/memory.py

memory = ConversationBufferMemory(
    memory_key="chat_history",
    input_key="input",
    output_key="output",
    return_messages=True
)