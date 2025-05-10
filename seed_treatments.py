from app import create_app
from app.extensions import db
from app.models.tratamento import CategoriaTratamento, Tratamento

app = create_app()


def seed_dental_procedures():
    """
    Seed the database with common dental categories and procedures
    """
    with app.app_context():
        # Create categories
        categories = [
            {
                "name": "Clínica Geral",
                "description": "Procedimentos básicos e de rotina",
                "treatments": [
                    {"name": "Consulta / Avaliação", "price": 100.00, "duration": "30min"},
                    {"name": "Limpeza Dental (Profilaxia)", "price": 150.00, "duration": "45min"},
                    {"name": "Aplicação de Flúor", "price": 80.00, "duration": "20min"},
                    {
                        "name": "Restauração de Resina (1 face)",
                        "price": 120.00,
                        "duration": "40min",
                    },
                    {
                        "name": "Restauração de Resina (2 faces)",
                        "price": 150.00,
                        "duration": "50min",
                    },
                    {
                        "name": "Restauração de Resina (3 faces)",
                        "price": 180.00,
                        "duration": "60min",
                    },
                    {
                        "name": "Restauração de Amálgama (1 face)",
                        "price": 110.00,
                        "duration": "40min",
                    },
                    {
                        "name": "Restauração de Amálgama (2 faces)",
                        "price": 140.00,
                        "duration": "50min",
                    },
                    {"name": "Exame Radiográfico", "price": 50.00, "duration": "15min"},
                ],
            },
            {
                "name": "Periodontia",
                "description": "Tratamento das gengivas e estruturas de suporte dos dentes",
                "treatments": [
                    {
                        "name": "Raspagem e Alisamento Radicular (por arcada)",
                        "price": 180.00,
                        "duration": "60min",
                    },
                    {"name": "Tratamento de Gengivite", "price": 150.00, "duration": "45min"},
                    {"name": "Cirurgia Periodontal", "price": 400.00, "duration": "90min"},
                    {"name": "Enxerto Gengival", "price": 600.00, "duration": "120min"},
                    {"name": "Manutenção Periodontal", "price": 150.00, "duration": "40min"},
                ],
            },
            {
                "name": "Endodontia",
                "description": "Tratamentos de canal",
                "treatments": [
                    {
                        "name": "Tratamento de Canal - Incisivos e Caninos",
                        "price": 500.00,
                        "duration": "90min",
                    },
                    {
                        "name": "Tratamento de Canal - Pré-Molares",
                        "price": 600.00,
                        "duration": "120min",
                    },
                    {
                        "name": "Tratamento de Canal - Molares",
                        "price": 800.00,
                        "duration": "150min",
                    },
                    {"name": "Retratamento Endodôntico", "price": 900.00, "duration": "120min"},
                ],
            },
            {
                "name": "Cirurgia",
                "description": "Procedimentos cirúrgicos odontológicos",
                "treatments": [
                    {"name": "Extração Simples", "price": 180.00, "duration": "45min"},
                    {
                        "name": "Extração de Dente Incluso (Siso)",
                        "price": 450.00,
                        "duration": "90min",
                    },
                    {"name": "Biópsia", "price": 300.00, "duration": "60min"},
                    {"name": "Frenectomia", "price": 350.00, "duration": "60min"},
                ],
            },
            {
                "name": "Ortodontia",
                "description": "Correção do alinhamento dos dentes e maxilares",
                "treatments": [
                    {"name": "Avaliação Ortodôntica", "price": 150.00, "duration": "45min"},
                    {
                        "name": "Aparelho Fixo Metálico (instalação)",
                        "price": 1200.00,
                        "duration": "120min",
                    },
                    {
                        "name": "Aparelho Fixo Estético (instalação)",
                        "price": 2500.00,
                        "duration": "120min",
                    },
                    {
                        "name": "Alinhadores Transparentes (por arcada)",
                        "price": 4000.00,
                        "duration": "60min",
                    },
                    {"name": "Manutenção Ortodôntica", "price": 180.00, "duration": "30min"},
                    {"name": "Documentação Ortodôntica", "price": 350.00, "duration": "30min"},
                ],
            },
            {
                "name": "Prótese Dentária",
                "description": "Reabilitação com próteses dentárias",
                "treatments": [
                    {"name": "Coroa Provisória", "price": 200.00, "duration": "60min"},
                    {"name": "Coroa de Porcelana", "price": 900.00, "duration": "90min"},
                    {"name": "Coroa de Zircônia", "price": 1200.00, "duration": "90min"},
                    {"name": "Prótese Parcial Removível", "price": 800.00, "duration": "120min"},
                    {"name": "Prótese Total", "price": 1000.00, "duration": "120min"},
                    {"name": "Faceta de Porcelana", "price": 1100.00, "duration": "90min"},
                ],
            },
            {
                "name": "Implantodontia",
                "description": "Implantes dentários",
                "treatments": [
                    {"name": "Avaliação para Implante", "price": 200.00, "duration": "45min"},
                    {
                        "name": "Implante Dentário (unitário)",
                        "price": 2500.00,
                        "duration": "120min",
                    },
                    {"name": "Enxerto Ósseo", "price": 800.00, "duration": "90min"},
                    {"name": "Coroa sobre Implante", "price": 1200.00, "duration": "90min"},
                    {"name": "Manutenção de Implante", "price": 180.00, "duration": "45min"},
                ],
            },
            {
                "name": "Odontopediatria",
                "description": "Tratamentos odontológicos para crianças",
                "treatments": [
                    {"name": "Consulta Infantil", "price": 120.00, "duration": "30min"},
                    {"name": "Aplicação de Selante", "price": 90.00, "duration": "30min"},
                    {"name": "Pulpotomia", "price": 180.00, "duration": "60min"},
                    {"name": "Restauração em Dente Decíduo", "price": 130.00, "duration": "45min"},
                    {"name": "Coroa de Aço", "price": 200.00, "duration": "60min"},
                    {"name": "Mantenedor de Espaço", "price": 250.00, "duration": "60min"},
                ],
            },
            {
                "name": "Estética Dental",
                "description": "Procedimentos para melhoria da estética do sorriso",
                "treatments": [
                    {
                        "name": "Clareamento a Laser (consultório)",
                        "price": 900.00,
                        "duration": "120min",
                    },
                    {
                        "name": "Clareamento Caseiro (com moldeira)",
                        "price": 500.00,
                        "duration": "45min",
                    },
                    {
                        "name": "Lentes de Contato Dental (unidade)",
                        "price": 1500.00,
                        "duration": "90min",
                    },
                    {"name": "Harmonização Orofacial", "price": 1200.00, "duration": "90min"},
                ],
            },
        ]

        print("Iniciando cadastro de categorias e tratamentos odontológicos...")

        for cat in categories:
            print(f"Cadastrando categoria: {cat['name']}")
            # Check if the category already exists
            existing_category = CategoriaTratamento.query.filter_by(nome=cat["name"]).first()

            if not existing_category:
                category = CategoriaTratamento(nome=cat["name"], descricao=cat["description"])
                db.session.add(category)
                db.session.commit()
            else:
                category = existing_category
                print(f"  Categoria já existente: {cat['name']}")

            # Add treatments to the category
            for treatment in cat["treatments"]:
                # Check if this treatment already exists in the category
                existing_treatment = Tratamento.query.filter_by(
                    categoria_id=category.id, nome=treatment["name"]
                ).first()

                if not existing_treatment:
                    print(f"  Cadastrando tratamento: {treatment['name']}")
                    new_treatment = Tratamento(
                        categoria_id=category.id,
                        nome=treatment["name"],
                        descricao="",
                        preco=treatment["price"],
                        duracao_estimada=treatment["duration"],
                        ativo=True,
                    )
                    db.session.add(new_treatment)
                else:
                    print(f"  Tratamento já existente: {treatment['name']}")

            db.session.commit()

        print("Cadastro de categorias e tratamentos concluído com sucesso!")


if __name__ == "__main__":
    seed_dental_procedures()
