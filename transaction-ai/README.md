# AI Transaction Intelligence

A web-based financial transaction analysis application that evaluates transaction information, identifies unusual activity, calculates risk scores, and provides explainable recommendations.

## Live Demo

[Open AI Transaction Intelligence](https://kelvin-portfolio-4epd.onrender.com)

## Project Overview

AI Transaction Intelligence is a Flask-powered web application designed to demonstrate how transaction data can be analyzed using rule-based risk assessment.

The application allows users to enter transaction details and receive an assessment based on factors such as transaction amount, transaction type, account age, transaction time, location, and previous transaction history.

## Key Features

- Transaction amount detection
- Transaction type classification
- Transaction purpose identification
- Local rule-based risk scoring
- Unusual transaction activity detection
- Explainable risk indicators
- Transaction history
- Dashboard with transaction summaries
- SQLite database integration
- Responsive web interface
- Online deployment with Render

## Risk Analysis

The application evaluates transaction information using a local analysis engine.

Risk indicators may include:

- Large transaction amounts
- Late-night transactions
- Recently created accounts
- Limited transaction history
- Other unusual transaction patterns

The system generates a risk score and a recommendation to help users review potentially unusual transactions.

**Note:** This is a portfolio demonstration and not a banking security system. Risk scores are indicators for review and do not prove that a transaction is fraudulent.

## Technologies Used

- Python
- Flask
- HTML5
- CSS3
- SQLite
- Git and GitHub
- Gunicorn
- Render

## Application Pages

### Analyzer

Enter transaction information and receive a risk assessment, risk score, explanation, and recommendation.

### Dashboard

View transaction summaries and an overview of analyzed transactions.

### History

Review previously analyzed transactions.

## Skills Demonstrated

- Python development
- Flask web application development
- Frontend development
- Database integration
- Rule-based data analysis
- Risk assessment logic
- Problem solving
- Git version control
- Web application deployment

## Run the Project Locally

### 1. Clone the repository

`ash
git clone https://github.com/k64053906-star/kelvin-portfolio.git
`

### 2. Open the project folder

`ash
cd kelvin-portfolio/transaction-ai
`

### 3. Install dependencies

`ash
pip install -r requirements.txt
`

### 4. Start the application

`ash
python app.py
`

### 5. Open the application

Visit:

http://127.0.0.1:5000

## Deployment

The application is deployed using Render.

The project uses Gunicorn as its production web server.

## Project Structure

`	ext
transaction-ai/
├── app.py
├── ai_engine.py
├── requirements.txt
├── templates/
├── static/
└── README.md
`

## Future Improvements

- CSV transaction file upload
- Transaction trend visualizations
- Advanced anomaly detection
- Improved transaction categorization
- User authentication
- More detailed financial reports

## Developer

Kelvin

GitHub: https://github.com/k64053906-star

## License

This project is intended for portfolio and educational demonstration purposes.
