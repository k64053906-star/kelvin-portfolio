# AI Transaction Intelligence

A local financial transaction analysis system built with Python and Flask.

The application analyzes transaction information, detects unusual activity, calculates risk scores, and provides explainable recommendations.

## Live Demo

https://kelvin-portfolio-4epd.onrender.com

## Project Overview

AI Transaction Intelligence is a portfolio project demonstrating how a web application can process transaction information and identify potentially unusual financial activity using a local rule-based risk-analysis engine.

The system does not require a paid AI API or an API key.

## Features

- Transaction amount and currency detection
- Transaction type classification
- Transaction purpose identification
- Location and transaction-time extraction
- Account age and transaction-history analysis
- Risk scoring from 0 to 10
- Low, Medium, and High risk classifications
- Unusual activity detection
- Explainable risk indicators
- Actionable transaction recommendations
- Transaction storage using SQLite
- Dashboard with transaction statistics
- Transaction history page
- Flask web interface
- Responsive website layout

## Technologies Used

- Python
- Flask
- SQLite
- HTML5
- CSS3
- Regular expressions
- Git and GitHub
- Render deployment

## Risk Analysis

The local risk engine evaluates available transaction information, including:

- Transaction amount
- Transaction time
- Account age
- Previous transaction count
- Transaction type

The system produces a risk score, a risk classification, detected indicators, and a recommendation.

### Example

Input:

Amount: 150000 KES  
Type: Online transfer  
Location: Nairobi  
Time: 2:30 AM  
Account age: 2 months  
Previous transactions: 3  
Purpose: Payment for consulting services

Example result:

- Risk level: High Risk
- Risk score: 9/10
- Detected indicators: Large transaction amount, late-night transaction, new account, and limited transaction history

## Project Structure

transaction-ai/

├── app.py  
├── ai_engine.py  
├── requirements.txt  
├── render.yaml  
├── .gitignore  
├── transactions.db  
├── templates/  
│   ├── index.html  
│   ├── dashboard.html  
│   └── history.html  
└── static/  
    └── style.css

## Running Locally

Clone the repository:

git clone https://github.com/k64053906-star/kelvin-portfolio.git

Open the project directory:

cd kelvin-portfolio/transaction-ai

Install dependencies:

pip install -r requirements.txt

Run the application:

python app.py

Open the local application:

http://127.0.0.1:5000

## Deployment

The application is configured for deployment on Render using Gunicorn.

Build command:

pip install -r requirements.txt

Start command:

gunicorn app:app

## Portfolio Purpose

This project demonstrates practical skills in:

- Python development
- Flask web development
- Database integration
- Risk-analysis logic
- Data processing
- Explainable system design
- Git version control
- Cloud deployment

## Disclaimer

This is a portfolio demonstration project. Its risk scores are based on simplified rules and should not be treated as professional financial, banking, or fraud-detection advice.

## Author

Kelvin

GitHub: https://github.com/k64053906-star/kelvin-portfolio

---

## Freelance Project Showcase

### Project Overview

AI Transaction Intelligence is a web-based transaction analysis system designed to help users understand financial transaction information and identify potentially unusual activity.

The application demonstrates how Python, Flask, SQLite, and rule-based artificial intelligence can be combined to create a practical business-focused web application.

### Business Problems Addressed

This project demonstrates solutions for:

- Reviewing transaction information
- Identifying incoming and outgoing transactions
- Detecting unusually large transactions
- Identifying late-night transactions
- Highlighting activity from new accounts
- Detecting limited transaction history
- Assigning transaction risk scores
- Presenting transaction information through dashboards
- Maintaining a searchable transaction history

### Skills Demonstrated

- Python development
- Flask web application development
- HTML and CSS interface development
- SQLite database management
- Rule-based AI and decision systems
- Data extraction from text
- Risk scoring logic
- Dashboard development
- Backend and frontend integration
- Git and GitHub
- Cloud deployment

### Potential Freelance Applications

The techniques used in this project can be adapted for:

- Business transaction monitoring systems
- Expense tracking applications
- Financial reporting dashboards
- Customer activity analysis
- Invoice and payment analysis
- Business intelligence tools
- Internal company management systems
- Custom data-processing applications

### Project Status

The application is deployed online and can be accessed through the live demo:

**Live Demo:** https://kelvin-portfolio-4epd.onrender.com

This project is intended as a portfolio demonstration and is not a certified banking, investment, or fraud-detection system.

### Developer

**Kelvin**

GitHub: https://github.com/k64053906-star/kelvin-portfolio

