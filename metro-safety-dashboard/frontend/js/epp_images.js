
(function () {

    const API = window.API_BASE_URL || "/api";



    function formatDate(value) {

        if (!value) return "-";



        const date = new Date(String(value).replace(" ", "T"));

        if (isNaN(date.getTime())) return value;



        return date.toLocaleString("es-CL", { timeZone: "America/Santiago", timeZone: "America/Santiago",

            day: "2-digit",

            month: "2-digit",

            year: "numeric",

            hour: "2-digit",

            minute: "2-digit"

        });

    }



    function badgeClass(level) {

        const normalized = String(level || "").toUpperCase();



        if (normalized === "HIGH") return "epp-alert-high";

        if (normalized === "LOW") return "epp-alert-low";

        return "epp-alert-info";

    }



    function openModal(src) {

        const modal = document.createElement("div");

        modal.className = "epp-modal";

        modal.innerHTML = `<img src="${src}" alt="Imagen procesada EPP">`;

        modal.addEventListener("click", () => modal.remove());

        document.body.appendChild(modal);

    }



    function renderImages(images) {

        const section = document.getElementById("epp-images-section");

        if (!section) return;



        if (!images || images.length === 0) {

            section.innerHTML = `

                <div class="epp-images-header">

                    <div>

                        <h2 class="epp-images-title">Últimas imágenes procesadas EPP</h2>

                        <p class="epp-images-subtitle">Evidencia visual asociada a eventos de detección EPP.</p>

                    </div>

                </div>

                <div class="epp-empty">

                    Aún no hay imágenes procesadas cargadas en la plataforma.

                </div>

            `;

            return;

        }



        section.innerHTML = `

            <div class="epp-images-header">

                <div>

                    <h2 class="epp-images-title">Últimas imágenes procesadas EPP</h2>

                    <p class="epp-images-subtitle">Se muestran las últimas imágenes registradas por la plataforma.</p>

                </div>

            </div>



            <div class="epp-images-grid">

                ${images.map(item => `

                    <article class="epp-image-card">

                        <img src="${new URL(item.image_url, window.location.origin).href}" alt="Imagen procesada EPP" data-src="${new URL(item.image_url, window.location.origin).href}">

                        <div class="epp-image-info">

                            <div class="epp-image-row">

                                <span class="epp-device">${item.device_id || "EPP"}</span>

                                <span class="epp-alert-badge ${badgeClass(item.alert_level)}">${item.alert_level || "INFO"}</span>

                            </div>

                            <div class="epp-summary">

                                ${item.missing_ppe_summary || "Evento EPP procesado"}

                            </div>

                            <div class="epp-time">

                                ${formatDate(item.timestamp || item.created_at)}

                            </div>

                        </div>

                    </article>

                `).join("")}

            </div>

        `;



        section.querySelectorAll("img[data-src]").forEach(img => {

            img.addEventListener("click", () => openModal(img.dataset.src));

        });

    }



    async function loadEppImages() {

        try {

            const token = localStorage.getItem("token");

            const headers = token ? { "Authorization": `Bearer ${token}` } : {};



            const response = await fetch(`${API}/dashboard/latest-images`, {

                headers

            });



            if (!response.ok) {

                throw new Error(`Error cargando imágenes EPP: ${response.status}`);

            }



            const data = await response.json();

            renderImages([...(data.compliant || []), ...(data.non_compliant || [])]);



        } catch (error) {

            console.error(error);

            renderImages([]);

        }

    }



    document.addEventListener("DOMContentLoaded", function () {

        loadEppImages();

        setInterval(loadEppImages, 10000);

    });

})();

