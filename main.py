import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO, StringIO
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

# Helper Function to Generate PDF Report
def generate_pdf_report(report_data, output_file):
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
    
    pdf.output(output_file)

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
            if df is None:
                st.error("No table found in the PDF.")
                st.stop()
        else:
            st.error("Unsupported file type.")
            st.stop()

        st.subheader("Data Preview")
        st.dataframe(df.head())

        # Select columns for analysis
        date_column = st.selectbox("Select the date column", df.columns)

        # Clean the date column
        df[date_column] = pd.to_datetime(df[date_column], errors='coerce')
        df = df.dropna(subset=[date_column])  # Drop rows where date parsing failed
        df = df.sort_values(by=date_column)

        # Identify numeric columns, ignoring those with non-numeric values
        numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()
        
        # Check if any numeric columns are available for selection
        if not numeric_columns:
            st.warning("No valid numeric columns available for analysis.")
        else:
            selected_columns = st.multiselect("Select numeric columns for analysis", numeric_columns)

            if selected_columns:
                # Initialize Report Content
                report_content = {"Overview": f"Date Range: {df[date_column].min().date()} to {df[date_column].max().date()}"}

                st.subheader("Growth Analysis")
                for column in selected_columns:
                    # Calculate Growth Rates
                    df[f"{column}_growth"] = df[column].pct_change() * 100

                    # Insights
                    avg_growth = df[f"{column}_growth"].mean()
                    recent_growth = df[f"{column}_growth"].iloc[-1]
                    total_growth = ((df[column].iloc[-1] - df[column].iloc[0]) / df[column].iloc[0]) * 100

                    # Display Insights in App
                    st.write(f"**{column.capitalize()} Analysis:**")
                    st.write(f"- Total Growth: {total_growth:.2f}%")
                    st.write(f"- Average Growth: {avg_growth:.2f}%")
                    st.write(f"- Most Recent Growth: {recent_growth:.2f}%")

                    # Add Insights to Report
                    report_content[f"{column.capitalize()} Analysis"] = (
                        f"- Total Growth: {total_growth:.2f}%\n"
                        f"- Average Growth: {avg_growth:.2f}%\n"
                        f"- Most Recent Growth: {recent_growth:.2f}%\n"
                    )

                    # Plot Growth
                    st.line_chart(df[[date_column, f"{column}_growth"]].set_index(date_column))

                # Summary Section
                summary = ""
                for column in selected_columns:
                    past = df[column].iloc[0]
                    recent = df[column].iloc[-1]
                    total_growth = ((recent - past) / past) * 100
                    summary += (
                        f"- {column.capitalize()} grew from {past:.2f} to {recent:.2f}, "
                        f"a total growth of {total_growth:.2f}% over the period.\n"
                    )
                report_content["Summary"] = summary

                # Generate and Download PDF Report
                st.subheader("Download Report")
                pdf_buffer = BytesIO()
                generate_pdf_report(report_content, pdf_buffer)
                pdf_buffer.seek(0)

                st.download_button(
                    label="Download PDF Report",
                    data=pdf_buffer,
                    file_name="financial_analysis_report.pdf",
                    mime="application/pdf"
                )

    except Exception as e:
        st.error(f"An error occurred: {e}")
