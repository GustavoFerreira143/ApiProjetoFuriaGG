import json
import re
import os
from werkzeug.utils import secure_filename

from flask import Flask, request, jsonify, make_response, g, send_from_directory
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_cors import CORS

from dotenv import load_dotenv
import google.generativeai as genai
import jwt
from functools import wraps

from ConsultasFuncionarios.LoginUser import autenticar_usuario
from ConsultasFuncionarios.InsereUser import inserir_funcionario_furia
from ConsultasFuncionarios.BuscaUser import obter_todos_usuarios
from ConsultasFuncionarios.EditaUser import atualizar_funcionario
from ConsultasFuncionarios.EnvioEmailPromocional import enviaEmailUsers
from ConsultasFuncionarios.EnviaNoticias import AdicionaNoticia
from ConsultasBanco.ColetaNoticias import recebe_noticias
from ConsultasFuncionarios.DeletaNoticia import deletaNoticia
from ConsultasFuncionarios.RetornaInfosPesquisa import retornaUsers
from ConsultasFuncionarios.mudaVizualizado import altera_visualizado
from ConsultasFuncionarios.DashboardFunctions import (
    obter_distribuicao_idades,
    obter_fans_receber_promocoes,
    obter_usuarios_por_estado,
    obter_interesse_em_comp,
    obter_interesse_em_catalogo,
    obter_fans_por_rede_social,
    obter_rank_jogos_mais_amados
)
from ConsultasFuncionarios.CriaGraficoPersonalizado import gerar_dados_personalizados_grafico

from ConsultasBanco.CadastraFa import cadastrar_ou_atualizar_usuario
from ConsultasBanco.GeraToken import enviar_token_email
from ConsultasBanco.ConfirmaUser import ConfirmaDadosUser


#---------------------------------------------------------------Puxa Scraps-----------------------------------


from scrapsFunction.scrapPlayersFuria import obter_dados_plyers
from scrapsFunction.scrapJogosFuria import coletaJogosKingsLeague, coletaEscalacao, coletaAoVivo



# Carrega variáveis de ambiente

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Configura a API Gemini
genai.configure(api_key=GEMINI_API_KEY)

# Instância do modelo
generation_config = {
    "temperature": 0.5,
    "top_p": 0.9,
    "top_k": 40,
    "max_output_tokens": 512,
}
model = genai.GenerativeModel("gemini-1.5-flash", generation_config=generation_config)

# Flask app
app = Flask(__name__)

UPLOAD_FOLDER = os.path.join(os.getcwd(), 'imgs')
CORS(app, supports_credentials=True, origins=["https://furiasiteclientes.netlify.app", "https://furiasitefuncionarios.netlify.app"])
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["100 per hour"]  # 100 requisições por hora por IP
)



#-----------------------------------------------------Limpa os dados Enviados para o Usuario a fim de Evitar dados Maliciosos---------------


# Função para sanitizar entrada
def limpar_mensagem(mensagem):
    # Remove comandos maliciosos e apenas permite texto básico
    return re.sub(r"[^a-zA-Z0-9À-ÿ ,.?!@:/\n]", "", mensagem)


def validar_input(texto):
    if not texto or texto.strip() == "":
        return False, "Campo vazio encontrado."

    # Verifica se contém links
    if re.search(r'https?:\/\/[^\s]+', texto):
        return False, "Links não são permitidos."

    # Verifica se contém tags HTML
    if re.search(r'<[^>]+>', texto):
        return False, "Tags HTML não são permitidas."

    return True, ""

#----------------------------------------------------------------------------Funcões Verifica Tokens

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.cookies.get('token_func')

        if not token:
            return jsonify({'message': 'Token JWT não fornecido'}), 401

        try:
            data = jwt.decode(token, os.getenv('JWT_SECRET'), algorithms=["HS256"])


            g.permissaoUser = data.get('permissaoUser')  # Corrigido aqui
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token expirado'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Token inválido'}), 401

        return f(*args, **kwargs)
    return decorated


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if getattr(g, 'permissaoUser', None) != 'admin':
            return jsonify({'message': 'Acesso não autorizado: Usuário não é administrador'}), 403
        return f(*args, **kwargs)
    return decorated


