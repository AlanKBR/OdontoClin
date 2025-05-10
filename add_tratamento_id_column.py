from app import create_app
from app.extensions import db

app = create_app()

with app.app_context():
    # Add the missing column to the procedimento table
    db.session.execute(
        "ALTER TABLE procedimento ADD COLUMN tratamento_id INTEGER REFERENCES tratamento(id)"
    )
    db.session.commit()
    print("Successfully added tratamento_id column to procedimento table!")
