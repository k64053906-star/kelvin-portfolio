from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import re
from datetime import datetime

app = Flask(__name__)

DATABASE = "transactions.db"


def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def ensure_database():
    conn = get_db()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            message TEXT,
            amount REAL,
            currency TEXT,
            transaction_type TEXT,
            purpose TEXT,
            location TEXT,
            transaction_time TEXT,
            account_age TEXT,
            previous_transactions TEXT,
            risk_level TEXT,
            risk_score INTEGER,
            risk_explanation TEXT,
            unusual_indicators TEXT,
            recommendation TEXT,
            created_at TEXT
        )
    """)

    existing = [row["name"] for row in conn.execute("PRAGMA table_info(transactions)").fetchall()]

    columns = {
        "currency": "TEXT",
        "transaction_type": "TEXT",
        "purpose": "TEXT",
        "location": "TEXT",
        "transaction_time": "TEXT",
        "account_age": "TEXT",
        "previous_transactions": "TEXT",
        "risk_level": "TEXT",
        "risk_score": "INTEGER",
        "risk_explanation": "TEXT",
        "unusual_indicators": "TEXT",
        "recommendation": "TEXT",
        "created_at": "TEXT"
    }

    for column, datatype in columns.items():
        if column not in existing:
            conn.execute(f"ALTER TABLE transactions ADD COLUMN {column} {datatype}")

    conn.commit()
    conn.close()


def extract_value(message, labels):
    for label in labels:
        pattern = rf"{label}\s*:\s*([^\n\r]+)"
        match = re.search(pattern, message, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    return "Not specified"


def analyze_transaction(message):

    amount = 0.0

    amount_match = re.search(
        r"(?:amount|value)\s*:\s*(?:KES|KSh|USD|\$)?\s*([\d,]+(?:\.\d+)?)",
        message,
        re.IGNORECASE
    )

    if amount_match:
        amount = float(amount_match.group(1).replace(",", ""))
    else:
        money_match = re.search(
            r"(?:KES|KSh|USD|\$)\s*([\d,]+(?:\.\d+)?)",
            message,
            re.IGNORECASE
        )
        if money_match:
            amount = float(money_match.group(1).replace(",", ""))

    currency = extract_value(message, ["Currency"])

    if currency == "Not specified":
        if re.search(r"\bKES\b|\bKSh\b", message, re.IGNORECASE):
            currency = "KES"
        elif re.search(r"\bUSD\b|\$", message, re.IGNORECASE):
            currency = "USD"

    transaction_type = extract_value(
        message,
        ["Type", "Transaction type", "Transaction Type"]
    )

    purpose = extract_value(message, ["Purpose"])

    location = extract_value(message, ["Location"])

    transaction_time = extract_value(
        message,
        ["Time", "Transaction time", "Transaction Time"]
    )

    account_age = extract_value(
        message,
        ["Account age", "Account Age"]
    )

    previous_transactions = extract_value(
        message,
        ["Previous transactions", "Previous Transactions"]
    )

    score = 0
    indicators = []

    # Large transaction
    if amount >= 100000:
        score += 2
        indicators.append("Large transaction amount")
    elif amount >= 50000:
        score += 1
        indicators.append("Moderately large transaction amount")

    # Late-night transaction
    late_night = False

    time_match = re.search(
        r"(\d{1,2})(?::(\d{2}))?\s*(AM|PM)",
        transaction_time,
        re.IGNORECASE
    )

    if time_match:
        hour = int(time_match.group(1))
        minute = int(time_match.group(2) or 0)
        period = time_match.group(3).upper()

        if period == "PM" and hour != 12:
            hour += 12
        elif period == "AM" and hour == 12:
            hour = 0

        if hour >= 23 or hour < 5:
            late_night = True

    if late_night or "late night" in transaction_time.lower():
        score += 2
        indicators.append("Late-night transaction")

    # New account
    age_match = re.search(r"(\d+)\s*(month|months|year|years)", account_age, re.IGNORECASE)

    if age_match:
        age_number = int(age_match.group(1))
        age_unit = age_match.group(2).lower()

        if "month" in age_unit and age_number <= 3:
            score += 2
            indicators.append("New account")
        elif "year" in age_unit and age_number < 1:
            score += 2
            indicators.append("New account")

    # Limited transaction history
    previous_match = re.search(r"\d+", previous_transactions)

    if previous_match:
        previous_count = int(previous_match.group())

        if previous_count <= 5:
            score += 2
            indicators.append("Limited transaction history")

    # Outgoing transfers get a small baseline risk
    if transaction_type != "Not specified":
        if any(word in transaction_type.lower() for word in ["transfer", "withdrawal", "online"]):
            score += 1

    # Cap score
    score = min(score, 10)

    if score >= 7:
        risk_level = "High"
    elif score >= 4:
        risk_level = "Medium"
    else:
        risk_level = "Low"

    if indicators:
        risk_explanation = "Risk assessment is based on: " + "; ".join(indicators) + "."
        unusual_indicators = "; ".join(indicators)
    else:
        risk_explanation = "No major unusual patterns were detected from the available information."
        unusual_indicators = "None detected"

    if risk_level == "High":
        recommendation = "Review the transaction carefully and verify the account activity before approving or completing the transaction."
    elif risk_level == "Medium":
        recommendation = "Consider reviewing the transaction and checking whether the activity is consistent with the account history."
    else:
        recommendation = "Transaction appears relatively normal based on the information provided."

    return {
        "amount": amount,
        "currency": currency,
        "transaction_type": transaction_type,
        "purpose": purpose,
        "location": location,
        "transaction_time": transaction_time,
        "account_age": account_age,
        "previous_transactions": previous_transactions,
        "risk_level": risk_level,
        "risk_score": score,
        "risk_explanation": risk_explanation,
        "unusual_indicators": unusual_indicators,
        "recommendation": recommendation
    }


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/analyze", methods=["POST"])
def analyze():

    message = request.form.get("message", "").strip()

    if not message:
        return render_template(
            "index.html",
            error="Please enter transaction information."
        )

    result = analyze_transaction(message)

    conn = get_db()

    conn.execute("""
        INSERT INTO transactions (
            message,
            amount,
            currency,
            transaction_type,
            purpose,
            location,
            transaction_time,
            account_age,
            previous_transactions,
            risk_level,
            risk_score,
            risk_explanation,
            unusual_indicators,
            recommendation,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        message,
        result["amount"],
        result["currency"],
        result["transaction_type"],
        result["purpose"],
        result["location"],
        result["transaction_time"],
        result["account_age"],
        result["previous_transactions"],
        result["risk_level"],
        result["risk_score"],
        result["risk_explanation"],
        result["unusual_indicators"],
        result["recommendation"],
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))

    conn.commit()
    conn.close()

    return render_template(
        "index.html",
        message=message,
        result=result
    )


