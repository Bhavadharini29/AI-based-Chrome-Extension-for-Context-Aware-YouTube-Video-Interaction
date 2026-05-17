# YouTube RAG Chatbot

This project is a Chrome Extension that allows you to chat with any YouTube video based on its transcript using an AI RAG (Retrieval-Augmented Generation) backend.

## Project Structure

- `backend/`: Contains the Python FastAPI application that handles video transcription, embeddings, and LangChain setup.
- `extension/`: Contains the Chrome Extension UI built with HTML, CSS, and JS.

## Prerequisites

- Python 3.9+
- An OpenAI API Key (added in `backend/.env`)

## Setting Up the Backend

1. Open a terminal and navigate to the `backend` folder:
   ```bash
   cd backend
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the FastAPI backend server:
   ```bash
   uvicorn app:app --reload
   ```

The backend server will run on `http://localhost:8000`.

## Installing the Chrome Extension

1. Open Google Chrome and go to `chrome://extensions/`.
2. Enable **Developer mode** using the toggle switch in the top right corner.
3. Click on the **Load unpacked** button.
4. Select the `extension` folder from this project repository (`c:\Users\keert\OneDrive\Desktop\YTChatBot\extension`).
5. The extension "YouTube RAG Chatbot" will appear in your list.
6. Open any YouTube video page, click on the extension icon, and start asking questions!

## How it works

1. When you open the extension on a YouTube video, it grabs the `video_id` from the URL.
2. It sends your question and the `video_id` to the FastAPI backend.
3. The backend fetches the transcript using `youtube-transcript-api`.
4. The transcript is chunked and stored in a FAISS vector database using OpenAI embeddings.
5. LangChain uses a RAG pipeline with GPT-4o-mini to answer your question precisely based on the context from the video.
