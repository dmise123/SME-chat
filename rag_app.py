import streamlit as st
import pandas as pd
import os
from llama_index.llms.ollama import Ollama
from pathlib import Path
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex, Settings
from llama_index.embeddings.fastembed import FastEmbedEmbedding
from llama_index.core.llms import ChatMessage
from llama_index.core.storage.chat_store import SimpleChatStore
from llama_index.core.memory import ChatMemoryBuffer
from llama_index.core.chat_engine import CondensePlusContextChatEngine


# Function to save order to CSV
def save_order(order_data):
    order_csv_path = "order/order.csv"
    order_df = pd.DataFrame(order_data)
    if os.path.exists(order_csv_path):
        order_df.to_csv(order_csv_path, mode='a', header=False, index=False)
    else:
        order_df.to_csv(order_csv_path, index=False)


# Function to process order based on user input and bakery menu
def process_order(user_input, bakery_data):
    ordered_items = []
    total_price = 0

    # Tokenize user input and match it with available bakery items
    for _, row in bakery_data.iterrows():
        item_name = row["Item"].lower()
        if item_name in user_input.lower():
            ordered_items.append({"Item": row["Item"], "Price": row["Price"]})
            total_price += row["Price"]

    if ordered_items:
        return ordered_items, total_price
    return None, 0


class Chatbot:
    def __init__(self, llm="llama3.1:latest", embedding_model="intfloat/multilingual-e5-large", vector_store=None):
        self.Settings = self.set_setting(llm, embedding_model)

        # Indexing
        self.index = self.load_data()

        # Memory
        self.memory = self.create_memory()

        # Chat Engine
        self.chat_engine = self.create_chat_engine(self.index)

    def set_setting(self, llm, embedding_model):
        Settings.llm = Ollama(model=llm, base_url="http://127.0.0.1:11434")
        Settings.embed_model = FastEmbedEmbedding(
            model_name=embedding_model, cache_dir="./fastembed_cache")
        Settings.system_prompt = """
                                You are a bakery customer service assistant. 
                                You will help customers with product inquiries, order status, promotions, 
                                and other general bakery-related questions. 
                                If you don't know the answer, politely let the customer know.
                                """

        return Settings

    @st.cache_resource(show_spinner=False)
    def load_data(_self, vector_store=None):
        with st.spinner(text="Loading bakery-related documents..."):
            # Read & load document from folder
            reader = SimpleDirectoryReader(input_dir="./docs", recursive=True)
            documents = reader.load_data()

        if vector_store is None:
            index = VectorStoreIndex.from_documents(documents)
        return index

    def set_chat_history(self, messages):
        self.chat_history = [ChatMessage(role=message["role"], content=message["content"]) for message in messages]
        self.chat_store.store = {"chat_history": self.chat_history}

    def create_memory(self):
        self.chat_store = SimpleChatStore()
        return ChatMemoryBuffer.from_defaults(chat_store=self.chat_store, chat_store_key="chat_history", token_limit=16000)

    def create_chat_engine(self, index):
        return CondensePlusContextChatEngine(
            verbose=True,
            memory=self.memory,
            retriever=index.as_retriever(),
            llm=Settings.llm
        )


# Main Program
st.title("Bakery Customer Service Chatbot")
chatbot = Chatbot()

# Load bakery data from CSV
bakery_data_path = "docs/data.csv"
bakery_data = pd.read_csv(bakery_data_path)

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant",
         "content": "Hello there 👋!\n\n Good to see you, Welcome to our Bakery! How can I assist you today? Feel free to ask me 😁"}
    ]

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

chatbot.set_chat_history(st.session_state.messages)

# React to user input
if prompt := st.chat_input("What is up?"):
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Process order based on user input
    ordered_items, total_price = process_order(prompt, bakery_data)

    # Respond based on whether items were found in the bakery menu
    if ordered_items:
        response_content = f"Your order:\n\n"
        for item in ordered_items:
            response_content += f"- {item['Item']}: ${item['Price']}\n"
        response_content += f"\nTotal: ${total_price:.2f}"

        # Save order to CSV
        save_order(ordered_items)

    else:
        # Call the chatbot's response engine if it's not an order
        response = chatbot.chat_engine.chat(prompt)
        response_content = response.response

    # Display assistant's response
    with st.chat_message("assistant"):
        st.markdown(response_content)

    # Add assistant message to chat history
    st.session_state.messages.append(
        {"role": "assistant", "content": response_content})
