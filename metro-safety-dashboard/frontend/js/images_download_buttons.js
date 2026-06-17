
(function () {

    function getFileNameFromSrc(src, index) {

        try {

            const url = new URL(src, window.location.origin);

            const name = url.pathname.split("/").pop();

            if (name && name.includes(".")) return name;

        } catch (e) {}



        return `imagen_epp_${index + 1}.jpg`;

    }



    async function downloadImage(src, filename) {

        try {

            const response = await fetch(src, { cache: "no-store" });



            if (!response.ok) {

                alert("No se pudo descargar la imagen.");

                return;

            }



            const blob = await response.blob();

            const url = URL.createObjectURL(blob);



            const a = document.createElement("a");

            a.href = url;

            a.download = filename;



            document.body.appendChild(a);

            a.click();

            document.body.removeChild(a);



            URL.revokeObjectURL(url);

        } catch (error) {

            console.error("Error descargando imagen:", error);

            alert("Error al descargar la imagen.");

        }

    }



    function addDownloadButtons() {

        const main = document.querySelector("main") || document.body;

        const images = Array.from(main.querySelectorAll("img"));



        images.forEach((img, index) => {

            if (!img.src) return;

            if (img.dataset.downloadButtonAdded === "true") return;



            img.dataset.downloadButtonAdded = "true";



            const button = document.createElement("button");

            button.textContent = "Descargar imagen";

            button.className = "download-epp-image-btn";



            button.style.cssText = `

                margin-top: 12px;

                background: #059669;

                color: #ffffff;

                border: none;

                border-radius: 8px;

                padding: 10px 14px;

                font-weight: 800;

                cursor: pointer;

                width: fit-content;

            `;



            button.addEventListener("click", function () {

                const filename = getFileNameFromSrc(img.src, index);

                downloadImage(img.src, filename);

            });



            const card =

                img.closest(".image-card") ||

                img.closest(".card") ||

                img.parentElement;



            if (card && !card.querySelector(".download-epp-image-btn")) {

                card.appendChild(button);

            }

        });

    }



    document.addEventListener("DOMContentLoaded", function () {

        addDownloadButtons();



        // Por si las imágenes se cargan después por fetch

        setInterval(addDownloadButtons, 2000);

    });

})();

