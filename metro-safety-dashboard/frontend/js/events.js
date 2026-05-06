async function loadEvents() {
    const type = document.getElementById('filter-type').value;
    const device = document.getElementById('filter-device').value;
    
    let url = '/api/events?limit=100';
    if (type) url += `&event_type=${type}`;
    if (device) url += `&device_id=${device}`;

    try {
        const events = await fetchAPI(url);
        if (events) {
            const tbody = document.getElementById('events-table-body');
            tbody.innerHTML = '';
            events.forEach(ev => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td>${ev.event_id}</td>
                    <td>${ev.event_type}</td>
                    <td>${ev.device_id}</td>
                    <td>${new Date(ev.received_at).toLocaleString('es-CL')}</td>
                    <td><span class="risk-badge risk-${ev.validation_status === 'VALID' ? 'LOW' : 'HIGH'}" style="font-size: 0.8rem; padding: 0.2rem 0.4rem;">${ev.validation_status}</span></td>
                `;
                tbody.appendChild(tr);
            });
        }
    } catch (err) {
        console.error("Error loading events:", err);
    }
}

async function exportCSV() {
    const type = document.getElementById('filter-type').value;
    const device = document.getElementById('filter-device').value;
    
    let url = '/api/export/csv?';
    if (type) url += `event_type=${type}&`;
    if (device) url += `device_id=${device}&`;

    try {
        const blob = await fetchAPI(url, { responseType: 'blob' });
        if (blob) {
            const downloadUrl = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = downloadUrl;
            a.download = `eventos_${new Date().getTime()}.csv`;
            document.body.appendChild(a);
            a.click();
            a.remove();
        }
    } catch (err) {
        console.error("Error exporting csv:", err);
    }
}

if (window.location.pathname.endsWith('events.html')) {
    loadEvents();
}
