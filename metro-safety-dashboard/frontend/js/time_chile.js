
(function () {

    window.formatChileDateTime = function (value) {

        if (!value) return "-";



        let textValue = String(value);



        // Si viene como "2026-06-03 15:10:13", convertir a formato ISO.

        if (textValue.includes(" ") && !textValue.includes("T")) {

            textValue = textValue.replace(" ", "T");

        }



        // Si no trae zona horaria, asumimos que viene en UTC desde backend/AWS.

        if (

            !textValue.endsWith("Z") &&

            !textValue.includes("+") &&

            !textValue.match(/-\d{2}:\d{2}$/)

        ) {

            textValue = textValue + "Z";

        }



        const date = new Date(textValue);



        if (isNaN(date.getTime())) {

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

            hour12: false

        }).format(date);

    };



    window.formatChileNow = function () {

        return new Intl.DateTimeFormat("es-CL", {

            timeZone: "America/Santiago",

            day: "2-digit",

            month: "2-digit",

            year: "numeric",

            hour: "2-digit",

            minute: "2-digit",

            second: "2-digit",

            hour12: false

        }).format(new Date());

    };

})();

