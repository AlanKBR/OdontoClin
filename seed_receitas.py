"""
Script para popular o banco de dados de receitas com medicamentos comuns em odontologia.
"""

import os
import sys

from app import create_app
from app.extensions import db
from app.models.receita import Medicamento

# Adiciona o diretório raiz ao path para que os imports funcionem
sys.path.append(os.path.abspath(os.path.dirname(__file__)))


# Medicamentos comuns em odontologia com suas posologias
MEDICAMENTOS = [
    {
        "nome": "Amoxicilina",
        "principio_ativo": "Amoxicilina",
        "concentracao": "500mg",
        "forma_farmaceutica": "Cápsula",
        "posologia_padrao": "Tomar 1 cápsula de 8 em 8 horas por 7 dias.\nIngerir com água e de preferência após as refeições.",
        "via_administracao": "Oral",
        "indicacoes": "Infecções bacterianas, profilaxia de endocardite bacteriana.",
        "contraindicacoes": "Hipersensibilidade a penicilinas, mononucleose infecciosa.",
        "efeitos_colaterais": "Náuseas, vômitos, diarreia, reações alérgicas.",
        "observacoes": "Em caso de esquecimento, tomar assim que lembrar e ajustar o horário das próximas doses.",
        "odontologico": True,
    },
    {
        "nome": "Nimesulida",
        "principio_ativo": "Nimesulida",
        "concentracao": "100mg",
        "forma_farmaceutica": "Comprimido",
        "posologia_padrao": "Tomar 1 comprimido de 12 em 12 horas por 5 dias.\nIngerir após as refeições e com um copo cheio de água.",
        "via_administracao": "Oral",
        "indicacoes": "Dor e inflamação pós-operatória, dor de dente.",
        "contraindicacoes": "Úlcera péptica ativa, insuficiência renal grave, crianças menores de 12 anos.",
        "efeitos_colaterais": "Dispepsia, náuseas, diarreia, elevação de enzimas hepáticas.",
        "observacoes": "Não utilizar por mais de 5 dias sem orientação profissional.",
        "odontologico": True,
    },
    {
        "nome": "Dipirona Sódica",
        "principio_ativo": "Dipirona",
        "concentracao": "500mg",
        "forma_farmaceutica": "Comprimido",
        "posologia_padrao": "Tomar 1 comprimido de 6 em 6 horas em caso de dor.\nNão exceder 4 comprimidos por dia.",
        "via_administracao": "Oral",
        "indicacoes": "Dor e febre.",
        "contraindicacoes": "Alergia aos componentes da fórmula, discrasias sanguíneas.",
        "efeitos_colaterais": "Reações alérgicas, hipotensão, agranulocitose (rara).",
        "observacoes": "Suspender o uso em caso de reações alérgicas ou sangramentos.",
        "odontologico": True,
    },
    {
        "nome": "Ibuprofeno",
        "principio_ativo": "Ibuprofeno",
        "concentracao": "600mg",
        "forma_farmaceutica": "Comprimido",
        "posologia_padrao": "Tomar 1 comprimido de 8 em 8 horas por até 5 dias.\nTomar após as refeições.",
        "via_administracao": "Oral",
        "indicacoes": "Dor, inflamação e edema pós-operatório.",
        "contraindicacoes": "Úlcera péptica, insuficiência renal grave, hipersensibilidade conhecida.",
        "efeitos_colaterais": "Desconforto gástrico, náuseas, dor de cabeça.",
        "observacoes": "Não usar com outros anti-inflamatórios sem orientação.",
        "odontologico": True,
    },
    {
        "nome": "Paracetamol",
        "principio_ativo": "Paracetamol",
        "concentracao": "750mg",
        "forma_farmaceutica": "Comprimido",
        "posologia_padrao": "Tomar 1 comprimido de 6 em 6 horas em caso de dor ou febre.\nNão exceder 4 comprimidos por dia.",
        "via_administracao": "Oral",
        "indicacoes": "Dor leve a moderada, febre.",
        "contraindicacoes": "Doença hepática grave.",
        "efeitos_colaterais": "Hepatotoxicidade em doses excessivas, reações alérgicas (raras).",
        "observacoes": "Seguro para uso em gestantes. Não usar com bebida alcoólica.",
        "odontologico": True,
    },
    {
        "nome": "Amoxicilina + Clavulanato de Potássio",
        "principio_ativo": "Amoxicilina + Ácido Clavulânico",
        "concentracao": "875mg + 125mg",
        "forma_farmaceutica": "Comprimido",
        "posologia_padrao": "Tomar 1 comprimido de 12 em 12 horas por 7 dias.\nTomar com alimentos para reduzir desconforto gastrointestinal.",
        "via_administracao": "Oral",
        "indicacoes": "Infecções bacterianas resistentes à amoxicilina, abcessos odontogênicos.",
        "contraindicacoes": "Hipersensibilidade a penicilinas, histórico de icterícia/disfunção hepática associada a amoxicilina/clavulanato.",
        "efeitos_colaterais": "Diarreia, náuseas, vômitos, candidíase.",
        "observacoes": "Manter hidratação adequada durante o tratamento.",
        "odontologico": True,
    },
    {
        "nome": "Dexametasona",
        "principio_ativo": "Dexametasona",
        "concentracao": "4mg",
        "forma_farmaceutica": "Comprimido",
        "posologia_padrao": "Tomar 1 comprimido de 12 em 12 horas por 3 dias.\nTomar após as refeições.",
        "via_administracao": "Oral",
        "indicacoes": "Controle de edema pós-operatório, reações inflamatórias graves.",
        "contraindicacoes": "Infecções fúngicas sistêmicas, tuberculose ativa, úlcera péptica ativa.",
        "efeitos_colaterais": "Hiperglicemia, retenção hídrica, ganho de peso, hipertensão.",
        "observacoes": "Tratamento de curta duração para minimizar efeitos colaterais. Não interromper abruptamente.",
        "odontologico": True,
    },
    {
        "nome": "Clorexidina",
        "principio_ativo": "Digluconato de Clorexidina",
        "concentracao": "0,12%",
        "forma_farmaceutica": "Solução Bucal",
        "posologia_padrao": "Realizar bochechos com 15ml por 30 segundos, 2 vezes ao dia (manhã e noite).\nNão ingerir. Não se alimentar ou beber por 30 minutos após o uso.",
        "via_administracao": "Tópica Oral",
        "indicacoes": "Antisséptico bucal, prevenção de infecções após procedimentos cirúrgicos bucais, tratamento de gengivite.",
        "contraindicacoes": "Hipersensibilidade aos componentes da fórmula.",
        "efeitos_colaterais": "Manchamento dentário, alteração do paladar, descamação da mucosa oral (raro).",
        "observacoes": "Utilizar após a escovação. Pode manchar os dentes com uso prolongado.",
        "odontologico": True,
    },
    {
        "nome": "Cefalexina",
        "principio_ativo": "Cefalexina",
        "concentracao": "500mg",
        "forma_farmaceutica": "Cápsula",
        "posologia_padrao": "Tomar 1 cápsula de 6 em 6 horas por 7 dias.\nPode ser tomada com ou sem alimentos.",
        "via_administracao": "Oral",
        "indicacoes": "Infecções bacterianas, alternativa para pacientes alérgicos a penicilinas (sem reação anafilática).",
        "contraindicacoes": "Hipersensibilidade a cefalosporinas, história de reação anafilática a penicilinas.",
        "efeitos_colaterais": "Diarreia, náuseas, reações alérgicas.",
        "observacoes": "Completar todo o tratamento mesmo que os sintomas melhorem antes.",
        "odontologico": True,
    },
    {
        "nome": "Metronidazol",
        "principio_ativo": "Metronidazol",
        "concentracao": "400mg",
        "forma_farmaceutica": "Comprimido",
        "posologia_padrao": "Tomar 1 comprimido de 8 em 8 horas por 7 dias.\nTomar durante ou após as refeições.",
        "via_administracao": "Oral",
        "indicacoes": "Infecções anaeróbicas, periodontite, gengivite ulcerativa necrosante.",
        "contraindicacoes": "Primeiro trimestre de gravidez, amamentação, pacientes com distúrbios neurológicos.",
        "efeitos_colaterais": "Gosto metálico, náuseas, coloração escura da urina.",
        "observacoes": "Não ingerir bebida alcoólica durante e por pelo menos 24h após o término do tratamento.",
        "odontologico": True,
    },
]


def seed_receitas():
    """Popula o banco de dados de receitas com dados iniciais."""
    app = create_app()
    with app.app_context():
        # Verifica se já existem medicamentos cadastrados
        if Medicamento.query.count() > 0:
            print("O banco de dados de receitas já possui medicamentos cadastrados.")
            return

        # Adiciona medicamentos
        for med_data in MEDICAMENTOS:
            medicamento = Medicamento(**med_data)
            db.session.add(medicamento)

        # Salva no banco de dados
        db.session.commit()
        print(f"Foram cadastrados {len(MEDICAMENTOS)} medicamentos no banco de dados de receitas.")


if __name__ == "__main__":
    seed_receitas()
