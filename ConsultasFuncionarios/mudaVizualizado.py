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
    

def altera_visualizado(id_fa):
    try:
        # Estabelecer conexão com o banco de dados
        conn = conectar_banco()
        cursor = conn.cursor()

        # Consulta SQL para alterar o campo 'visualizado' para True
        query = "UPDATE fansfuria SET vizualizado = TRUE WHERE id_fa = %s"
        cursor.execute(query, (id_fa,))

        # Commit da transação para salvar as alterações
        conn.commit()

        # Verificar se algum registro foi afetado
        if cursor.rowcount > 0:
            return "sucesso"
        else:
            return "erro"

    except mysql.connector.Error as err:
        print(f"Erro ao alterar o registro: {err}")
        return "erro"

    finally:
        # Fechar cursor e conexão
        cursor.close()
        conn.close()