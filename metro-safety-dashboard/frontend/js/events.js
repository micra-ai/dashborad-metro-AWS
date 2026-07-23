
(function () {

    const API = window.API_BASE_URL || "/api";



    function getToken() {

        return localStorage.getItem("token");

    }



    function authHeaders() {

        const token = getToken();



        return token

            ? { Authorization: `Bearer ${token}` }

            : {};

    }



    function chileDate(value) {

        if (!value) return "Sin fecha";



        let normalized = String(value).trim();



        if (

            !normalized.endsWith("Z") &&

            !/[+-]\d{2}:\d{2}$/.test(normalized)

        ) {

            normalized += "Z";

        }



        const date = new Date(normalized);



        if (Number.isNaN(date.getTime())) {

            return value;

        }



        return new Intl.DateTimeFormat("es-CL", {

            timeZone: "America/Santiago",

            day: "2-digit",

            month: "2-digit",

            year: "numeric",

            hour: "2-digit",

            minute: "2-digit",

            second: "2-digit",

            hour12: true

        }).format(date);

    }



    function escapeHtml(value) {

        return String(value ?? "")

            .replaceAll("&", "&amp;")

            .replaceAll("<", "&lt;")

            .replaceAll(">", "&gt;")

            .replaceAll('"', "&quot;")

            .replaceAll("'", "&#039;");

    }



    function absoluteImageUrl(imageUrl) {

        if (!imageUrl) return "";

        return new URL(imageUrl, window.location.origin).href;

    }



    function renderAlerts(alerts) {

        const tbody = document.getElementById("events-table-body");



        if (!tbody) return;



        if (!alerts.length) {

            tbody.innerHTML = `

                <tr>

                    <td colspan="6" style="text-align:center;padding:32px;">

                        No hay alertas EPP registradas.

                    </td>

                </tr>

            `;

            return;

        }



        tbody.innerHTML = alerts.map((alert) => {

            const imageUrl = absoluteImageUrl(alert.image_url);



            const evidence = imageUrl

                ? `

                    <a href="${escapeHtml(imageUrl)}"

                       target="_blank"

                       rel="noopener noreferrer">

                        <img

                            src="${escapeHtml(imageUrl)}"

                            alt="Evidencia EPP"

                            style="

                                width:120px;

                                height:75px;

                                object-fit:cover;

                                border-radius:8px;

                                border:1px solid #475569;

                            "

                        >

                    </a>

                `

                : `<span style="opacity:.7;">Sin imagen</span>`;



            return `

                <tr>

                    <td>${escapeHtml(chileDate(alert.timestamp))}</td>

                    <td>${escapeHtml(alert.device_id || "EPP")}</td>

                    <td>${escapeHtml(alert.workers_detected || 0)}</td>

                    <td>

                        <strong>

                            ${escapeHtml(alert.missing_summary || "Sin detalle")}

                        </strong>

                    </td>

                    <td>${escapeHtml(alert.alert_level || "INFO")}</td>

                    <td>${evidence}</td>

                </tr>

            `;

        }).join("");

    }



    window.loadEvents = async function loadEvents() {

        try {

            const deviceId =

                document.getElementById("filter-device")?.value?.trim() || "";



            const params = new URLSearchParams({

                limit: "200"

            });



            if (deviceId) {

                params.set("device_id", deviceId);

            }



            const response = await fetch(

                `${API}/dashboard/epp-alerts?${params.toString()}`,

                {

                    headers: authHeaders()

                }

            );



            if (response.status === 401) {

                localStorage.removeItem("token");

                window.location.href = "/login.html";

                return;

            }



            if (!response.ok) {

                throw new Error(`HTTP ${response.status}`);

            }



            const data = await response.json();

            renderAlerts(data.alerts || []);

        } catch (error) {

            console.error("Error cargando alertas EPP:", error);

            renderAlerts([]);

        }

    };



    async function downloadAlerts() {

        try {

            const deviceId =

                document.getElementById("filter-device")?.value?.trim() || "";



            const params = new URLSearchParams({

                limit: "100"

            });



            if (deviceId) {

                params.set("device_id", deviceId);

            }



            const url =

                `${API}/export/alerts-with-images-xlsx?${params.toString()}`;



            console.log("Descargando Excel:", url);



            const response = await fetch(url, {

                method: "GET",

                headers: authHeaders()

            });



            if (response.status === 401) {

                localStorage.removeItem("token");

                window.location.href = "/login.html";

                return;

            }



            if (!response.ok) {

                const detail = await response.text();

                throw new Error(`HTTP ${response.status}: ${detail}`);

            }



            const blob = await response.blob();



            if (!blob.size) {

                throw new Error("El archivo recibido está vacío");

            }



            const downloadUrl = URL.createObjectURL(blob);

            const link = document.createElement("a");



            link.href = downloadUrl;

            link.download =

                `alertas_epp_con_imagenes_${Date.now()}.xlsx`;



            document.body.appendChild(link);

            link.click();

            link.remove();



            setTimeout(() => {

                URL.revokeObjectURL(downloadUrl);

            }, 1500);

        } catch (error) {

            console.error("Error descargando alertas EPP:", error);

            alert("No fue posible descargar las alertas EPP.");

        }

    }



    window.exportCSV = downloadAlerts;



    document.addEventListener("DOMContentLoaded", () => {

        window.loadEvents();

        setInterval(window.loadEvents, 10000);

    });

})();

