import mysql.connector
from dotenv import load_dotenv
import os

# Carregar variáveis de ambiente
load_dotenv()

DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')  # nova variável
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_NAME = os.getenv('DB_NAME')

def recebe_noticias():
    try:
        conn = mysql.connector.connect(
            host=DB_HOST,
            port=int(DB_PORT) if DB_PORT else 3306,  # usa a porta se definida
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT id_noticia, img_noticia, texto_noticia FROM noticiasfuria ORDER BY id_noticia DESC")
        resultados = cursor.fetchall()

        if not resultados:
            return {'error': 'Nenhuma notícia encontrada'}

        noticias_formatadas = []
        for item in resultados:
            imagem = item['img_noticia']
            texto = item['texto_noticia'] or 'Sem Texto Anexado'
            id = item['id_noticia']
            # Concatena o caminho público
            imagem_url = f"https://web-production-7ea7.up.railway.app/imgs/{imagem}"

            noticias_formatadas.append({
                'imagem': imagem_url,
                'mensagem': texto,
                'id': id
            })

        return {'success': True, 'noticias': noticias_formatadas}

    except Exception as e:
        return {'error': str(e)}

    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()