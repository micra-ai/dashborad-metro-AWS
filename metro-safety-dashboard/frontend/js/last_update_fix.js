
(function () {

    function parseTimestampMinusFourHours(value) {

        if (!value) return "-";



        let raw = String(value).trim();



        // Ej: 2026-06-03 15:36:09.767646

        raw = raw.split(".")[0];



        const parts = raw.match(/^(\d{4})-(\d{2})-(\d{2})[ T](\d{2}):(\d{2}):(\d{2})$/);

        if (!parts) return value;



        const year = Number(parts[1]);

        const month = Number(parts[2]) - 1;

        const day = Number(parts[3]);

        const hour = Number(parts[4]);

        const minute = Number(parts[5]);

        const second = Number(parts[6]);



        // Corrección visual solicitada: el dato viene adelantado 4 horas

        const date = new Date(year, month, day, hour - 4, minute, second);



        return new Intl.DateTimeFormat("es-CL", {

            day: "2-digit",

            month: "2-digit",

            year: "numeric",

            hour: "2-digit",

            minute: "2-digit",

            second: "2-digit",

            hour12: false

        }).format(date);

    }



    async function updateLastUpdateFromApi() {

        const el = document.getElementById("last-update");

        if (!el) return;



        try {

            const response = await fetch("/dashboard/epp-metrics?minutes=15", {

                cache: "no-store"

            });



            if (!response.ok) return;



            const data = await response.json();

            const timestamp = data.latest_timestamp || data.last_update;



            if (!timestamp) return;



            el.textContent = parseTimestampMinusFourHours(timestamp);

        } catch (error) {

            console.error("No se pudo corregir la hora:", error);

        }

    }



    document.addEventListener("DOMContentLoaded", function () {

        updateLastUpdateFromApi();

        setInterval(updateLastUpdateFromApi, 10000);

    });

})();

