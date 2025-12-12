from flask import Flask, request, jsonify, render_template
import stripe
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# 🔐 Claves Stripe obtenidas desde Environment Variables de Render
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")


# ======================
#     RUTA PRINCIPAL
# ======================
@app.route("/")
def index():
    return render_template(
        "checkout.html",
        publishable_key=os.getenv("STRIPE_PUBLISHABLE_KEY")
    )


# ==========================
#   CREAR PAYMENT INTENT
# ==========================
@app.route("/create-payment-intent", methods=["POST"])
def create_payment_intent():
    try:
        data = request.get_json()

        # Monto recibido desde el frontend
        amount = int(float(data["amount"]) * 100)  # Convierte MXN → centavos

        description = data.get("description", "Pago desde la web")

        intent = stripe.PaymentIntent.create(
            amount=amount,
            currency="mxn",
            description=description,
            automatic_payment_methods={"enabled": True}
        )

        return jsonify({"clientSecret": intent.client_secret})

    except Exception as e:
        return jsonify({"error": str(e)}), 400


# ==========================
#    SUCCESS PAGE OPCIONAL
# ==========================
@app.route("/success")
def success():
    return "<h1>PAGO COMPLETADO ✔</h1>"


if __name__ == "__main__":
    app.run(port=5000, debug=True)
