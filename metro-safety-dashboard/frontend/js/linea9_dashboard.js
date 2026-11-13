const appState = {
    summary: null,
    lastEppEventId: null
};

const el = id => document.getElementById(id);


/* =========================================================
   UTILIDADES
========================================================= */

const duration = seconds => {
    seconds = Number(seconds);

    if (!Number.isFinite(seconds)) {
        return '—';
    }

    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);

    if (hours) {
        return `${hours} h ${String(minutes).padStart(2, '0')}`;
    }

    return `${minutes} min`;
};


const parseDate = value => {
    if (typeof value === 'string' && !/(?:Z|[+-]\d{2}:?\d{2})$/i.test(value)) {
        return new Date(`${value}Z`);
    }
    return new Date(value);
};


const time = value => {
    if (!value) {
        return '—';
    }

    return parseDate(value).toLocaleTimeString('es-CL', {
        hour: '2-digit',
        minute: '2-digit'
    });
};


const dateTime = value => {
    if (!value) {
        return '—';
    }

    return parseDate(value).toLocaleString('es-CL', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
};


const esc = value =>
    String(value ?? '').replace(
        /[&<>"']/g,
        char => ({
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#39;'
        })[char]
    );


function activeStage(cycle) {
    return (
        cycle?.stages?.find(stage => stage.status === 'IN_PROGRESS') ||
        cycle?.stages?.at(-1)
    );
}


/* =========================================================
   CICLO DE EXCAVACIÓN
========================================================= */

function updateConnectivity(data) {
    const candidates = [];
    for (const cycle of data.recent_cycles || []) {
        if (cycle.started_at) candidates.push(cycle.started_at);
        if (cycle.ended_at) candidates.push(cycle.ended_at);
    }
    const active = data.active_cycle;
    if (active?.started_at) candidates.push(active.started_at);
    for (const stage of active?.stages || []) {
        if (stage.started_at) candidates.push(stage.started_at);
        if (stage.ended_at) candidates.push(stage.ended_at);
    }
    const latest = candidates
        .map(value => parseDate(value))
        .filter(value => Number.isFinite(value.getTime()))
        .sort((a, b) => b - a)[0];
    const latestCycle = active || (data.recent_cycles || [])[0] || null;
    const device = latestCycle?.device_id;

    el('api-state').textContent = 'DISPONIBLE';
    el('connection').textContent = latestCycle
        ? 'API disponible · hay ciclos registrados; origen LoRaWAN no verificado'
        : 'API disponible · aún no hay ciclos registrados';
    el('lora-state').textContent = latestCycle ? 'NO VERIFICADO' : 'SIN CICLOS';
    el('lora-last-event').textContent = latestCycle
        ? `Ciclo ${latestCycle.cycle_id} · dispositivo ${device || 'sin identificar'}${latest ? ` · inicio/actividad ${dateTime(latest.toISOString())}` : ''}`
        : 'Aún no hay ciclos registrados en el backend';
}


function renderCycles(data) {

    appState.summary = data;

    const cycle = data.active_cycle || data.latest_cycle;
    const cycleIsActive = cycle?.status === 'IN_PROGRESS';
    const stage = activeStage(cycle);


    /* KPIs resumen */

    el('sum-stage').textContent =
        stage?.stage_name || 'Sin ciclo activo';

    el('sum-stage-time').textContent =
        stage
            ? `${cycleIsActive ? 'En curso' : 'Finalizado'} · ${duration(stage.duration_seconds)}`
            : '—';

    el('sum-duration').textContent =
        cycle
            ? duration(cycle.duration_seconds)
            : duration(data.average_duration_seconds);

    el('sum-advance').textContent =
        `${Number(data.advance_meters || 0).toFixed(1)} m`;


    /* KPIs ciclo */

    el('cycles-total').textContent =
        data.cycles_total || 0;

    el('cycles-avg').textContent =
        duration(data.average_duration_seconds);

    el('cycles-stage').textContent =
        stage?.stage_name || '—';

    el('cycles-advance').textContent =
        `${Number(data.advance_meters || 0).toFixed(1)} m`;


    /* Ciclo activo */

    el('cycle-name').textContent =
        cycle
            ? `${cycleIsActive ? 'Ciclo activo' : 'Último ciclo'} · ${cycle.cycle_id}`
            : 'Ciclo activo';

    el('cycle-meta').textContent =
        cycle
            ? `Inicio ${time(cycle.started_at)}${!cycleIsActive && cycle.ended_at ? ` · fin ${time(cycle.ended_at)}` : ''} · dispositivo ${cycle.device_id || 'sin identificar'} · objetivo ${duration(cycle.target_duration_seconds)}`
            : 'Esperando eventos del túnel';


    /* Lista de hitos */

    if (cycle?.stages?.length) {

        el('stage-list').innerHTML =
            cycle.stages.map((stageItem, index) => {

                const current =
                    stageItem.status === 'IN_PROGRESS';

                const completed =
                    stageItem.status === 'COMPLETED';

                return `
                    <div class="stage ${current ? 'current' : ''}">

                        <i>
                            ${completed ? '✓' : index + 1}
                        </i>

                        <div>
                            <b>
                                ${esc(stageItem.stage_name)}
                            </b>

                            <small>
                                ${time(stageItem.started_at)}
                                –
                                ${time(stageItem.ended_at)}
                            </small>
                        </div>

                        <b>
                            ${duration(stageItem.duration_seconds)}
                        </b>

                    </div>
                `;

            }).join('');

    } else {

        el('stage-list').innerHTML = `
            <p class="empty">
                El ciclo aparecerá cuando se reciban eventos por LoRa.
            </p>
        `;
    }


    /* Tabla de hitos */

    if (cycle?.stages?.length) {

        el('stage-table').innerHTML =
            cycle.stages.map((stageItem, index) => {

                const deviation =
                    Number(stageItem.deviation_seconds || 0);

                return `
                    <tr>

                        <td>
                            ${index + 1}
                        </td>

                        <td>
                            ${esc(stageItem.stage_name)}
                            ${
                                stageItem.tracked_object === 'brazo_hp1'
                                    ? ' · brazo HP1'
                                    : ''
                            }
                        </td>

                        <td>
                            ${time(stageItem.started_at)}
                        </td>

                        <td>
                            ${time(stageItem.ended_at)}
                        </td>

                        <td>
                            ${duration(stageItem.duration_seconds)}
                        </td>

                        <td>
                            ${duration(stageItem.target_duration_seconds)}
                        </td>

                        <td>
                            ${deviation > 0 ? '+' : ''}
                            ${duration(Math.abs(deviation))}
                        </td>

                        <td>
                            <span class="status ${
                                stageItem.status === 'IN_PROGRESS'
                                    ? 'running'
                                    : ''
                            }">

                                ${
                                    stageItem.status === 'COMPLETED'
                                        ? 'Terminado'
                                        : 'En curso'
                                }

                            </span>
                        </td>

                    </tr>
                `;

            }).join('');

    } else {

        el('stage-table').innerHTML = `
            <tr>
                <td colspan="8" class="empty">
                    No hay ciclos registrados
                </td>
            </tr>
        `;
    }


    const recent = data.recent_cycles || [];

    /* Gráfico últimos ciclos */

    const finishedCycles =
        recent
            .filter(item => item.status === 'COMPLETED')
            .slice(0, 5)
            .reverse();


    if (finishedCycles.length) {

        el('chart').innerHTML =
            finishedCycles.map(item => {

                const max =
                    Math.max(
                        item.duration_seconds,
                        item.target_duration_seconds,
                        1
                    );

                return `
                    <div class="bar-pair">

                        <i
                            style="
                                height:
                                ${
                                    item.target_duration_seconds /
                                    max *
                                    90
                                }%
                            "
                        ></i>

                        <i
                            class="real"
                            style="
                                height:
                                ${
                                    item.duration_seconds /
                                    max *
                                    90
                                }%
                            "
                        ></i>

                        <label>
                            ${esc(item.cycle_id)}
                        </label>

                    </div>
                `;

            }).join('');

    } else {

        el('chart').innerHTML = `
            <p class="empty">
                Sin ciclos terminados
            </p>
        `;
    }


}


/* =========================================================
   MÉTRICAS EPP
========================================================= */

function renderEpp(data) {

    const percentage =
        Number(data.compliance_observed_pct || 0);


    const requiredPpe =
        (data.epp_breakdown || []).filter(item => {

            const name =
                String(item.name || '').toLowerCase();

            return (
                name === 'casco' ||
                name === 'chaleco reflectante' ||
                name === 'chaleco'
            );
        });


    el('sum-epp').textContent =
        `${percentage.toFixed(1)}%`;

    el('epp-total').textContent =
        data.events_epp_evaluated || 0;

    el('epp-pct').textContent =
        `${percentage.toFixed(1)}%`;

    el('epp-fails').textContent =
        data.events_non_compliant || 0;

    el('epp-missing').textContent =
        data.most_missing_epp || '—';


    if (requiredPpe.length) {

        el('epp-breakdown').innerHTML =
            requiredPpe.map(item => {

                const pct =
                    Number(item.detected_pct || 0);

                return `
                    <div class="epp">

                        <span>
                            ${esc(item.name)}
                        </span>

                        <b>
                            ${pct.toFixed(1)}%
                        </b>

                        <div class="progress">
                            <i
                                style="
                                    width:
                                    ${Math.min(pct, 100)}%
                                "
                            ></i>
                        </div>

                    </div>
                `;

            }).join('');

    } else {

        el('epp-breakdown').innerHTML = `
            <p class="empty">
                Sin evaluaciones de casco y chaleco
            </p>
        `;
    }
}


/* =========================================================
   EVENTOS EPP CON EVIDENCIA
========================================================= */

function renderImages(images) {

    /*
        IMPORTANTE:

        Este bloque NO representa video en vivo.

        El endpoint devuelve imágenes que ya fueron
        almacenadas como evidencia de un evento EPP.

        El dashboard simplemente consulta si existe
        un evento guardado más reciente.
    */


    const events = [
        ...(images?.non_compliant || []),
        ...(images?.compliant || [])
    ]
    .filter(event => event.image_url)
    .sort(
        (a, b) =>
            new Date(b.timestamp) -
            new Date(a.timestamp)
    );


    const latest = events[0];

    const image =
        el('live-epp-image');

    const empty =
        el('camera-empty');


    /* -------------------------------------------
       NO HAY EVENTOS GUARDADOS
    ------------------------------------------- */

    if (!latest) {

        image.removeAttribute('src');
        image.style.display = 'none';

        empty.style.display = 'flex';

        el('camera-time').textContent = '';

        el('camera-location').textContent =
            'Cámara EPP · Frente Norte';

        el('live-epp-title').textContent =
            'Sin eventos EPP registrados';

        el('live-epp-meta').textContent =
            'Casco y chaleco';

        el('live-epp-status').textContent =
            '—';

        el('epp-latest-grid').innerHTML = `
            <p class="empty">
                Sin eventos registrados
            </p>
        `;

        el('evidence-grid').innerHTML = `
            <article class="panel empty">
                Sin imágenes EPP registradas.
            </article>
        `;

        return;
    }


    /* -------------------------------------------
       ÚLTIMO EVENTO EPP GUARDADO
    ------------------------------------------- */

    image.src =
        latest.image_url;

    image.style.display =
        'block';

    empty.style.display =
        'none';


    el('camera-time').textContent =
        dateTime(latest.timestamp);


    el('camera-location').textContent =
        [
            latest.area,
            latest.zone
        ]
        .filter(Boolean)
        .join(' · ') ||
        'Cámara EPP · Frente Norte';


    const compliance =
        Number(
            latest.overall_compliance_percentage || 0
        );


    const compliant =
        compliance >= 100;


    el('live-epp-title').textContent =
        compliant
            ? 'Evento EPP conforme'
            : 'Incumplimiento EPP registrado';


    el('live-epp-meta').textContent =
        `${latest.workers_detected || 0} persona(s) · ${compliance.toFixed(1)}% cumplimiento`;


    el('live-epp-status').textContent =
        compliant
            ? '✓'
            : '!';


    /*
        Guardamos el ID únicamente para saber cuál
        es el último evento mostrado.

        No implica transmisión ni monitoreo visual.
    */

    appState.lastEppEventId =
        latest.event_id || latest.timestamp;


    /* -------------------------------------------
       GALERÍA DE ÚLTIMOS EVENTOS
    ------------------------------------------- */

    el('epp-latest-grid').innerHTML =
        events
            .slice(0, 4)
            .map(event => `

                <div class="mini-event">

                    <img
                        src="${esc(event.image_url)}"
                        alt="Evidencia EPP ${esc(event.event_id)}"
                    >

                    <small>
                        ${dateTime(event.timestamp)}
                    </small>

                </div>

            `)
            .join('');


    /* Galería exclusiva de evidencias EPP */

    el('evidence-grid').innerHTML =
        events.map(event => {

            const eventCompliance = Number(
                event.overall_compliance_percentage || 0
            );

            const eventCompliant = eventCompliance >= 100;

            return `
                <article class="panel">

                    <img
                        src="${esc(event.image_url)}"
                        alt="Evidencia EPP ${esc(event.event_id || '')}"
                    >

                    <h3>
                        ${eventCompliant
                            ? 'EPP conforme'
                            : 'Incumplimiento EPP'}
                    </h3>

                    <small>
                        ${dateTime(event.timestamp)} ·
                        ${event.workers_detected || 0} persona(s)
                    </small>

                    <p>
                        Casco y chaleco ·
                        ${eventCompliance.toFixed(1)}% cumplimiento
                    </p>

                </article>
            `;

        }).join('');
}


/* =========================================================
   CARGA DE DATOS
========================================================= */

async function load() {

    try {

        const [
            cycles,
            epp,
            images
        ] = await Promise.all([

            fetchAPI(
                '/cycles/summary'
            ),

            fetchAPI(
                '/dashboard/epp-metrics?minutes=1440'
            ),

            fetchAPI(
                '/dashboard/latest-images?limit=4'
            )

        ]);


        el('api-state').textContent = 'DISPONIBLE';
        renderCycles(cycles);

        renderEpp(epp);

        renderImages(images);


        el('last-update').textContent =
            `Consulta actualizada ${new Date().toLocaleTimeString('es-CL', {
                hour: '2-digit', minute: '2-digit', second: '2-digit'
            })}`;


        el('last-update').textContent =
            `Actualizado ${
                new Date().toLocaleTimeString(
                    'es-CL',
                    {
                        hour: '2-digit',
                        minute: '2-digit',
                        second: '2-digit'
                    }
                )
            }`;

    } catch (error) {

        console.error(
            'Error cargando dashboard:',
            error
        );


        el('connection').textContent =
            'No fue posible consultar la API';
        el('api-state').textContent = 'SIN CONEXIÓN';
    }
}


/* =========================================================
   EXPORTAR CSV
========================================================= */

function csv(rows, filename) {

    if (!rows?.length) {
        return;
    }


    const keys =
        Object.keys(rows[0]);


    const body = [

        keys.join(';'),

        ...rows.map(row =>
            keys.map(key =>
                `"${String(row[key] ?? '')
                    .replaceAll('"', '""')}"`
            ).join(';')
        )

    ].join('\n');


    const link =
        document.createElement('a');


    link.href =
        URL.createObjectURL(
            new Blob(
                [body],
                {
                    type:
                        'text/csv;charset=utf-8'
                }
            )
        );


    link.download =
        filename;


    link.click();


    URL.revokeObjectURL(
        link.href
    );
}


/* =========================================================
   NAVEGACIÓN
========================================================= */

document
    .querySelectorAll('[data-view]')
    .forEach(button => {

        button.onclick = () => {

            const id =
                button.dataset.view;


            document
                .querySelectorAll('.view')
                .forEach(view => {

                    view.classList.toggle(
                        'active',
                        view.id === id
                    );

                });


            document
                .querySelectorAll('[data-view]')
                .forEach(item => {

                    item.classList.toggle(
                        'active',
                        item.dataset.view === id
                    );

                });


            el('title').textContent = {

                summary:
                    'Resumen operacional',

                epp:
                    'Control de EPP',

                cycle:
                    'Ciclo de excavación',

                evidence:
                    'Imágenes procesadas EPP',

                history:
                    'Historial de ciclos'

            }[id];
        };
    });


/* =========================================================
   BOTONES
========================================================= */

el('refresh').onclick =
    load;


el('export-active').onclick =
    () =>
        csv(
            appState.summary
                ?.active_cycle
                ?.stages,
            'ciclo-activo-linea9.csv'
        );


/* =========================================================
   INICIO
========================================================= */

document.addEventListener(
    'DOMContentLoaded',
    () => {

        load();

        /*
            Esto NO actualiza video.

            Solo consulta periódicamente AWS para saber:
            - si existe un nuevo evento EPP guardado
            - si llegó un nuevo hito LoRa
            - si cambió el ciclo de excavación
        */

        setInterval(
            load,
            5000
        );
    }
);


// Consulta independiente: un fallo de EPP no impide mostrar los mensajes LoRa.
let loraPollBusy = false;
async function pollLoRa() {
    if (loraPollBusy) return;
    loraPollBusy = true;
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 10000);
    try {
        const data = await fetchAPI('/v1/lorawan/linea9-status', {
            cache: 'no-store', signal: controller.signal
        });
        if (!data) return;
        const latest = data.latest_event;
        el('lora-poll-state').textContent = `Consulta automática cada 5 s · última consulta ${time(data.generated_at)}`;
        el('lora-state').textContent = latest ? 'DATOS RECIBIDOS' : 'ESPERANDO DATOS';
        el('lora-last-event').textContent = latest
            ? `${latest.event_type} · ${latest.device_id} · recibido ${dateTime(latest.received_at)}`
            : 'Aún no hay mensajes LoRa recibidos en el backend';
        el('lora-payload').textContent = latest
            ? JSON.stringify({

                ...latest,

                received_at_chile: new Date(latest.received_at).toLocaleString('es-CL', {

                    timeZone: 'America/Santiago',

                    hour12: false

                })

            }, (key, value) => value === null ? undefined : value, 2) : 'Esperando mensajes del gateway';
        const hb = data.heartbeat;
        el('lora-camera-status').textContent = hb
            ? `Cámara reportada: ${hb.camera_online === true ? 'en línea' : hb.camera_online === false ? 'fuera de línea' : 'sin dato'} · etapa: ${hb.active_stage_code || 'ninguna'} · ciclos: ${hb.daily_completed_cycles ?? '—'} · cola: ${hb.pending_offline_queue ?? '—'} · estado recibido ${dateTime(hb.received_at)}`
            : 'Sin estado de cámara recibido';
        el('lora-event-list').innerHTML = (data.recent_events || []).map(event =>
            `<p>${esc(dateTime(event.received_at))} · ${esc(event.event_type)} · ${esc(event.object.cycle_id || event.device_id)}</p>`
        ).join('');
    } catch (error) {
        el('lora-poll-state').textContent = 'No se pudo consultar LoRa. Reintentando automáticamente; se conserva el último dato.';
        el('lora-state').textContent = 'ERROR DE CONSULTA';
    } finally {
        clearTimeout(timeout);
        loraPollBusy = false;
    }
}
document.addEventListener('DOMContentLoaded', () => {
    pollLoRa();
    setInterval(pollLoRa, 5000);
});


// Historial independiente: un fallo de EPP no bloquea su consulta.
const receivedHistory = { page: 1, total: 0, busy: false, version: 0 };
const serverTime = value => value ? String(value).replace('T', ' ').slice(0, 19) : '—';
function historyQuery() {
    return new URLSearchParams({ date_from: el('history-from').value,
        date_to: el('history-to').value, stage: el('history-stage').value });
}
function historyDuration(value) {
    if (value === null || value === undefined) return '—';
    const n = Math.floor(Number(value));
    return `${Math.floor(n / 3600)} h ${String(Math.floor(n % 3600 / 60)).padStart(2, '0')} min ${String(n % 60).padStart(2, '0')} s`;
}
async function loadReceivedHistory(reset = false) {
    if (reset) receivedHistory.page = 1;
    const version = ++receivedHistory.version;
    const query = historyQuery();
    query.set('page', receivedHistory.page); query.set('page_size', '50');
    el('history-note').textContent = 'Consultando historial…';
    try {
        const data = await fetchAPI(`/cycles/history?${query}`);
        if (version !== receivedHistory.version) return;
        receivedHistory.total = data.total;
        const labels = { STAGE_START: 'Inicio de etapa', STAGE_END: 'Término de etapa', CYCLE_START: 'Inicio de ciclo', CYCLE_END: 'Término de ciclo' };
        el('history-table').innerHTML = data.items.length ? data.items.map(r => `<tr>
          <td>${esc(serverTime(r.first_received_at))}</td><td>${esc(r.cycle_id)}</td>
          <td>${esc(r.stage_name || r.stage_code || '—')}</td><td>${esc(labels[r.event_type] || r.event_type)}</td>
          <td>${esc(historyDuration(r.duration_seconds))}</td><td>${Number(r.message_count)}${r.message_count > 1 ? ' · posible repetición' : ''}</td>
          <td>${r.confidence == null ? '—' : esc((Number(r.confidence) * 100).toFixed(1)) + '%'}</td></tr>`).join('') : '<tr><td colspan="7">No hay eventos para este filtro.</td></tr>';
        el('history-note').textContent = `${data.total} grupos provisionales · ${data.original_count} mensajes. ${data.note}${data.invalid_count ? ' Mensajes no interpretables: ' + data.invalid_count : ''}`;
        el('history-page').textContent = `Página ${receivedHistory.page} de ${Math.max(1, Math.ceil(data.total / 50))}`;
        el('history-prev').disabled = receivedHistory.page <= 1;
        el('history-next').disabled = receivedHistory.page * 50 >= data.total;
    } catch (error) {
        if (version !== receivedHistory.version) return;
        el('history-table').innerHTML = '<tr><td colspan="7">No se pudo consultar el historial.</td></tr>';
        el('history-note').textContent = error.message || 'Error consultando historial';
    }
}
el('history-to').value = new Intl.DateTimeFormat('en-CA', { timeZone: 'America/Santiago', year: 'numeric', month: '2-digit', day: '2-digit' }).format(new Date());
el('history-apply').onclick = () => loadReceivedHistory(true);
el('history-prev').onclick = () => { if (receivedHistory.page > 1) { receivedHistory.page--; loadReceivedHistory(); } };
el('history-next').onclick = () => { if (receivedHistory.page * 50 < receivedHistory.total) { receivedHistory.page++; loadReceivedHistory(); } };
el('export-history').onclick = async () => {
    const button = el('export-history'); button.disabled = true; button.textContent = 'Preparando Excel…';
    try {
        const data = await fetchAPI(`/cycles/history/export?${historyQuery()}`);
        const bytes = Uint8Array.from(atob(data.content_base64), c => c.charCodeAt(0));
        const url = URL.createObjectURL(new Blob([bytes], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' }));
        const a = document.createElement('a'); a.href = url; a.download = data.filename; document.body.appendChild(a); a.click(); a.remove();
        setTimeout(() => URL.revokeObjectURL(url), 10000);
    } catch (error) { el('history-note').textContent = `No se pudo descargar: ${error.message}`; }
    finally { button.disabled = false; button.textContent = 'Descargar Excel'; }
};
loadReceivedHistory();
setInterval(() => { if (document.getElementById('history').classList.contains('active')) loadReceivedHistory(); }, 30000);
