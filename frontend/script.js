document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('analysis-form');
    const dropZone = document.getElementById('drop-zone');
    const imageInput = document.getElementById('image-upload');
    const imagePreview = document.getElementById('image-preview');
    const dropContent = document.querySelector('.drop-content');
    const fileNameDisplay = document.getElementById('file-name');
    const contextInput = document.getElementById('clinical-context');
    const loadingOverlay = document.getElementById('loading-overlay');
    
    const emptyState = document.getElementById('empty-state');
    const resultsContent = document.getElementById('results-content');
    const observationsList = document.getElementById('observations-list');
    const pathologiesList = document.getElementById('pathologies-list');
    const recommendationsList = document.getElementById('recommendations-list');
    const exportPdfBtn = document.getElementById('export-pdf-btn');

    // Drag and Drop functionality
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, () => dropZone.classList.add('dragover'), false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, () => dropZone.classList.remove('dragover'), false);
    });

    dropZone.addEventListener('drop', handleDrop, false);
    dropZone.addEventListener('click', () => imageInput.click());
    imageInput.addEventListener('change', handleFiles);

    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        if(files.length) {
            imageInput.files = files; // Assign files to input
            handleFiles();
        }
    }

    function handleFiles() {
        const file = imageInput.files[0];
        if (file && file.type.startsWith('image/')) {
            fileNameDisplay.textContent = file.name;
            
            const reader = new FileReader();
            reader.onload = (e) => {
                imagePreview.src = e.target.result;
                imagePreview.style.display = 'block';
                dropContent.style.display = 'none';
            }
            reader.readAsDataURL(file);
        }
    }

    // Form Submission
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const file = imageInput.files[0];
        const context = contextInput.value;

        if (!file) {
            alert('Please upload a medical image.');
            return;
        }
        if (!context.trim()) {
            alert('Please provide clinical context.');
            return;
        }

        // Show Loading
        loadingOverlay.style.display = 'flex';
        
        // Prepare FormData
        const formData = new FormData();
        formData.append('image', file);
        formData.append('context', context);

        try {
            // Call the FastAPI Backend
            const response = await fetch('/api/analyze', {
                method: 'POST',
                headers: {
                    'ngrok-skip-browser-warning': 'true'
                },
                body: formData
            });

            if (!response.ok) {
                throw new Error('Network response was not ok');
            }

            const data = await response.json();
            
            // Hide loading and show results
            loadingOverlay.style.display = 'none';
            displayResults(data.results);

        } catch (error) {
            console.error('Error:', error);
            loadingOverlay.style.display = 'none';
            alert('Error connecting to the analysis server. Make sure the FastAPI backend is running.');
        }
    });

    function displayResults(results) {
        // Toggle views
        emptyState.style.display = 'none';
        resultsContent.style.display = 'block';

        // Clear previous results
        observationsList.innerHTML = '';
        pathologiesList.innerHTML = '';
        recommendationsList.innerHTML = '';

        // Populate Observations
        results.observations.forEach((obs, index) => {
            const li = document.createElement('li');
            li.textContent = obs;
            li.style.animationDelay = `${index * 0.1}s`;
            observationsList.appendChild(li);
        });

        // Populate Pathologies
        results.suspected_pathologies.forEach((pathology, index) => {
            const div = document.createElement('div');
            div.className = 'pathology-card';
            div.style.animationDelay = `${(results.observations.length * 0.1) + (index * 0.1)}s`;
            
            let badgeClass = '';
            let confidenceColor = '';
            if(pathology.confidence > 80) confidenceColor = 'rgba(16, 185, 129, 0.15)'; // Green
            else if(pathology.confidence > 50) confidenceColor = 'rgba(245, 158, 11, 0.15)'; // Yellow
            else confidenceColor = 'rgba(239, 68, 68, 0.15)'; // Red

            div.innerHTML = `
                <span class="pathology-name">${pathology.name}</span>
                <span class="confidence-badge" style="background: ${confidenceColor}">${pathology.confidence}%</span>
            `;
            pathologiesList.appendChild(div);
        });

        // Populate Recommendations
        results.recommended_exams.forEach((rec, index) => {
            const li = document.createElement('li');
            li.textContent = rec;
            const delay = (results.observations.length * 0.1) + (results.suspected_pathologies.length * 0.1) + (index * 0.1);
            li.style.animationDelay = `${delay}s`;
            recommendationsList.appendChild(li);
        });
    }

    // PDF Export Functionality
    if (exportPdfBtn) {
        exportPdfBtn.addEventListener('click', () => {
            const element = document.getElementById('results-content');
            
            // Hide the export button temporarily so it doesn't appear in the PDF
            exportPdfBtn.style.display = 'none';
            // Add a class to force high contrast light mode for the PDF
            element.classList.add('pdf-mode');

            const opt = {
                margin:       0.5,
                filename:     'MedInsight_Diagnostic_Report.pdf',
                image:        { type: 'jpeg', quality: 0.98 },
                html2canvas:  { scale: 2, useCORS: true },
                jsPDF:        { unit: 'in', format: 'letter', orientation: 'portrait' }
            };

            // Generate PDF
            html2pdf().set(opt).from(element).save().then(() => {
                // Restore the export button and UI styling
                exportPdfBtn.style.display = '';
                element.classList.remove('pdf-mode');
            });
        });
    }
});
