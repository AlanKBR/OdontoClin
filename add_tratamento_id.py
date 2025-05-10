import sqlite3

# Connect to the database
conn = sqlite3.connect("instance/app.db")
cursor = conn.cursor()

try:
    # Check if tratamento_id column exists
    cursor.execute("PRAGMA table_info(procedimento)")
    columns = cursor.fetchall()
    column_names = [col[1] for col in columns]

    print(f"Current columns: {column_names}")

    # Add tratamento_id if it doesn't exist
    if "tratamento_id" not in column_names:
        print("Adding tratamento_id column...")
        cursor.execute("ALTER TABLE procedimento ADD COLUMN tratamento_id INTEGER")
        conn.commit()
        print("Column added successfully!")
    else:
        print("tratamento_id column already exists")

    # Verify column addition
    cursor.execute("PRAGMA table_info(procedimento)")
    columns = cursor.fetchall()
    column_names = [col[1] for col in columns]
    print(f"Final columns: {column_names}")

except sqlite3.Error as e:
    print(f"Error: {e}")
finally:
    conn.close()
