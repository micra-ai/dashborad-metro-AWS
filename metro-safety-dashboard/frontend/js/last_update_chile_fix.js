
(function () {

    let isUpdating = false;



    function formatMinusFourHours(value) {

        if (!value) return "-";



        let raw = String(value).trim().split(".")[0];



        const match = raw.match(/^(\d{4})-(\d{2})-(\d{2})[ T](\d{2}):(\d{2}):(\d{2})$/);

        if (!match) return value;



        const year = Number(match[1]);

        const month = Number(match[2]) - 1;

        const day = Number(match[3]);

        const hour = Number(match[4]);

        const minute = Number(match[5]);

        const second = Number(match[6]);



        const date = new Date(year, month, day, hour - 4, minute, second);



        return new Intl.DateTimeFormat("es-CL", {

            day: "2-digit",

            month: "2-digit",

            year: "numeric",

            hour: "2-digit",

            minute: "2-digit",

            second: "2-digit",

            hour12: true

        }).format(date);

    }



    async function applyChileTime() {

        if (isUpdating) return;



        const el = document.getElementById("last-update");

        if (!el) return;



        try {

            isUpdating = true;



            const response = await fetch("/dashboard/epp-metrics?minutes=15", {

                cache: "no-store"

            });



            if (!response.ok) return;



            const data = await response.json();

            const ts = data.latest_timestamp || data.last_update;



            if (!ts) return;



            el.textContent = formatMinusFourHours(ts);

        } catch (err) {

            console.error("Error ajustando hora Chile:", err);

        } finally {

            isUpdating = false;

        }

    }



    function initChileTimeFix() {

        const el = document.getElementById("last-update");

        if (!el) {

            setTimeout(initChileTimeFix, 500);

            return;

        }



        applyChileTime();



        const observer = new MutationObserver(function () {

            if (!isUpdating) {

                setTimeout(applyChileTime, 50);

            }

        });



        observer.observe(el, {

            childList: true,

            characterData: true,

            subtree: true

        });



        setInterval(applyChileTime, 10000);

    }



    if (document.readyState === "loading") {

        document.addEventListener("DOMContentLoaded", initChileTimeFix);

    } else {

        initChileTimeFix();

    }

})();

