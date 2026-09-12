from flask import Flask, request, render_template
import sqlite3
import re
from ai_engine import get_ai_analysis

app = Flask(__name__)

DATABASE = "transactions.db"


def init_db():
    conn = sqlite3.connect(DATABASE)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            message TEXT NOT NULL,
            transaction_type TEXT,
            amount TEXT,
            currency TEXT,
            purpose TEXT,
            location TEXT,
            transaction_time TEXT,
            account_age TEXT,
            previous_transactions TEXT,
            risk_score INTEGER,
            risk_level TEXT,
            risk_explanation TEXT,
            unusual_indicators TEXT,
            recommendation TEXT,
            ai_explanation TEXT,
            ai_indicators TEXT
        )
    """)

    conn.commit()
    conn.close()


def analyze_transaction(message):
    text = message.lower()

    amount = "Not detected"
    currency = "Not detected"
    location = "Not detected"
    transaction_time = "Not detected"
    account_age = "Not detected"
    previous_transactions = "Not detected"

    indicators = []
    risk_score = 0

    currency_patterns = {
        "KES": [
            r"(?:kes|ksh|kshs)\s*([\d,]+(?:\.\d+)?)",
            r"([\d,]+(?:\.\d+)?)\s*(?:kes|ksh|kshs)"
        ],
        "USD": [
            r"(?:usd|\$)\s*([\d,]+(?:\.\d+)?)",
            r"([\d,]+(?:\.\d+)?)\s*(?:usd|dollars?)"
        ],
        "EUR": [
            r"(?:eur|€)\s*([\d,]+(?:\.\d+)?)",
            r"([\d,]+(?:\.\d+)?)\s*(?:eur|euros?)"
        ],
        "GBP": [
            r"(?:gbp|£)\s*([\d,]+(?:\.\d+)?)",
            r"([\d,]+(?:\.\d+)?)\s*(?:gbp|pounds?)"
        ]
    }

    for code, patterns in currency_patterns.items():
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                currency = code
                amount = match.group(1).replace(",", "")
                break

        if currency != "Not detected":
            break

    if any(word in text for word in [
        "received",
        "payment received",
        "deposit",
        "credited",
        "incoming",
        "money received"
    ]):
        transaction_type = "Incoming Payment"

    elif any(word in text for word in [
        "sent",
        "paid",
        "payment to",
        "transferred",
        "transfer",
        "outgoing",
        "send money"
    ]):
        transaction_type = "Outgoing Payment"

    elif any(word in text for word in [
        "withdraw",
        "withdrawal",
        "cash out",
        "atm"
    ]):
        transaction_type = "Cash Withdrawal"

    elif any(word in text for word in [
        "purchase",
        "purchased",
        "bought",
        "shopping",
        "merchant"
    ]):
        transaction_type = "Purchase"

    elif any(word in text for word in [
        "refund",
        "refunded",
        "reversal"
    ]):
        transaction_type = "Refund / Reversal"

    else:
        transaction_type = "Other / Unknown"

    if any(word in text for word in [
        "salary",
        "wages",
        "payroll",
        "monthly salary"
    ]):
        purpose = "Salary or employment income"

    elif any(word in text for word in [
        "consulting",
        "consultancy",
        "professional services"
    ]):
        purpose = "Professional or consulting services"

    elif any(word in text for word in [
        "rent",
        "lease",
        "house payment"
    ]):
        purpose = "Rent or property payment"

    elif any(word in text for word in [
        "invoice",
        "business payment",
        "supplier",
        "business"
    ]):
        purpose = "Business transaction"

    elif any(word in text for word in [
        "purchase",
        "shopping",
        "goods",
        "merchant"
    ]):
        purpose = "Purchase of goods or services"

    elif any(word in text for word in [
        "school",
        "tuition",
        "education",
        "college",
        "university"
    ]):
        purpose = "Education-related payment"

    elif any(word in text for word in [
        "medical",
        "hospital",
        "clinic",
        "medicine"
    ]):
        purpose = "Medical or healthcare payment"

    else:
        purpose = "Purpose not clearly identified"

    location_match = re.search(
        r"location\s*[:\-]?\s*([a-zA-Z][a-zA-Z\s]+?)(?:\s+time|\s+account|\s+previous|$)",
        message,
        re.IGNORECASE
    )

    if location_match:
        location = location_match.group(1).strip()

    time_match = re.search(
        r"(?:time\s*[:\-]?\s*)?(\d{1,2}:\d{2}\s*(?:am|pm))",
        text,
        re.IGNORECASE
    )

    if time_match:
        transaction_time = time_match.group(1).upper()

        hour_match = re.match(
            r"(\d{1,2}):(\d{2})\s*(AM|PM)",
            transaction_time
        )

        if hour_match:
            hour = int(hour_match.group(1))
            period = hour_match.group(3)

            if period == "PM" and hour != 12:
                hour += 12

            if period == "AM" and hour == 12:
                hour = 0

            if 0 <= hour < 5:
                indicators.append("Late-night transaction")
                risk_score += 2

    account_match = re.search(
        r"account\s+age\s*[:\-]?\s*(\d+)\s*(day|days|month|months|year|years)",
        text
    )

    if account_match:
        age = int(account_match.group(1))
        unit = account_match.group(2)

        account_age = f"{age} {unit}"

        if "day" in unit:
            age_months = age / 30
        elif "month" in unit:
            age_months = age
        else:
            age_months = age * 12

        if age_months < 3:
            indicators.append("New account")
            risk_score += 2

    previous_match = re.search(
        r"previous\s+transactions\s*[:\-]?\s*(\d+)",
        text
    )

    if previous_match:
        previous_transactions = previous_match.group(1)
        previous_count = int(previous_match.group(1))

        if previous_count < 5:
            indicators.append("Limited transaction history")
            risk_score += 1

    high_risk_words = [
        "anonymous",
        "unknown sender",
        "gambling",
        "cryptocurrency",
        "crypto",
        "offshore",
        "suspicious",
        "money laundering",
        "fraud",
        "stolen"
    ]

    for word in high_risk_words:
        if word in text:
            indicators.append(word.title())
            risk_score += 3

    medium_risk_words = [
        "third party",
        "unusual",
        "large transfer",
        "multiple transfers",
        "urgent",
        "new beneficiary",
        "unknown beneficiary"
    ]

    for word in medium_risk_words:
        if word in text:
            indicators.append(word.title())
            risk_score += 2

    if amount != "Not detected":
        try:
            numeric_amount = float(amount)

            if currency == "KES" and numeric_amount >= 100000:
                indicators.append("Large transaction amount")
                risk_score += 2

            elif currency in ["USD", "EUR", "GBP"] and numeric_amount >= 1000:
                indicators.append("Large transaction amount")
                risk_score += 2

        except ValueError:
            pass

    if transaction_type == "Cash Withdrawal":
        if amount != "Not detected":
            try:
                if float(amount) >= 50000 and currency == "KES":
                    indicators.append("Large cash withdrawal")
                    risk_score += 2
            except ValueError:
                pass

    indicators = list(dict.fromkeys(indicators))

    if risk_score >= 7:
        risk_level = "High"
        risk_explanation = (
            "Several risk indicators were detected. "
            "The transaction should receive detailed review "
            "and additional verification before approval."
        )

    elif risk_score >= 3:
        risk_level = "Medium"
        risk_explanation = (
            "Some unusual transaction characteristics were detected. "
            "Additional verification and monitoring may be appropriate."
        )

    else:
        risk_level = "Low"
        risk_explanation = (
            "No significant risk indicators were detected "
            "from the information provided."
        )

    if indicators:
        unusual_indicators = ", ".join(indicators)
    else:
        unusual_indicators = "None detected"

    if risk_level == "High":
        recommendation = (
            "Review the transaction, verify the source of funds, "
            "confirm the parties involved, and perform additional "
            "verification before approval."
        )

    elif risk_level == "Medium":
        recommendation = (
            "Perform additional verification, confirm the "
            "transaction details, and monitor for further unusual activity."
        )

    else:
        recommendation = "Record and monitor the transaction normally."

    return {
        "transaction_type": transaction_type,
        "amount": amount,
        "currency": currency,
        "purpose": purpose,
        "location": location,
        "transaction_time": transaction_time,
        "account_age": account_age,
        "previous_transactions": previous_transactions,
        "risk_score": risk_score,
        "risk_level": risk_level,
        "risk_explanation": risk_explanation,
        "unusual_indicators": unusual_indicators,
        "recommendation": recommendation
    }


def save_transaction(message, result):
    conn = sqlite3.connect(DATABASE)

    conn.execute("""
        INSERT INTO transactions (
            message,
            transaction_type,
            amount,
            currency,
            purpose,
            location,
            transaction_time,
            account_age,
            previous_transactions,
            risk_score,
            risk_level,
            risk_explanation,
            unusual_indicators,
            recommendation,
            ai_explanation,
            ai_indicators
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        message,
        result["transaction_type"],
        result["amount"],
        result["currency"],
        result["purpose"],
        result["location"],
        result["transaction_time"],
        result["account_age"],
        result["previous_transactions"],
        result["risk_score"],
        result["risk_level"],
        result["risk_explanation"],
        result["unusual_indicators"],
        result["recommendation"],
        result.get("ai_explanation", ""),
        result.get("ai_indicators", "")
    ))

    conn.commit()
    conn.close()


