from utils.database import get_database_connection

connection = get_database_connection()

if connection is not None and connection.is_connected():
    print("✅ Database connected successfully!")
    connection.close()
else:
    print("❌ Database connection failed.")