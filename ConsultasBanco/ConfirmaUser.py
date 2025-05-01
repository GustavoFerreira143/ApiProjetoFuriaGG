import mysql.connector
from dotenv import load_dotenv
import os

# Carregar variáveis de ambiente
load_dotenv()

DB_HOST = os.getenv('DB_HOST')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_NAME = os.getenv('DB_NAME')

def ConfirmaDadosUser(id_token, token, email_ref):
    try:
        # Conexão com o banco de dados
        conn = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        cursor = conn.cursor()

        # Consulta para verificar se existe um registro com os três dados
        query = """
            SELECT COUNT(*) FROM tokenuser
            WHERE id_token = %s AND token = %s AND email_ref = %s
        """
        cursor.execute(query, (id_token, token, email_ref))
        resultado = cursor.fetchone()

        # Verifica se encontrou um registro correspondente
        if resultado and resultado[0] > 0:
            return True
        else:
            return False

    except mysql.connector.Error as err:
        print(f"Erro de banco de dados: {err}")
        return False

    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()