@app.route("/dashboard")
def dashboard():

    conn = get_db()

    transactions = conn.execute("""
        SELECT *
        FROM transactions
        ORDER BY id DESC
    """).fetchall()

    total = len(transactions)

    incoming = sum(
        1 for t in transactions
        if t["transaction_type"]
        and "incoming" in t["transaction_type"].lower()
    )

    outgoing = sum(
        1 for t in transactions
        if t["transaction_type"]
        and "outgoing" in t["transaction_type"].lower()
    )

    withdrawals = sum(
        1 for t in transactions
        if t["transaction_type"]
        and "withdraw" in t["transaction_type"].lower()
    )

    high_risk = sum(
        1 for t in transactions
        if t["risk_level"] == "High"
    )

    medium_risk = sum(
        1 for t in transactions
        if t["risk_level"] == "Medium"
    )

    low_risk = sum(
        1 for t in transactions
        if t["risk_level"] == "Low"
    )

    conn.close()

    return render_template(
        "dashboard.html",
        transactions=transactions,
        total=total,
        incoming=incoming,
        outgoing=outgoing,
        withdrawals=withdrawals,
        high_risk=high_risk,
        medium_risk=medium_risk,
        low_risk=low_risk
    )


@app.route("/history")
def history():

    conn = get_db()

    transactions = conn.execute("""
        SELECT *
        FROM transactions
        ORDER BY id DESC
    """).fetchall()

    conn.close()

    return render_template(
        "history.html",
        transactions=transactions
    )


ensure_database()

if __name__ == "__main__":
    ensure_database()
    app.run(debug=True)

