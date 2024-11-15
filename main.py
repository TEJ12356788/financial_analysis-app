import streamlit as st
import pandas as pd
from io import BytesIO
from fpdf import FPDF
import datetime

# Function to load data
def load_data(uploaded_file):
    try:
        if uploaded_file.name.endswith('.csv'):
            data = pd.read_csv(uploaded_file)
        elif uploaded_file.name.endswith('.pdf'):
            data = extract_text_from_pdf(uploaded_file)  # You may need to implement a text extraction function
        else:
            st.error("Unsupported file type")
            return None
        return data
    except Exception as e:
        st.error(f"An error occurred while loading the file: {e}")
        return None

# Function to generate a report summary
def generate_report(data, date_column, numeric_columns):
    report = {}

    # General information
    report['Total Rows'] = len(data)
    report['Total Columns'] = len(data.columns)

    # Date-related analysis
    if date_column:
        data[date_column] = pd.to_datetime(data[date_column], errors='coerce')
        report['Date Range'] = f"{data[date_column].min()} to {data[date_column].max()}"

    # Numeric analysis
    for column in numeric_columns:
        column_data = data[column]
        report[f'{column} - Total'] = column_data.sum()
        report[f'{column} - Mean'] = column_data.mean()
        report[f'{column} - Max'] = column_data.max()
        report[f'{column} - Min'] = column_data.min()

    return report

# Function to convert the report to a text format for display
def format_report(report):
    report_text = ""
    for key, value in report.items():
        report_text += f"{key}: {value}\n"
    return report_text

# Function to generate PDF report
def generate_pdf_report(report_data):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.set_font("Arial", style="B", size=16)
    pdf.cell(0, 10, "Financial Analysis Report", ln=True, align='C')

    pdf.set_font("Arial", size=12)
    for section, content in report_data.items():
        pdf.set_font("Arial", style="B", size=14)
        pdf.cell(0, 10, section, ln=True)
        pdf.set_font("Arial", size=12)
        pdf.multi_cell(0, 10, str(content))
    
    # Save the PDF data to a BytesIO object
    pdf_buffer = BytesIO()
    pdf.output(pdf_buffer, 'S').encode('latin1')
    pdf_buffer.seek(0)
    return pdf_buffer

# Streamlit interface
st.title("Financial Document Analysis Tool")

# File upload
uploaded_file = st.file_uploader("Upload a CSV or PDF file", type=['csv', 'pdf'])
if uploaded_file is not None:
    data = load_data(uploaded_file)
    if data is not None:
        st.write("Data Preview:")
        st.write(data.head())

        # Column selection for analysis
        date_column = st.selectbox("Select the date column", [None] + list(data.columns))
        numeric_columns = st.multiselect("Select numeric columns for analysis", data.select_dtypes(include='number').columns)

        # Run analysis
        if st.button("Analyze"):
            with st.spinner("Analyzing..."):
                try:
                    report_content = generate_report(data, date_column, numeric_columns)
                    formatted_report = format_report(report_content)
                    st.text_area("Report Summary", formatted_report, height=200)
                except Exception as e:
                    st.error(f"An error occurred during analysis: {e}")

        # Generate and Download PDF Report
        st.subheader("Download Report")
        pdf_buffer = generate_pdf_report(report_content)

        st.download_button(
            label="Download PDF Report",
            data=pdf_buffer,
            file_name="financial_analysis_report.pdf",
            mime="application/pdf"
        )
