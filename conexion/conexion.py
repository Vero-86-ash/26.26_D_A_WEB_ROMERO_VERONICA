import os
import psycopg2

def get_db_connection():
    try:
        # 1. Busca la URL de Render (variable de entorno en la nube)
        database_url = os.environ.get('DATABASE_URL')
        
        if database_url:
            # Conexión directa a Render mediante su URL con SSL obligatorio
            conn = psycopg2.connect(database_url, sslmode='require')
        else:
            # 2. Conexión local alternativa mientras desarrollas en tu PC
            # (o puedes pegar directamente tu External Database URL de Render aquí)
            RENDER_EXTERNAL_URL = "TU_EXTERNAL_DATABASE_URL_DE_RENDER_AQUI"
            
            if RENDER_EXTERNAL_URL and not RENDER_EXTERNAL_URL.startswith("TU_EXTERNAL"):
                conn = psycopg2.connect(RENDER_EXTERNAL_URL, sslmode='require')
            else:
                conn = psycopg2.connect(
                    host="localhost",
                    database="barberia_hernandez_db",
                    user="postgres",
                    password="Cristian1986@",
                    port="5432"
                )
        return conn
    except psycopg2.Error as e:
        print(f"Error conectando a la base de datos: {e}")
        return None
    