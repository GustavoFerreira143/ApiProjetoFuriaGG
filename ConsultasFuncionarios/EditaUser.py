import mysql.connector
from dotenv import load_dotenv
import os
import bcrypt

# Carregar variáveis de ambiente
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

def atualizar_funcionario(id, nome, email, senha, permisaoUser, desativado):
    try:
        conn = conectar_banco()
        cursor = conn.cursor()

        # Hash da nova senha
        senha_hash = bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        query = """
            UPDATE funcionariosfuria 
            SET nome = %s, email = %s, senha = %s, permisaoUser = %s, desativado = %s 
            WHERE id_func = %s
        """
        valores = (nome, email, senha_hash, permisaoUser, desativado, id)
        cursor.execute(query, valores)
        conn.commit()

        if cursor.rowcount == 0:
            return {'message': 'Nenhum funcionário atualizado. ID pode não existir.'}, 404

        return {'message': 'Funcionário atualizado com sucesso.'}, 200

    except mysql.connector.Error as err:
        return {'message': f'Erro ao atualizar funcionário: {err}'}, 500

    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()
