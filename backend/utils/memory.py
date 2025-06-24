from langchain.memory import ConversationBufferMemory
from langchain.memory.chat_message_histories import ChatMessageHistory

memory = ConversationBufferMemory(
    return_messages=True,
    chat_memory=ChatMessageHistory()
) 