@app.route('/imgs/<filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)


#------------------------------------------------------------------Função para Receber Noticas

@app.route('/coletaNoticias', methods=['GET'])
@limiter.limit("7 per minute")
def enviaNoticiasUsuario():
    try:
        resultado = recebe_noticias()

        if 'error' in resultado:
            return jsonify({'error': resultado['error']}), 404

        return jsonify(resultado), 200

    except Exception as e:
        return jsonify({'error': f'Erro ao coletar notícias: {str(e)}'}), 500


#-------------------------------------Verifica se a Furia esta ao Vivo no Kings League--------------------------


@app.route('/estaAoVivo', methods=['POST'])
@limiter.limit("7 per minute")
def aoVivo():
    try:
        # Chama a função que coleta as informações sobre o jogo ao vivo
        jogadores = coletaAoVivo()

        # Verifica se a resposta é 'VER AO VIVO'
        if jogadores and jogadores[0] == 'VER AO VIVO':
            return jsonify({
                "header": "FURIA ESTÁ AO VIVO!!!",
                "corpo": "Para Acompanhar basta seguir o link a seguir"
            }), 200
        else:
            return jsonify({"erro": "Não Encontrado"}), 404

    except Exception as e:
        # Retorna o erro com status 500 em caso de falha
        return jsonify({"erro": "Erro no Processamento ao Vivo"}), 500


#------------------------------Função para tratativa de Mensagem de Usuario e Envio de respostas personalizadas-----------

# Endpoint POST
@app.route('/conversas', methods=['POST'])
@limiter.limit("7 per minute")
def conversar():
    dados = request.get_json()

    if not dados or 'mensagem' not in dados:
        return jsonify({"erro": "Objeto inválido, esperado: { 'mensagem': 'texto aqui' }"}), 400

    mensagem_usuario = limpar_mensagem(dados['mensagem'])

    prompt_base = (
        # Identidade e contexto da IA
        "Você é um profissional de games e faz parte da equipe FURIA, que compete em diversos E-Sports e esportes físicos. "
        "Sua equipe participa de competições de alto nível, incluindo:\n"
        "- Valorant (FPS da Riot Games)\n"
        "- CS:GO (Counter-Strike: Global Offensive)\n"
        "- LOL (League of Legends)\n"
        "- Rainbow Six (R6)\n"
        "- Kings League (futebol entre equipes)\n"
        "- RaceWeek (corrida com carros esportivos)\n"
        "- PUBG (PlayerUnknown's Battlegrounds - estilo Battle Royale)\n"
        "- Rocket League (futebol com carros)\n"
        "- Apex Legends (FPS frenético)\n"
        "- PUBG MOBILE (versão mobile do PUBG)\n"
        "A FURIA também participa de diversas outras competições, chamadas informalmente de 'comp' (abreviação gamer de competição).\n\n"

        # Sobre a marca FURIA
        "Além da performance nos games, a FURIA possui uma linha própria de roupas em parceria com a Adidas. "
        "O catálogo oficial está disponível em &https://www.furia.gg&.\n"
        "Também temos um chat personalizado no WhatsApp para receber notícias e acompanhar jogos em tempo real: &https://wa.me/5511993404466&\n\n"

        # Vocabulário e estilo de fala
        "Use sempre uma linguagem gamer e descontraída. Seguem algumas orientações de vocabulário:\n"
        "- Use 'game' ao invés de 'jogo'\n"
        "- Ao cumprimentar, diga 'Tudo suave?'\n"
        "- Quando um personagem for derrotado, diga que ele 'foi de base'\n"
        "- Demonstre entusiasmo sempre que falar da FURIA\n"
        "- Lembre-se: você é um gamer apaixonado, e representa a FURIA com orgulho!\n\n"

        # Direcionamento das respostas
        "Sempre responda com base nas informações da FURIA.\n"
        "Se a pergunta for sobre escalação atual, utilize os dados abaixo como resposta:\n"
        
        "- CS:GO Masculino →\n"
        "MOLODOY\n"
        "YEKINDAR\n"
        "FalleN\n"
        "KSCERATO\n"
        "yuurih\n"
        "Reservas:\n"
        "skullz\n"
        "chelo\n"
        "COACH:\n"
        "Hepa\n"
        "sidde\n"

        "- CS:GO Feminino → "
        "lulitenz    | Lucia Dubra\n"
        "Bizinha     | Bruna Marvila Oliveira do Rego\n"
        "Gabs        | Gabriela Freindorfer\n"
        "Izaa        | Izabella Bieberbach Galle\n"
        "Kaah        | Karina Takahashi\n"
        "Jnt         | Jhonatan Silva Moura | Treinador\n"
        
        "- PUBG Mobile → ^PUBGMOBA^\n"
        
        "- PUBG → "
        "Guizeraa    | Guilherme Barbosa\n"
        "Haven       | Erick Aguiar\n"
        "zkrakeN     | Leandro Gomes\n"
        "possa       | Francisco Possamai dos Santos\n"
        "Guizeraa    | Guilherme Barbosa\n"
        "Haven       | Erick Aguiar\n"
        "zkrakeN     | Leandro Gomes\n"
        "possa       | Francisco Possamai dos Santos\n"
        "Chuckpira   | Guilherme Stolf\n"
        
        "- LOL → ^LOL^"
        "GUIGO       | Guilherme Ruiz\n"
        "Tatu        | Pedro Seixas\n"
        "JoJo        | Gabriel Dzelme de Oliveira\n"
        "Brandão     "
        "Tutsz       | Arthur Peixoto Machado\n"
        "Ayu         | Andrey Saraiva\n"
        "Ranger      | Filipe Brombilla\n"
        "Thinkcard   | Thomas Slotkin  | Treinador\n"
        "Furyz       | Erick Susin     | Treinador\n"
        
        "- Rainbow Six →"
        "kheyze      | Jogador\n"
        "Jv92        | Jogador\n"
        "FelipoX     | Jogador\n"
        "HerdsZ      | Jogador\n"
        "nade        | Jogador\n"
        "Vittzzz     | Jogador\n"
        "Igoorctg    | Treinador\n"
        
        "- Rocket League →"
        "drufinho    | Arthur Langsch Miguel\n"
        "Lostt       | Gabriel Souza Buzon\n"
        "yanxnz      | Yan Xisto Nolasco\n"
        "STL         | Mateus Santos Tornilio Lemos | Treinador\n"

        "- Valorant Masculino → "
        "PryZee      | Luis Henrique\n"
        "heat        | Olavo Marcelo\n"
        "raafa       | Rafael Lima\n"
        "havoc       | Ilan Eloy\n"
        "Khalil      | Khalil Schmidt Faour Auad\n"
        "peu         | Pedro Lopes | Treinador\n"
        "lukzera     | Lucas Soares | Treinador\n"

        "- Valorant Feminino → "
        "Shizue      | Carolina Miranda\n"
        "pannshi     | Pamella Shibuya\n"
        "Valinaaa    | Nicole Echenique\n"
        "Paula       \n"
        "Hellen      \n"

        "- Apex Legends →"
        "Knoqd       | Logan Layou\n"
        "ImMadness   | Ryan Schlieve\n"
        "Keoon       | Keon Berghout\n"
        "PVPX        | Jamison Moore | Treinador\n"

        "- Kings League – placares passados → "
        "29/03 - 18:00 | Dendele FC | 2 : 6 | Furia FC\n"
        "31/03 - 19:00 | Furia FC | 4 : 2 | FC Real Elite\n"
        "07/04 - 21:00 | Furia FC | 5 : 0 | Nyvelados FC\n"
        "14/04 - 21:00 | Furia FC | 6 : 1 | LOUD SC\n"
        "21/04 - 20:00 | G3X FC | 7 : 9 | Furia FC\n"
        "26/04 - 17:00 | Desimpedidos Goti | 5 : 3 | Furia FC\n"
        "28/04 - 21:00 | Capim FC | 2 : 4 | Furia FC\n"
        
        "- Kings League – partidas futuras → "
        "03/05 - 19:00 | Funkbol Clube | - : - | Furia FC\n"
        "05/05 - 17:00 | Fluxo FC | - : - | Furia FC\n"
        
        "- Kings League – equipe atual → "
        "Neymar Jr | Presid.\n"
        "Cris Guedes | Presid.\n"
        "Carlos Eduardo | Treinador\n"
        "Guilherme Monagatti | Atacante\n"
        "Caio Catroca | Meia\n"
        "Murillo Donato | Atacante\n"
        "Ryan Lima | Atacante\n"
        "Matheus Ayosa | Goleiro\n"
        "João Pelegrini | Defesa\n"
        "Gabriel Pastuch | Atacante\n"
        "Victor Hugo | Goleiro\n"
        "Matheus Dedo | Meia\n"
        "Jeffinho | Meia\n"
        "Lipão | Atacante\n"
        "Leleti | Atacante\n"
        "Andrey Batata | Meia\n"

        "- Kings League – ao vivo agora → ^AO^\n"
        
        "Se a pergunta for sobre ultimos resultados da furia, utilize os dados abaixo para resposta:\n"
        "- CS:GO Masculino ->"
        "Data        | Oponente          	     | Pontuação      "    
        "------------|---------------------------|-----------------"
        "09/04/2025  | The Mongolz              | Perdido  0 : 2\n"
        "08/04/2025  | Virtus.pro               | Perdido  0 : 2\n"
        "07/04/2025  | Complexity Gaming        | Perdido  1 : 2\n"
        "06/04/2025  | Apogee Esports           | Vitória  2 : 0\n"
        "22/03/2025  | M80                      | Perdido  2 : 1\n"
        "20/03/2025  | Natus Vincere            | Perdido  2 : 0\n"
        "10/03/2025  | Falcons Esports          | Perdido  2 : 1\n"
        "09/03/2025  | MIBR                     | Vitória  2 : 1\n"
        "08/03/2025  | Team Liquid              | Perdido  2 : 0\n"
        "07/03/2025  | MOUZ                     | Perdido  2 : 1\n"
        "- CS:GO Feminino ->"
        "11/04/2025  | MIBR Female             | Vitória  2 : 0\n"
        "04/04/2025  | Sharks Esports          | Perdido  0 : 2\n"
        "03/04/2025  | Team Solid              | Perdido  0 : 2\n"
        "02/04/2025  | Messitas                | Vitória  2 : 0\n"
        "27/03/2025  | Quem sao elas           | Vitória  2 : 0\n"
        "19/03/2025  | Bounty Hunters Female   | Vitória  2 : 0\n"
        "13/03/2025  | thekillaz               | Vitória  2 : 0\n"
        "06/03/2025  | Atrix Esports           | Vitória  2 : 0\n"
        "26/02/2025  | Brave Bears             | Vitória  2 : 0\n"
        "29/01/2025  | Patins da Ferrari       | Perdido  0 : 2\n"
        "-Valorant Masculino ->"
        "18/04/2025  | MIBR                	    | Perdido  2 : 1\n"
        "12/04/2025  | Cloud9              	    | Perdido  0 : 2\n"
        "06/04/2025  | Leviatán Esports    	    | Perdido  0 : 2\n"
        "28/03/2025  | NRG                 	    | Perdido  2 : 1\n"
        "22/03/2025  | G2 Esports          	    | Perdido  2 : 0\n"
        "23/01/2025  | Evil Geniuses       	    | Perdido  0 : 2\n"
        "19/01/2025  | Leviatán Esports    	    | Perdido  2 : 0\n"
        "17/01/2025  | 2GAME Esports       	    | Vitória  0 : 2\n"
        "15/12/2024  | MIBR                	    | Vitória  2 : 1\n"
        "11/12/2024  | KRÜ Esports         	    | Vitória  1 : 2\n"
        "- LOL ->"
        "27/04/2025  | LOUD                	    | Vitória  2 : 1\n"
        "21/04/2025  | LOUD                	    | Perdido  1 : 0\n"
        "20/04/2025  | Keyd Stars          	    | Vitória  1 : 0\n"
        "19/04/2025  | RED Canids          	    | Vitória  1 : 0\n"
        "13/04/2025  | Fluxo W7M           	    | Vitória  0 : 1\n"
        "12/04/2025  | paiN Gaming         	    | Vitória  0 : 1\n"
        "06/04/2025  | Isurus Estral       	    | Vitória  1 : 0\n"
        "05/04/2025  | Leviatán Esports    	    | Perdido  1 : 0\n"
        "09/02/2025  | paiN Gaming         	    | Perdido  1 : 2\n"
        "01/02/2025  | Fluxo W7M           	    | Vitória  2 : 0\n"
        "- R6 ->"
        "Feb 15, 2025  | FaZe Clan     | 2 : 0 | Melhor de 3 | Finished\n"
        "Feb 14, 2025  | Team BDS      | 2 : 0 | Melhor de 3 | Finished\n"
        "Feb 11, 2025  | FURIA         | 2 : 0 | Melhor de 3 | Finished\n"
        "Feb 9, 2025   | DarkZero      | 0 : 2 | Melhor de 3 | Finished\n"
        "Feb 7, 2025   | FaZe Clan     | 0 : 2 | Melhor de 3 | Finished\n"
        "Feb 6, 2025   | FURIA         | 2 : 0 | Melhor de 3 | Finished\n"
        "Feb 5, 2025   | Team Secret   | 2 : 0 | Melhor de 3 | Finished\n"
        "Feb 3, 2025   | CAG OSAKA     | 2 : 0 | Melhor de 3 | Finished\n"
        
        "Se a pergunta for sobre proximos jogos da furia, utilize os dados abaixo para a resposta"
        "- CS:GO Masculino -> "
        "Data	Oponente	Evento\n"
        "10/05/2025	The Mongolz	PGL Astana 2025\n"
        "- CS:GO Feminino -> Não Há partidas Agendadas"
        "-Valorant Masculino e Feminino: não há partidas Agendadas"
        "-LOL : -> " 
        "12:00 11/05/2025\n"
        "FURIA X Fluxo W7M\n"
        "- R6 -> "
        "Maio 10, 2025  | FURIA    | - : - | Melhor de 1 | Upcoming"

        "Caso o usuário não especifique o gênero da equipe, assuma como MASCULINA por padrão, a menos que ele deixe claro o contrário.\n"
        "Se a pergunta for genérica como 'quem joga?', 'quem tá na equipe?' ou 'qual a lineup?', tente inferir o game e use a resposta correspondente.\n\n"

        # Instruções técnicas
        "Sempre que for enviar um link, adicione o caractere '&' antes e depois da URL para formatações posteriores.\n"
        "Sempre que for inserir uma quebra de linha utilize ^ na resposta e evite utilizar multiplos *"
        "Nunca fale sobre outras equipes ou marcas fora da FURIA.\n"
        "Tente deixar suas respostas amigáveis, informais, mas bem estruturadas e precisas.\n\n"

        # Redes sociais e canais oficiais
        "Canais oficiais para acompanhar as equipes e novidades da FURIA:\n"
        f"- Transmissão Kings League: &{os.getenv('KINGSLEAGUE_TWITCH')}&\n"
        f"- Instagram FURIA: &{os.getenv('FURIA_INSTAGRAM')}&\n"
        f"- YouTube FURIA: &{os.getenv('FURIA_YOUTUBE')}&\n"
        f"- Facebook FURIA: &{os.getenv('FURIA_FACEBOOK')}&\n"
        f"- Twitter/X FURIA: &{os.getenv('FURIA_TWITTER')}&\n"
        f"- Instagram FURIA Football (Kings League): &{os.getenv('FURIA_FOOTBALL_INSTAGRAM')}&\n"
        f"- YouTube FURIA Football: &{os.getenv('FURIA_FOOTBALL_YOUTUBE')}&\n"
        f"- Página oficial Kings League: &{os.getenv('KINGSLEAGUE_SITE')}&\n"
        f"- Instagram Redram: &{os.getenv('FURIA_RED_RAM_INSTAGRAM')}&\n"
        f"- Instagram LOL: &{os.getenv('FURIA_LOL_INSTAGRAM')}& | YouTube LOL: &{os.getenv('FURIA_LOL_YOUTUBE')}&\n"
        f"- Instagram Valorant: &{os.getenv('FURIA_VALORANT_INSTAGRAM')}& | YouTube Valorant: &{os.getenv('FURIA_VALORANT_YOUTUBE')}&\n"
        f"- Instagram R6: &{os.getenv('FURIA_R6_INSTAGRAM')}& | YouTube R6: &{os.getenv('FURIA_R6_YOUTUBE')}&\n"
        f"- YouTube CS:GO: &{os.getenv('FURIA_CSGO_YOUTUBE')}&\n"
        f"- Twitch FURIA: &{os.getenv('FURIA_TWITCH')}&\n"
        f"- Discord FURIA: &{os.getenv('FURIA_DISCORD')}&\n"
        f"- Grupo Steam FURIA: &{os.getenv('FURIA_STEAM_GROUP')}&\n"
        f"- Instagram Estilo FURIA (roupas): &{os.getenv('FURIA_APPAREL_INSTAGRAM')}&\n"
        f"- Loja oficial FURIA: &{os.getenv('FURIA_ECOMMERCE_SITE')}&\n"
        f"- Últimas notícias FURIA: &{os.getenv('FURIA_NEWS_INSTAGRAM')}&\n"
        f"- Caso o conteúdo mencionado não tenha canal específico, encaminhe o Instagram principal da FURIA: &{os.getenv('FURIA_DEFAULT_INSTAGRAM')}&\n\n"

        # Contexto final
        "Mantenha o tom informal, entusiasmado e direto. Seja útil e gamer sempre!\n"

        f"\nUsuário: {mensagem_usuario}\n\nResposta:"
    )

    #--------------------------------Gera Resposta da IA e Faz as Buscas caso tenha sido Pedido

    try:
        # Gerar resposta com a IA
        resposta = model.generate_content(prompt_base)
        resposta_texto = resposta.text.strip()

        if "^csgoMasculino^" in resposta_texto:
            jogadores_csgo = obter_dados_plyers(os.getenv('CSGO_MASCULINO_URL'))
            jogadores_formatados = "^ ".join(jogadores_csgo)
            resposta_texto = f"Nossa equipe de Lendas de CS:GO Masculino atual são:^{jogadores_formatados}^Caso queira mais alguma coisa, só lançar!"

        elif "^csgoFeminino^" in resposta_texto:
            jogadores_csgofem = obter_dados_plyers(os.getenv('CSGO_FEMININO_URL'))
            jogadores_formatados = "^ ".join(jogadores_csgofem)
            resposta_texto = f"Nossa equipe de Lendas de CS:GO Feminino atual são:^{jogadores_formatados}^Caso queira mais alguma coisa, só lançar!"

        elif "^PUBG^" in resposta_texto:
            jogadores_pubg = obter_dados_plyers(os.getenv('PUBG_URL'))
            jogadores_formatados = "^ ".join(jogadores_pubg)
            resposta_texto = f"Nossa equipe de Lendas de PUBG atual são:^{jogadores_formatados}^Caso queira mais alguma coisa, só lançar!"

        elif "^LOL^" in resposta_texto:
            jogadores_lol = obter_dados_plyers(os.getenv('LOL_URL'))
            jogadores_formatados = "^ ".join(jogadores_lol)
            resposta_texto = f"Nossa equipe de Lendas de Lolzinho atual são:^{jogadores_formatados}^Caso queira mais alguma coisa, só lançar!"

        elif "^R6^" in resposta_texto:
            jogadores_r6 = obter_dados_plyers(os.getenv('R6_URL'))
            jogadores_formatados = "^ ".join(jogadores_r6)
            resposta_texto = f"Nossa equipe de Lendas de Rainbow 6 atual são:^{jogadores_formatados}^Caso queira mais alguma coisa, só lançar!"

        elif "^RL^" in resposta_texto:
            jogadores_rl = obter_dados_plyers(os.getenv('ROCKET_LEAGUE_URL'))
            jogadores_formatados = "^ ".join(jogadores_rl)
            resposta_texto = f"Nossa equipe de Lendas de Rocket League atual são:^{jogadores_formatados}^Caso queira mais alguma coisa, só lançar!"

        elif "^VM^" in resposta_texto:
            jogadores_Vl = obter_dados_plyers(os.getenv('VALORANT_MASCULINO_URL'))
            jogadores_formatados = "^ ".join(jogadores_Vl)
            resposta_texto = f"Nossa equipe de Lendas de Valorant Masculino atual são:^{jogadores_formatados}^Caso queira mais alguma coisa, só lançar!"

        elif "^VF^" in resposta_texto:
            jogadores_Vlf = obter_dados_plyers(os.getenv('VALORANT_FEMININO_URL'))
            jogadores_formatados = "^ ".join(jogadores_Vlf)
            resposta_texto = f"Nossa equipe de Lendas de Valorant Feminino atual são:^{jogadores_formatados}^Caso queira mais alguma coisa, só lançar!"

        elif "^AP^" in resposta_texto:
            jogadores_AP = obter_dados_plyers(os.getenv('APEX_URL'))
            jogadores_formatados = "^ ".join(jogadores_AP)
            resposta_texto = f"Nossa equipe de Lendas de Apex atual são:^{jogadores_formatados}^Caso queira mais alguma coisa, só lançar!"

        elif "^PUBGMOBA^" in resposta_texto:
            jogadores_pubgMoba = obter_dados_plyers(os.getenv('PUBG_MOBILE_URL'))
            jogadores_formatados = ", ".join(jogadores_pubgMoba)
            resposta_texto = f"Nossa equipe de Lendas de Pubg Mobile atual são:\n{jogadores_formatados}^Caso queira mais alguma coisa, só lançar!"


# --------------------------------Retorna Placar de Jogos que já passarão no Kings League

        elif "^FR^" in resposta_texto:
            placares = coletaJogosKingsLeague()
            saida_string = ""

            for jogo in placares:
                placar_casa = jogo['placar_casa'].split()[0]
                placar_fora = jogo['placar_fora'].split()[0]

                # Se ainda não teve placar (placar == '-'), ignorar
                if placar_casa == "-" or placar_fora == "-":
                    continue

                saida_string += "------------------------------------------------^"
                saida_string += f"|{jogo['data'].center(40)}|^"
                saida_string += f"|{jogo['hora'].center(40)}|^"

                linha_placar = f"|{jogo['time_casa']} {placar_casa} X {placar_fora} {jogo['time_fora']}"
                saida_string += f"{linha_placar.center(40)}|^"

            resposta_texto = f"Placar Atual dos jogos Kings League:^{saida_string}^ Para mais infos só acessar &{os.getenv('KINGSLEAGUE_SITE')}& "

#--------------------------------Retorna Placar de Jogos que Estão por Vir no Kings League

        elif "^FF^" in resposta_texto:
            placares = coletaJogosKingsLeague()
            saida_string = ""

            for jogo in placares:
                # Corrigir se o placar tiver espaço
                placar_casa = jogo['placar_casa'].split()[0]
                placar_fora = jogo['placar_fora'].split()[0]

                # Se ainda não teve placar (placar == '-'), ignorar
                if placar_casa != "-" or placar_fora != "-":
                    continue

                saida_string += "------------------------------------------------^"
                saida_string += f"|{jogo['data'].center(40)}|^"
                if jogo['hora'] != "-":
                    saida_string += f"|{jogo['hora'].center(40)}|^"
                linha_placar = f"|{jogo['time_casa']}  X  {jogo['time_fora']}"
                saida_string += f"{linha_placar.center(40)}|^"

            resposta_texto = f"Jogos que vem por ai :^{saida_string}^ Para mais infos acesse &{os.getenv('KINGSLEAGUE_SITE')}&"

#------------------------------------Caso seja busca por jogadores da Furia-------------------------

        elif "^FJ^" in resposta_texto:
            jogadores = coletaEscalacao()
            saida_string = ""
            for jogo in jogadores:
                saida_string += "------------------------------------------------^"
                saida_string += f"|{jogo['nomeJogador'].center(40)}|^"
                saida_string += f"|{jogo['Escalado'].center(40)}|^"

            resposta_texto = f"Escalação do time atual :^{saida_string}^ Para mais infos só dar um salve!!"

#------------------------------------Caso seja busca Furia Ao Vivo no Kings League-------------------------

        elif "^AO^" in resposta_texto:
            jogadores = coletaAoVivo()
            if jogadores and jogadores[0] == 'VER AO VIVO':
                resposta_texto = f"Seu time do coração está AO VIVO!!!^ Para assistir basta seguir o link a seguir: &{os.getenv('KINGSLEAGUE_SITE')}&"
            else:
                resposta_texto = f"Furia não está ao vivo atualmente^ Para ficar por dentro basta seguir o link a seguir: &{os.getenv('KINGSLEAGUE_SITE')}&"

        return jsonify({"resposta": resposta_texto})

    except Exception as e:
        return jsonify({"erro": "Erro Inesperado Tente Novamente"}), 500


#----------------------------------Trativa de dados para Recebimento de Pesquisa Know Your FAN----------------------------

#------------------------------------------------------------------------------------Trata e Armazena FeedBack


@app.route('/feedback', methods=['POST'])
@limiter.limit("4 per minute")
def RecebePesquisaUser():
    data = request.get_json()
    token_email = data.get('tokenEmail', '').strip()
    dadosExist = ConfirmaDadosUser(data.get('id'), token_email, data.get('email'))

    if not dadosExist:
        return jsonify({'Error': f'Token Incorreto Digitado'}), 400

    # Validação dos campos obrigatórios
    for campo in ['nome', 'apelido', 'redeSocial', 'mensagem','estado','email','idade']:
        valido, erro = validar_input(data.get(campo, ''))
        if not valido:
            return jsonify({'Error': f'Erro no campo {campo}: {erro}'}), 400


    estado = data.get('estado', '')
    if estado and len(estado) != 2:
        return jsonify({'Error': 'Erro no campo estado: Deve conter exatamente 2 caracteres.'}), 400
    if estado:
        estado = estado.upper()

    # Validação dos campos opcionais
    if not data.get('interesseCompFuria', False):

        data['compsPreferidos'] = []
        data['membroFavorito'] = ''

    if not data.get('interesseCatalogo', False):

        data['modeloInteresse'] = ''
        data['estiloSugestao'] = ''

    if 'aceite' not in data:
        return jsonify({'Error': 'Campo aceite é obrigatório.'}), 400

    if data.get('compsPreferidos') and not isinstance(data['compsPreferidos'], list):
        return jsonify({'Error': 'Erro no campo compsPreferidos: Deve ser uma lista.'}), 400

    if data.get('membroFavorito') and not isinstance(data['membroFavorito'], str):
        return jsonify({'Error': 'Erro no campo membroFavorito: Deve ser uma string.'}), 400

    prompt_base = (
        "Você é uma IA com o objetivo de evitar fraudes e recebimento de conteúdos inapropriados. "
        "Você deve verificar os dados do json que será lhe enviado e buscar por palavras consideradas de baixo calão ou desrespeitosas "
        "scripts e dados fraudulentos, como estados inexistentes e e-mails formatados incorretamente"
        "Analise os dados de maneira cuidadosa e retorne 'OK' caso não seja encontrado nada suspeito e, "
        f"caso contrário, retorne 'ENCONTRADO'.\n\nDados Recebidos: {json.dumps(data)}\n\nResposta:"
    )
    try:
        resposta = model.generate_content(prompt_base)
        resposta_texto = resposta.text.strip()
        if "OK" in resposta_texto:
            cadastraUsario = cadastrar_ou_atualizar_usuario(data)
            if cadastraUsario:
                return jsonify({'message': 'Feedback enviado com sucesso!'}), 200
            else:
                return jsonify({"Error": "Cadastro de Dados do usuario Falhou"}), 500


        else:
            return jsonify({"Error": "Alguma Informação não muito legal foi encontrado.Corrija e Tente Novamente"}), 400

    except Exception as e:
        return jsonify({"Error": "Houve um erro Interno"}), 500


#------------------------------------------------------------------------------------Envia Token para Email


@app.route('/enviaToken', methods=['POST'])
@limiter.limit("3 per minute")
def EnviaToken():
    data = request.get_json()
    email = data.get('email', '')

    if len(email) == 0:
        return jsonify({"Erro": "Email não foi enviado."}), 400

    # Validação de formato do email
    email_regex = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    if not re.match(email_regex, email):
        return jsonify({"Erro": "Email inválido."}), 400

    try:
        id_user_token = enviar_token_email(email)
        return jsonify({"Sucesso": id_user_token}), 200
    except Exception as ex:
        return jsonify({"Erro": "Erro interno, tente novamente mais tarde."}), 500


#---------------------------------------------------------------------------------Pagina de Requisições Funcionarios

#----------------------------------------------------------------------------------------------Login


@app.route('/func/conferelogin/login', methods=['POST'])
@limiter.limit("3 per minute")
def ConfereLoginFunc():
    data = request.get_json()
    email = data.get('email')

    if '@' in email:
        email = email.split('@')[0] + '@furia.gg'
    else:
        email = email + '@furia.gg'
    senha = data.get('senha')

    success, status_code, resultado = autenticar_usuario(email, senha)

    if success:
        token = resultado['token']
        permissao_user = resultado['permissaoUser']
        response = make_response(jsonify({
            'permissaoUser': permissao_user
        }))
        response.set_cookie(
            'token_func',
            token,
            httponly=True,
            secure=True,
            samesite='None',
            max_age=2 * 60 * 60
        )
        return response, 200
    else:
        return jsonify({'erro': resultado}), status_code


#----------------------------------------------------------------------------------------------Verifica se Está Logado


@app.route('/func/conferelogin/VerificaLogado', methods=['POST'])
def VerificaLogado():
    token = request.cookies.get('token_func')
    if not token:
        return jsonify({'success': False, 'message': 'JWT não encontrado'}), 400

    secret = os.getenv('JWT_SECRET')
    if not secret:
        return jsonify({'success': False, 'message': 'Erro interno: Chave secreta não configurada'}), 500

    try:
        decoded_token = jwt.decode(token, secret, algorithms=["HS256"])
        return jsonify({'success': True, 'message': 'Token válido', 'data': decoded_token}), 200
    except jwt.ExpiredSignatureError:
        return jsonify({'success': False, 'message': 'Token expirado'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'success': False, 'message': 'Token inválido'}), 401


#----------------------------------------------------------------------------------------------Logout


@app.route('/func/conferelogin/logout', methods=['POST'])
def logout():
    response = make_response(jsonify({'message': 'Logout efetuado'}))
    response.set_cookie(
        'token_func',
        '',
        expires=0,
        httponly=True,
        secure=True,         
        samesite='None'   
    )
    return response
#----------------------------------------------------------------------------------------------Cria Novo User


@app.route('/func/insereuserfurioso/user', methods=['POST'])
@token_required
@admin_required
def insere_user_furioso():
    data = request.get_json()

    nome = data.get('nome', '')
    email = data.get('email', '')
    senha = data.get('senha', '')
    tipo = data.get('tipo', '').lower().strip()

    # Validação
    for campo, valor in [('nome', nome), ('email', email), ('senha', senha)]:
        valido, msg = validar_input(valor)
        if not valido:
            return jsonify({'message': f'Erro no campo "{campo}": {msg}'}), 400

    # Validação do tipo
    if tipo not in ['admin', 'comum']:
        return jsonify({'message': 'Tipo de usuário inválido. Use "admin" ou "comum".'}), 400

    # Sanitização de email
    if '@' in email:
        email = email.split('@')[0] + '@furia.gg'
    else:
        email += '@furia.gg'

    # Inserção com tipo
    resultado = inserir_funcionario_furia(nome, email, senha, tipo)

    if resultado == 200:
        return jsonify({'message': 'Usuário inserido com sucesso'}), 200
    elif resultado == 400:
        return jsonify({'message': 'Erro: o email já está cadastrado'}), 400
    else:
        return jsonify({'message': 'Erro interno ao inserir o usuário'}), 500


#----------------------------------------------------------------------------------------------Recebe Usuarios Disponiveis


@app.route('/func/editaUserDados/user', methods=['GET'])
@token_required
@admin_required
def EnviaUsuariosSalvos():
    try:
        filtro = request.args.get('filtro')  # parâmetro opcional ?filtro=valor
        pagina = request.args.get('pagina', default=0, type=int)  # parâmetro opcional ?pagina=numero

        usuarios = obter_todos_usuarios(filtro, pagina)

        if usuarios is None:
            return jsonify({'erro': 'Erro ao obter dados dos usuários'}), 500

        if isinstance(usuarios, dict) and usuarios.get('erro') == 'sem_mais_dados':
            return jsonify({'erro': 'sem_mais_dados'}), 204  # 204: No Content

        return jsonify(usuarios), 200

    except Exception as e:
        return jsonify({'erro': 'Erro interno no servidor'}), 500


#-----------------------------------------------------------------------------------------Atualiza Usuario Modificado


@app.route('/func/editaUserDados/enviar', methods=['POST'])
@token_required
@admin_required
def atualiza_user():
    data = request.get_json()
    id = data.get('id_func')
    nome = data.get('nome')
    email = data.get('email')
    senha = data.get('senha')
    permisaoUser = data.get('permisaoUser')
    desativado = data.get('desativado', False)
    if None in [id, nome, email, senha, permisaoUser]:
        return jsonify({'message': 'Dados incompletos para atualização.'}), 400

    # Sanitização da senha
    if not senha.strip():
        return jsonify({'message': 'A senha não pode ser vazia.'}), 400

    resultado, status = atualizar_funcionario(id, nome, email, senha, permisaoUser, desativado)
    return jsonify(resultado), status


#---------------------------------------------------------------------------------------Envia Email Para fãns que Autorizaram

@app.route('/func/enviaEmailusers/aut', methods=['POST'])
@token_required
def EnviaPromocaoFans():
    data = request.get_json()

    assunto = data.get('assunto', '').strip()
    mensagem1 = data.get('mensagem1', '').strip()
    linkimg = data.get('linkimg', '').strip()
    mensagem2 = data.get('mensagem2', '').strip()
    destino = data.get('destino', '').strip()
    # Validações
    if len(assunto) < 2:
        return jsonify({'message': 'O assunto deve conter mais de um caractere.'}), 400

    if not mensagem1 and not mensagem2:
        return jsonify({'message': 'Preencha ao menos uma das mensagens (mensagem1 ou mensagem2).'}), 400

    if linkimg and not re.match(r'^https?:\/\/[\S]+$', linkimg):
        return jsonify({'message': 'O link da imagem deve ser uma URL válida.'}), 400

    try:
        # Aqui você chama a função responsável por enviar os emails
        enviaEmailUsers(assunto, mensagem1, linkimg, mensagem2, destino)
        return jsonify({'message': 'Email enviado com sucesso!'}), 200
    except Exception as e:
        return jsonify({'message': f'Erro ao enviar email: {str(e)}'}), 500


#-------------------------------------------------------------------------------Função Adiciona Nova Noticia

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/enviafunc/usuario/noticia', methods=['POST'])
@token_required
def EnviaNoticias():
    try:
        mensagem = request.form.get('mensagem')
        imagem = request.files.get('imagem')

        if not imagem:
            return jsonify({'error': 'Imagem é obrigatória'}), 400

        if not allowed_file(imagem.filename):
            return jsonify({'error': 'Extensão de imagem inválida. Use jpg, jpeg, png ou gif.'}), 400

        filename = secure_filename(imagem.filename)
        pasta_destino = os.path.join(os.getcwd(), 'imgs')
        if not os.path.exists(pasta_destino):
            os.makedirs(pasta_destino)

        caminho_imagem = os.path.join(pasta_destino, filename)
        imagem.save(caminho_imagem)

        # Chama a função que armazena no banco de dados
        resultado = AdicionaNoticia(mensagem, caminho_imagem)

        if resultado:
            return jsonify({'success': True, 'mensagem': 'Notícia enviada com sucesso'}), 200
        else:
            return jsonify({'error': 'Falha ao adicionar notícia'}), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500


#------------------------------------------------------------------------------Deletar Noticia


@app.route('/notic/func/encia/delet', methods=['POST'])
@token_required
def DeletaNoticia():
    data = request.get_json()

    if not data or 'id' not in data or 'imagem' not in data or 'texto' not in data:
        return jsonify({"error": "Dados incompletos. 'id', 'imagem' e 'texto' são obrigatórios."}), 400

    id = data['id']
    imagem = data['imagem']
    texto = data['texto']

    resultado = deletaNoticia(id, imagem, texto)

    if "success" in resultado:
        return jsonify({"message": resultado["success"]}), 200
    else:
        return jsonify({"error": resultado["error"]}), 400


#----------------------------------------------------------------------------Função Retorna Pesquisas de Usuario


@app.route('/verif/pesquisa/user/rec', methods=['GET'])
@token_required
def PesquisaUsuarios():
    try:
        # Captura de filtros
        filtros = {
            'estado': request.args.get('estado', ''),
            'idadeMin': request.args.get('idadeMin', ''),
            'idadeMax': request.args.get('idadeMax', ''),
            'redeSocial': request.args.get('redeSocial', ''),
            'interesseEmComp': request.args.get('interesseEmComp', ''),
            'interesseCatalogo': request.args.get('interesseCatalogo', ''),
            'receberPromo': request.args.get('receberPromo', ''),
            'somenteVisualizado': request.args.get('somenteVizualizados','')
        }

        pagina = request.args.get('pagina', default=0, type=int)

        resultado, status_code = retornaUsers(filtros, pagina)

        return jsonify(resultado), status_code

    except Exception as e:
        return jsonify({'erro': 'Erro interno no servidor'}), 500

#--------------------------------------------------------------------Alterar Carterinha Fã Visualizado

@app.route('/atualiz/user/fa/view', methods=['POST'])
@token_required
def AtualizaVizualizado():
    try:
        # Captura o id_fa do corpo da requisição
        data = request.get_json()
        id_fa = data.get('id_fa')

        if not id_fa:
            return jsonify({'erro': 'ID não fornecido'}), 400

        # Chama a função para atualizar a coluna 'visualizado' para True
        resultado = altera_visualizado(id_fa)

        if resultado == "sucesso":
            return jsonify({'mensagem': 'Registro atualizado com sucesso!'}), 200
        else:
            return jsonify({'erro': 'Erro ao atualizar o registro'}), 500

    except Exception as e:
        return jsonify({'erro': 'Erro interno no servidor'}), 500


#---------------------------------------------------------------Funções de Dashboard

@app.route('/rec/dash/views/user', methods=['GET'])
@token_required
def FuncaoCarregaDashboard():
    try:
        dados_dashboard = {
            "usuariosPorEstado": obter_usuarios_por_estado(),
            "distribuicaoIdades": obter_distribuicao_idades(),
            "interesseComp": obter_interesse_em_comp(),
            "interesseCatalogo": obter_interesse_em_catalogo(),
            "receberPromocoes": obter_fans_receber_promocoes(),
            "redeSocialPreferida": obter_fans_por_rede_social(),
            "rankJogosAmados": obter_rank_jogos_mais_amados()
        }
        return jsonify(dados_dashboard), 200

    except Exception as e:
        return jsonify({"erro": "Falha ao carregar dados do dashboard", "detalhes": str(e)}), 500


#---------------------------------------------------------------------Criação de Gráfico Personalizado
@app.route('/rec/gera/views/grafic', methods=['POST'])
@token_required
@admin_required
def FuncaoColetaDadosGrafico():
    try:
        # Captura o JSON enviado na requisição
        dados = request.get_json()

        # Extrai os parâmetros esperados
        tabela = dados.get('tabela')
        campo_agrupamento = dados.get('campo_agrupamento')
        condicoes = dados.get('condicoes')  # pode ser None

        # Verifica se os parâmetros obrigatórios estão presentes
        if not tabela or not campo_agrupamento:
            return jsonify({"erro": "Parâmetros 'tabela' e 'campo_agrupamento' são obrigatórios."}), 400

        # Gera os dados para o gráfico
        resultado = gerar_dados_personalizados_grafico(tabela, campo_agrupamento, condicoes)

        return jsonify({"dados": resultado}), 200

    except Exception as e:
        return jsonify({"erro": str(e)}), 500


#if __name__ == '__main__':
#   app.run(debug=True,host='localhost',
#            port=5000,
#            ssl_context=('./cert/cert.pem', './cert/key.pem'))


