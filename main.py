import tkinter as tk
from tkinter import filedialog, messagebox
import pdfplumber
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from datetime import datetime

def read_pdf(file_path):
    """Extract text from a PDF file."""
    with pdfplumber.open(file_path) as pdf:
        text = ""
        for page in pdf.pages:
            text += page.extract_text()
    return text

def generate_pdf_report(data, growth, output_path):
    """Generate a PDF report with the financial analysis."""
    try:
        c = canvas.Canvas(output_path, pagesize=letter)
        c.setFont("Helvetica", 12)
        c.drawString(30, 750, f"Financial Analysis Report")
        c.drawString(30, 730, f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        c.drawString(30, 710, f"Revenue: ${data.get('Revenue', 'N/A')}")
        c.drawString(30, 690, f"Profit: ${data.get('Profit', 'N/A')}")
        c.drawString(30, 670, f"Growth: {growth:.2f}%")
        c.drawString(30, 650, f"Year of Report: {data.get('Year', 'N/A')}")
        c.save()
        messagebox.showinfo("Success", f"PDF Report generated at {output_path}")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred while generating the report: {e}")

def browse_pdf_file():
    """Open file dialog to select a PDF file."""
    file_path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
    if file_path:
        entry_pdf.delete(0, tk.END)
        entry_pdf.insert(0, file_path)
    else:
        messagebox.showwarning("File Not Selected", "No file was selected.")

def browse_output_file():
    """Open file dialog to select where to save the report."""
    file_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF Files", "*.pdf")])
    if file_path:
        entry_output.delete(0, tk.END)
        entry_output.insert(0, file_path)
    else:
        messagebox.showwarning("No output file", "Please choose where to save the output report.")

def generate_report():
    """Generate the financial analysis report."""
    input_pdf = entry_pdf.get()
    output_path = entry_output.get()

    if not input_pdf or not output_path:
        messagebox.showwarning("Input Missing", "Please select both the input PDF and the output location.")
        return

    # Read the PDF and perform basic text extraction (simplified for now)
    document_text = read_pdf(input_pdf)

    # Extract some basic data (example, make sure your extraction is working properly)
    data = {'Revenue': 1000000, 'Profit': 200000, 'Year': 2024}
    growth = 10.0  # Just a placeholder for growth rate calculation

    # Generate the report (PDF)
    generate_pdf_report(data, growth, output_path)

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

# Generate report button
button_generate = tk.Button(window, text="Generate Report", command=generate_report)
button_generate.pack(pady=20)

window.mainloop()

