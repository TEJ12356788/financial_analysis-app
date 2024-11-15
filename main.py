import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO
import pdfplumber
from fpdf import FPDF

# App Title
st.title("Financial Document Analysis with Growth Insights and PDF Reporting")

# Helper Function to Extract Table from PDF
def extract_pdf_table(pdf_file):
    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables()
            if tables:
                # Assume the first table is the relevant one
                df = pd.DataFrame(tables[0][1:], columns=tables[0][0])
                return df
    return None

# Helper Function to Clean and Normalize Column Names
def clean_column_names(df):
    df.columns = df.columns.str.strip()  # Remove leading/trailing spaces
    return df

# Helper Function to Calculate Growth Insights
def calculate_growth(df, salary_column, amount_column):
    # Convert non-numeric columns to NaN (use 'coerce' to handle errors)
    df[amount_column] = pd.to_numeric(df[amount_column], errors='coerce')
    
    # Check if the columns to be analyzed are numeric
    df = df.select_dtypes(include=[np.number])  # Ensure only numeric columns are used
    
    # Check that the salary and amount columns exist
    if salary_column in df.columns and amount_column in df.columns:
        # Calculate growth rate for the Total Amount
        df['Growth Rate'] = df[amount_column].pct_change() * 100  # Growth rate in percentage
    return df

# Helper Function to Generate PDF Report
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
        pdf.multi_cell(0, 10, content)

    # Use a BytesIO buffer to output the PDF data
    pdf_buffer = BytesIO()
    pdf.output(pdf_buffer, 'S').encode('latin1')
    pdf_buffer.seek(0)
    return pdf_buffer

# Upload Section
uploaded_file = st.file_uploader("Upload a financial document (CSV, Excel, or PDF)", type=["csv", "xlsx", "pdf"])

if uploaded_file:
    try:
        # Load Data
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        elif uploaded_file.name.endswith(".xlsx"):
            df = pd.read_excel(uploaded_file)
        elif uploaded_file.name.endswith(".pdf"):
            df = extract_pdf_table(uploaded_file)
        
        # Clean column names
        if df is not None:
            df = clean_column_names(df)

            # Display the DataFrame with nice styling
            st.markdown("### Uploaded Data Preview:")
            st.dataframe(df.style.highlight_max(axis=0))  # Highlights the maximum values for each column
            
            # Display column names to help users understand the data structure
            st.markdown("### Column Names:")
            st.write(df.columns)

            # Explicit column mapping (based on the output you shared)
            column_mapping = {
                'Salary Amount': 'Salary',
                'Total Amount': 'Total Amount'
            }

            # Check for columns by mapping
            mapped_columns = {new_col: old_col for old_col, new_col in column_mapping.items() if old_col in df.columns}

            # Directly use the mapped columns without displaying them
            salary_column = mapped_columns.get('Salary', None)
            amount_column = mapped_columns.get('Total Amount', None)

            if salary_column and amount_column:
                # Calculate Growth Insights using the mapped columns
                df = calculate_growth(df, salary_column, amount_column)

                # Display the growth insights in a styled table
                st.markdown("### Growth Insights:")
                st.dataframe(df[[salary_column, amount_column, 'Growth Rate']].style.format({salary_column: "{:,.0f}", amount_column: "{:,.2f}", 'Growth Rate': "{:.2f}%"}))

                # Plot the Growth Insights
                st.markdown("### Growth Insights Visualization:")
                fig, ax = plt.subplots(figsize=(10, 6))
                ax.plot(df[salary_column], df[amount_column], label="Total Amount", marker='o')
                ax.set_xlabel('Salary')
                ax.set_ylabel('Total Amount')
                ax.set_title('Total Amount Growth Over Salary')
                ax.legend()
                st.pyplot(fig)

                # Plot the Growth Rate
                fig2, ax2 = plt.subplots(figsize=(10, 6))
                ax2.plot(df[salary_column], df['Growth Rate'], label="Growth Rate", marker='x', color='r')
                ax2.set_xlabel('Salary')
                ax2.set_ylabel('Growth Rate (%)')
                ax2.set_title('Growth Rate Based on Salary')
                ax2.legend()
                st.pyplot(fig2)

                # Create the PDF Report
                report_data = {
                    "Overview": "This report provides insights into the financial performance, including growth rates and total amount trends.",
                    "Growth Insights": f"The total amount growth rates for the different salary levels are detailed in the table above.",
                    "Growth Visualization": "The following visualizations show the total amount trends and growth rates over different salary levels."
                }
                pdf_report = generate_pdf_report(report_data)

                # Provide a download link for the PDF report
                st.markdown("### Download PDF Report:")
                st.download_button(
                    label="Download PDF Report",
                    data=pdf_report,
                    file_name="financial_analysis_report.pdf",
                    mime="application/pdf"
                )
            else:
                st.error("Could not identify appropriate columns for 'Salary' and 'Total Amount'.")
        else:
            st.error("Could not extract data from the uploaded document.")

    except Exception as e:
        st.error(f"An error occurred: {e}")
