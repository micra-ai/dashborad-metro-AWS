

function formatUtcToChile(value) {

    if (!value) return "-";



    let raw = String(value).trim();

    raw = raw.replace(/\.\d+$/, "");



    if (raw.includes(" ") && !raw.includes("T")) {

        raw = raw.replace(" ", "T");

    }



    if (!raw.endsWith("Z") && !/[+-]\d{2}:\d{2}$/.test(raw)) {

        raw = raw + "Z";

    }



    const date = new Date(raw);



    if (isNaN(date.getTime())) {

        return String(value);

    }



    return new Intl.DateTimeFormat("es-CL", {

        timeZone: "America/Santiago",

        day: "2-digit",

        month: "2-digit",

        year: "numeric",

        hour: "2-digit",

        minute: "2-digit",

        second: "2-digit",

        hour12: false

    }).format(date);

}








(function () {

    const API = window.API_BASE_URL || "/api";



    function injectStyles() {

        if (document.getElementById("epp-clean-style")) return;



        const style = document.createElement("style");

        style.id = "epp-clean-style";

        style.textContent = `

            body {

                overflow-x: hidden;

            }



            main {

                max-width: 100%;

                overflow-x: hidden;

            }



            .epp-breakdown-compact {

                margin-top: 18px;

                background: #111827;

                border-radius: 12px;

                padding: 16px;

            }



            .epp-breakdown-title {

                margin: 0 0 14px 0;

                color: #f9fafb;

                font-size: 1rem;

                font-weight: 700;

            }



            .epp-bar-row {

                display: grid;

                grid-template-columns: 150px 1fr 70px;

                gap: 12px;

                align-items: center;

                margin-bottom: 10px;

            }



            .epp-bar-name {

                color: #cbd5e1;

                font-size: .88rem;

                font-weight: 600;

            }



            .epp-bar-track {

                width: 100%;

                height: 10px;

                background: #1f2937;

                border-radius: 999px;

                overflow: hidden;

            }



            .epp-bar-fill {

                height: 100%;

                border-radius: 999px;

            }



            .epp-bar-value {

                text-align: right;

                font-weight: 800;

                font-size: .95rem;

            }



            .epp-caption {

                margin-top: 10px;

                color: #9ca3af;

                font-size: .8rem;

                line-height: 1.25rem;

            }



            @media (max-width: 1100px) {

                .epp-bar-row {

                    grid-template-columns: 120px 1fr 60px;

                }

            }

        `;

        document.head.appendChild(style);

    }



    function colorByPct(pct) {

        if (pct >= 85) return "#22c55e";

        if (pct >= 50) return "#f59e0b";

        return "#ef4444";

    }



    function setCard(id, title, value, note, color) {

        const valueEl = document.getElementById(id);

        if (!valueEl) return;



        valueEl.textContent = value;



        if (color) {

            valueEl.style.color = color;

        }



        const card = valueEl.closest("div");

        if (!card) return;



        const titleEl = card.querySelector("h3, h4");

        if (titleEl) titleEl.textContent = title;



        let noteEl = card.querySelector(".metric-note");

        if (!noteEl) {

            noteEl = document.createElement("p");

            noteEl.className = "metric-note";

            noteEl.style.fontSize = "0.85rem";

            noteEl.style.marginTop = "8px";

            noteEl.style.color = "#9ca3af";

            noteEl.style.lineHeight = "1.25rem";

            card.appendChild(noteEl);

        }



        noteEl.textContent = note;

    }



    function setHeading() {

        const h1 = document.querySelector("h1");

        if (h1) {

            h1.textContent = "Estado real de detección EPP";

        }



        document.querySelectorAll("h2, h3").forEach((el) => {

            const text = el.textContent.trim();



            if (

                text.includes("Control EPP") ||

                text.includes("Métricas Operacionales") ||

                text.includes("Datos actuales") ||

                text.includes("Indicadores Operacionales")

            ) {

                el.textContent = "Métricas reales de EPP";

            }



            if (

                text.includes("Frente de Trabajo") ||

                text.includes("Monitoreo")

            ) {

                el.textContent = "Monitoreo actual de frente de trabajo";

            }

        });

    }



    function formatDate(value) {

        if (!value) return "-";



        const date = new Date(value.replace(" ", "T"));

        if (isNaN(date.getTime())) return value;



        return date.toLocaleString("es-CL", { timeZone: "America/Santiago",

            day: "2-digit",

            month: "2-digit",

            year: "numeric",

            hour: "2-digit",

            minute: "2-digit"

        });

    }



    function renderCompactBreakdown(data) {

        const items = data.epp_breakdown || [];



        const eppMissing = document.getElementById("epp-missing");

        if (!eppMissing) return;



        const panel = eppMissing.closest("section, .card, div");

        const container = panel?.parentElement?.parentElement || panel?.parentElement;

        if (!container) return;



        let box = document.getElementById("epp-breakdown-compact");



        if (!box) {

            box = document.createElement("div");

            box.id = "epp-breakdown-compact";

            box.className = "epp-breakdown-compact";

            container.appendChild(box);

        }



        box.innerHTML = `

            <h3 class="epp-breakdown-title">Detección por elemento EPP</h3>



            ${items.map(item => {

                const pct = Number(item.detected_pct || 0);

                const color = colorByPct(pct);



                return `

                    <div class="epp-bar-row">

                        <div class="epp-bar-name">${item.name}</div>

                        <div class="epp-bar-track">

                            <div class="epp-bar-fill" style="width:${pct}%; background:${color};"></div>

                        </div>

                        <div class="epp-bar-value" style="color:${color};">${pct}%</div>

                    </div>

                `;

            }).join("")}



            <p class="epp-caption">

                Información actualizada automáticamente desde la API cada 5 segundos.

            </p>

        `;

    }



    async function loadEppMetrics() {

        try {

            injectStyles();



            const token = localStorage.getItem("token");

            const headers = token ? { "Authorization": `Bearer ${token}` } : {};



            const response = await fetch(`${API}/dashboard/epp-metrics?minutes=15`, {

                headers

            });



            if (!response.ok) {

                throw new Error(`Error API EPP: ${response.status}`);

            }



            const data = await response.json();



            setHeading();



            const compliance = Number(data.compliance_observed_pct || 0);

            const complianceColor = colorByPct(compliance);



            setCard(

                "total-events",

               "Eventos EPP actualizados",

                data.events_epp_evaluated,

                `Información actualizada automáticamente desde la API cada 5 segundos.`,

                "#3b82f6"

            );



            setCard(

                "active-devices",

                "Cumplimiento EPP observado",

                `${compliance}%`,

                "Porcentaje real de eventos conformes en la ventana reciente",

                complianceColor

            );



            setCard(

                "epp-workers",

                "Eventos con incumplimiento EPP",

                data.events_non_compliant,

                "Eventos donde falta al menos un elemento requerido",

                "#ef4444"

            );



            setCard(

                "epp-compliance",

                "Eventos EPP conformes",

                data.events_compliant,

                "Eventos donde el sistema registra cumplimiento completo",

                "#22c55e"

            );



            setCard(

                "epp-full",

                "EPP faltante predominante",

                data.most_missing_epp,

                `Elemento faltante más recurrente (${data.most_missing_epp_count} registros)`,

                "#f59e0b"

            );



            setCard(

                "epp-missing",

                "Nivel de alerta EPP predominante",

                data.dominant_alert_level,

                `Nivel más recurrente en eventos EPP recientes (${data.dominant_alert_count} registros)`,

                data.dominant_alert_level === "HIGH" ? "#ef4444" : "#f59e0b"

            );



            setCard(

                "exc-risk-level",

                "Nivel de riesgo actual",

                document.getElementById("exc-risk-level")?.textContent || "LOW",

                "Estado reportado por el monitoreo actual",

                "#22c55e"

            );



            setCard(

                "exc-rocks",

                "Rocas grandes detectadas",

                document.getElementById("exc-rocks")?.textContent || "0",

                "Eventos detectados en frente de trabajo"

            );



            setCard(

                "exc-landslides",

                "Deslizamientos detectados",

                document.getElementById("exc-landslides")?.textContent || "0",

                "Eventos críticos detectados"

            );



            setCard(

                "exc-alarms",

                "Alertas activadas",

                document.getElementById("exc-alarms")?.textContent || "0",

                "Alertas generadas por condición de riesgo",

                "#ef4444"

            );



            const lastUpdate = document.getElementById("last-update");

            if (lastUpdate) {

                lastUpdate.textContent = formatDate(data.latest_timestamp);

            }



            renderCompactBreakdown(data);



        } catch (error) {

            console.error("No se pudieron cargar métricas EPP:", error);

        }

    }



    document.addEventListener("DOMContentLoaded", function () {

        injectStyles();

        setHeading();

        loadEppMetrics();

        setInterval(loadEppMetrics, 5000);

    });

})();

