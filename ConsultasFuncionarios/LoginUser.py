import mysql.connector
import jwt
import datetime
import bcrypt
from dotenv import load_dotenv
import os

# Carregar variáveis de ambiente
load_dotenv()

DB_HOST = os.getenv('DB_HOST')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_NAME = os.getenv('DB_NAME')
JWT_SECRET = os.getenv('JWT_SECRET')  # Use uma variável de ambiente para o segredo também

def conectar_banco():
    return mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )

def autenticar_usuario(email, senha):
    try:
        conexao = conectar_banco()
        cursor = conexao.cursor(dictionary=True)

        query = """
            SELECT id_func, desativado, permisaoUser, senha 
            FROM funcionariosfuria 
            WHERE email = %s
        """
        cursor.execute(query, (email,))
        resultado = cursor.fetchone()

        if resultado:
            senha_hash = resultado['senha']

            # Verifica se a senha fornecida confere com o hash
            if not bcrypt.checkpw(senha.encode('utf-8'), senha_hash.encode('utf-8')):
                return False, 400, 'Credenciais inválidas'

            if resultado.get('desativado'):
                return False, 401, 'Usuário desativado'

            # Usuário autenticado
            id_func = resultado['id_func']
            permissao_user = resultado['permisaoUser']

            payload = {
                'id_func': id_func,
                'permissaoUser': permissao_user,
                'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=2)
            }
            token = jwt.encode(payload, JWT_SECRET, algorithm='HS256')

            return True, 200, {
                'token': token,
                'permissaoUser': permissao_user
            }

        else:
            return False, 400, 'Usuário não encontrado'

    except Exception as e:
        print(f'Erro ao autenticar usuário: {e}')
        return False, 500, 'Erro interno no servidor'

    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conexao' in locals():
            conexao.close()
