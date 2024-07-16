import os
import requests
import json
import time
from flask import Flask, request, jsonify
import google.generativeai as genai
from flask_cors import CORS, cross_origin

app = Flask(__name__)

cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

Glif_API_KEY = os.environ.get('Glif_API_KEY')
Google_AI_Studio_API_KEY = os.environ.get('Google_AI_Studio_API_KEY')
Senha_API = os.environ.get('Senha_API')

genai.configure(api_key=Google_AI_Studio_API_KEY)
generation_config = {"candidate_count": 1, "temperature": 0.5}
safety_settings = {"HARASSMENT": "BLOCK_NONE", "HATE": "BLOCK_NONE", "SEXUAL": "BLOCK_NONE", "DANGEROUS": "BLOCK_NONE"}
model = genai.GenerativeModel(model_name="gemini-1.0-pro", generation_config=generation_config, safety_settings=safety_settings)



def ias_integradas(ideia):
    try:
        # Geração de sinopse
        sinopse = model.generate_content("Desenvolva a seguinte ideia como um cenário de RPG de mesa (sem inventar nomes) escreva esse cenário como uma sinopse de dois parágrafos e só, no final dê apenas algumas dicas para o mestre: " + ideia).text

        # Tentativas de solicitação à API externa com recuo exponencial
        max_attempts = 5
        for attempt in range(max_attempts):
            try:
                response = requests.post(
                    "https://simple-api.glif.app",
                    json={"id": "clpn2mwdr000yd8clc9chw75s", "inputs": [ideia]},
                    headers={"Authorization": "Bearer " + Glif_API_KEY},
                    timeout=20  # Aumentando o timeout para 20 segundos
                )

                # Verificação do status da resposta
                if response.status_code == 200:
                    break
                else:
                    print(f"Tentativa {attempt + 1} falhou: {response.status_code}, {response.text}")
            except requests.exceptions.Timeout:
                print(f"Tentativa {attempt + 1} falhou: Tempo de solicitação excedido.")
            
            # Recuo exponencial
            time.sleep(2 ** attempt)
        else:
            return jsonify({'erro': 'Tempo de solicitação à API externa excedido'}), 504

        # Processamento da resposta
        imagem = json.loads(response.text)['output']
        resposta = {'sinopse': sinopse, 'imagem': imagem}
        return jsonify(resposta)
    except Exception as e:
        print(f"Erro no processamento da ideia: {str(e)}")
        return jsonify({'erro': 'Erro no processamento da ideia'}), 500


@app.route('/', methods=["POST"])
def api():
    try:
        ideia = request.json['ideia']
        senha = request.json['senha']
        if senha == Senha_API:
            return ias_integradas(ideia)
        else:
            return jsonify({'erro': 'Senha incorreta'}), 403
    except Exception as e:
        print(f"Erro na solicitação recebida: {str(e)}")
        return jsonify({'erro': 'Erro na solicitação recebida'}), 400

if __name__ == '__main__':
    app.run(debug=True, port=8001)
