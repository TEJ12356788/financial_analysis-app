# main.py with Tkinter GUI

import pdfplumber
import numpy as np
import pandas as pd
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import tkinter as tk
from tkinter import filedialog, messagebox

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

def browse_pdf_file():
    """Open file dialog to select a PDF file."""
    file_path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
    entry_pdf.delete(0, tk.END)
    entry_pdf.insert(0, file_path)

def browse_output_file():
    """Open file dialog to select where to save the report."""
    file_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF Files", "*.pdf"), ("Text Files", "*.txt")])
    entry_output.delete(0, tk.END)
    entry_output.insert(0, file_path)

def generate_report():
    """Run financial analysis and generate the report."""
    input_pdf = entry_pdf.get()
    output_path = entry_output.get()
    report_format = var_report_format.get()
    
    if not input_pdf or not output_path:
        messagebox.showerror("Error", "Please select both input PDF and output path.")
        return
    
    # Read the document
    document_text = read_pdf(input_pdf)
    
    # Extract financial data
    financial_data = extract_financial_data(document_text)
    
    # Calculate growth
    growth_rate = calculate_growth(financial_data)
    
    # Generate the report
    try:
        if report_format == "pdf":
            generate_pdf_report(financial_data, growth_rate, output_path)
            messagebox.showinfo("Success", f"PDF Report generated successfully at {output_path}")
        else:
            generate_text_report(financial_data, growth_rate, output_path)
            messagebox.showinfo("Success", f"Text Report generated successfully at {output_path}")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")

# Create the GUI window
window = tk.Tk()
window.title("Financial Analysis Tool")
window.geometry("500x300")

# PDF file selection
label_pdf = tk.Label(window, text="Select input PDF:")
label_pdf.pack(pady=5)
entry_pdf = tk.Entry(window, width=50)
entry_pdf.pack(pady=5)
button_browse_pdf = tk.Button(window, text="Browse", command=browse_pdf_file)
button_browse_pdf.pack(pady=5)

# Output file selection
label_output = tk.Label(window, text="Select output file:")
label_output.pack(pady=5)
entry_output = tk.Entry(window, width=50)
entry_output.pack(pady=5)
button_browse_output = tk.Button(window, text="Browse", command=browse_output_file)
button_browse_output.pack(pady=5)

# Report format selection
label_report_format = tk.Label(window, text="Select report format:")
label_report_format.pack(pady=5)
var_report_format = tk.StringVar(value="pdf")
radio_pdf = tk.Radiobutton(window, text="PDF", variable=var_report_format, value="pdf")
radio_pdf.pack(pady=5)
radio_text = tk.Radiobutton(window, text="Text", variable=var_report_format, value="text")
radio_text.pack(pady=5)

# Generate report button
button_generate = tk.Button(window, text="Generate Report", command=generate_report)
button_generate.pack(pady=20)

# Start the Tkinter event loop
window.mainloop()
