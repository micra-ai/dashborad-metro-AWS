async function loadDashboardData() {
    try {
        const summary = await fetchAPI('/api/dashboard/summary');
        if (summary) {
            document.getElementById('total-events').innerText = summary.total_events;
            document.getElementById('active-devices').innerText = summary.active_devices_count;
            document.getElementById('last-update').innerText = window.formatChileDateTime(summary.last_update);
        }

        const epp = await fetchAPI('/api/dashboard/epp');
        if (epp) {
            document.getElementById('epp-workers').innerText = epp.total_workers_detected;
            document.getElementById('epp-compliance').innerText = epp.overall_compliance_percentage.toFixed(1) + '%';
            document.getElementById('epp-full').innerText = epp.workers_full_compliance;
            document.getElementById('epp-missing').innerText = epp.most_frequent_missing_ppe || '-';
        }

        const exc = await fetchAPI('/api/dashboard/excavation');
        if (exc) {
            const statusBadge = document.getElementById('exc-device-status');
            if (statusBadge) {
                const isOnline = exc.device_status === 'Online';
                statusBadge.innerText = isOnline ? 'Online' : 'Offline';
                statusBadge.style.backgroundColor = isOnline ? '#22c55e' : '#ef4444';
                statusBadge.style.color = '#ffffff';
                statusBadge.style.fontWeight = 'bold';
            }
            
            if (document.getElementById('exc-rocks')) document.getElementById('exc-rocks').innerText = exc.rocas_detectadas ?? 0;
            if (document.getElementById('exc-landslides')) document.getElementById('exc-landslides').innerText = exc.deslizamientos ?? 0;
            if (document.getElementById('exc-advance')) document.getElementById('exc-advance').innerText = (exc.avance_metros || 0).toFixed(1) + ' m';
        }
    } catch (err) {
        console.error("Error loading dashboard data:", err);
    }
}

if (window.location.pathname.endsWith('dashboard.html')) {
    loadDashboardData();
    setInterval(loadDashboardData, DASHBOARD_REFRESH_INTERVAL_MS);
}
