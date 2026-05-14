from django.db import connection

def update_charset():
    with connection.cursor() as cursor:
        cursor.execute("ALTER DATABASE Blog CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci;")
        cursor.execute("SHOW TABLES;")
        tables = cursor.fetchall()
        for table in tables:
            cursor.execute(f"ALTER TABLE {table[0]} CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
    print("Database charset updated to utf8mb4 successfully.")

update_charset()
