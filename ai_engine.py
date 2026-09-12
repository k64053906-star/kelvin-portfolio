
import re


def get_ai_analysis(message):
    """
    Local transaction-purpose analysis.

    This function does not require an OpenAI API key.
    It provides a fallback explanation for the application.
    """

    text = message.lower()

    purpose = "General transaction"
    explanation = "The transaction purpose could not be clearly identified."
    indicators = "None"

    # Identify the likely transaction purpose
    if any(word in text for word in [
        "salary",
        "wages",
        "payroll",
        "monthly pay"
    ]):
        purpose = "Salary"
        explanation = (
            "The transaction contains terms associated "
            "with salary or employment income."
        )

    elif any(word in text for word in [
        "rent",
        "house rent",
        "apartment"
    ]):
        purpose = "Rent"
        explanation = (
            "The transaction contains terms associated "
            "with housing or rental payments."
        )

    elif any(word in text for word in [
        "school",
        "college",
        "university",
        "tuition",
        "education",
        "fees"
    ]):
        purpose = "Education"
        explanation = (
            "The transaction contains terms associated "
            "with education or school-related payments."
        )

    elif any(word in text for word in [
        "hospital",
        "doctor",
        "medical",
        "clinic",
        "medicine",
        "pharmacy"
    ]):
        purpose = "Medical"
        explanation = (
            "The transaction contains terms associated "
            "with medical services or healthcare expenses."
        )

    elif any(word in text for word in [
        "consulting",
        "consultancy",
        "consultant"
    ]):
        purpose = "Consulting"
        explanation = (
            "The transaction contains terms associated "
            "with consulting services."
        )

    elif any(word in text for word in [
        "supplier",
        "client",
        "business",
        "business payment"
    ]):
        purpose = "Business"
        explanation = (
            "The transaction contains terms associated "
            "with business activity or commercial payments."
        )

    elif any(word in text for word in [
        "groceries",
        "shopping",
        "purchase",
        "bought",
        "goods",
        "services",
        "restaurant",
        "food"
    ]):
        purpose = "Goods / Services"
        explanation = (
            "The transaction contains terms associated "
            "with purchasing goods or services."
        )

    # Identify additional unusual characteristics
    unusual_terms = []

    if any(word in text for word in [
        "unknown",
        "anonymous",
        "suspicious",
        "urgent",
        "fraud",
        "stolen",
        "money laundering"
    ]):
        unusual_terms.append(
            "The transaction contains terms that may require review."
        )

    if unusual_terms:
        indicators = "; ".join(unusual_terms)

    return {
        "purpose": purpose,
        "ai_explanation": explanation,
        "ai_indicators": indicators
    }