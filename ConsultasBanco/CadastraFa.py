import mysql.connector
from dotenv import load_dotenv
import os

# Carregar variáveis de ambiente
load_dotenv()

DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_NAME = os.getenv('DB_NAME')

def cadastrar_ou_atualizar_usuario(dados_usuario):
    try:
        conn = mysql.connector.connect(
            host=DB_HOST,
            port=int(DB_PORT) if DB_PORT else 3306,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        cursor = conn.cursor()

        # Primeiro, verificar se o email já existe
        email = dados_usuario['email']
        cursor.execute("SELECT id_fa FROM fansfuria WHERE email = %s", (email,))
        resultado = cursor.fetchone()

        if resultado:
            # Usuário existe - Atualizar os dados
            id_fa = resultado[0]
            idade = dados_usuario['idade']
            query_update = """
                UPDATE fansfuria SET
                    nome = %s,
                    estado = %s,
                    redeSocial = %s,
                    userRede = %s,
                    interesseEmComp = %s,
                    membroFavorito = %s,
                    interesseCatalogo = %s,
                    modeloInteresse = %s,
                    estiloSugestao = %s,
                    receberPromo = %s,
                    mensagem = %s,
                    idade = %s
                WHERE email = %s
            """
            valores_update = (
                dados_usuario['nome'],
                dados_usuario['estado'],
                dados_usuario['redeSocial'],
                dados_usuario['apelido'],
                dados_usuario['interesseCompFuria'],
                dados_usuario['membroFavorito'] if dados_usuario['membroFavorito'] else None,
                dados_usuario['interesseCatalogo'],
                dados_usuario['modeloInteresse'] if dados_usuario['modeloInteresse'] else None,
                dados_usuario['estiloSugestao'] if dados_usuario['estiloSugestao'] else None,
                dados_usuario['aceite'],
                dados_usuario['mensagem'],
                dados_usuario['idade'],  # Corrigido
                email,
            )

            cursor.execute(query_update, valores_update)
            conn.commit()

            # Atualizar JogosFavoritos: Deletar antigos e inserir novos
            cursor.execute("DELETE FROM jogosfavoritos WHERE id_fa = %s", (id_fa,))
            for jogo in dados_usuario['compsPreferidos']:
                if jogo.strip():  
                    cursor.execute(
                        "INSERT INTO jogosfavoritos (id_fa, nomeJogo) VALUES (%s, %s)",
                        (id_fa, jogo)
                    )
            conn.commit()
            return True

        else:
            # Usuário não existe - Inserir novo
            query_insert = """
                INSERT INTO fansfuria (
                    nome, estado, email, redeSocial, userRede,
                    interesseEmComp, membroFavorito, interesseCatalogo,
                    modeloInteresse, estiloSugestao, mensagem, receberPromo, idade
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            valores_insert = (
                dados_usuario['nome'],
                dados_usuario['estado'],
                email,
                dados_usuario['redeSocial'],
                dados_usuario['apelido'],
                dados_usuario['interesseCompFuria'],
                dados_usuario['membroFavorito'] if dados_usuario['membroFavorito'] else None,
                dados_usuario['interesseCatalogo'],
                dados_usuario['modeloInteresse'] if dados_usuario['modeloInteresse'] else None,
                dados_usuario['estiloSugestao'] if dados_usuario['estiloSugestao'] else None,
                dados_usuario['mensagem'],
                dados_usuario['aceite'],
                dados_usuario['idade']
            )
            cursor.execute(query_insert, valores_insert)
            conn.commit()

            id_fa = cursor.lastrowid  # Recuperar o id_fa do usuário inserido

            # Inserir JogosFavoritos se houver
            for jogo in dados_usuario['compsPreferidos']:
                if jogo.strip(): 
                    cursor.execute(
                        "INSERT INTO jogosfavoritos (id_fa, nomeJogo) VALUES (%s, %s)",
                        (id_fa, jogo)
                    )
            conn.commit()
            return True

    except mysql.connector.Error as err:
        print(f"Erro de banco de dados: {err}")
        return False
    finally:
        if cursor:
            cursor.close()
        if conn.is_connected():
            conn.close()

