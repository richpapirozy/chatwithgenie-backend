from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from typing import List
# from langchain_core.documents import Documents
from chroma_utils import vectorstore
from dotenv import load_dotenv

retriever = vectorstore.as_retriever(search_kwargs = {"k": 2})
load_dotenv()

output_parser = StrOutputParser()

# set up prompts and chains
contextualize_q_system_prompt = (
    "Given a chat history and the latest User question "
    "which might reference contexxt in the chat history,"
    "formulate a standaolne question which can be understood"
    "without the chat history do not answer the question,"
    "just formulate it if needed and otherwise return it as it is"
)

contextualize_q_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", contextualize_q_system_prompt),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}")
    ]
)

qa_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful AI Assistant. Use the following context to answer the user's question"),
    ("system", "Context: {context}"),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{input}")
])

def get_rag_chain(model='gpt-4o-mini'):
    llm = ChatOpenAI(model=model)
    # retriever with contextualization for follow-up questions
    history_aware_retriever = create_history_aware_retriever(llm, retriever, contextualize_q_prompt)
    question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)
    # combining the cntext and question for final Rag-Chain
    rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)
    return rag_chain