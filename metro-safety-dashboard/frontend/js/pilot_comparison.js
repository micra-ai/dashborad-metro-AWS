
(function () {

    function setNote(card, text) {

        if (!card) return;



        let note = card.querySelector(".metric-note");

        if (!note) {

            note = document.createElement("p");

            note.className = "metric-note";

            note.style.fontSize = "0.85rem";

            note.style.marginTop = "8px";

            note.style.color = "#9ca3af";

            note.style.lineHeight = "1.25rem";

            card.appendChild(note);

        }



        note.textContent = text;

    }



    function renameCardByValueId(id, title, note) {

        const valueEl = document.getElementById(id);

        if (!valueEl) return;



        const card = valueEl.closest("div");

        if (!card) return;



        const titleEl = card.querySelector("h3, h4");

        if (titleEl) titleEl.textContent = title;



        setNote(card, note);

    }



    function replaceText(selector, oldText, newText) {

        document.querySelectorAll(selector).forEach((el) => {

            if (el.textContent.trim().includes(oldText)) {

                el.textContent = newText;

            }

        });

    }



    function injectComparisonSection() {

        if (document.getElementById("pilot-comparison-section")) return;



        const mainTitle = document.querySelector("h1");

        if (!mainTitle) return;



        const section = document.createElement("section");

        section.id = "pilot-comparison-section";

        section.style.margin = "24px 0 28px 0";



        section.innerHTML = `

            <div style="

                background:#1f2937;

                border-radius:14px;

                padding:24px 28px;

                box-shadow:0 8px 18px rgba(0,0,0,.18);

            ">

                <h2 style="margin:0 0 10px 0;color:#f9fafb;font-size:1.5rem;">

                    Comparativa del piloto

                </h2>



                <p style="margin:0 0 22px 0;color:#cbd5e1;line-height:1.5;">

                    La plataforma ya se encuentra operativa y recibiendo eventos desde el sistema actual.

                    Los indicadores de precisión se medirán formalmente cuando las cámaras sean reubicadas

                    en su posición definitiva y se complete la calibración del modelo.

                </p>



                <div style="

                    display:grid;

                    grid-template-columns:repeat(3,minmax(0,1fr));

                    gap:16px;

                ">

                    <div style="background:#111827;border-radius:12px;padding:18px;">

                        <h3 style="margin:0 0 12px 0;color:#93c5fd;">Estado actual</h3>

                        <p style="margin:0;color:#e5e7eb;">Validación de conectividad, recepción de eventos y visualización operacional.</p>

                    </div>



                    <div style="background:#111827;border-radius:12px;padding:18px;">

                        <h3 style="margin:0 0 12px 0;color:#a78bfa;">Objetivos KPI</h3>

                        <p style="margin:0;color:#e5e7eb;">Precisión EPP ≥85%, desprendimientos ≥85%, reducción de reporte ≥30% y disponibilidad ≥99%.</p>

                    </div>



                    <div style="background:#111827;border-radius:12px;padding:18px;">

                        <h3 style="margin:0 0 12px 0;color:#34d399;">Próxima etapa</h3>

                        <p style="margin:0;color:#e5e7eb;">Reubicación de cámaras, calibración de perspectiva y medición formal de KPIs en terreno.</p>

                    </div>

                </div>

            </div>

        `;



        mainTitle.insertAdjacentElement("afterend", section);

    }



    function applyView() {

        replaceText("h1", "Indicadores de Éxito del Piloto Metro Visión", "Estado Actual y Próxima Etapa del Piloto Metro Visión");

        replaceText("h1", "Indicadores Objetivo del Piloto Metro Visión", "Estado Actual y Próxima Etapa del Piloto Metro Visión");

        replaceText("h1", "KPIs del Piloto SafeTech", "Estado Actual y Próxima Etapa del Piloto Metro Visión");

        replaceText("h1", "Resumen Operacional", "Estado Actual y Próxima Etapa del Piloto Metro Visión");



        injectComparisonSection();



        replaceText("h2, h3", "Control EPP (Equipos de Protección)", "Estado actual de operación");

        replaceText("h2, h3", "Indicadores Operacionales del Piloto", "Estado actual de operación");

        replaceText("h2, h3", "Métricas Operacionales de Apoyo", "Estado actual de operación");

        replaceText("h2, h3", "Frente de Trabajo / Excavación", "Monitoreo actual de frente de trabajo");

        replaceText("h2, h3", "Monitoreo de Frente de Trabajo", "Monitoreo actual de frente de trabajo");



        renameCardByValueId(

            "total-events",

            "Eventos recibidos",

            "Dato real registrado por la API durante la operación actual"

        );



        renameCardByValueId(

            "active-devices",

            "Dispositivos activos",

            "Dispositivos reportando eventos actualmente"

        );



        renameCardByValueId(

            "epp-workers",

            "Trabajadores detectados",

            "Conteo operativo recibido desde el sistema de detección"

        );



        renameCardByValueId(

            "epp-compliance",

            "Cumplimiento actual",

            "Métrica operativa actual; no corresponde aún al KPI final del piloto"

        );



        renameCardByValueId(

            "epp-full",

            "Eventos con cumplimiento completo",

            "Registro operativo de eventos con detección completa"

        );



        renameCardByValueId(

            "epp-missing",

            "Elemento EPP más faltante",

            "Dato operacional detectado por el sistema actual"

        );



        renameCardByValueId(

            "exc-risk-level",

            "Nivel de riesgo actual",

            "Estado reportado por el monitoreo actual"

        );



        renameCardByValueId(

            "exc-rocks",

            "Rocas grandes detectadas",

            "Eventos detectados en frente de trabajo"

        );



        renameCardByValueId(

            "exc-landslides",

            "Deslizamientos detectados",

            "Eventos críticos detectados"

        );



        renameCardByValueId(

            "exc-alarms",

            "Alertas activadas",

            "Alertas generadas por condición de riesgo"

        );

    }



    document.addEventListener("DOMContentLoaded", function () {

        applyView();

        setInterval(applyView, 1000);

    });

})();

