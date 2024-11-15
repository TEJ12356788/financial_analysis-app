import streamlit as st
import pandas as pd
import pdfplumber
import matplotlib.pyplot as plt
from dotenv import load_dotenv
import os

load_dotenv()
GOOGLE_API_KEY = os.getenv("AIzaSyD4hZdqWNVQaC2yQh-yXsw4VzFmmm8qRLQ")

# Main application
def main():
    st.title("Financial Analysis App")
    
    file = st.file_uploader("Upload a financial document", type=["pdf", "csv", "xlsx"])
    
    if file:
        # Add processing logic here
        st.success("File uploaded successfully!")
        st.write("Processing the document...")

if __name__ == "__main__":
    main()
