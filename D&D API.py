import requests
import json
from flask import Flask, request, jsonify
#!pip install -q -U google-generativeai
import google.generativeai as genai

app = Flask(__name__)

Stable_Diffusion_API_KEY = 'wEJBYH63AOu6zDfWQMXoiYS7vHptnOqhRSDFY0yZDWncUIiDUecVqfV9qQUa'
Google_AI_Studio_API_KEY = 'AIzaSyC6zxB47mEhvS2SIik7DEiTtmfWmlW7c6Q'

genai.configure(api_key=Google_AI_Studio_API_KEY)
generation_config = { "candidate_count": 1, "temperature": 0.5,}
safety_settings = {"HARASSMENT": "BLOCK_NONE","HATE": "BLOCK_NONE","SEXUAL": "BLOCK_NONE","DANGEROUS": "BLOCK_NONE",}
model = genai.GenerativeModel(model_name="gemini-1.0-pro",generation_config=generation_config,safety_settings=safety_settings)

def ias_integradas(ideia):
	sinopse = model.generate_content("Desenvolva a seguinte ideia como um cenário de RPG de mesa (sem inventar nomes) escreva esse cenário como uma sinopse de dois parágrafos e só, no final dê apenas algumas dicas para o mestre: "+ideia).text
	url = "https://modelslab.com/api/v6/realtime/text2img"
	payload = json.dumps({
		"key" : Stable_Diffusion_API_KEY,
		"prompt": model.generate_content("Escreva um promt em inglês e apenas o promt de forma que esteja pronto para uso para uma IA de imagens (Stable Diffusion) ara gerar uma ilustração fantasiosa, RPG de mesa focando extamente no que está sendo pedido da ideia: "+ideia).text,
		"negative_prompt": None,
		"width": "512",
		"height": "512",
		"safety_checker": False,
		"seed": None,
		"samples":1,
		"base64":False,
		"webhook": None,
		"track_id": None
	})
	headers = {
	'Content-Type': 'application/json'
	}
	response = requests.request("POST", url, headers=headers, data=payload)
	response_dict = json.loads(response.text)
	imagem = response_dict['output']
	resposta = {'sinopse': sinopse,'imagem':imagem}
	return jsonify(resposta)
  

@app.route('/', methods=["POST"])
def api():
	ideia = request.json['ideia']
	senha = request.json['senha']
	if senha=="123":
		return ias_integradas(ideia)
	else:
		return None


app.run(host='0.0.0.0')