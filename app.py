from flask import Flask, request, jsonify, render_template
import stripe
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Stripe keys (Render las tomará desde Environment Variables)
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")


# ------------------------------
#   ROUTA PRINCIPAL - CHECKOUT
# ------------------------------
@app.route("/")
def index():
    return render_template("checkout.html",
                           publishable_key=os.getenv("STRIPE_PUBLISHABLE_KEY")
                           )


# ------------------------------
#   CREAR PAYMENT INTENT
# ------------------------------
@app.route("/create-payment-intent", methods=["POST"])
def create_payment():
    data = request.get_json()
    amount = int(float(data["amount"]) * 100)

    intent = stripe.PaymentIntent.create(
        amount=amount,
        currency="mxn",
        automatic_payment_methods={"enabled": True},
    )

    return jsonify({"clientSecret": intent["client_secret"]})


# ------------------------------
#       WEBHOOK DE STRIPE
# ------------------------------
@app.route("/webhook", methods=["POST"])
def stripe_webhook():
    payload = request.data
    sig_header = request.headers.get("Stripe-Signature")

    try:
        event = stripe.Webhook.construct_event(
            payload,
            sig_header,
            os.getenv("STRIPE_WEBHOOK_SECRET")
        )
    except Exception as e:
        return str(e), 400

    event_type = event["type"]

    if event_type == "payment_intent.succeeded":
        intent = event["data"]["object"]

        amount = intent.get("amount_received", intent.get("amount"))

        customer_email = None
        customer_name = None

        if "charges" in intent and intent["charges"]["data"]:
            charge = intent["charges"]["data"][0]
            billing = charge.get("billing_details", {})
            customer_email = billing.get("email")
            customer_name = billing.get("name")

        print("✔ Pago aprobado:", intent["id"])
        print("Monto:", amount / 100)
        print("Cliente email:", customer_email)
        print("Cliente nombre:", customer_name)

    return "OK", 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
