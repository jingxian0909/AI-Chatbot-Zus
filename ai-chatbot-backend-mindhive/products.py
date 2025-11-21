import os
from dotenv import load_dotenv
from fastapi import APIRouter, Query
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableSequence, RunnablePassthrough
from langchain_pinecone import PineconeVectorStore, Pinecone
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from pinecone import Pinecone, ServerlessSpec

load_dotenv()
router = APIRouter(tags=["Products"])
conv_history = []
index_name  = "pinecone-chatbot"  

def pineconeConnect() :
    pinecone_api_key = os.environ["PINECONE_API_KEY"] 
    openai_api_key = os.environ["OPENAI_API_KEY"]  

    client = Pinecone(pinecone_api_key) 
    index = client.Index(index_name)
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    vectorstore = PineconeVectorStore(
        index=index,
        embedding=embeddings
    )
    retriever = vectorstore.as_retriever(
        search_kwargs={"k": 3, "score_threshold": 0.4}
    )
    return retriever

def combineAnswer(answers):
    return "\n\n".join(answer.page_content for answer in answers)

def formatConvHistory(messages):
    return (
        "\n".join(
            f"Human: {message}" if i%2==0 else f"AI: {message}"
            for i, message in enumerate(messages)
        )
    )

@router.get("/products")
def main(query: str):
    retriever = pineconeConnect()
    llm = ChatOpenAI(model="gpt-5-mini-2025-08-07")
    standaloneQ_template = ("Given some conversation history (if any) and a question, convert the question to a standalone question. " 
                            "conversation history: {conv_history}"
                            "question: {question}"
                            "standalone question:")
    standaloneQ_prompt = PromptTemplate.from_template(standaloneQ_template)

    answer_template = ("You are a helpful and enthusiastic support bot who can answer a given question about Zus products based on the "
    "context provided and the conversation history. Try to find the answer in the context. "
    "If the answer is not given in the context, try to find the answe in the conversation history if possible. "
    "If you really don't know the answer, say I'm sorry, I don't know the answer to that." 
    "And direct the questioner to email support@zuscoffee.com."
    "Don't try to make up an answer. Always speak as if you were chatting to a friend."
    "Dont ask follow up question, just answer the user question and end."
    "context: {context}"
    "conv_history: {conv_history}"
    "question: {question}"
    "answer: ")

    answer_prompt = PromptTemplate.from_template(answer_template)

    standaloneQ_chain = standaloneQ_prompt.pipe(llm).pipe(StrOutputParser())

    answer_chain = answer_prompt.pipe(llm).pipe(StrOutputParser())

    retriever_chain = RunnableSequence(
        lambda x: x["standaloneQ"],
        retriever,
        combineAnswer
    )

    chain = RunnableSequence(
        {
            "standaloneQ" : standaloneQ_chain,
            "ori_input" : RunnablePassthrough()
        },
        {   "context" : retriever_chain,
            "question": lambda x: x["ori_input"]["question"],
            "conv_history": lambda x: x["ori_input"]["conv_history"],
        },
        answer_chain
    )


    response = chain.invoke(
        {
            "question": query,
            "conv_history": formatConvHistory(conv_history)
        }
    )

    conv_history.append(query)
    conv_history.append(response)
    return response

if __name__ == "__main__":
    main("Do you have blue tumblers from ZUS?")