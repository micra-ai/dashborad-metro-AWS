async function loadDashboardData() {
    try {
        const summary = await fetchAPI('/api/dashboard/summary');
        if (summary) {
            document.getElementById('total-events').innerText = summary.total_events;
            document.getElementById('active-devices').innerText = summary.active_devices_count;
            document.getElementById('last-update').innerText = new Date(summary.last_update).toLocaleString('es-CL');
        }

        const epp = await fetchAPI('/api/dashboard/epp');
        if (epp) {
            document.getElementById('epp-workers').innerText = epp.total_workers_detected;
            document.getElementById('epp-compliance').innerText = epp.overall_compliance_percentage.toFixed(1) + '%';
            document.getElementById('epp-full').innerText = epp.workers_full_compliance;
            document.getElementById('epp-missing').innerText = epp.most_frequent_missing_ppe || '-';
            document.getElementById('epp-positive').innerText = epp.positive_compliance_count;
            document.getElementById('epp-negative').innerText = epp.negative_compliance_count;
        }

        const exc = await fetchAPI('/api/dashboard/excavation');
        if (exc) {
            const riskBadge = document.getElementById('exc-risk-level');
            riskBadge.innerText = exc.current_risk_level;
            riskBadge.className = 'risk-badge risk-' + exc.current_risk_level;
            
            document.getElementById('exc-rocks').innerText = exc.total_large_rocks_detections;
            document.getElementById('exc-landslides').innerText = exc.total_landslide_detections;
            document.getElementById('exc-alarms').innerText = exc.total_alarms_triggered;
        }

        const imagesData = await fetchAPI('/api/dashboard/latest-images');
        if (imagesData) {
            renderImages(imagesData.compliant, 'compliant-images-list', true);
            renderImages(imagesData.non_compliant, 'non-compliant-images-list', false);
        }
    } catch (err) {
        console.error("Error loading dashboard data:", err);
    }
}

function renderImages(images, containerId, isCompliant) {
    const container = document.getElementById(containerId);
    if (!container) return;
    container.innerHTML = '';
    
    if (!images || images.length === 0) {
        container.innerHTML = `<div style="color: #9ca3af; font-size: 0.9rem; text-align: center; padding: 1.5rem; border: 1px dashed #374151; border-radius: 8px;">No hay imágenes registradas</div>`;
        return;
    }

    images.forEach(img => {
        const card = document.createElement('div');
        card.className = 'image-card';
        card.onclick = () => openModal(img, isCompliant);

        // Build path. If image_url starts with http, use it directly, else prepend API base url
        const imgUrl = img.image_url ? (img.image_url.startsWith('http') ? img.image_url : `${API_BASE_URL}${img.image_url}`) : 'https://placehold.co/400?text=No+Image';

        const dateStr = new Date(img.timestamp).toLocaleString('es-CL');
        const badgeClass = isCompliant ? 'badge-compliant' : 'badge-non-compliant';
        const badgeText = isCompliant ? 'Cumple' : 'Alerta';

        card.innerHTML = `
            <div class="image-card-img-container">
                <img src="${imgUrl}" alt="EPP Image">
            </div>
            <div class="image-card-content">
                <div>
                    <div class="image-card-title">${img.site} - ${img.area}</div>
                    <div class="image-card-meta">${dateStr}</div>
                </div>
                <div class="image-card-badge ${badgeClass}">${badgeText}</div>
            </div>
        `;
        container.appendChild(card);
    });
}

function openModal(img, isCompliant) {
    const modal = document.getElementById('image-modal');
    const modalImg = document.getElementById('modal-img');
    const modalTitle = document.getElementById('modal-title');
    const modalEventId = document.getElementById('modal-event-id');
    const modalTime = document.getElementById('modal-time');
    const modalLocation = document.getElementById('modal-location');
    const modalWorkers = document.getElementById('modal-workers');
    const modalCompliance = document.getElementById('modal-compliance');
    const missingContainer = document.getElementById('modal-missing-container');
    const missingList = document.getElementById('modal-missing-list');

    if (!modal) return;

    const imgUrl = img.image_url ? (img.image_url.startsWith('http') ? img.image_url : `${API_BASE_URL}${img.image_url}`) : 'https://placehold.co/400?text=No+Image';
    modalImg.src = imgUrl;

    modalTitle.innerText = isCompliant ? "Evento en Regla (EPP Completo)" : "Alerta de Incumplimiento de EPP";
    modalTitle.style.color = isCompliant ? "#10b981" : "#f87171";

    modalEventId.innerText = img.event_id;
    modalTime.innerText = new Date(img.timestamp).toLocaleString('es-CL');
    modalLocation.innerText = `${img.site} - ${img.area} (Zona ${img.zone})`;
    modalWorkers.innerText = `${img.workers_full_compliance} / ${img.workers_detected} en regla`;
    modalCompliance.innerText = `${img.overall_compliance_percentage.toFixed(1)}%`;

    if (!isCompliant) {
        missingContainer.style.display = 'block';
        missingList.innerHTML = '';
        const missingItems = [];
        if (img.missing_helmet_count > 0) missingItems.push(`Casco faltante (${img.missing_helmet_count} personas)`);
        if (img.missing_gloves_count > 0) missingItems.push(`Guantes faltantes (${img.missing_gloves_count} personas)`);
        if (img.missing_goggles_count > 0) missingItems.push(`Lentes/Gafas faltantes (${img.missing_goggles_count} personas)`);
        if (img.missing_reflective_vest_count > 0) missingItems.push(`Chaleco reflectante faltante (${img.missing_reflective_vest_count} personas)`);
        if (img.missing_mask_count > 0) missingItems.push(`Mascarilla faltante (${img.missing_mask_count} personas)`);

        if (missingItems.length === 0) {
            missingItems.push("Incumplimiento detectado");
        }

        missingItems.forEach(item => {
            const li = document.createElement('li');
            li.innerText = item;
            missingList.appendChild(li);
        });
    } else {
        missingContainer.style.display = 'none';
    }

    modal.style.display = 'flex';
}

function closeModal() {
    const modal = document.getElementById('image-modal');
    if (modal) {
        modal.style.display = 'none';
    }
}

// Close modal when clicking outside
window.onclick = function(event) {
    const modal = document.getElementById('image-modal');
    if (event.target === modal) {
        modal.style.display = 'none';
    }
}

if (window.location.pathname.endsWith('dashboard.html')) {
    loadDashboardData();
    setInterval(loadDashboardData, DASHBOARD_REFRESH_INTERVAL_MS);
}
