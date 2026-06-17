
(function () {

    const USER_NAMES = {

        "admin": "Administrador",

        "rdiaz": "Rodrigo Díaz",

        "scantin": "Sergio Cantín",

        "nedelgado": "Natalie Delgado",

        "gepenam": "Gabriel Peña",

        "kromer": "Karen Romero",

        "sordenesc": "Sergio Ordenes",

        "mroberts": "Maximiliano Roberts"

    };



    function getDisplayName() {

        const username = localStorage.getItem("username") || "";

        return USER_NAMES[username] || username || "Usuario";

    }



    function getInitials(name) {

        return name

            .split(" ")

            .filter(Boolean)

            .slice(0, 2)

            .map(part => part[0].toUpperCase())

            .join("");

    }



    function isDashboardPage() {

        const path = window.location.pathname.toLowerCase();

        return path.includes("dashboard.html") || path.endsWith("/");

    }



    function injectStyles() {

        if (document.getElementById("user-display-style")) return;



        const style = document.createElement("style");

        style.id = "user-display-style";

        style.textContent = `

            .user-session-card {

                position: fixed;

                top: 22px;

                right: 34px;

                z-index: 100;

                display: flex;

                align-items: center;

                gap: 10px;

                background: rgba(31, 41, 55, 0.96);

                color: #e5e7eb;

                border: 1px solid rgba(59, 130, 246, 0.35);

                border-radius: 999px;

                padding: 8px 14px;

                box-shadow: 0 10px 22px rgba(0,0,0,.22);

                min-width: auto;

            }



            .user-session-card.user-session-lower {

                top: 56px;

            }



            .user-session-icon {

                width: 28px;

                height: 28px;

                border-radius: 999px;

                display: flex;

                align-items: center;

                justify-content: center;

                background: rgba(59, 130, 246, 0.20);

                color: #60a5fa;

                font-size: 0.72rem;

                font-weight: 900;

                flex-shrink: 0;

                border: 1px solid rgba(96, 165, 250, 0.35);

            }



            .user-session-text {

                display: flex;

                align-items: baseline;

                gap: 6px;

                line-height: 1;

            }



            .user-session-label {

                font-size: 0.76rem;

                color: #9ca3af;

                font-weight: 600;

                letter-spacing: .2px;

            }



            .user-session-name {

                font-size: 0.86rem;

                color: #ffffff;

                font-weight: 800;

            }



            @media (max-width: 900px) {

                .user-session-card,

                .user-session-card.user-session-lower {

                    position: static;

                    margin: 12px 16px;

                    width: fit-content;

                }

            }

        `;

        document.head.appendChild(style);

    }



    function injectUserDisplay() {

        injectStyles();



        const existing = document.getElementById("user-session-display");

        if (existing) existing.remove();



        const name = getDisplayName();

        const initials = getInitials(name);



        const box = document.createElement("div");

        box.id = "user-session-display";

        box.className = "user-session-card";



        if (!isDashboardPage()) {

            box.classList.add("user-session-lower");

        }



        box.innerHTML = `

            <div class="user-session-icon">${initials}</div>

            <div class="user-session-text">

                <span class="user-session-label">Sesión activa</span>

                <span class="user-session-name">${name}</span>

            </div>

        `;



        document.body.appendChild(box);

    }



    document.addEventListener("DOMContentLoaded", injectUserDisplay);

})();

