import mysql.connector
from dotenv import load_dotenv
import os

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

def retornaUsers(filtros=None, pagina=0):
    try:
        conn = conectar_banco()
        cursor = conn.cursor(dictionary=True)

        limite = 10
        offset = pagina * limite

        base_query = """
            SELECT f.*, j.id_jogo, j.nomeJogo
            FROM fansfuria f
            LEFT JOIN jogosfavoritos j ON f.id_fa = j.id_fa
        """
        where_clauses = []
        params = []

        if filtros:
            if 'estado' in filtros and filtros['estado']:
                where_clauses.append("f.estado = %s")
                params.append(filtros['estado'].upper())

            if 'idadeMin' in filtros and filtros['idadeMin'].isdigit():
                where_clauses.append("f.idade >= %s")
                params.append(int(filtros['idadeMin']))

            if 'idadeMax' in filtros and filtros['idadeMax'].isdigit():
                where_clauses.append("f.idade <= %s")
                params.append(int(filtros['idadeMax']))

            if 'redeSocial' in filtros and filtros['redeSocial']:
                where_clauses.append("f.redeSocial = %s")
                params.append(filtros['redeSocial'])

            if 'interesseEmComp' in filtros and filtros['interesseEmComp'] != '':
                where_clauses.append("f.interesseEmComp = %s")
                params.append(filtros['interesseEmComp'] == 'true')

            if 'interesseCatalogo' in filtros and filtros['interesseCatalogo'] != '':
                where_clauses.append("f.interesseCatalogo = %s")
                params.append(filtros['interesseCatalogo'] == 'true')

            if 'receberPromo' in filtros and filtros['receberPromo'] != '':
                where_clauses.append("f.receberPromo = %s")
                params.append(filtros['receberPromo'] == 'true')

            if 'somenteVisualizado' in filtros and filtros['somenteVisualizado'] != '':
                where_clauses.append("f.vizualizado = %s")
                params.append(filtros['somenteVisualizado'] == 'true')

        if where_clauses:
            base_query += " WHERE " + " AND ".join(where_clauses)

        base_query += " ORDER BY f.id_fa DESC LIMIT %s OFFSET %s"
        params.extend([limite, offset])

        cursor.execute(base_query, tuple(params))
        resultados = cursor.fetchall()

        usuarios = {}
        for row in resultados:
            id_fa = row['id_fa']
            if id_fa not in usuarios:
                infosdofa = {
                    key: row[key] for key in row if not key.startswith('id_jogo') and not key.startswith('nomeJogo')
                }
                usuarios[id_fa] = {
                    'infosdofa': infosdofa,
                    'jogosfavoritos': []
                }

            if row['id_jogo']:
                usuarios[id_fa]['jogosfavoritos'].append({
                    'nome_jogo': row['nomeJogo']
                })

        resultado_final = list(usuarios.values())
        return resultado_final, 200

    except mysql.connector.Error as err:
        return {'message': f'Erro ao buscar usuários: {err}'}, 500

    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()



