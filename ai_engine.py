import re


def get_ai_analysis(message):
    """
    Local transaction-analysis engine.

    No OpenAI API, API key, internet connection,
    or paid service required.
    """

    if not isinstance(message, str):
        message = str(message)

    text = message.lower().strip()
    indicators = []

    purpose = "General transaction"
    explanation = (
        "The transaction purpose could not be determined "
        "with high confidence."
    )

    # --------------------------------------------------
    # 1. Detect transaction purpose
    # --------------------------------------------------

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
            "beneficiary", "new recipient", "new beneficiary"
        ],
        "Cash Withdrawal": [
            "withdraw", "withdrawal", "cash out", "atm"
        ],
        "Refund": [
            "refund", "refunded", "reversal"
        ]
    }

    for category, keywords in purpose_keywords.items():
        if any(keyword in text for keyword in keywords):
            purpose = category
            break

    explanations = {
        "Salary": (
            "The message contains terms associated with "
            "salary or employment income."
        ),
        "Consulting": (
            "The message contains terms associated with "
            "consulting services."
        ),
        "Rent": (
            "The message contains terms associated with "
            "rent or housing expenses."
        ),
        "Business": (
            "The message contains terms associated with "
            "business activity, suppliers, clients, or invoices."
        ),
        "Goods / Services": (
            "The message contains terms associated with "
            "purchases, goods, food, or services."
        ),
        "Education": (
            "The message contains terms associated with "
            "education or tuition expenses."
        ),
        "Medical": (
            "The message contains terms associated with "
            "medical services or medicine."
        ),
        "Transfer": (
            "The message contains terms associated with "
            "transferring money to another party."
        ),
        "Cash Withdrawal": (
            "The message contains terms associated with "
            "withdrawing cash."
        ),
        "Refund": (
            "The message contains terms associated with "
            "a refund or transaction reversal."
        )
    }

    if purpose in explanations:
        explanation = explanations[purpose]

    # --------------------------------------------------
    # 2. Detect transaction amount
    # --------------------------------------------------

    amount_matches = re.findall(
        r"(?:ksh|kes|sh|usd|\$|€|eur|gbp|£)?\s*"
        r"\d[\d,]*(?:\.\d+)?\s*"
        r"(?:ksh|kes|sh|usd|dollars?|euros?|pounds?)?",
        text
    )

    amounts = []

    for amount_text in amount_matches:
        numbers = re.findall(r"\d[\d,]*(?:\.\d+)?", amount_text)

        if numbers:
            try:
                amount = float(numbers[0].replace(",", ""))
                amounts.append(amount)
            except ValueError:
                pass

    if amounts:
        largest_amount = max(amounts)

        if largest_amount >= 100000:
            indicators.append(
                "Large transaction amount detected: "
                f"{largest_amount:,.2f}"
            )

        elif largest_amount >= 50000:
            indicators.append(
                "Elevated transaction amount detected: "
                f"{largest_amount:,.2f}"
            )

    # --------------------------------------------------
    # 3. Detect late-night transactions
    # --------------------------------------------------

    time_matches = re.findall(
        r"\b(\d{1,2})(?::(\d{2}))?\s*(am|pm)\b",
        text
    )

    for hour_text, minute_text, period in time_matches:
        hour = int(hour_text)

        if period == "pm" and hour != 12:
            hour += 12

        if period == "am" and hour == 12:
            hour = 0

        if hour >= 0 and hour < 5:
            indicators.append(
                "Late-night transaction detected."
            )
            break

    # Also recognize 24-hour time, such as 02:30.
    time_24_matches = re.findall(
        r"\b([01]\d|2[0-3]):([0-5]\d)\b",
        text
    )

    for hour_text, minute_text in time_24_matches:
        hour = int(hour_text)

        if hour < 5:
            indicators.append(
                "Late-night transaction detected."
            )
            break

    # --------------------------------------------------
    # 4. Detect new or unknown recipients
    # --------------------------------------------------

    recipient_terms = [
        "new recipient",
        "new beneficiary",
        "unknown recipient",
        "unknown beneficiary",
        "unfamiliar recipient",
        "unrecognized recipient",
        "third party"
    ]

    found_recipient_terms = [
        term for term in recipient_terms if term in text
    ]

    if found_recipient_terms:
        indicators.append(
            "New or unfamiliar recipient detected: "
            + ", ".join(found_recipient_terms)
        )

    # --------------------------------------------------
    # 5. Detect account age
    # --------------------------------------------------

    account_age_match = re.search(
        r"account\s*(?:age)?\s*:?\s*(?:is\s+)?(\d+)\s*(day|days|week|weeks|month|months|year|years)",
        text
    )

    if account_age_match:
        age_value = int(account_age_match.group(1))
        age_unit = account_age_match.group(2)

        age_in_days = age_value

        if "week" in age_unit:
            age_in_days = age_value * 7
        elif "month" in age_unit:
            age_in_days = age_value * 30
        elif "year" in age_unit:
            age_in_days = age_value * 365

        if age_in_days <= 90:
            indicators.append(
                "Recently created account detected."
            )

    # --------------------------------------------------
    # 6. Detect previous transaction history
    # --------------------------------------------------

    previous_match = re.search(
        r"previous\s+transactions?\s*:?\s*(\d+)",
        text
    )

    if not previous_match:
        previous_match = re.search(
            r"(?:only\s+)?(\d+)\s+previous\s+transactions?",
            text
        )

    if previous_match:
        previous_count = int(previous_match.group(1))

        if previous_count < 10:
            indicators.append(
                "Limited previous transaction history detected."
            )

    # --------------------------------------------------
    # 7. Detect high-risk terms
    # --------------------------------------------------

    high_risk_words = [
        "anonymous",
        "unknown sender",
        "gambling",
        "offshore",
        "suspicious",
        "money laundering",
        "fraud",
        "stolen",
        "scam",
        "phishing",
        "unauthorized"
    ]

    medium_risk_words = [
        "unusual",
        "urgent",
        "multiple transfers",
        "rapid transfers",
        "unrecognized",
        "unfamiliar"
    ]

    found_high = [
        word for word in high_risk_words if word in text
    ]

    found_medium = [
        word for word in medium_risk_words if word in text
    ]

    if found_high:
        indicators.append(
            "High-risk terms: " + ", ".join(found_high)
        )

    if found_medium:
        indicators.append(
            "Unusual terms: " + ", ".join(found_medium)
        )

    # --------------------------------------------------
    # 8. Remove duplicate indicators
    # --------------------------------------------------

    unique_indicators = []

    for indicator in indicators:
        if indicator not in unique_indicators:
            unique_indicators.append(indicator)

    if unique_indicators:
        indicators_text = "; ".join(unique_indicators)
    else:
        indicators_text = "None"

    # --------------------------------------------------
    # 9. Return the same fields expected by the Flask app
    # --------------------------------------------------

    return {
        "purpose": purpose,
        "ai_explanation": explanation,
        "ai_indicators": indicators_text
    }

