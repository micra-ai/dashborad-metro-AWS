
(function () {

    function setCard(id, title, value, note) {

        const valueEl = document.getElementById(id);

        if (!valueEl) return;



        valueEl.textContent = value;



        const card = valueEl.closest("div");

        if (!card) return;



        const titleEl = card.querySelector("h3, h4");

        if (titleEl) titleEl.textContent = title;



        let noteEl = card.querySelector(".kpi-note");

        if (!noteEl) {

            noteEl = document.createElement("p");

            noteEl.className = "kpi-note";

            noteEl.style.fontSize = "0.85rem";

            noteEl.style.marginTop = "8px";

            noteEl.style.color = "#9ca3af";

            noteEl.style.lineHeight = "1.25rem";

            card.appendChild(noteEl);

        }



        noteEl.textContent = note;

    }



    function replaceHeading(oldText, newText) {

        document.querySelectorAll("h1, h2, h3, h4").forEach((el) => {

            if (el.textContent.trim().includes(oldText)) {

                el.textContent = newText;

            }

        });

    }



    function applyKpiView() {

        replaceHeading("Indicadores de Éxito del Piloto Metro Visión", "Indicadores Objetivo del Piloto Metro Visión");

        replaceHeading("KPIs del Piloto SafeTech", "Indicadores Objetivo del Piloto Metro Visión");

        replaceHeading("Resumen Operacional", "Indicadores Objetivo del Piloto Metro Visión");



        document.querySelectorAll("h2, h3").forEach((el) => {

            const text = el.textContent.trim();



            if (

                text.includes("Control EPP") ||

                text.includes("Indicadores Operacionales") ||

                text.includes("Métricas Operacionales")

            ) {

                el.textContent = "Objetivos Operacionales del Piloto";

            }



            if (

                text.includes("Frente de Trabajo") ||

                text.includes("Monitoreo de Frente")

            ) {

                el.textContent = "Monitoreo de Frente de Trabajo";

            }

        });



        setCard(

            "kpi-epp-precision",

            "Objetivo: precisión detección uso de EPP",

            "Meta ≥ 85%",

            "Indicador objetivo: precisión mínima esperada para identificar uso correcto de EPP durante el piloto"

        );



        setCard(

            "kpi-excavation-precision",

            "Objetivo: precisión detección de desprendimientos",

            "Meta ≥ 85%",

            "Indicador objetivo: precisión mínima esperada para detectar eventos de riesgo en frente de trabajo"

        );



        setCard(

            "kpi-report-reduction",

            "Objetivo: reducción tiempo de reporte",

            "Meta ≥ 30%",

            "Indicador objetivo: reducción esperada respecto al proceso manual de reporte"

        );



        setCard(

            "kpi-availability",

            "Objetivo: disponibilidad sistema local + nube",

            "Meta ≥ 99%",

            "Indicador objetivo: continuidad operacional esperada del sistema durante el piloto"

        );



        setCard(

            "kpi-pilot-status",

            "Estado del piloto",

            "Activo",

            "Ambiente de prueba operativo para demostración y validación inicial"

        );



        setCard(

            "kpi-pilot-results",

            "Resultados del piloto",

            "En validación",

            "Los resultados reales serán medidos durante la ejecución del piloto"

        );



        setCard(

            "exc-risk-level",

            "Nivel de riesgo actual",

            "LOW",

            "Estado actual reportado por el sistema de monitoreo"

        );



        setCard(

            "exc-rocks",

            "Rocas grandes detectadas",

            "0",

            "Eventos detectados en frente de trabajo"

        );



        setCard(

            "exc-landslides",

            "Deslizamientos detectados",

            "0",

            "Eventos críticos detectados"

        );



        setCard(

            "exc-alarms",

            "Alertas activadas",

            "0",

            "Alertas generadas por condición de riesgo"

        );

    }



    document.addEventListener("DOMContentLoaded", function () {

        applyKpiView();

        setInterval(applyKpiView, 500);

    });

})();

