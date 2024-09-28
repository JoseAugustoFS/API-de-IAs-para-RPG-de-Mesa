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
ID_Glif = os.environ.get('ID_Glif')

genai.configure(api_key=Google_AI_Studio_API_KEY)
generation_config = {"candidate_count": 1, "temperature": 0.5}
safety_settings = {"HARASSMENT": "BLOCK_NONE", "HATE": "BLOCK_NONE", "SEXUAL": "BLOCK_NONE", "DANGEROUS": "BLOCK_NONE"}
model = genai.GenerativeModel(model_name="gemini-1.0-pro", generation_config=generation_config, safety_settings=safety_settings)

prompt = """Bem-vindo à pesquisa sobre Criação de Histórias e Ferramentas de Suporte para Mestres de RPG! Abaixo, insira suas respostas nos campos apropriados:

Sistemas de RPG que você já jogou ou conhece:
(Ex.: D&D, Tormenta, Call of Cthulhu, Vampiro, etc.)

Sistema de RPG que você mais joga atualmente:
(Ex.: D&D 5e, Pathfinder, outros.)

Quantas vezes você atua como mestre de RPG por mês?
(Opções: Menos de 1 vez, 1-2 vezes, 3-4 vezes, Mais de 4 vezes)

Quais são os maiores desafios ao criar uma aventura de RPG?
(Ex.: Criar enigmas, balancear desafios, desenvolver NPCs, etc.)

Qual estilo de aventura você prefere mestrar?
(Opções: Lineares, Abertas, Mistura de ambos)

Que tipo de ferramenta ou suporte você gostaria para facilitar suas aventuras?
(Ex.: Ferramentas para criação de NPCs, geração aleatória de itens e eventos, etc.)

Você gostaria de uma ferramenta de suporte para gerenciar combates (ex.: controlar PV de várias criaturas simultaneamente)?
(Opções: Sim, Não, Não sei)

Comentários, sugestões ou necessidades para o desenvolvimento deste projeto:
(Campo aberto para responder)

Bem-vindo à nossa pesquisa sobre Criação de Histórias e Ferramentas de Suporte para Mestres de RPG! Por favor, insira suas respostas nos campos abaixo para nos ajudar a entender melhor suas necessidades.

Primeiramente, nos conte sobre os sistemas de RPG que você já jogou ou conhece. Exemplos podem incluir D&D, Tormenta, Call of Cthulhu, Vampiro, entre outros. Em seguida, diga qual é o sistema de RPG que você mais joga atualmente, como D&D 5e, Pathfinder, ou outro de sua preferência.

Agora, gostaríamos de saber com que frequência você atua como mestre. Responda quantas vezes, em média, você mestre RPG por mês, escolhendo entre as opções: menos de 1 vez, 1-2 vezes, 3-4 vezes ou mais de 4 vezes.

Sobre a criação de aventuras, conte-nos quais são os principais desafios que você enfrenta. Por exemplo, pode ser difícil criar enigmas interessantes, balancear os desafios para os jogadores, desenvolver NPCs envolventes, entre outros.

Nosso próximo interesse é saber sobre o estilo de aventura que você prefere mestrar. Você costuma preferir aventuras mais lineares, onde os jogadores seguem um caminho claro, abertas, onde têm mais liberdade, ou uma mistura de ambos?

Pensando em ferramentas de suporte, quais seriam mais úteis para você? Seriam ferramentas para criação de NPCs, geração de itens e eventos aleatórios, ou talvez algo para balancear combates e inimigos?

Também gostaríamos de saber se você gostaria de uma ferramenta de suporte para gerenciar combates, como uma que permita controlar os pontos de vida de várias criaturas ao mesmo tempo. Sim, não, ou talvez, se você ainda não tem certeza.

Por fim, compartilhe conosco qualquer comentário, sugestão ou necessidade adicional que você gostaria de ver atendida para melhorar a criação e gestão das suas aventuras de RPG.


A partir da pesquisa acima, gere um texto contando uma historia inicial, dando dicas para o mestre do RPG com o tema: """

def ias_integradas(ideia):
    try:
        # Geração de sinopse
        sinopse = model.generate_content(prompt + ideia).text

        # Tentativas de solicitação à API externa com recuo exponencial
        max_attempts = 5
        for attempt in range(max_attempts):
            try:
                print(f"Tentativa {attempt + 1} de solicitação à API Glif...")
                response = requests.post(
                    "https://simple-api.glif.app",
                    json={"id": ID_Glif, "inputs": [ideia]},
                    headers={"Authorization": "Bearer " + Glif_API_KEY},
                )

                # Verificação do status da resposta
                if response.status_code == 200:
                    print(f"Solicitação bem-sucedida na tentativa {attempt + 1}")
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
