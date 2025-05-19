/* global Engine */

// Inicializa o odontograma em modo somente visualização
document.addEventListener('DOMContentLoaded', function () {
  const canvas = document.getElementById('canvas');
  if (canvas) {
    const engine = new Engine();
    engine.setCanvas(canvas);
    engine.init();

    // Desabilitar interatividade
    canvas.style.pointerEvents = 'none';

    // Carregar dados do paciente
    if (window.odontogramaData) {
      try {
        // Exibir os dados do odontograma
        const patientData = window.odontogramaData.patient || {};

        // Carregar os dados de marcação do odontograma
        if (window.odontogramaData.dados) {
          engine.loadOdontogramaData(window.odontogramaData.dados);
        }

        // Configurar informações do paciente
        engine.loadPatientData(
          patientData.dentista || '',
          patientData.pacienteNome || '',
          patientData.pacienteId || '',
          patientData.planoId || '',
          patientData.data || '',
          patientData.dentistaResponsavel || '',
          patientData.observacoes || '',
          ''
        );
      } catch (error) {
        console.error('Erro ao carregar odontograma:', error);
      }
    }
  }
});

