import mysql.connector
from mysql.connector import IntegrityError
from dotenv import load_dotenv
import os
import bcrypt 

# Carregar variáveis de ambiente
load_dotenv()

DB_HOST = os.getenv('DB_HOST')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_NAME = os.getenv('DB_NAME')


def inserir_funcionario_furia(nome, email, senha, tipo):
    try:
        # Gerar hash da senha
        senha_bytes = senha.encode('utf-8')  # Converte para bytes
        hashed_senha = bcrypt.hashpw(senha_bytes, bcrypt.gensalt())

        conexao = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        cursor = conexao.cursor()

        query = "INSERT INTO funcionariosfuria (nome, email, senha, permisaoUser) VALUES (%s, %s, %s, %s)"
        cursor.execute(query, (nome, email, hashed_senha.decode('utf-8'), tipo))  # decode para armazenar como string
        conexao.commit()

        return 200

    except IntegrityError as err:
        return 400

    except mysql.connector.Error as err:
        return 500

    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conexao' in locals():
            conexao.close()
