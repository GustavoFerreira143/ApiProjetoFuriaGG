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

def obter_usuarios_por_estado():
    conexao = conectar_banco()
    cursor = conexao.cursor()

    try:
        cursor.execute("""
            SELECT estado, COUNT(*) AS quantidade
            FROM fansfuria
            GROUP BY estado
            ORDER BY quantidade DESC;
        """)
        resultados = cursor.fetchall()

        dados = []
        for estado, quantidade in resultados:
            dados.append({
                "estado": estado,
                "Quantidade": quantidade
            })

        return dados

    except mysql.connector.Error as err:
        print(f"Erro ao buscar dados: {err}")
        return []

    finally:
        cursor.close()
        conexao.close()


def obter_distribuicao_idades():
    conexao = conectar_banco()
    cursor = conexao.cursor()

    try:
        cursor.execute("""
            SELECT 
                CASE
                    WHEN idade BETWEEN 0 AND 9 THEN '0-9'
                    WHEN idade BETWEEN 10 AND 19 THEN '10-19'
                    WHEN idade BETWEEN 20 AND 29 THEN '20-29'
                    WHEN idade BETWEEN 30 AND 39 THEN '30-39'
                    WHEN idade BETWEEN 40 AND 49 THEN '40-49'
                    WHEN idade BETWEEN 50 AND 59 THEN '50-59'
                    ELSE '60+'
                END AS faixa_etaria,
                COUNT(*) AS quantidade
            FROM fansFuria
            GROUP BY faixa_etaria
            ORDER BY faixa_etaria;
        """)
        resultados = cursor.fetchall()

        dados = []
        for faixa, quantidade in resultados:
            dados.append({
                "faixa_etaria": faixa,
                "Quantidade": quantidade
            })

        return dados

    except mysql.connector.Error as err:
        print(f"Erro ao buscar dados de idade: {err}")
        return []

    finally:
        cursor.close()
        conexao.close()


def obter_interesse_em_comp():
    conexao = conectar_banco()
    cursor = conexao.cursor()

    try:
        cursor.execute("""
            SELECT 
                interesseEmComp,
                COUNT(*) AS quantidade
            FROM fansfuria
            GROUP BY interesseEmComp;
        """)
        resultados = cursor.fetchall()

        dados = []
        for interesse, quantidade in resultados:
            dados.append({
                "interesseEmComp": "Sim" if interesse else "Não",
                "Quantidade": quantidade
            })

        return dados

    except mysql.connector.Error as err:
        print(f"Erro ao buscar interesse em competições: {err}")
        return []

    finally:
        cursor.close()
        conexao.close()


def obter_interesse_em_catalogo():
    conexao = conectar_banco()
    cursor = conexao.cursor()

    try:
        cursor.execute("""
            SELECT 
                interesseCatalogo,
                COUNT(*) AS quantidade
            FROM fansfuria
            GROUP BY interesseCatalogo;
        """)
        resultados = cursor.fetchall()

        dados = []
        for interesse, quantidade in resultados:
            dados.append({
                "interesseCatalogo": "Sim" if interesse else "Não",
                "Quantidade": quantidade
            })

        return dados

    except mysql.connector.Error as err:
        print(f"Erro ao buscar interesse em catálogo: {err}")
        return []

    finally:
        cursor.close()
        conexao.close()


def obter_fans_receber_promocoes():
    conexao = conectar_banco()
    cursor = conexao.cursor()

    try:
        cursor.execute("""
            SELECT 
                receberPromo,
                COUNT(*) AS quantidade
            FROM fansfuria
            GROUP BY receberPromo;
        """)
        resultados = cursor.fetchall()

        dados = []
        for deseja_receber, quantidade in resultados:
            dados.append({
                "receberPromo": "Sim" if deseja_receber else "Não",
                "Quantidade": quantidade
            })

        return dados

    except mysql.connector.Error as err:
        print(f"Erro ao buscar dados sobre promoções: {err}")
        return []

    finally:
        cursor.close()
        conexao.close()


def obter_fans_por_rede_social():
    conexao = conectar_banco()
    cursor = conexao.cursor()

    try:
        cursor.execute("""
            SELECT 
                redeSocial,
                COUNT(*) AS quantidade
            FROM fansfuria
            GROUP BY redeSocial;
        """)
        resultados = cursor.fetchall()

        dados = []
        for rede_social, quantidade in resultados:
            dados.append({
                "redeSocial": rede_social,
                "Quantidade": quantidade
            })

        return dados

    except mysql.connector.Error as err:
        print(f"Erro ao buscar dados por rede social: {err}")
        return []

    finally:
        cursor.close()
        conexao.close()


def obter_rank_jogos_mais_amados():
    conexao = conectar_banco()
    cursor = conexao.cursor()

    # Ordem predefinida dos jogos
    ordem_jogos = [
        'CS2', 'PUBG', 'LOL', 'R6', 'Valorant', 'RocketLeague', 'Apex',
        'PUBG Mobile', 'Free Fire', 'Fifa', 'Kings League', 'Furia Redram', 'Outros'
    ]

    try:
        cursor.execute("""
            SELECT 
                nomeJogo,
                COUNT(*) AS quantidade
            FROM jogosfavoritos
            GROUP BY nomeJogo;
        """)
        resultados = cursor.fetchall()

        # Converter resultados para dicionário
        contagem_jogos = {jogo: 0 for jogo in ordem_jogos}
        for nome_jogo, quantidade in resultados:
            if nome_jogo in contagem_jogos:
                contagem_jogos[nome_jogo] = quantidade
            else:
                contagem_jogos['Outros'] += quantidade

        # Ordenar do menos amado ao mais amado
        rank = sorted(contagem_jogos.items(), key=lambda x: x[1])

        # Formatar para saída com dicionários
        dados_formatados = [
            {"jogo": jogo, "Quantidade": qtd}
            for jogo, qtd in rank
        ]

        return dados_formatados

    except mysql.connector.Error as err:
        print(f"Erro ao buscar ranking de jogos: {err}")
        return []

    finally:
        cursor.close()
        conexao.close()

