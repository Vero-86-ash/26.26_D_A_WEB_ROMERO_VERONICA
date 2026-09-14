import psycopg2

def get_db_connection():
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="barberia_hernandez_db", 
            user="postgres", 
            password="Cristian1986@",  # <--- Tu nueva contraseña real
            port="5432"
        )
        return conn
    except psycopg2.Error as e:
        print(f"Error conectando a PostgreSQL: {e}")
        return None