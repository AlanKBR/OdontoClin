/**
 * AI Configuration Panel JavaScript - Modern Interface
 * Unified model management with dashboard and grid view
 */

class AIConfigManager {
    constructor() {
        this.hardwareInfo = null;
        this.availableModels = [];
        this.currentConfig = {};
        this.installedModels = [];
        this.searchResults = [];
        this.allModels = [];
        this.currentView = 'all'; // 'all', 'installed', 'available'
        this.currentFilter = 'all';
        this.isLoading = false;
        this.diskUsage = null;
        this.currentPage = 1;
        this.modelsPerPage = 6;
        
        // Sistema de progresso de download
        this.downloadingModels = new Set();
        this.downloadProgress = {};
        this.downloadIntervals = {};
        
        this.initializeEventListeners();
        this.loadInitialData();
    }
    
    initializeEventListeners() {
        // Status refresh button
        document.getElementById('btn-refresh-status').addEventListener('click', () => {
            this.refreshStatus();
        });
        
        // Configuration form
        document.getElementById('config-form').addEventListener('change', () => {
            this.validateConfiguration();
        });
        
        // Temperature slider
        const temperatureSlider = document.getElementById('temperature');
        temperatureSlider.addEventListener('input', (e) => {
            document.getElementById('temperature-value').textContent = e.target.value;
        });
        
        // Action buttons
        document.getElementById('btn-save-config').addEventListener('click', () => {
            this.saveConfiguration();
        });
        
        document.getElementById('btn-start-ai').addEventListener('click', () => {
            this.startAI();
        });
        
        document.getElementById('btn-stop-ai').addEventListener('click', () => {
            this.stopAI();
        });
        
        // Model management event listeners
        this.initializeModelManagementListeners();
    }
    
