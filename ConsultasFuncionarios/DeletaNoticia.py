import os
import mysql.connector
from dotenv import load_dotenv
from urllib.parse import urlparse


load_dotenv()

DB_HOST = os.getenv('DB_HOST')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_NAME = os.getenv('DB_NAME')

def conectar_banco():
    return mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )

def deletaNoticia(id, imagem, mensagem):
    try:
        # Deletar do banco
        conn = conectar_banco()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM noticiasfuria WHERE id_noticia = %s", (id,))
        conn.commit()

        if cursor.rowcount == 0:
            return {"error": "Notícia com o ID especificado não foi encontrada no banco de dados."}

        cursor.close()
        conn.close()

        # Extrair nome da imagem da URL
        imagem_nome = os.path.basename(urlparse(imagem).path)

        # Caminho completo do arquivo
        caminho_imagem = os.path.join("imgs", imagem_nome)

        # Deletar imagem do sistema de arquivos
        if os.path.exists(caminho_imagem):
            os.remove(caminho_imagem)
            return {"success": "Notícia e imagem removidas com sucesso."}
        else:
            return {"error": "Notícia removida do banco, mas a imagem não foi encontrada no servidor."}

    except Exception as e:
        return {"error": f"Ocorreu um erro ao deletar a notícia: {str(e)}"}
