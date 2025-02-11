from flask import Flask, request, jsonify
import openai

app = Flask(__name__)

# Chave da API OpenAI configurada no backend
openai.api_key = "sua-chave-api-aqui"

@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.json
    user_input = data.get("message")
    if not user_input:
        return jsonify({"error": "Nenhuma mensagem fornecida"}), 400

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": user_input}],
            temperature=0.5
        )
        return jsonify({"response": response.choices[0].message["content"]})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
