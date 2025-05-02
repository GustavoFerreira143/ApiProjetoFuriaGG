import mysql.connector
from dotenv import load_dotenv
import os
from datetime import datetime
import shutil

# Carregar variáveis de ambiente
load_dotenv()

DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_NAME = os.getenv('DB_NAME')

def conectar_banco():
    return mysql.connector.connect(
        host=DB_HOST,
        port=int(DB_PORT) if DB_PORT else 3306,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )
    

def AdicionaNoticia(mensagem, caminho_imagem_original):
    try:
        # Gera nome único para a imagem
        extensao = os.path.splitext(caminho_imagem_original)[1]
        nome_unico = datetime.now().strftime('%Y%m%d%H%M%S') + extensao

        # Caminho final da imagem na pasta pública
        pasta_publica = os.path.join(os.getcwd(), 'imgs')
        if not os.path.exists(pasta_publica):
            os.makedirs(pasta_publica)

        caminho_final = os.path.join(pasta_publica, nome_unico)

        # Copia a imagem para a pasta pública
        shutil.move(caminho_imagem_original, caminho_final)

        # Insere no banco de dados
        conn = conectar_banco()
        cursor = conn.cursor()
        query = "INSERT INTO noticiasfuria (img_noticia, texto_noticia) VALUES (%s, %s)"
        cursor.execute(query, (nome_unico, mensagem))
        conn.commit()
        cursor.close()
        conn.close()

        return True

    except Exception as e:
        print(f"Erro ao adicionar notícia: {e}")
        return False
