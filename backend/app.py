from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import os
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableParallel, RunnablePassthrough, RunnableLambda
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

vector_stores = {}

class ChatRequest(BaseModel):
    video_id: str
    question: str

@app.get("/")
async def root():
    return {"message": "YouTube RAG Chatbot API is running!"}

@app.post("/chat")
async def chat(request: ChatRequest):
    try:
        video_id = request.video_id
        question = request.question
        
        if video_id not in vector_stores:
            # Step 1: Indexing
            try:
                api = YouTubeTranscriptApi()
                transcript_list_data = api.fetch(video_id, languages=['en'])
                transcript = " ".join(chunk.text for chunk in transcript_list_data)
            except TranscriptsDisabled:
                raise HTTPException(status_code=400, detail="No captions available for this video.")
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Error fetching transcript: {str(e)}")
                
            splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
            chunks = splitter.create_documents([transcript])
            
            embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-2")
            vector_store = FAISS.from_documents(chunks, embeddings)
            vector_stores[video_id] = vector_store

        vector_store = vector_stores[video_id]
        
        # Step 2: Retrieval & Chain
        retriever = vector_store.as_retriever(search_type="similarity", search_kwargs={"k": 4})
        llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.2)
        
        prompt = PromptTemplate(
            template="""
              You are a helpful assistant.
              Answer ONLY from the provided transcript context.
              If the context is insufficient, just say you don't know.

              {context}
              Question: {question}
            """,
            input_variables = ['context', 'question']
        )
        
        def format_docs(retrieved_docs):
            return "\n\n".join(doc.page_content for doc in retrieved_docs)
        
        parallel_chain = RunnableParallel({
            'context': retriever | RunnableLambda(format_docs),
            'question': RunnablePassthrough()
        })
        
        parser = StrOutputParser()
        main_chain = parallel_chain | prompt | llm | parser
        
        answer = main_chain.invoke(question)
        return {"answer": answer}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server Error: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
