import os
import requests
import json
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
generation_config = { "candidate_count": 1, "temperature": 0.5,}
safety_settings = {"HARASSMENT": "BLOCK_NONE","HATE": "BLOCK_NONE","SEXUAL": "BLOCK_NONE","DANGEROUS": "BLOCK_NONE",}
model = genai.GenerativeModel(model_name="gemini-1.0-pro",generation_config=generation_config,safety_settings=safety_settings)

def ias_integradas(ideia):
	sinopse = model.generate_content("Desenvolva a seguinte ideia como um cenário de RPG de mesa (sem inventar nomes) escreva esse cenário como uma sinopse de dois parágrafos e só, no final dê apenas algumas dicas para o mestre: "+ideia).text
	response = requests.post(
    		"https://simple-api.glif.app",
    		json={"id": "clpn2mwdr000yd8clc9chw75s", "inputs": [sinopse]},
    		headers={"Authorization": "Bearer "+Glif_API_KEY},
	)
	#imagens sao 16:9
	imagem = json.loads(response.text)['output']+""
	resposta = {'sinopse': sinopse,'imagem':imagem}
	return jsonify(resposta)
  

@app.route('/', methods=["POST"])
def api():
	ideia = request.json['ideia']
	senha = request.json['senha']
	if senha==Senha_API:
		return ias_integradas(ideia)
	else:
		return None

if __name__ == '__main__':
    app.run(debug=True, port=8001)
