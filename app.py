from flask import Flask, request, render_template
import sqlite3
import re
from ai_engine import get_ai_analysis

app = Flask(__name__)

DATABASE = "transactions.db"


# --------------------------------------------------
# DATABASE
# --------------------------------------------------

def init_db():
    conn = sqlite3.connect(DATABASE)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            message TEXT NOT NULL,
            transaction_type TEXT,
            amount REAL,
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


# --------------------------------------------------
# TRANSACTION ANALYSIS ENGINE
# --------------------------------------------------

def analyze_transaction(message):
    text = message.lower()

    amount_match = re.search(
        r"(?:ksh|kes|ksh\.|kes\.)?\s*([\d,]+(?:\.\d+)?)",
        text,
        re.IGNORECASE
    )

    amount = 0.0
    if amount_match:
        amount = float(amount_match.group(1).replace(",", ""))

    currency = "KES" if ("ksh" in text or "kes" in text) else "Unknown"

    if any(word in text for word in [
        "received", "receive", "deposit", "deposited",
        "income", "paid me", "payment received"
    ]):
        transaction_type = "Incoming"
    elif any(word in text for word in [
        "sent", "send", "transfer", "transferred",
        "paid", "payment to", "withdraw"
    ]):
        transaction_type = "Outgoing"
    else:
        transaction_type = "Other"

    if any(word in text for word in [
        "salary", "wage", "payroll"
    ]):
        purpose = "Salary"
    elif any(word in text for word in [
        "consulting", "business", "service", "client"
    ]):
        purpose = "Business"
    elif any(word in text for word in [
        "rent", "house", "landlord"
    ]):
        purpose = "Rent"
    elif any(word in text for word in [
        "school", "fee", "tuition"
    ]):
        purpose = "Education"
    elif any(word in text for word in [
        "food", "shopping", "groceries"
    ]):
        purpose = "Shopping"
    elif any(word in text for word in [
        "sent", "send", "transfer", "transferred",
        "paid", "recipient"
    ]):
        purpose = "Transfer"
    else:
        purpose = "General transaction"

    locations = [
        "Nairobi", "Mombasa", "Kisumu", "Nakuru",
        "Embu", "Siakago", "Kampala", "Kigali"
    ]

    location = "Not specified"
    for place in locations:
        if place.lower() in text:
            location = place
            break

    transaction_time = "Not specified"

    clock_match = re.search(
        r"\b(0?[1-9]|1[0-2])(?::[0-5]\d)?\s*(am|pm)\b",
        text,
        re.IGNORECASE
    )

    if clock_match:
        hour = int(clock_match.group(1))
        meridiem = clock_match.group(2).lower()

        if meridiem == "am" and hour >= 12:
            transaction_time = "Late night"
        elif meridiem == "am" and hour <= 5:
            transaction_time = "Late night"
        elif meridiem == "am":
            transaction_time = "Morning"
        elif meridiem == "pm" and hour < 5:
            transaction_time = "Afternoon"
        else:
            transaction_time = "Evening"
    elif any(word in text for word in [
        "midnight", "late night", "2am", "3am", "4am", "1am"
    ]):
        transaction_time = "Late night"
    elif "morning" in text:
        transaction_time = "Morning"
    elif "afternoon" in text:
        transaction_time = "Afternoon"
    elif "evening" in text or "night" in text:
        transaction_time = "Evening"

    account_age_match = re.search(
        r"account\s+(?:is\s+)?(\d+)\s*(day|days|week|weeks|month|months|year|years)\s*old",
        text
    )

    account_age = "Not specified"
    account_age_months = None

    if account_age_match:
        number = int(account_age_match.group(1))
        unit = account_age_match.group(2)

        if "day" in unit:
            account_age_months = number / 30
        elif "week" in unit:
            account_age_months = number / 4
        elif "year" in unit:
            account_age_months = number * 12
        else:
            account_age_months = number

        account_age = f"{number} {unit}"

    previous_match = re.search(
        r"(\d+)\s+(?:previous\s+)?transactions",
        text
    )

    previous_transactions = "Not specified"
    previous_count = None

    if previous_match:
        previous_count = int(previous_match.group(1))
        previous_transactions = str(previous_count)

    score = 0
    indicators = []

    if transaction_time == "Late night":
        score += 2
        indicators.append("Late-night transaction")

    if account_age_months is not None and account_age_months <= 3:
        score += 2
        indicators.append("Recently created account")

    if previous_count is not None and previous_count <= 5:
        score += 2
        indicators.append("Limited transaction history")

    if amount >= 100000:
        score += 3
        indicators.append("Large transaction amount")

    if any(word in text for word in [
        "new recipient", "unknown recipient",
        "unfamiliar recipient", "first time recipient"
    ]):
        score += 2
        indicators.append("New or unfamiliar recipient")

    if any(word in text for word in [
        "hacked", "fraud", "scam", "suspicious",
        "unauthorized", "unknown transfer"
    ]):
        score += 4
        indicators.append("Possible fraud-related wording")

    if score >= 7:
        risk_level = "High"
    elif score >= 3:
        risk_level = "Medium"
    else:
        risk_level = "Low"

    if indicators:
        risk_explanation = "Risk assessment is based on: " + "; ".join(indicators) + "."
        unusual_indicators = "; ".join(indicators)
    else:
        risk_explanation = "No major unusual indicators were detected."
        unusual_indicators = "None"

    if risk_level == "High":
        recommendation = "Review this transaction carefully and confirm that it was authorized."
    elif risk_level == "Medium":
        recommendation = "Consider reviewing the transaction and checking whether the activity is consistent with the account history."
    else:
        recommendation = "The transaction appears relatively normal, but continue monitoring account activity."

    return {
        "transaction_type": transaction_type,
        "amount": amount,
        "currency": currency,
        "purpose": purpose,
        "location": location,
        "transaction_time": transaction_time,
        "account_age": account_age,
        "previous_transactions": previous_transactions,
        "risk_score": score,
        "risk_level": risk_level,
        "risk_explanation": risk_explanation,
        "unusual_indicators": unusual_indicators,
        "recommendation": recommendation
    }


