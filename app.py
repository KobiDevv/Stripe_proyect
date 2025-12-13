from flask import Flask, request, jsonify, render_template
import stripe
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Clave secreta Stripe
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")


@app.route("/")
def index():
    return render_template(
        "checkout.html",
        publishable_key=os.getenv("STRIPE_PUBLISHABLE_KEY")
    )


@app.route("/create-payment-intent", methods=["POST"])
def create_payment():
    try:
        data = request.get_json()

        amount_str = data.get("amount", "").strip()

        # Validación del monto recibido
        if not amount_str.isdigit():
            return jsonify({"error": "Monto inválido"}), 400

        amount = int(amount_str)

        if amount < 10:
            return jsonify({"error": "El monto mínimo es $10 MXN"}), 400

        amount_centavos = amount * 100

        intent = stripe.PaymentIntent.create(
            amount=amount_centavos,
            currency="mxn",
            description="Pago desde la web",
            automatic_payment_methods={"enabled": True}
        )

        return jsonify({"clientSecret": intent.client_secret})

    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route("/success")
def success():
    return "<h1 style='color:green;text-align:center;'>✔ PAGO COMPLETADO</h1>"


if __name__ == "__main__":
    app.run(port=5000, debug=True)
