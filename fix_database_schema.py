import os
import sqlite3
import traceback


def main():
    try:
        # Ensure the instance directory exists
        if not os.path.exists("instance"):
            os.makedirs("instance")

        # Connect to the database
        print("Connecting to database...")
        conn = sqlite3.connect("instance/app.db")
        cursor = conn.cursor()

        # Check the current structure
        print("Checking current table structure...")
        cursor.execute("PRAGMA table_info(procedimento)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        print(f"Current columns: {column_names}")

        # Check if 'tratamento_id' column exists
        if "tratamento_id" not in column_names:
            print("Adding 'tratamento_id' column to procedimento table...")
            try:
                cursor.execute(
                    "ALTER TABLE procedimento ADD COLUMN tratamento_id INTEGER "
                    "REFERENCES tratamento(id)"
                )
                conn.commit()
                print("Column 'tratamento_id' added successfully!")
            except sqlite3.Error as e:
                print(f"Error adding column 'tratamento_id': {e}")
        else:
            print("Column 'tratamento_id' already exists.")

        # Define all required columns from model
        model_columns = [
            "id",
            "plano_id",
            "tratamento_id",
            "descricao",
            "dente",
            "dentes_selecionados",
            "quadrantes",
            "boca_completa",
            "valor",
            "status",
            "data_prevista",
            "data_realizado",
            "observacoes",
        ]

        # Add any missing columns
        for col in model_columns:
            if col not in column_names and col != "id" and col != "tratamento_id":
                print(f"Adding missing column '{col}' to procedimento table...")

                # Determine column type based on model definition
                if col in ("dentes_selecionados", "observacoes"):
                    col_type = "TEXT"
                elif col == "boca_completa":
                    col_type = "BOOLEAN DEFAULT 0"
                elif col == "valor":
                    col_type = "FLOAT DEFAULT 0.0"
                elif col in ("data_prevista", "data_realizado"):
                    col_type = "DATE"
                elif col == "quadrantes":
                    col_type = "VARCHAR(20)"
                else:
                    col_type = "VARCHAR(100)"

                try:
                    cursor.execute(f"ALTER TABLE procedimento ADD COLUMN {col} {col_type}")
                    conn.commit()
                    print(f"Column '{col}' added successfully!")
                except sqlite3.Error as e:
                    print(f"Error adding column '{col}': {e}")

        # Check for the 'valoor' column (typo)
        if "valoor" in column_names and "valor" not in column_names:
            print("Found 'valoor' column - fixing to 'valor'...")

            try:
                # Create a new table with the correct schema
                cursor.execute(
                    """
                CREATE TABLE procedimento_new (
                    id INTEGER PRIMARY KEY,
                    plano_id INTEGER NOT NULL,
                    tratamento_id INTEGER,
                    descricao VARCHAR(200) NOT NULL,
                    dente VARCHAR(100),
                    dentes_selecionados TEXT,
                    quadrantes VARCHAR(20),
                    boca_completa BOOLEAN DEFAULT 0,
                    valor FLOAT DEFAULT 0.0,
                    status VARCHAR(20),
                    data_prevista DATE,
                    data_realizado DATE,
                    observacoes TEXT,
                    FOREIGN KEY (plano_id) REFERENCES plano_tratamento(id),
                    FOREIGN KEY (tratamento_id) REFERENCES tratamento(id)
                )
                """
                )

                # Copy data from old table to new table, fixing column name
                cursor.execute(
                    """
                INSERT INTO procedimento_new
                (id, plano_id, descricao, dente, valor,
                status, data_prevista, data_realizado, observacoes)
                SELECT id, plano_id, descricao, dente,
                valoor, status, data_prevista,
                data_realizado, observacoes
                FROM procedimento
                """
                )

                # Drop old table and rename new one
                cursor.execute("DROP TABLE procedimento")
                cursor.execute("ALTER TABLE procedimento_new RENAME TO procedimento")

                conn.commit()
                print("Successfully fixed 'valoor' to 'valor'")
            except sqlite3.Error as e:
                print(f"Error fixing 'valoor' column: {e}")

        # Final check of the table structure
        cursor.execute("PRAGMA table_info(procedimento)")
        final_columns = cursor.fetchall()
        print("\nFinal procedimento table structure:")
        for col in final_columns:
            print(col)

        conn.close()
        print("\nDatabase schema update completed.")

    except (sqlite3.Error, OSError) as e:
        print(f"A database or file system error occurred: {e}")
        traceback.print_exc()


if __name__ == "__main__":
    main()
