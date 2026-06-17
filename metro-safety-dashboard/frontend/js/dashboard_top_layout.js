
(function () {

    function injectStyles() {

        if (document.getElementById("dashboard-top-layout-style")) return;



        const style = document.createElement("style");

        style.id = "dashboard-top-layout-style";

        style.textContent = `

            .last-update-card {

                position: fixed;

                top: 72px;

                right: 34px;

                z-index: 90;

                background: rgba(31, 41, 55, 0.96);

                color: #cbd5e1;

                border: 1px solid rgba(148, 163, 184, 0.22);

                border-radius: 999px;

                padding: 8px 14px;

                box-shadow: 0 10px 22px rgba(0,0,0,.18);

                font-size: 0.84rem;

                white-space: nowrap;

            }



            .last-update-card strong,

            .last-update-card #last-update {

                color: #ffffff;

                font-weight: 800;

            }



            @media (max-width: 900px) {

                .last-update-card {

                    position: static;

                    margin: 8px 16px;

                    width: fit-content;

                }

            }

        `;

        document.head.appendChild(style);

    }



    function moveLastUpdate() {

        injectStyles();



        const lastUpdate = document.getElementById("last-update");

        if (!lastUpdate) return;



        const oldWrapper = lastUpdate.parentElement;

        if (!oldWrapper) return;



        if (oldWrapper.classList.contains("last-update-card")) return;



        oldWrapper.classList.add("last-update-card");

        document.body.appendChild(oldWrapper);

    }



    document.addEventListener("DOMContentLoaded", function () {

        moveLastUpdate();

        setInterval(moveLastUpdate, 1000);

    });

})();

