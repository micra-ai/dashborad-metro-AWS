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


const time = value => {
    if (!value) {
        return '—';
    }

    return new Date(value).toLocaleTimeString('es-CL', {
        hour: '2-digit',
        minute: '2-digit'
    });
};


const dateTime = value => {
    if (!value) {
        return '—';
    }

    return new Date(value).toLocaleString('es-CL', {
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

function renderCycles(data) {

    appState.summary = data;

    const cycle = data.active_cycle;
    const stage = activeStage(cycle);


    /* KPIs resumen */

    el('sum-stage').textContent =
        stage?.stage_name || 'Sin ciclo activo';

    el('sum-stage-time').textContent =
        stage
            ? `En curso · ${duration(stage.duration_seconds)}`
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
            ? `Ciclo activo · ${cycle.cycle_id}`
            : 'Ciclo activo';

    el('cycle-meta').textContent =
        cycle
            ? `Inicio ${time(cycle.started_at)} · objetivo ${duration(cycle.target_duration_seconds)}`
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
                    Sin ciclo activo
                </td>
            </tr>
        `;
    }


    /* Historial */

    const recent = data.recent_cycles || [];

    if (recent.length) {

        el('history-table').innerHTML =
            recent.map(item => `

                <tr>

                    <td>
                        ${esc(item.cycle_id)}
                    </td>

                    <td>
                        ${dateTime(item.started_at)}
                    </td>

                    <td>
                        ${esc(item.shift)}
                    </td>

                    <td>
                        ${esc(item.front)}
                    </td>

                    <td>
                        ${duration(item.duration_seconds)}
                    </td>

                    <td>
                        ${duration(item.target_duration_seconds)}
                    </td>

                    <td>
                        ${Number(item.advance_meters || 0).toFixed(1)} m
                    </td>

                    <td>

                        <span class="status ${
                            item.status === 'IN_PROGRESS'
                                ? 'running'
                                : ''
                        }">

                            ${
                                item.status === 'COMPLETED'
                                    ? 'Terminado'
                                    : 'En curso'
                            }

                        </span>

                    </td>

                </tr>

            `).join('');

    } else {

        el('history-table').innerHTML = `
            <tr>
                <td colspan="8" class="empty">
                    No hay ciclos registrados
                </td>
            </tr>
        `;
    }


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


        renderCycles(cycles);

        renderEpp(epp);

        renderImages(images);


        el('connection').textContent =
            'Servicios operacionales conectados';


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


el('export-history').onclick =
    () =>
        csv(
            appState.summary
                ?.recent_cycles,
            'historial-ciclos-linea9.csv'
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
