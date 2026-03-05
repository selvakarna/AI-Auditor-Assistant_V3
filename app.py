import streamlit as st
import pdfplumber
import pandas as pd
import re

st.title("AI Auditor Assistant")

salary_file = st.file_uploader("Upload Salary Slip", type=["pdf"])
bank_file = st.file_uploader("Upload Bank Statement", type=["pdf"])
form16_file = st.file_uploader("Upload Form-16", type=["pdf"])
invoice_files = st.file_uploader("Upload Invoices", type=["pdf"], accept_multiple_files=True)


def extract_pdf_text(file):
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            t = page.extract_text()
            if t:
                text += t
    return text


def extract_salary_data(text):

    data = {}

    pan = re.search(r"PAN\s*[:\-]?\s*([A-Z0-9]+)", text)
    gross = re.search(r"GROSS EARNINGS\s*(\d+)", text)
    net = re.search(r"NET PAY\s*(\d+)", text)
    tax = re.search(r"INCOME TAX\s*(\d+)", text)

    data["PAN"] = pan.group(1) if pan else ""
    data["Gross Salary"] = int(gross.group(1)) if gross else 0
    data["Net Salary"] = int(net.group(1)) if net else 0
    data["Income Tax"] = int(tax.group(1)) if tax else 0

    return data


if st.button("Generate Tax Summary"):

    salary_data = {}
    bank_income = 0
    invoice_total = 0

    if salary_file:
        text = extract_pdf_text(salary_file)
        salary_data = extract_salary_data(text)

    if bank_file:
        text = extract_pdf_text(bank_file)
        interest = re.findall(r"INTEREST\s*(\d+)", text)
        bank_income = sum([int(i) for i in interest]) if interest else 0

    if invoice_files:
        for file in invoice_files:
            text = extract_pdf_text(file)
            amounts = re.findall(r"TOTAL\s*(\d+)", text)
            invoice_total += sum([int(a) for a in amounts]) if amounts else 0

    summary = {
        "Category": [
            "Salary Income",
            "Bank Interest",
            "Business Expenses",
            "Tax Deducted"
        ],
        "Amount": [
            salary_data.get("Gross Salary",0),
            bank_income,
            invoice_total,
            salary_data.get("Income Tax",0)
        ]
    }

    df = pd.DataFrame(summary)

    st.subheader("Tax Summary")
    st.table(df)

    st.download_button(
        "Download CSV",
        df.to_csv(index=False),
        file_name="tax_summary.csv"
    )
