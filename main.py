import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from io import StringIO

# App Title
st.title("Financial Document Analysis with Growth Insights and Reporting")

# Upload Section
uploaded_file = st.file_uploader("Upload a financial document (CSV or Excel)", type=["csv", "xlsx"])

if uploaded_file:
    try:
        # Load Data
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        st.subheader("Data Preview")
        st.dataframe(df.head())

        # Select columns for analysis
        date_column = st.selectbox("Select the date column", df.columns)
        numeric_columns = st.multiselect("Select numeric columns for analysis", df.select_dtypes(include=np.number).columns)

        if date_column and numeric_columns:
            # Ensure the date column is a datetime type
            df[date_column] = pd.to_datetime(df[date_column])
            df = df.sort_values(by=date_column)

            # Initialize Report Content
            report_content = StringIO()
            report_content.write("## Financial Analysis Report\n\n")
            report_content.write(f"### Date Range: {df[date_column].min().date()} to {df[date_column].max().date()}\n\n")

            st.subheader("Growth Analysis")
            for column in numeric_columns:
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
                report_content.write(f"#### {column.capitalize()} Analysis\n")
                report_content.write(f"- Total Growth: {total_growth:.2f}%\n")
                report_content.write(f"- Average Growth: {avg_growth:.2f}%\n")
                report_content.write(f"- Most Recent Growth: {recent_growth:.2f}%\n\n")

                # Plot Growth
                st.line_chart(df[[date_column, f"{column}_growth"]].set_index(date_column))

            # Summary Section
            report_content.write("### Summary\n")
            for column in numeric_columns:
                past = df[column].iloc[0]
                recent = df[column].iloc[-1]
                report_content.write(f"- {column.capitalize()} grew from {past:.2f} to {recent:.2f}, a total growth of {((recent - past) / past) * 100:.2f}% over the period.\n")

            # Display Report Download Button
            st.subheader("Download Report")
            st.download_button(
                label="Download Report",
                data=report_content.getvalue(),
                file_name="financial_analysis_report.txt",
                mime="text/plain"
            )

    except Exception as e:
        st.error(f"An error occurred: {e}")
