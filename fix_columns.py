import sqlite3

try:
    # Connect to the database
    conn = sqlite3.connect("instance/app.db")
    cursor = conn.cursor()

    # Check if tratamento_id column exists
    cursor.execute("PRAGMA table_info(procedimento)")
    columns = cursor.fetchall()
    column_names = [col[1] for col in columns]

    print(f"Current columns: {column_names}")

    # Add tratamento_id if it doesn't exist
    try:
        print("Adding tratamento_id column...")
        cursor.execute("ALTER TABLE procedimento ADD COLUMN tratamento_id INTEGER")
        conn.commit()
        print("Column added successfully!")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("tratamento_id column already exists")
        else:
            print(f"Error adding column: {e}")

    # Verify column addition
    cursor.execute("PRAGMA table_info(procedimento)")
    columns = cursor.fetchall()
    column_names = [col[1] for col in columns]
    print(f"Final columns: {column_names}")

    # Check for additional required columns
    required_columns = {
        "dentes_selecionados": "TEXT",
        "quadrantes": "VARCHAR(20)",
        "boca_completa": "BOOLEAN DEFAULT 0",
        "tratamento_id": "INTEGER",
    }

    for col_name, col_type in required_columns.items():
        if col_name not in column_names:
            print(f"Adding {col_name} column...")
            try:
                cursor.execute(f"ALTER TABLE procedimento ADD COLUMN {col_name} {col_type}")
                conn.commit()
                print(f"Added {col_name} column successfully")
            except sqlite3.OperationalError as e:
                print(f"Error adding {col_name} column: {e}")

    # Final check
    cursor.execute("PRAGMA table_info(procedimento)")
    columns = cursor.fetchall()
    column_names = [col[1] for col in columns]
    print(f"Final schema: {columns}")

except sqlite3.Error as e:
    print(f"General error: {e}")
finally:
    if "conn" in locals():
        conn.close()
        print("Database connection closed")
