import re


def get_ai_analysis(message):
    """
    Local transaction-analysis engine.
    No OpenAI API, API key, internet connection, or paid service required.
    """

    text = message.lower().strip()

    purpose = "General transaction"
    explanation = "The transaction purpose could not be determined with high confidence."
    indicators = []

    purpose_keywords = {
        "Salary": [
            "salary", "wages", "payroll", "monthly pay"
        ],
        "Consulting": [
            "consulting", "consultancy", "consultant"
        ],
        "Rent": [
            "rent", "house rent", "apartment"
        ],
        "Business": [
            "business", "supplier", "client", "invoice"
        ],
        "Goods / Services": [
            "groceries", "shopping", "purchase", "bought",
            "goods", "services", "restaurant", "food"
        ],
        "Education": [
            "school", "college", "university",
            "tuition", "fees", "education"
        ],
        "Medical": [
            "hospital", "doctor", "medical",
            "clinic", "medicine", "pharmacy"
        ],
        "Transfer": [
            "transfer", "sent", "send", "recipient",
            "beneficiary"
        ],
        "Cash Withdrawal": [
            "withdraw", "withdrawal", "cash out", "atm"
        ],
        "Refund": [
            "refund", "refunded", "reversal"
        ]
    }

    for category, keywords in purpose_keywords.items():
        for keyword in keywords:
            if keyword in text:
                purpose = category
                break
        if purpose != "General transaction":
            break

    if purpose == "Salary":
        explanation = "The message contains terms associated with salary or employment income."

    elif purpose == "Consulting":
        explanation = "The message contains terms associated with consulting services."

    elif purpose == "Rent":
        explanation = "The message contains terms associated with rent or housing expenses."

    elif purpose == "Business":
        explanation = "The message contains terms associated with business activity, suppliers, clients, or invoices."

    elif purpose == "Goods / Services":
        explanation = "The message contains terms associated with purchases, goods, food, or services."

    elif purpose == "Education":
        explanation = "The message contains terms associated with education or tuition expenses."

    elif purpose == "Medical":
        explanation = "The message contains terms associated with medical services or medicine."

    elif purpose == "Transfer":
        explanation = "The message contains terms associated with transferring money to another party."

    elif purpose == "Cash Withdrawal":
        explanation = "The message contains terms associated with withdrawing cash."

    elif purpose == "Refund":
        explanation = "The message contains terms associated with a refund or transaction reversal."

    # Detect potentially unusual terms locally.
    high_risk_words = [
        "anonymous",
        "unknown sender",
        "gambling",
        "offshore",
        "suspicious",
        "money laundering",
        "fraud",
        "stolen"
    ]

    medium_risk_words = [
        "third party",
        "unusual",
        "urgent",
        "new beneficiary",
        "unknown beneficiary",
        "multiple transfers"
    ]

    found_high = [word for word in high_risk_words if word in text]
    found_medium = [word for word in medium_risk_words if word in text]

    if found_high:
        indicators.append(
            "High-risk terms: " + ", ".join(found_high)
        )

    if found_medium:
        indicators.append(
            "Unusual terms: " + ", ".join(found_medium)
        )

    if not indicators:
        indicators_text = "None"
    else:
        indicators_text = "; ".join(indicators)

    return {
        "purpose": purpose,
        "ai_explanation": explanation,
        "ai_indicators": indicators_text
    }
