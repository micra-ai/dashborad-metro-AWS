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
    } catch (err) {
        console.error("Error loading dashboard data:", err);
    }
}

if (window.location.pathname.endsWith('dashboard.html')) {
    loadDashboardData();
    setInterval(loadDashboardData, DASHBOARD_REFRESH_INTERVAL_MS);
}
