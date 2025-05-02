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

def gerar_dados_personalizados_grafico(tabela, campo_agrupamento, condicoes=None):
    """
    Gera dados personalizados para gráficos com base na tabela e campo informados.

    Parâmetros:
    - tabela: str - nome da tabela (ex: 'fansFuria')
    - campo_agrupamento: str - campo pelo qual os dados serão agrupados (ex: 'estado', 'redeSocial', etc.)
    - condicoes: str (opcional) - cláusulas adicionais de filtro SQL (ex: "idade > 18 AND estado = 'SP'")

    Retorna:
    - lista de dicionários com os valores agrupados e suas quantidades
    """
    conexao = conectar_banco()
    cursor = conexao.cursor()

    try:
        query = f"""
            SELECT {campo_agrupamento}, COUNT(*) AS quantidade
            FROM {tabela}
        """

        if condicoes:
            query += f" WHERE {condicoes}"

        query += f" GROUP BY {campo_agrupamento} ORDER BY quantidade DESC"

        cursor.execute(query)
        resultados = cursor.fetchall()

        dados_formatados = [
            {campo_agrupamento: linha[0], "quantidade": linha[1]}
            for linha in resultados
        ]

        return dados_formatados

    except mysql.connector.Error as err:
        print(f"Erro ao executar consulta personalizada: {err}")
        return []

    finally:
        cursor.close()
        conexao.close()