# --------------------------------------------------
# SAVE TRANSACTION
# --------------------------------------------------

def save_transaction(message, result):
    from datetime import datetime

    conn = sqlite3.connect(DATABASE)

    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

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
            ai_indicators,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        message,
        result.get("transaction_type"),
        result.get("amount"),
        result.get("currency"),
        result.get("purpose"),
        result.get("location"),
        result.get("transaction_time"),
        result.get("account_age"),
        result.get("previous_transactions"),
        result.get("risk_score"),
        result.get("risk_level"),
        result.get("risk_explanation"),
        result.get("unusual_indicators"),
        result.get("recommendation"),
        result.get("ai_explanation"),
        result.get("ai_indicators"),
        created_at
    ))

    conn.commit()
    conn.close()


# --------------------------------------------------
# HOME PAGE
# --------------------------------------------------

@app.route("/")
def home():

    return render_template("index.html")


# --------------------------------------------------
# ANALYZE TRANSACTION
# --------------------------------------------------

@app.route("/analyze", methods=["POST"])
def analyze():

    message = request.form.get("message", "").strip()

    if not message:

        return render_template(
            "index.html",
            error="Please enter a transaction."
        )

    # Local rule-based analysis
    result = analyze_transaction(message)

    # AI analysis
    ai_result = get_ai_analysis(message)

    # Use AI purpose when local engine cannot identify one
    if (
        result.get("purpose") == "General transaction"
        and ai_result.get("purpose")
    ):
        result["purpose"] = ai_result["purpose"]

    result["ai_explanation"] = ai_result.get(
        "ai_explanation",
        "AI analysis unavailable."
    )

    result["ai_indicators"] = ai_result.get(
        "ai_indicators",
        "None"
    )

    # Save to database
    save_transaction(message, result)

    return render_template(
        "index.html",
        message=message,
        result=result
    )


# --------------------------------------------------
# HISTORY
# --------------------------------------------------

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


# --------------------------------------------------
# DASHBOARD
# --------------------------------------------------

@app.route("/dashboard")
def dashboard():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row

    total = conn.execute("""
        SELECT COUNT(*) FROM transactions
    """).fetchone()[0]

    incoming = conn.execute("""
        SELECT COUNT(*)
        FROM transactions
        WHERE transaction_type = 'Incoming'
    """).fetchone()[0]

    outgoing = conn.execute("""
        SELECT COUNT(*)
        FROM transactions
        WHERE transaction_type = 'Outgoing'
    """).fetchone()[0]

    purchases = conn.execute("""
        SELECT COUNT(*)
        FROM transactions
        WHERE transaction_type = 'Outgoing'
        AND purpose = 'Goods / Services'
    """).fetchone()[0]

    withdrawals = conn.execute("""
        SELECT COUNT(*)
        FROM transactions
        WHERE transaction_type = 'Cash Withdrawal'
    """).fetchone()[0]

    low_risk = conn.execute("""
        SELECT COUNT(*)
        FROM transactions
        WHERE risk_level = 'Low'
    """).fetchone()[0]

    medium_risk = conn.execute("""
        SELECT COUNT(*)
        FROM transactions
        WHERE risk_level = 'Medium'
    """).fetchone()[0]

    high_risk = conn.execute("""
        SELECT COUNT(*)
        FROM transactions
        WHERE risk_level = 'High'
    """).fetchone()[0]

    recent_transactions = conn.execute("""
        SELECT
            id,
            created_at,
            transaction_type,
            amount,
            purpose,
            location,
            transaction_time,
            risk_score,
            risk_level,
            unusual_indicators
        FROM transactions
        ORDER BY id DESC
        LIMIT 10
    """).fetchall()

    conn.close()

    stats = {
        "total": total,
        "incoming": incoming,
        "outgoing": outgoing,
        "purchases": purchases,
        "withdrawals": withdrawals,
        "low_risk": low_risk,
        "medium_risk": medium_risk,
        "high_risk": high_risk
    }

    return render_template(
        "dashboard.html",
        stats=stats,
        recent_transactions=recent_transactions
    )


# --------------------------------------------------
# START APPLICATION
# --------------------------------------------------

if __name__ == "__main__":

    init_db()

    app.run(
        debug=True
    )