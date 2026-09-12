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

    # -----------------------------
    # Amount and currency
    # -----------------------------

    amount = None
    currency = "Unknown"

    currency_patterns = [
        (r"(?:ksh|kes|ksh\.?)\s*([\d,]+(?:\.\d+)?)", "KES"),
        (r"([\d,]+(?:\.\d+)?)\s*(?:ksh|kes)", "KES"),
        (r"\$\s*([\d,]+(?:\.\d+)?)", "USD"),
        (r"([\d,]+(?:\.\d+)?)\s*usd", "USD"),
        (r"€\s*([\d,]+(?:\.\d+)?)", "EUR"),
        (r"([\d,]+(?:\.\d+)?)\s*eur", "EUR"),
        (r"£\s*([\d,]+(?:\.\d+)?)", "GBP"),
        (r"([\d,]+(?:\.\d+)?)\s*gbp", "GBP"),
    ]

    for pattern, curr in currency_patterns:
        match = re.search(pattern, text)

        if match:
            try:
                amount = float(match.group(1).replace(",", ""))
                currency = curr
            except ValueError:
                pass

            break

    # General number fallback
    if amount is None:
        numbers = re.findall(r"\b\d[\d,]*(?:\.\d+)?\b", text)

        if numbers:
            try:
                amount = float(numbers[0].replace(",", ""))
            except ValueError:
                amount = None

    # -----------------------------
    # Transaction type
    # -----------------------------

    transaction_type = "Other"

    if any(word in text for word in [
        "received",
        "deposit",
        "incoming",
        "credited",
        "salary",
        "payment received"
    ]):
        transaction_type = "Incoming"

    elif any(word in text for word in [
        "withdraw",
        "withdrawal",
        "cash out",
        "atm"
    ]):
        transaction_type = "Cash Withdrawal"

    elif any(word in text for word in [
        "refund",
        "refunded",
        "reversal"
    ]):
        transaction_type = "Refund"

    elif any(word in text for word in [
        "spent",
        "paid",
        "purchase",
        "bought",
        "payment"
    ]):
        transaction_type = "Outgoing"

    # -----------------------------
    # Purpose
    # -----------------------------

    purpose = "General transaction"

    purpose_keywords = {
        "Salary": [
            "salary",
            "wages",
            "payroll",
            "monthly pay"
        ],

        "Consulting": [
            "consulting",
            "consultancy",
            "consultant"
        ],

        "Rent": [
            "rent",
            "house rent",
            "apartment"
        ],

        "Business": [
            "business",
            "business payment",
            "supplier",
            "client"
        ],

        "Goods / Services": [
            "groceries",
            "shopping",
            "purchase",
            "bought",
            "goods",
            "services",
            "restaurant",
            "food"
        ],

        "Education": [
            "school",
            "college",
            "university",
            "tuition",
            "fees",
            "education"
        ],

        "Medical": [
            "hospital",
            "doctor",
            "medical",
            "clinic",
            "medicine",
            "pharmacy"
        ]
    }

    for category, keywords in purpose_keywords.items():

        if any(keyword in text for keyword in keywords):
            purpose = category
            break

    # -----------------------------
    # Location
    # -----------------------------

    location = "Not specified"

    locations = [
        "nairobi",
        "mombasa",
        "kisumu",
        "nakuru",
        "eldoret",
        "embu",
        "kenya",
        "uganda",
        "tanzania",
        "usa",
        "united states",
        "london",
        "uk"
    ]

    for place in locations:

        if place in text:
            location = place.title()
            break

    # -----------------------------
    # Transaction time
    # -----------------------------

    transaction_time = "Not specified"

    if any(word in text for word in [
        "midnight",
        "late night",
        "2am",
        "3am",
        "4am",
        "1am"
    ]):
        transaction_time = "Late night"

    elif any(word in text for word in [
        "morning",
        "8am",
        "9am",
        "10am",
        "11am"
    ]):
        transaction_time = "Morning"

    elif any(word in text for word in [
        "afternoon",
        "12pm",
        "1pm",
        "2pm",
        "3pm",
        "4pm"
    ]):
        transaction_time = "Afternoon"

    elif any(word in text for word in [
        "evening",
        "5pm",
        "6pm",
        "7pm",
        "8pm",
        "9pm"
    ]):
        transaction_time = "Evening"

    # -----------------------------
    # Account age
    # -----------------------------

    account_age = "Not specified"

    account_match = re.search(
        r"account\s+(?:is\s+)?(\d+)\s*(day|days|month|months|year|years)\s*old",
        text
    )

    if account_match:
        account_age = (
            account_match.group(1)
            + " "
            + account_match.group(2)
        )

    # -----------------------------
    # Previous transactions
    # -----------------------------

    previous_transactions = "Not specified"

    previous_match = re.search(
        r"(\d+)\s+(?:previous|past|prior)\s+transactions",
        text
    )

    if previous_match:
        previous_transactions = previous_match.group(1)

    # -----------------------------
    # Risk analysis
    # -----------------------------

    risk_score = 0
    indicators = []

    # Late-night activity
    if transaction_time == "Late night":
        risk_score += 2
        indicators.append("Late-night transaction")

    # New account
    if account_age != "Not specified":

        age_match = re.search(r"(\d+)", account_age)

        if age_match:

            age_value = int(age_match.group(1))

            if "day" in account_age and age_value <= 30:
                risk_score += 3
                indicators.append("Very new account")

            elif "month" in account_age and age_value <= 3:
                risk_score += 2
                indicators.append("Recently created account")

    # Limited history
    if previous_transactions != "Not specified":

        try:
            previous_count = int(previous_transactions)

            if previous_count <= 2:
                risk_score += 2
                indicators.append("Limited transaction history")

        except ValueError:
            pass

    # High-risk words
    high_risk_words = [
        "anonymous",
        "unknown sender",
        "gambling",
        "crypto",
        "offshore",
        "suspicious",
        "money laundering",
        "fraud",
        "stolen"
    ]

    found_high_risk = []

    for word in high_risk_words:

        if word in text:
            found_high_risk.append(word)

    if found_high_risk:

        risk_score += 4

        indicators.append(
            "High-risk terms: " + ", ".join(found_high_risk)
        )

    # Medium-risk words
    medium_risk_words = [
        "third party",
        "unusual",
        "large transfer",
        "multiple transfers",
        "urgent",
        "new beneficiary",
        "unknown beneficiary"
    ]

    found_medium_risk = []

    for word in medium_risk_words:

        if word in text:
            found_medium_risk.append(word)

    if found_medium_risk:

        risk_score += 2

        indicators.append(
            "Unusual transaction terms: "
            + ", ".join(found_medium_risk)
        )

    # Large transaction
    if amount is not None:

        if currency == "KES" and amount >= 100000:
            risk_score += 3
            indicators.append("Large transaction amount")

        elif currency == "USD" and amount >= 5000:
            risk_score += 3
            indicators.append("Large transaction amount")

        elif currency == "EUR" and amount >= 5000:
            risk_score += 3
            indicators.append("Large transaction amount")

        elif currency == "GBP" and amount >= 5000:
            risk_score += 3
            indicators.append("Large transaction amount")

    # Large cash withdrawal
    if transaction_type == "Cash Withdrawal":

        if amount is not None:

            if currency == "KES" and amount >= 50000:
                risk_score += 3
                indicators.append("Large cash withdrawal")

            elif currency in ["USD", "EUR", "GBP"] and amount >= 2000:
                risk_score += 3
                indicators.append("Large cash withdrawal")

    # -----------------------------
    # Risk level
    # -----------------------------

    if risk_score >= 7:
        risk_level = "High"

    elif risk_score >= 3:
        risk_level = "Medium"

    else:
        risk_level = "Low"

    # -----------------------------
    # Risk explanation
    # -----------------------------

    if indicators:

        risk_explanation = (
            "Risk assessment is based on: "
            + "; ".join(indicators)
            + "."
        )

    else:

        risk_explanation = (
            "No major unusual indicators were detected "
            "by the local transaction analysis engine."
        )

    # -----------------------------
    # Recommendation
    # -----------------------------

    if risk_level == "High":

        recommendation = (
            "Review the transaction carefully and verify "
            "the sender, recipient, amount and transaction context."
        )

    elif risk_level == "Medium":

        recommendation = (
            "Consider reviewing the transaction and checking "
            "whether the activity is consistent with the account history."
        )

    else:

        recommendation = (
            "No immediate unusual activity was detected. "
            "Continue normal monitoring."
        )

    # -----------------------------
    # Return result
    # -----------------------------

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
        "unusual_indicators": "; ".join(indicators) if indicators else "None",
        "recommendation": recommendation
    }


# --------------------------------------------------
# SAVE TRANSACTION
# --------------------------------------------------

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
        result.get("ai_indicators")
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
        stats=stats
    )


# --------------------------------------------------
# START APPLICATION
# --------------------------------------------------

if __name__ == "__main__":

    init_db()

    app.run(
        debug=True
    )