import os


from dotenv import find_dotenv, load_dotenv
from flask import Flask, request
from flask_socketio import SocketIO, send
from flask_socketio import SocketIO, emit
from main_proto import Chat_With_PDFs_and_Summarize
import hashlib
import glob
from langchain.document_loaders import PyPDFLoader
from langchain.chat_models import ChatOpenAI
# from langchain import OpenAI
from langchain.docstore.document import Document
from langchain.chains.summarize import load_summarize_chain
from modify import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.chains import RetrievalQA

# local server object sender im using.
""" It is important to encode using b before sending it and .decode will save it properly  """
import socket
from rich import print
from rich.console import Console
from rich.table import Table

load_dotenv()  # load variables from .env file
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Initialize the chatbot
chatbot = Chat_With_PDFs_and_Summarize()

flask_app = Flask(__name__)
socketio = SocketIO(flask_app, cors_allowed_origins="*")

@socketio.on('message')
def handle_message(data):
    """
    Handle incoming SocketIO messages.
    """
    query = data['query']
    answer = chatbot.ask_question(query)
    emit('message', {'answer': answer})

@flask_app.route("/pdf", methods=["POST"])
def handle_pdf():
    """
    Handle incoming PDF data.
    """
    pdf_data = request.data
    page_range = request.json.get('page_range')
    chatbot.load_document(pdf_data, page_range)
    return 'PDF loaded.', 200

@flask_app.route("/summary", methods=["GET"])
def handle_summary():
    """
    Generate a summary of the loaded document.
    """
    summary = chatbot.summarize()
    return {'summary': summary}, 200

# Run the Flask app
if __name__ == "__main__":
    socketio.run(flask_app)