@app.route("/")
def home():
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

    ai_result = get_ai_analysis(message)

    if result["purpose"] == "Purpose not clearly identified":
        result["purpose"] = ai_result["purpose"]

    result["ai_explanation"] = ai_result["ai_explanation"]
    result["ai_indicators"] = ai_result["ai_indicators"]

    if ai_result["ai_indicators"] != "None":
        if result["unusual_indicators"] == "None detected":
            result["unusual_indicators"] = ai_result["ai_indicators"]
        else:
            result["unusual_indicators"] += ", " + ai_result["ai_indicators"]

    save_transaction(message, result)

    return render_template(
        "index.html",
        message=message,
        result=result
    )


@app.route("/history")
def history():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row

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


@app.route("/dashboard")
def dashboard():
    conn = sqlite3.connect(DATABASE)

    total_transactions = conn.execute(
        "SELECT COUNT(*) FROM transactions"
    ).fetchone()[0]

    incoming = conn.execute(
        "SELECT COUNT(*) FROM transactions "
        "WHERE transaction_type = 'Incoming Payment'"
    ).fetchone()[0]

    outgoing = conn.execute(
        "SELECT COUNT(*) FROM transactions "
        "WHERE transaction_type = 'Outgoing Payment'"
    ).fetchone()[0]

    purchases = conn.execute(
        "SELECT COUNT(*) FROM transactions "
        "WHERE transaction_type = 'Purchase'"
    ).fetchone()[0]

    withdrawals = conn.execute(
        "SELECT COUNT(*) FROM transactions "
        "WHERE transaction_type = 'Cash Withdrawal'"
    ).fetchone()[0]

    low_risk = conn.execute(
        "SELECT COUNT(*) FROM transactions "
        "WHERE risk_level = 'Low'"
    ).fetchone()[0]

    medium_risk = conn.execute(
        "SELECT COUNT(*) FROM transactions "
        "WHERE risk_level = 'Medium'"
    ).fetchone()[0]

    high_risk = conn.execute(
        "SELECT COUNT(*) FROM transactions "
        "WHERE risk_level = 'High'"
    ).fetchone()[0]

    conn.close()

    return render_template(
        "dashboard.html",
        total_transactions=total_transactions,
        incoming=incoming,
        outgoing=outgoing,
        purchases=purchases,
        withdrawals=withdrawals,
        low_risk=low_risk,
        medium_risk=medium_risk,
        high_risk=high_risk
    )


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