    initializeModelManagementListeners() {
        // Smart search functionality
        const searchInput = document.getElementById('model-search-input');
        const searchBtn = document.getElementById('btn-search-models');
        const clearBtn = document.getElementById('btn-clear-search');
        
        if (searchInput) {
            searchInput.addEventListener('input', () => {
                this.debounce(() => {
                    if (searchInput.value.length >= 3 || searchInput.value.length === 0) {
                        this.performSearch();
                    }
                }, 300);
            });
            
            searchInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    this.performSearch();
                }
            });
        }
        
        if (searchBtn) {
            searchBtn.addEventListener('click', () => {
                this.performSearch();
            });
        }
        
        if (clearBtn) {
            clearBtn.addEventListener('click', () => {
                this.clearSearch();
            });
        }
        
        // Filter functionality
        const filterSelect = document.getElementById('search-filter');
        if (filterSelect) {
            filterSelect.addEventListener('change', () => {
                this.currentFilter = filterSelect.value;
                this.performSearch();
            });
        }
        
        // Quick filter tags
        document.querySelectorAll('.filter-tag').forEach(tag => {
            tag.addEventListener('click', () => {
                const filter = tag.dataset.filter;
                this.applyQuickFilter(filter);
            });
        });
        
        // View toggles
        document.querySelectorAll('.view-toggle').forEach(toggle => {
            toggle.addEventListener('click', () => {
                const view = toggle.dataset.view;
                this.switchView(view);
            });
        });
        
        // Dashboard refresh buttons
        const refreshBtn = document.getElementById('btn-refresh-models');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => {
                this.refreshModelData();
            });
        }
        
        const cleanupBtn = document.getElementById('btn-cleanup-cache');
        if (cleanupBtn) {
            cleanupBtn.addEventListener('click', () => {
                this.cleanupCache();
            });
        }
    }
    
    async loadInitialData() {
        this.showLoading('Carregando configurações...', 'Detectando hardware e modelos disponíveis');
        
        try {
            // Load hardware info and models in parallel
            await Promise.all([
                this.loadHardwareInfo(),
                this.loadAvailableModels(),
                this.loadInstalledModels(),
                this.refreshStatus()
            ]);
            
            this.applyRecommendations();
            this.updateDashboard();
            this.renderCurrentView();
            
        } catch (error) {
            console.error('Error loading initial data:', error);
            this.showError('Erro ao carregar configurações iniciais');
        } finally {
            this.hideLoading();
        }
    }
    
    async refreshModelData() {
        this.showLoading('Atualizando modelos...', 'Carregando dados atualizados');
        
        try {
            await Promise.all([
                this.loadInstalledModels(),
                this.loadAvailableModels()
            ]);
            
            this.updateDashboard();
            this.renderCurrentView();
            this.showSuccess('Dados atualizados com sucesso!');
            
        } catch (error) {
            console.error('Error refreshing model data:', error);
            this.showError('Erro ao atualizar dados dos modelos');
        } finally {
            this.hideLoading();
        }
    }
    
    async loadHardwareInfo() {
        try {
            const response = await fetch('/ai/api/hardware-info');
            const data = await response.json();
            
            if (data.success) {
                this.hardwareInfo = data.hardware;
                this.displayHardwareInfo();
            } else {
                throw new Error(data.error || 'Falha na detecção de hardware');
            }
        } catch (error) {
            console.error('Error loading hardware info:', error);
            this.displayHardwareError();
        }
    }
    
    async loadAvailableModels() {
        try {
            const response = await fetch('/ai/api/available-models');
            const data = await response.json();
            
            if (data.success) {
                this.availableModels = data.models;
                this.combineModelData();
                this.displayAvailableModels();
            } else {
                throw new Error(data.error || 'Falha ao carregar modelos');
            }
        } catch (error) {
            console.error('Error loading models:', error);
            this.displayModelsError();
        }
    }
    
    async loadInstalledModels() {
        try {
            const response = await fetch('/ai/api/models/installed');
            const data = await response.json();
            
            if (data.success) {
                this.installedModels = data.models;
                this.diskUsage = data.disk_usage;
                this.combineModelData();
                this.updateDashboard();
            } else {
                throw new Error(data.error || 'Falha ao carregar modelos instalados');
            }
        } catch (error) {
            console.error('Error loading installed models:', error);
            this.displayModelsError();
        }
    }
    
    combineModelData() {
        // Combine installed and available models into a unified list
        const installedNames = new Set(this.installedModels.map(m => m.name));
        
        // Mark installed models
        const markedInstalled = this.installedModels.map(model => ({
            ...model,
            installed: true,
            status: 'installed'
        }));
        
        // Add available models that aren't installed
        const availableOnly = this.availableModels.filter(model => 
            !installedNames.has(model.name)
        ).map(model => ({
            ...model,
            installed: false,
            status: 'available'
        }));
        
        this.allModels = [...markedInstalled, ...availableOnly];
    }
    
    async refreshStatus() {
        try {
            const response = await fetch('/ai/api/status');
            const data = await response.json();
            
            if (data.success) {
                this.updateStatusDisplay(data.status);
            }
        } catch (error) {
            console.error('Error refreshing status:', error);
        }
    }
    
    // ============ Dashboard Methods ============
    
    updateDashboard() {
        this.updateDashboardCards();
        this.updateDiskUsageCard();
    }
    
    updateDashboardCards() {
        // Update installed models count
        const installedCard = document.getElementById('installed-models-count');
        if (installedCard) {
            installedCard.textContent = this.installedModels.length;
        }
        
        // Update available models count
        const availableCard = document.getElementById('available-models-count');
        if (availableCard) {
            availableCard.textContent = this.allModels.filter(m => !m.installed).length;
        }
        
        // Update total models count
        const totalCard = document.getElementById('total-models-count');
        if (totalCard) {
            totalCard.textContent = this.allModels.length;
        }
    }
    
    updateDiskUsageCard() {
        if (!this.diskUsage || this.diskUsage.error) {
            return;
        }
        
        const usedSpace = document.getElementById('disk-used-space');
        const freeSpace = document.getElementById('disk-free-space');
        const usageBar = document.getElementById('disk-usage-bar');
        
        if (usedSpace) {
            const used = this.diskUsage.total_size_gb >= 1 ? 
                `${this.diskUsage.total_size_gb} GB` : 
                `${this.diskUsage.total_size_mb} MB`;
            usedSpace.textContent = used;
        }
        
        if (freeSpace) {
            freeSpace.textContent = `${this.diskUsage.available_space_gb} GB`;
        }
        
        if (usageBar) {
            const usedGB = this.diskUsage.total_size_gb || 0;
            const totalGB = usedGB + this.diskUsage.available_space_gb;
            const percentage = totalGB > 0 ? Math.round((usedGB / totalGB) * 100) : 0;
            
            usageBar.style.width = `${percentage}%`;
            usageBar.setAttribute('aria-valuenow', percentage);
            
            // Change color based on usage
            usageBar.className = 'progress-bar';
            if (percentage > 80) {
                usageBar.classList.add('bg-danger');
            } else if (percentage > 60) {
                usageBar.classList.add('bg-warning');
            } else {
                usageBar.classList.add('bg-success');
            }
        }
    }
    
    // ============ Search and Filter Methods ============
    
    performSearch() {
        const searchInput = document.getElementById('model-search-input');
        const query = searchInput ? searchInput.value.trim() : '';
        
        if (query.length === 0) {
            this.clearSearch();
            return;
        }
        
        if (query.length >= 3) {
            this.searchHuggingFace(query);
        } else {
            this.filterLocalModels(query);
        }
    }
    
    async searchHuggingFace(query) {
        if (this.isLoading) return;
        
        this.isLoading = true;
        this.showSearchLoading();
        
        try {
            const params = new URLSearchParams({
                query: query,
                filter: this.currentFilter,
                limit: '50'
            });
            
            const response = await fetch(`/ai/api/models/search?${params}`);
            const data = await response.json();
            
            if (data.success) {
                this.searchResults = data.models.map(model => ({
                    ...model,
                    installed: this.installedModels.some(im => im.name === model.name),
                    status: this.installedModels.some(im => im.name === model.name) ? 'installed' : 'available'
                }));
                
                this.currentView = 'search';
                this.renderSearchResults(query);
                this.hideSearchLoading();
                
            } else {
                throw new Error(data.error || 'Falha na busca');
            }
        } catch (error) {
            console.error('Error searching models:', error);
            this.showError('Erro na busca: ' + error.message);
            this.hideSearchLoading();
        } finally {
            this.isLoading = false;
        }
    }
    
    filterLocalModels(query) {
        const filtered = this.allModels.filter(model => 
            model.name.toLowerCase().includes(query.toLowerCase()) ||
            (model.display_name && model.display_name.toLowerCase().includes(query.toLowerCase())) ||
            (model.description && model.description.toLowerCase().includes(query.toLowerCase()))
        );
        
        this.searchResults = filtered;
        this.currentView = 'search';
        this.renderSearchResults(query);
    }
    
    clearSearch() {
        const searchInput = document.getElementById('model-search-input');
        if (searchInput) {
            searchInput.value = '';
        }
        
        this.searchResults = [];
        this.currentView = 'all';
        this.renderCurrentView();
    }
    
    applyQuickFilter(filter) {
        const filterSelect = document.getElementById('search-filter');
        if (filterSelect) {
            filterSelect.value = filter;
        }
        
        this.currentFilter = filter;
        
        // Update active tag
        document.querySelectorAll('.filter-tag').forEach(tag => {
            tag.classList.toggle('active', tag.dataset.filter === filter);
        });
        
        if (this.currentView === 'search' && this.searchResults.length > 0) {
            this.performSearch();
        } else {
            this.renderCurrentView();
        }
    }
    
    switchView(view) {
        this.currentView = view;
        this.currentPage = 1;
        
        // Update active toggle
        document.querySelectorAll('.view-toggle').forEach(toggle => {
            toggle.classList.toggle('active', toggle.dataset.view === view);
        });
        
        this.renderCurrentView();
    }
    
    // ============ Rendering Methods ============
    
    renderCurrentView() {
        const container = document.getElementById('models-grid');
        if (!container) return;
        
        let modelsToShow = [];
        let title = '';
        
        switch (this.currentView) {
            case 'all':
                modelsToShow = this.allModels;
                title = 'Todos os Modelos';
                break;
            case 'installed':
                modelsToShow = this.allModels.filter(m => m.installed);
                title = 'Modelos Instalados';
                break;
            case 'available':
                modelsToShow = this.allModels.filter(m => !m.installed);
                title = 'Modelos Disponíveis';
                break;
            case 'search':
                modelsToShow = this.searchResults;
                title = 'Resultados da Busca';
                break;
        }
        
        // Apply current filter
        if (this.currentFilter !== 'all') {
            modelsToShow = modelsToShow.filter(model => {
                if (this.currentFilter === 'medical') {
                    return model.type === 'medical' || 
                           (model.tags && model.tags.includes('medical')) ||
                           (model.name && model.name.toLowerCase().includes('med'));
                } else if (this.currentFilter === 'conversational') {
                    return model.type === 'conversational' || 
                           (model.tags && model.tags.includes('conversational'));
                } else if (this.currentFilter === 'code') {
                    return model.type === 'code' || 
                           (model.tags && model.tags.includes('code'));
                }
                return true;
            });
        }
        
        this.renderModelsGrid(modelsToShow, title, container);
        this.updateResultsInfo(modelsToShow.length, title);
    }
    
    renderSearchResults(query) {
        const container = document.getElementById('models-grid');
        if (!container) return;
        
        const title = `Resultados para "${query}"`;
        this.renderModelsGrid(this.searchResults, title, container);
        this.updateResultsInfo(this.searchResults.length, title);
    }
    
    renderModelsGrid(models, title, container) {
        if (models.length === 0) {
            container.innerHTML = this.createEmptyState(title);
            return;
        }
        
        // Pagination
        const startIndex = (this.currentPage - 1) * this.modelsPerPage;
        const endIndex = startIndex + this.modelsPerPage;
        const paginatedModels = models.slice(startIndex, endIndex);
        
        let html = '';
        paginatedModels.forEach(model => {
            html += this.createModelCard(model);
        });
        
        container.innerHTML = html;
        
        // Render pagination if needed
        if (models.length > this.modelsPerPage) {
            this.renderPagination(models.length);
        } else {
            this.hidePagination();
        }
    }
    
    createModelCard(model) {
        const isInstalled = model.installed;
        const canDownload = !isInstalled;
        const canRemove = isInstalled;
        
        let typeClass = `model-type-${model.type || 'general'}`;
        let typeBadge = this.getTypeBadge(model.type);
        
        // Melhor exibição do tamanho
        let sizeInfo = '';
        if (model.size_estimate && model.size_estimate !== 'Desconhecido') {
            const sizeClass = this.getSizeClass(model.size_bytes || 0);
            sizeInfo = `<span class="model-size ${sizeClass}">
                <i class="fas fa-hdd"></i> ${model.size_estimate}
            </span>`;
        }
        
        let downloads = '';
        if (model.downloads && model.downloads !== 'N/A' && model.downloads > 0) {
            downloads = `<span class="model-downloads">
                <i class="fas fa-download"></i> ${model.downloads.toLocaleString()}
            </span>`;
        }
        
        // Verificar se está em download
        const isDownloading = this.downloadingModels.has(model.name);
        let progressBar = '';
        let actions = '';
        
        if (isDownloading) {
            const progress = this.downloadProgress[model.name] || { progress: 0, status: 'Iniciando...' };
            progressBar = `
                <div class="download-progress">
                    <div class="progress-header">
                        <span class="progress-text">${progress.status}</span>
                        <span class="progress-percent">${progress.progress}%</span>
                    </div>
                    <div class="progress">
                        <div class="progress-bar" role="progressbar" 
                             style="width: ${progress.progress}%" 
                             aria-valuenow="${progress.progress}" 
                             aria-valuemin="0" aria-valuemax="100">
                        </div>
                    </div>
                    <button class="btn btn-sm btn-outline-secondary" onclick="aiConfigManager.cancelDownload('${model.name}')">
                        <i class="fas fa-times"></i> Cancelar
                    </button>
                </div>
            `;
        } else {
            if (canDownload) {
                actions += `<button class="btn btn-primary btn-sm model-action-btn" onclick="aiConfigManager.downloadModel('${model.name}')">
                    <i class="fas fa-download"></i> Instalar
                </button>`;
            }
            if (canRemove) {
                actions += `<button class="btn btn-danger btn-sm model-action-btn" onclick="aiConfigManager.removeModel('${model.name}')">
                    <i class="fas fa-trash"></i> Remover
                </button>`;
            }
        }
        
        const cardClass = isInstalled ? 'model-card installed' : 'model-card available';
        
        return `
            <div class="${cardClass}" data-model="${model.name}">
                <div class="model-card-header">
                    <div class="model-info">
                        <h6 class="model-name">${model.display_name || model.name}</h6>
                        ${model.organization ? `<div class="model-org">${model.organization}</div>` : ''}
                    </div>
                    <div class="model-badges">
                        <span class="model-type-badge ${typeClass}">${typeBadge}</span>
                        ${isInstalled ? '<span class="model-status-badge installed"><i class="fas fa-check"></i> Instalado</span>' : ''}
                    </div>
                </div>
                
                <p class="model-description">${model.description || model.name}</p>
                
                <div class="model-meta">
                    ${sizeInfo}
                    ${downloads}
                </div>
                
                ${progressBar}
                ${actions ? `<div class="model-actions">${actions}</div>` : ''}
            </div>
        `;
    }
    
    getTypeBadge(type) {
        const typeMap = {
            'medical': 'Médico',
            'conversational': 'Conversacional',
            'code': 'Código',
            'language_model': 'Linguagem',
            'recommended': 'Recomendado'
        };
        return typeMap[type] || 'Geral';
    }
    
    createEmptyState(title) {
        let message = '';
        let icon = 'fas fa-search';
        
        if (this.currentView === 'installed') {
            message = 'Nenhum modelo instalado. Use a busca para encontrar e instalar modelos.';
            icon = 'fas fa-download';
        } else if (this.currentView === 'search') {
            message = 'Nenhum resultado encontrado. Tente termos diferentes.';
        } else {
            message = 'Nenhum modelo disponível no momento.';
        }
        
        return `
            <div class="empty-state">
                <i class="${icon} fa-3x mb-3"></i>
                <h5>${title}</h5>
                <p>${message}</p>
            </div>
        `;
    }
    
    updateResultsInfo(count, title) {
        const infoElement = document.getElementById('results-info');
        if (infoElement) {
            infoElement.textContent = `${title} (${count} modelo${count !== 1 ? 's' : ''})`;
        }
    }
    
    showSearchLoading() {
        const container = document.getElementById('models-grid');
        if (container) {
            container.innerHTML = `
                <div class="loading-state">
                    <div class="spinner-border text-primary" role="status">
                        <span class="sr-only">Carregando...</span>
                    </div>
                    <p class="mt-3">Buscando modelos...</p>
                </div>
            `;
        }
    }
    
    hideSearchLoading() {
        // Will be replaced by the results
    }
    
    renderPagination(totalItems) {
        const totalPages = Math.ceil(totalItems / this.modelsPerPage);
        const paginationContainer = document.getElementById('pagination-container');
        
        if (!paginationContainer || totalPages <= 1) {
            this.hidePagination();
            return;
        }
        
        let html = '<nav aria-label="Model pagination"><ul class="pagination justify-content-center">';
        
        // Previous button
        html += `<li class="page-item ${this.currentPage === 1 ? 'disabled' : ''}">
            <a class="page-link" href="#" onclick="aiConfigManager.goToPage(${this.currentPage - 1}); return false;">Anterior</a>
        </li>`;
        
        // Page numbers
        for (let i = 1; i <= totalPages; i++) {
            if (i === this.currentPage || i === 1 || i === totalPages || 
                (i >= this.currentPage - 2 && i <= this.currentPage + 2)) {
                html += `<li class="page-item ${i === this.currentPage ? 'active' : ''}">
                    <a class="page-link" href="#" onclick="aiConfigManager.goToPage(${i}); return false;">${i}</a>
                </li>`;
            } else if (i === this.currentPage - 3 || i === this.currentPage + 3) {
                html += '<li class="page-item disabled"><span class="page-link">...</span></li>';
            }
        }
        
        // Next button
        html += `<li class="page-item ${this.currentPage === totalPages ? 'disabled' : ''}">
            <a class="page-link" href="#" onclick="aiConfigManager.goToPage(${this.currentPage + 1}); return false;">Próxima</a>
        </li>`;
        
        html += '</ul></nav>';
        
        paginationContainer.innerHTML = html;
        paginationContainer.style.display = 'block';
    }
    
    hidePagination() {
        const paginationContainer = document.getElementById('pagination-container');
        if (paginationContainer) {
            paginationContainer.style.display = 'none';
        }
    }
    
    goToPage(page) {
        this.currentPage = page;
        this.renderCurrentView();
    }
    
    // ============ Model Actions ============
    
    async downloadModel(modelName) {
        try {
            // Marcar como em download
            this.downloadingModels.add(modelName);
            this.downloadProgress[modelName] = { progress: 0, status: 'Iniciando...' };
            
            // Iniciar monitoramento de progresso
            this.startProgressMonitoring(modelName);
            
            // Re-renderizar para mostrar a barra de progresso
            this.renderCurrentView();
            
            const response = await fetch('/ai/api/models/download', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ model_name: modelName })
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.showSuccess(`✅ Modelo "${modelName}" instalado com sucesso!`);
                await this.refreshModelData();
            } else {
                this.showError('Erro na instalação: ' + data.error);
            }
        } catch (error) {
            console.error('Error downloading model:', error);
            this.showError('Erro na instalação: ' + error.message);
        } finally {
            // Limpar progresso
            this.stopProgressMonitoring(modelName);
            this.downloadingModels.delete(modelName);
            delete this.downloadProgress[modelName];
            this.renderCurrentView();
        }
    }
    
    startProgressMonitoring(modelName) {
        const interval = setInterval(async () => {
            try {
                const response = await fetch(`/ai/api/models/${encodeURIComponent(modelName)}/progress`);
                const data = await response.json();
                
                if (data.success && data.progress) {
                    this.downloadProgress[modelName] = data.progress;
                    this.updateProgressBar(modelName, data.progress);
                    
                    // Se o download terminou, parar o monitoramento
                    if (!data.progress.downloading) {
                        this.stopProgressMonitoring(modelName);
                    }
                }
            } catch (error) {
                console.warn('Error monitoring progress:', error);
            }
        }, 1000); // Atualizar a cada 1 segundo
        
        this.downloadIntervals[modelName] = interval;
    }
    
    stopProgressMonitoring(modelName) {
        if (this.downloadIntervals[modelName]) {
            clearInterval(this.downloadIntervals[modelName]);
            delete this.downloadIntervals[modelName];
        }
    }
    
    updateProgressBar(modelName, progress) {
        const modelCard = document.querySelector(`[data-model="${modelName}"]`);
        if (modelCard) {
            const progressBar = modelCard.querySelector('.progress-bar');
            const progressText = modelCard.querySelector('.progress-text');
            const progressPercent = modelCard.querySelector('.progress-percent');
            
            if (progressBar) {
                progressBar.style.width = `${progress.progress}%`;
                progressBar.setAttribute('aria-valuenow', progress.progress);
            }
            
            if (progressText) {
                progressText.textContent = progress.status;
            }
            
            if (progressPercent) {
                progressPercent.textContent = `${progress.progress}%`;
            }
        }
    }
    
    cancelDownload(modelName) {
        if (confirm(`Cancelar download de "${modelName}"?`)) {
            this.stopProgressMonitoring(modelName);
            this.downloadingModels.delete(modelName);
            delete this.downloadProgress[modelName];
            this.renderCurrentView();
            this.showInfo(`Download de "${modelName}" cancelado`);        }
    }

    async removeModel(modelName) {
        if (!confirm(`Tem certeza que deseja remover o modelo "${modelName}"?\n\nIsso liberará espaço em disco mas você precisará instalar novamente se quiser usar.`)) {
            return;
        }
        
        try {
            const response = await fetch('/ai/api/models/remove', {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ model_name: modelName })
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.showSuccess(`Modelo removido! Espaço liberado: ${data.space_freed}`);
                await this.refreshModelData();
            } else {
                if (data.error.includes('em uso por outro processo')) {
                    this.showError(`⚠️ Remoção parcial: ${data.error}\n\n💡 Dicas:\n• Feche o navegador e tente novamente\n• Reinicie o aplicativo\n• Alguns arquivos serão removidos automaticamente`);
                } else {
                    this.showError('Erro na remoção: ' + data.error);
                }
            }
        } catch (error) {
            console.error('Error removing model:', error);
            if (error.message.includes('em uso por outro processo')) {
                this.showError('⚠️ Alguns arquivos do modelo estão em uso e não puderam ser removidos.\n\n💡 Tente:\n• Fechar o navegador completamente\n• Reiniciar o aplicativo\n• Os arquivos restantes serão removidos automaticamente quando possível');
            } else {
                this.showError('Erro na remoção: ' + error.message);
            }
        }
    }
    
    async cleanupCache() {
        if (!confirm('🧹 Limpar cache de modelos?\n\nIsso irá:\n• Remover arquivos temporários e incompletos\n• Liberar espaço em disco\n• Resolver problemas de remoção de modelos\n\nContinuar?')) {
            return;
        }
        
        try {
            const response = await fetch('/ai/api/models/cleanup', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.showSuccess(`✅ Cache limpo com sucesso!\n📁 ${data.cleaned_files} arquivos removidos\n💾 Espaço liberado: ${data.space_freed}`);
                await this.refreshModelData();
            } else {
                this.showError('Erro na limpeza: ' + data.error);
            }
        } catch (error) {
            console.error('Error cleaning cache:', error);
            this.showError('Erro na limpeza: ' + error.message);
        }
    }
    
    // ============ Hardware and Configuration Methods ============
    
    displayHardwareInfo() {
        const { cpu, gpu, memory } = this.hardwareInfo;
        
        // CPU Info
        const cpuElement = document.getElementById('cpu-details');
        if (cpu.error) {
            cpuElement.innerHTML = `<span class="text-danger">Erro: ${cpu.error}</span>`;
        } else {
            cpuElement.innerHTML = `
                <strong>${cpu.cores || 'N/A'} cores, ${cpu.threads || 'N/A'} threads</strong><br>
                <small class="text-muted">Performance IA: ${cpu.ai_performance || 'Desconhecida'}</small>
            `;
            
            document.getElementById('cpu-info').classList.add(
                cpu.suitable_for_ai ? 'hardware-available' : 'hardware-unavailable'
            );
        }
        
        // Memory Info
        const memoryElement = document.getElementById('memory-details');
        if (memory.error) {
            memoryElement.innerHTML = `<span class="text-danger">Erro: ${memory.error}</span>`;
        } else {
            memoryElement.innerHTML = `
                <strong>${memory.total_gb || 'N/A'} GB total</strong><br>
                <small class="text-muted">Performance IA: ${memory.ai_performance || 'Desconhecida'}</small>
            `;
            
            document.getElementById('memory-info').classList.add(
                memory.suitable_for_ai ? 'hardware-available' : 'hardware-unavailable'
            );
        }
        
        // GPU Info
        const gpuElement = document.getElementById('gpu-details');
        const gpuTypes = [];
        
        if (gpu.nvidia && gpu.nvidia.available) {
            gpuTypes.push(`NVIDIA (${gpu.nvidia.devices.length} dispositivo(s))`);
        }
        if (gpu.amd && gpu.amd.available) {
            gpuTypes.push(`AMD (${gpu.amd.devices.length} dispositivo(s))`);
        }
        if (gpu.integrated && gpu.integrated.available) {
            gpuTypes.push(`Integrada (${gpu.integrated.devices.length} dispositivo(s))`);
        }
        
        if (gpuTypes.length > 0) {
            gpuElement.innerHTML = `
                <strong>${gpuTypes.join(', ')}</strong><br>
                <small class="text-muted">Recomendado: ${gpu.recommended_backend}</small>
            `;
            document.getElementById('gpu-info').classList.add('hardware-available');
        } else {
            gpuElement.innerHTML = `
                <span class="text-muted">Nenhuma GPU dedicada detectada</span><br>
                <small class="text-muted">Usar processamento por CPU</small>
            `;
            document.getElementById('gpu-info').classList.add('hardware-unavailable');
        }
        
        // Show recommendations
        this.displayRecommendations();
    }
    
    displayHardwareError() {
        ['cpu-details', 'memory-details', 'gpu-details'].forEach(id => {
            document.getElementById(id).innerHTML = '<span class="text-danger">Erro na detecção</span>';
        });
    }
    
    displayRecommendations() {
        const recommendationsSection = document.getElementById('recommendations-section');
        const recommendationsList = document.getElementById('recommendations-list');
        
        if (this.hardwareInfo && this.hardwareInfo.recommendations) {
            recommendationsList.innerHTML = '';
            
            this.hardwareInfo.recommendations.forEach(recommendation => {
                const div = document.createElement('div');
                
                // Determine recommendation type based on emoji/content
                let className = 'recommendation info';
                if (recommendation.includes('✅')) className = 'recommendation success';
                else if (recommendation.includes('⚠️') || recommendation.includes('🟡')) className = 'recommendation warning';
                
                div.className = className;
                div.textContent = recommendation;
                recommendationsList.appendChild(div);
            });
            
            recommendationsSection.style.display = 'block';
        }
    }
    
    displayAvailableModels() {
        const modelsContainer = document.getElementById('available-models');
        
        if (this.availableModels.length === 0) {
            modelsContainer.innerHTML = `
                <div class="text-center text-muted">
                    <i class="fas fa-info-circle"></i> Nenhum modelo local encontrado
                    <p class="mt-2">Modelos serão baixados automaticamente quando necessário</p>
                </div>
            `;
            return;
        }
        
        modelsContainer.innerHTML = '';
        
        this.availableModels.forEach((model, index) => {
            const modelCard = document.createElement('div');
            modelCard.className = 'model-card';
            modelCard.dataset.modelName = model.name;
            
            modelCard.innerHTML = `
                <div class="d-flex justify-content-between align-items-start">
                    <div>
                        <h6 class="mb-1">${model.name}</h6>
                        <div class="model-meta">
                            Tipo: ${model.type} | Tamanho: ${model.size}
                        </div>
                    </div>
                    <input type="radio" name="selected_model" value="${model.name}" ${index === 0 ? 'checked' : ''}>
                </div>
            `;
            
            modelsContainer.appendChild(modelCard);
        });
    }
    
    displayModelsError() {
        const container = document.getElementById('models-grid');
        if (container) {
            container.innerHTML = `
                <div class="text-center text-danger py-4">
                    <i class="fas fa-exclamation-triangle fa-2x mb-3"></i>
                    <p>Erro ao carregar modelos</p>
                </div>
            `;
        }
    }
    
    validateConfiguration() {
        const form = document.getElementById('config-form');
        const formData = new FormData(form);
        const method = formData.get('processing_method');
        
        // Enable/disable start button based on selection
        const startButton = document.getElementById('btn-start-ai');
        startButton.disabled = !method;
        
        // Show warnings for specific configurations
        this.showConfigurationWarnings();
    }
    
    showConfigurationWarnings() {
        // Implementation can be added here for specific warnings
    }
    
    async saveConfiguration() {
        this.showLoading('Salvando configuração...', 'Aplicando novas configurações');
        
        try {
            const config = this.collectConfiguration();
            
            const response = await fetch('/ai/api/update-config', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(config)
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.showSuccess('Configuração salva com sucesso!');
            } else {
                throw new Error(data.error || 'Falha ao salvar configuração');
            }
        } catch (error) {
            console.error('Error saving configuration:', error);
            this.showError('Erro ao salvar configuração: ' + error.message);
        } finally {
            this.hideLoading();
        }
    }
    
    async startAI() {
        this.showLoading('Iniciando IA...', 'Carregando modelo e inicializando sistema');
        
        try {
            // Save configuration first
            await this.saveConfiguration();
            
            // Then start AI
            const response = await fetch('/ai/initialize', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.showSuccess('IA iniciada com sucesso!');
                await this.refreshStatus();
                
                // Redirect to main AI interface after short delay
                setTimeout(() => {
                    window.location.href = '/ai/';
                }, 2000);
            } else {
                throw new Error(data.error || 'Falha ao iniciar IA');
            }
        } catch (error) {
            console.error('Error starting AI:', error);
            this.showError('Erro ao iniciar IA: ' + error.message);
        } finally {
            this.hideLoading();
        }
    }
    
    async stopAI() {
        this.showLoading('Parando IA...', 'Liberando recursos do sistema');
        
        try {
            const response = await fetch('/ai/api/stop', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.showSuccess('IA parada com sucesso!');
                await this.refreshStatus();
            } else {
                throw new Error(data.error || 'Falha ao parar IA');
            }
        } catch (error) {
            console.error('Error stopping AI:', error);
            this.showError('Erro ao parar IA: ' + error.message);
        } finally {
            this.hideLoading();
        }
    }
    
    collectConfiguration() {
        const form = document.getElementById('config-form');
        const formData = new FormData(form);
        
        return {
            processing_method: formData.get('processing_method'),
            selected_model: formData.get('selected_model'),
            max_tokens: parseInt(document.getElementById('max-tokens').value),
            temperature: parseFloat(document.getElementById('temperature').value),
            provider_change: true
        };
    }
    
    updateStatusDisplay(status) {
        const statusElement = document.getElementById('current-status');
        const startButton = document.getElementById('btn-start-ai');
        const stopButton = document.getElementById('btn-stop-ai');
        
        if (status.initialized) {
            statusElement.textContent = 'Ativo';
            statusElement.className = 'status-indicator status-active';
            
            startButton.style.display = 'none';
            stopButton.style.display = 'inline-block';
        } else {
            statusElement.textContent = 'Não Inicializado';
            statusElement.className = 'status-indicator status-inactive';
            
            startButton.style.display = 'inline-block';
            stopButton.style.display = 'none';
        }
    }
    
    applyRecommendations() {
        // Apply hardware-based recommendations to the UI
        if (this.hardwareInfo && this.hardwareInfo.gpu) {
            const recommendedBackend = this.hardwareInfo.gpu.recommended_backend;
            
            // Auto-select recommended processing method if available
            const processingMethods = document.querySelectorAll('input[name="processing_method"]');
            processingMethods.forEach(method => {
                if (method.value === recommendedBackend) {
                    method.checked = true;
                }
            });
        }
    }
    
    // ============ Utility Methods ============
    
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
    
    showLoading(title, subtitle) {
        document.getElementById('loading-text').textContent = title;
        document.getElementById('loading-subtext').textContent = subtitle;
        document.getElementById('loading-overlay').style.display = 'flex';
    }
    
    hideLoading() {
        document.getElementById('loading-overlay').style.display = 'none';
    }
    
    showSuccess(message) {
        this.showToast(message, 'success');
    }
    
    showError(message) {
        this.showToast(message, 'error');
    }
    
    showWarning(message) {
        this.showToast(message, 'warning');
    }
    
    showToast(message, type = 'success') {
        const container = document.getElementById('toast-container');
        
        // Create toast element
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        
        const icon = type === 'success' ? 'fas fa-check-circle' : 
                    type === 'error' ? 'fas fa-exclamation-circle' : 
                    'fas fa-exclamation-triangle';
        
        toast.innerHTML = `
            <div style="display: flex; align-items: center;">
                <i class="${icon}" style="margin-right: 10px; font-size: 1.2em;"></i>
                <span>${message}</span>
                <button onclick="this.parentElement.parentElement.remove()" 
                        style="margin-left: auto; background: none; border: none; font-size: 1.2em; cursor: pointer; opacity: 0.6;">
                    ×
                </button>
            </div>
        `;
        
        container.appendChild(toast);
        
        // Show toast with animation
        setTimeout(() => toast.classList.add('show'), 100);
        
        // Auto remove after 5 seconds
        setTimeout(() => {
            if (toast.parentElement) {
                toast.classList.remove('show');
                setTimeout(() => toast.remove(), 300);
            }
        }, 5000);
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.aiConfigManager = new AIConfigManager();
});
