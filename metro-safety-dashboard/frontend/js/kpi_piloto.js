
(function () {

    function injectStyles() {

        if (document.getElementById("kpi-piloto-style")) return;



        const style = document.createElement("style");

        style.id = "kpi-piloto-style";

        style.textContent = `

            .kpi-piloto-section {

                background: #1f2937;

                border-radius: 14px;

                padding: 24px;

                margin: 28px 0;

                box-shadow: 0 8px 18px rgba(0,0,0,.16);

                border: 1px solid rgba(148,163,184,.10);

            }



            .kpi-piloto-header {

                margin-bottom: 18px;

                padding-bottom: 14px;

                border-bottom: 1px solid rgba(148,163,184,.18);

            }



            .kpi-piloto-header h2 {

                margin: 0;

                color: #ffffff;

                font-size: 1.45rem;

                font-weight: 800;

            }



            .kpi-piloto-header p {

                margin: 8px 0 0 0;

                color: #cbd5e1;

                font-size: 0.92rem;

                line-height: 1.45;

            }



            .kpi-piloto-grid {

                display: grid;

                grid-template-columns: repeat(4, minmax(0, 1fr));

                gap: 16px;

            }



            .kpi-piloto-card {

                background: #111827;

                border-radius: 12px;

                padding: 18px;

                border: 1px solid rgba(148,163,184,.10);

                min-height: 150px;

                display: flex;

                flex-direction: column;

                justify-content: space-between;

            }



            .kpi-piloto-title {

                color: #cbd5e1;

                font-size: 0.88rem;

                font-weight: 800;

                line-height: 1.25;

                margin-bottom: 12px;

            }



            .kpi-piloto-value {

                color: #ffffff;

                font-size: 1.75rem;

                font-weight: 900;

                margin-bottom: 8px;

            }



            .kpi-piloto-value.blue {

                color: #3b82f6;

            }



            .kpi-piloto-value.purple {

                color: #8b5cf6;

            }



            .kpi-piloto-value.green {

                color: #22c55e;

            }



            .kpi-piloto-value.orange {

                color: #f59e0b;

            }



            .kpi-piloto-meta {

                color: #94a3b8;

                font-size: 0.82rem;

                line-height: 1.35;

                margin-bottom: 12px;

            }



            .kpi-status {

                display: inline-flex;

                width: fit-content;

                padding: 5px 10px;

                border-radius: 999px;

                font-size: 0.72rem;

                font-weight: 900;

                letter-spacing: .2px;

            }



            .kpi-status.validation {

                background: rgba(245,158,11,.14);

                color: #f59e0b;

                border: 1px solid rgba(245,158,11,.28);

            }



            .kpi-status.operational {

                background: rgba(34,197,94,.14);

                color: #22c55e;

                border: 1px solid rgba(34,197,94,.28);

            }



            .kpi-status.pending {

                background: rgba(148,163,184,.14);

                color: #cbd5e1;

                border: 1px solid rgba(148,163,184,.28);

            }



            @media (max-width: 1300px) {

                .kpi-piloto-grid {

                    grid-template-columns: repeat(2, minmax(0, 1fr));

                }

            }



            @media (max-width: 800px) {

                .kpi-piloto-grid {

                    grid-template-columns: 1fr;

                }

            }

        `;

        document.head.appendChild(style);

    }



    function findMetricsSection() {

        const headings = Array.from(document.querySelectorAll("h2, h3"));

        const targetHeading = headings.find(h =>

            h.textContent.trim().toLowerCase().includes("métricas reales de epp")

        );



        if (!targetHeading) return null;



        return targetHeading.closest("section") ||

               targetHeading.closest(".card") ||

               targetHeading.parentElement;

    }



    function renderKpiPilotoSection() {

        injectStyles();



        if (document.getElementById("kpi-piloto-section")) return;



        const section = document.createElement("section");

        section.id = "kpi-piloto-section";

        section.className = "kpi-piloto-section";



        section.innerHTML = `

            <div class="kpi-piloto-header">

                <h2>Metas KPI del piloto</h2>

                <p>

                    Esta sección muestra las metas comprometidas del piloto. El resultado real de cada KPI se revisa en la pestaña Validación KPI. 

                    Las métricas de precisión requieren validación contra datos etiquetados o revisión humana para calcular TP, FP y FN.

                </p>

            </div>



            <div class="kpi-piloto-grid">

                <div class="kpi-piloto-card">

                    <div>

                        <div class="kpi-piloto-title">Precisión detección uso de EPP</div>

                        <div class="kpi-piloto-value blue">≥ 85%</div>

                        <div class="kpi-piloto-meta">Meta mínima para identificar uso correcto de elementos de protección personal.</div>

                    </div>

                    <span class="kpi-status validation">En validación</span>

                </div>



                <div class="kpi-piloto-card">

                    <div>

                        <div class="kpi-piloto-title">Precisión detección de desprendimientos</div>

                        <div class="kpi-piloto-value purple">≥ 85%</div>

                        <div class="kpi-piloto-meta">Meta mínima para detectar eventos de riesgo en frente de trabajo.</div>

                    </div>

                    <span class="kpi-status validation">En validación</span>

                </div>



                <div class="kpi-piloto-card">

                    <div>

                        <div class="kpi-piloto-title">Reducción del tiempo de reporte</div>

                        <div class="kpi-piloto-value orange">≥ 30%</div>

                        <div class="kpi-piloto-meta">Meta de reducción respecto al proceso manual de reporte operativo.</div>

                    </div>

                    <span class="kpi-status pending">Pendiente medición formal</span>

                </div>



                <div class="kpi-piloto-card">

                    <div>

                        <div class="kpi-piloto-title">Disponibilidad sistema local + nube</div>

                        <div class="kpi-piloto-value green">≥ 99%</div>

                        <div class="kpi-piloto-meta">Meta de continuidad operacional del sistema SafeTech durante el piloto.</div>

                    </div>

                    <span class="kpi-status operational">Operativo / En medición</span>

                </div>

            </div>

        `;



        const metricsSection = findMetricsSection();

        const main = document.querySelector("main") || document.querySelector(".main-content") || document.body;



        if (metricsSection && metricsSection.parentElement) {

            metricsSection.parentElement.insertBefore(section, metricsSection);

        } else {

            main.appendChild(section);

        }

    }



    document.addEventListener("DOMContentLoaded", renderKpiPilotoSection);

})();

