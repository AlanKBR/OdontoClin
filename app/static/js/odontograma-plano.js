/* global Engine */

/**
 * Visualizador de odontograma para o plano de tratamento
 * Este script carrega o odontograma do paciente no plano de tratamento
 */
document.addEventListener('DOMContentLoaded', function () {
  // Verificar se o canvas do plano existe nesta página
  const canvasElement = document.getElementById('planoCanvas');
  if (!canvasElement) {
    console.log('Canvas do plano não encontrado');
    return;
  }

  console.log('Inicializando odontograma no plano de tratamento');

  // Inicializar o engine
  const engine = new Engine();
  engine.setCanvas(canvasElement);
  engine.init();

  // Modo somente visualização
  engine.setViewMode(true);

  // Buscar dados do odontograma do paciente
  const pacienteId = canvasElement.getAttribute('data-paciente-id');
  if (!pacienteId) {
    console.log('ID do paciente não encontrado');
    return;
  }

  console.log('Buscando odontograma para o paciente ID:', pacienteId);

  // Configurar informações do paciente a partir de atributos data do canvas
  engine.loadPatientData(
    canvasElement.getAttribute('data-dentista') || '',
    canvasElement.getAttribute('data-paciente-nome') || '',
    pacienteId || '',
    canvasElement.getAttribute('data-plano-id') || '',
    canvasElement.getAttribute('data-data') || '',
    canvasElement.getAttribute('data-dentista-responsavel') || '',
    canvasElement.getAttribute('data-observacoes') || '',
    ''
  );

  fetch(`/paciente/${pacienteId}/get_ultimo_odontograma`)
    .then(response => {
      console.log('Resposta recebida do endpoint do odontograma');
      return response.json();
    })
    .then(data => {
      console.log('Dados recebidos:', data);

      if (data.success && data.dados) {
        try {
          console.log('Carregando dados do odontograma');
          const odontogramaData = JSON.parse(data.dados);
          engine.loadOdontogramaData(odontogramaData);
          console.log('Odontograma carregado com sucesso');
        } catch (error) {
          console.error('Erro ao processar odontograma:', error);
        }
      } else {
        console.log('Nenhum odontograma encontrado para este paciente');
      }
    })
    .catch(error => {
      console.error('Erro ao buscar odontograma:', error);
    });
});

