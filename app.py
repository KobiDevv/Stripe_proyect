from flask import Flask, request, jsonify, render_template
import stripe
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# 🔐 Clave secreta Stripe desde ENV en Render
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")


# ============================================
#   RUTA PRINCIPAL
# ============================================
@app.route("/")
def index():
    return render_template(
        "checkout.html",
        publishable_key=os.getenv("STRIPE_PUBLISHABLE_KEY")
    )


# ============================================
#   CREAR PAYMENT INTENT (corregido 2025)
# ============================================
@app.route("/create-payment-intent", methods=["POST"])
def create_payment_intent():
    try:
        data = request.get_json()

        amount_raw = str(data.get("amount", "0")).strip()

        # Validar número real
        if not amount_raw.replace(".", "", 1).isdigit():
            return jsonify({"error": "Monto inválido"}), 400

        amount_float = float(amount_raw)

        # ⚡ Monto mínimo permitido por tu sistema
        if amount_float < 1:
            return jsonify({"error": "El monto mínimo es $1 MXN"}), 400

        amount = int(amount_float * 100)  # convertir a centavos

        intent = stripe.PaymentIntent.create(
            amount=amount,
            currency="mxn",
            automatic_payment_methods={"enabled": True}
        )

        return jsonify({"clientSecret": intent.client_secret})

    except Exception as e:
        return jsonify({"error": str(e)}), 400


# ============================================
#   PÁGINA DE ÉXITO (opcional)
# ============================================
@app.route("/success")
def success():
    return "<h1>✔ Pago realizado con éxito</h1>"


if __name__ == "__main__":
    app.run(port=5000, debug=True)
