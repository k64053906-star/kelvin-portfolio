from flask import Flask, render_template, request, jsonify
import re
from datetime import datetime

app = Flask(__name__)

FAQS = {
    "refund": {
        "keywords": ["refund", "money back", "return money", "reimbursement"],
        "answer": "Refund requests are normally reviewed within 2 business days. Please provide your order number and reason for the refund.",
        "category": "Refund"
    },
    "delivery": {
        "keywords": ["delivery", "shipping", "arrive", "shipment", "deliver"],
        "answer": "Standard delivery normally takes 3–5 business days. Please provide your order number if you want help checking a delivery.",
        "category": "Delivery"
    },
    "payment": {
        "keywords": ["payment", "pay", "card", "charged", "transaction"],
        "answer": "We accept common card and digital payment methods. If you were charged incorrectly, provide your order number so the payment can be reviewed.",
        "category": "Payment"
    },
    "account": {
        "keywords": ["account", "password", "login", "sign in", "username"],
        "answer": "For account access problems, check your login details first. If you still cannot sign in, use the password-reset option or contact support.",
        "category": "Account"
    },
    "product": {
        "keywords": ["product", "item", "available", "stock", "price"],
        "answer": "I can help with product availability, pricing, and general product questions. Please provide the product name.",
        "category": "Product"
    }
}

def detect_intent(message):
    text = message.lower()
    best_category = "General"
    best_score = 0
    best_answer = "Thanks for contacting support. Please provide more details about your question so we can help."

    for item in FAQS.values():
        score = sum(1 for keyword in item["keywords"] if keyword in text)
        if score > best_score:
            best_score = score
            best_category = item["category"]
            best_answer = item["answer"]

    return best_category, best_score, best_answer

def sentiment(message):
    text = message.lower()
    negative = ["angry", "bad", "terrible", "wrong", "problem", "complaint", "unhappy", "failed"]
    positive = ["thanks", "thank you", "great", "good", "excellent", "helpful"]

    if any(word in text for word in negative):
        return "Needs attention"
    if any(word in text for word in positive):
        return "Positive"
    return "Neutral"

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/support", methods=["POST"])
def support():
    message = request.form.get("message", "").strip()

    if not message:
        return render_template(
            "index.html",
            message="",
            answer="Please enter a customer question.",
            category="General",
            confidence="Low",
            sentiment="Neutral"
        )

    category, score, answer = detect_intent(message)
    customer_sentiment = sentiment(message)

    confidence = "High" if score >= 2 else "Medium" if score == 1 else "Low"

    return render_template(
        "index.html",
        message=message,
        answer=answer,
        category=category,
        confidence=confidence,
        sentiment=customer_sentiment
    )

@app.route("/health")
def health():
    return jsonify({
        "status": "ok",
        "application": "AI Customer Support Assistant",
        "time": datetime.utcnow().isoformat()
    })

if __name__ == "__main__":
    app.run(debug=True)
