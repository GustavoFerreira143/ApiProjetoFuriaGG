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

def conectar_banco():
    return mysql.connector.connect(
        host=DB_HOST,
        port=int(DB_PORT) if DB_PORT else 3306,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )

def obter_todos_usuarios(filtro=None, pagina=0):
    try:
        conexao = conectar_banco()
        cursor = conexao.cursor(dictionary=True)

        limite = 10
        offset = pagina * limite

        if filtro:
            query = """
                SELECT * FROM funcionariosfuria
                WHERE nome LIKE %s OR email LIKE %s
                ORDER BY id_func DESC
                LIMIT %s OFFSET %s
            """
            like_filtro = f"%{filtro}%"
            cursor.execute(query, (like_filtro, like_filtro, limite, offset))
        else:
            query = """
                SELECT * FROM funcionariosfuria
                ORDER BY id_func DESC
                LIMIT %s OFFSET %s
            """
            cursor.execute(query, (limite, offset))

        resultado = cursor.fetchall()

        if not resultado:
            # Nenhum dado encontrado nessa página
            return {"erro": "sem_mais_dados"}

        return resultado

    except Exception as e:
        print(f"Erro ao buscar usuários: {e}")
        return None

    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conexao' in locals():
            conexao.close()

