# main.py

import pdfplumber
import numpy as np
import pandas as pd
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import argparse

def read_pdf(file_path):
    """Extract text from a PDF file."""
    with pdfplumber.open(file_path) as pdf:
        text = ""
        for page in pdf.pages:
            text += page.extract_text()
    return text

def extract_financial_data(text):
    """Extract financial figures from the document."""
    data = {}
    lines = text.split('\n')
    
    for line in lines:
        if 'Revenue' in line:
            data['Revenue'] = float(line.split(':')[1].strip().replace(',', '').replace('$', ''))
        elif 'Profit' in line:
            data['Profit'] = float(line.split(':')[1].strip().replace(',', '').replace('$', ''))
        elif 'Year' in line:
            data['Year'] = int(line.split(':')[1].strip())
    
    return data

def calculate_growth(data):
    """Calculate growth between years."""
    growth = 0
    if 'Year' in data and len(data) > 1:
        year_difference = data['Year'] - min(data['Year'])
        if year_difference > 0:
            growth = ((data['Revenue'] - data['Revenue']) / data['Revenue']) * 100
    return growth

def generate_pdf_report(data, growth, output_path):
    """Generate a PDF report with the financial analysis."""
    c = canvas.Canvas(output_path, pagesize=letter)
    c.setFont("Helvetica", 12)

    c.drawString(30, 750, f"Financial Analysis Report")
    c.drawString(30, 730, f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    c.drawString(30, 710, f"Revenue: ${data.get('Revenue', 'N/A')}")
    c.drawString(30, 690, f"Profit: ${data.get('Profit', 'N/A')}")
    c.drawString(30, 670, f"Growth: {growth:.2f}%")
    
    c.drawString(30, 650, f"Year of Report: {data.get('Year', 'N/A')}")
    
    c.save()

def generate_text_report(data, growth, output_path):
    """Generate a plain text report."""
    with open(output_path, 'w') as f:
        f.write(f"Financial Analysis Report\n")
        f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        f.write(f"Revenue: ${data.get('Revenue', 'N/A')}\n")
        f.write(f"Profit: ${data.get('Profit', 'N/A')}\n")
        f.write(f"Growth: {growth:.2f}%\n")
        
        f.write(f"Year of Report: {data.get('Year', 'N/A')}\n")

def main():
    # Set up argument parser for customization
    parser = argparse.ArgumentParser(description="Financial Analysis Tool")
    parser.add_argument("input_pdf", help="Path to the input PDF file for analysis")
    parser.add_argument("output", help="Path for the output report (PDF or text file)")
    parser.add_argument("--report_format", choices=["pdf", "text"], default="pdf", 
                        help="Specify the output format: 'pdf' or 'text' (default: 'pdf')")
    
    args = parser.parse_args()
    
    # Step 1: Read the document
    document_text = read_pdf(args.input_pdf)
    
    # Step 2: Extract financial data
    financial_data = extract_financial_data(document_text)
    
    # Step 3: Calculate financial metrics (e.g., growth rate)
    growth_rate = calculate_growth(financial_data)
    
    # Step 4: Generate report based on user choice (PDF or text)
    if args.report_format == "pdf":
        generate_pdf_report(financial_data, growth_rate, args.output)
        print(f"PDF Report generated successfully at {args.output}")
    else:
        generate_text_report(financial_data, growth_rate, args.output)
        print(f"Text Report generated successfully at {args.output}")

if __name__ == "__main__":
    main()

