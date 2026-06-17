
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

            .join("") || "U";

    }



    function injectStyles() {

        if (document.getElementById("user-sidebar-style")) return;



        const style = document.createElement("style");

        style.id = "user-sidebar-style";

        style.textContent = `

            .sidebar,

            .sidebard {

                display: flex !important;

                flex-direction: column !important;

                min-height: 100vh !important;

                box-sizing: border-box !important;

            }



            .sidebar-bottom {

                margin-top: auto !important;

                padding-top: 24px !important;

                padding-bottom: 24px !important;

                display: flex !important;

                flex-direction: column !important;

                gap: 14px !important;

            }



            .sidebar-user-card {

                background: #111827 !important;

                border: 1px solid rgba(59, 130, 246, 0.32) !important;

                border-radius: 14px !important;

                padding: 14px !important;

                display: flex !important;

                align-items: center !important;

                gap: 12px !important;

                box-shadow: 0 10px 22px rgba(0,0,0,.18) !important;

            }



            .sidebar-user-avatar {

                width: 38px !important;

                height: 38px !important;

                border-radius: 999px !important;

                display: flex !important;

                align-items: center !important;

                justify-content: center !important;

                background: rgba(59, 130, 246, 0.20) !important;

                color: #60a5fa !important;

                border: 1px solid rgba(96, 165, 250, 0.35) !important;

                font-size: 0.82rem !important;

                font-weight: 900 !important;

                flex-shrink: 0 !important;

            }



            .sidebar-user-info {

                display: flex !important;

                flex-direction: column !important;

                min-width: 0 !important;

            }



            .sidebar-user-label {

                color: #9ca3af !important;

                font-size: 0.75rem !important;

                font-weight: 600 !important;

                margin-bottom: 4px !important;

            }



            .sidebar-user-name {

                color: #ffffff !important;

                font-size: 0.92rem !important;

                font-weight: 800 !important;

                line-height: 1.2 !important;

                word-break: break-word !important;

            }



            .sidebar-logout-red {

                display: block !important;

                padding: 14px 16px !important;

                border-radius: 12px !important;

                background: rgba(239, 68, 68, 0.12) !important;

                border: 1px solid rgba(239, 68, 68, 0.35) !important;

                color: #ef4444 !important;

                font-weight: 800 !important;

                text-decoration: none !important;

                text-align: center !important;

                transition: all 0.2s ease !important;

            }



            .sidebar-logout-red:hover {

                background: rgba(239, 68, 68, 0.22) !important;

                color: #ffffff !important;

            }

        `;

        document.head.appendChild(style);

    }



    function renderUserSidebar() {

        injectStyles();



        const sidebar =

            document.querySelector(".sidebar") ||

            document.querySelector(".sidebard") ||

            document.querySelector("aside");



        if (!sidebar) return;



        document.getElementById("sidebar-bottom")?.remove();



        // Quitar cualquier link antiguo de cerrar sesión, esté o no dentro de nav

        Array.from(sidebar.querySelectorAll("a")).forEach(a => {

            if (a.textContent.trim().toLowerCase().includes("cerrar")) {

                a.remove();

            }

        });



        const name = getDisplayName();

        const initials = getInitials(name);



        const bottom = document.createElement("div");

        bottom.id = "sidebar-bottom";

        bottom.className = "sidebar-bottom";



        const card = document.createElement("div");

        card.id = "sidebar-user-card";

        card.className = "sidebar-user-card";

        card.innerHTML = `

            <div class="sidebar-user-avatar">${initials}</div>

            <div class="sidebar-user-info">

                <span class="sidebar-user-label">Sesión activa</span>

                <span class="sidebar-user-name">${name}</span>

            </div>

        `;



        const logoutButton = document.createElement("a");

        logoutButton.id = "sidebar-logout-red";

        logoutButton.className = "sidebar-logout-red";

        logoutButton.href = "#";

        logoutButton.textContent = "Cerrar sesión";



        logoutButton.addEventListener("click", function (event) {

            event.preventDefault();



            if (typeof window.logout === "function") {

                window.logout();

            } else {

                localStorage.removeItem("token");

                localStorage.removeItem("username");

                window.location.href = "/login.html";

            }

        });



        bottom.appendChild(card);

        bottom.appendChild(logoutButton);

        sidebar.appendChild(bottom);

    }



    document.addEventListener("DOMContentLoaded", renderUserSidebar);

})();




/* Ajuste global seguro para menú lateral */

(function () {

    function fixSidebarMenuLayout() {

        const styleId = "sidebar-menu-fix-style";

        if (document.getElementById(styleId)) return;



        const style = document.createElement("style");

        style.id = styleId;

        style.textContent = `

            .sidebar nav {

                display: flex !important;

                flex-direction: column !important;

                gap: 12px !important;

                width: 100% !important;

            }



            .sidebar nav a {

                display: block !important;

                width: 100% !important;

                padding: 13px 16px !important;

                margin: 0 !important;

                border-radius: 10px !important;

                color: #cbd5e1 !important;

                text-decoration: none !important;

                line-height: 1.2 !important;

                font-size: 1rem !important;

                box-sizing: border-box !important;

            }



            .sidebar nav a:hover,

            .sidebar nav a.active {

                background: #374151 !important;

                color: #ffffff !important;

            }

        `;

        document.head.appendChild(style);

    }



    document.addEventListener("DOMContentLoaded", fixSidebarMenuLayout);

})();




/* Corrección final de separación del menú lateral */

(function () {

    function fixSidebarSpacing() {

        const styleId = "sidebar-spacing-final-style";

        if (document.getElementById(styleId)) return;



        const style = document.createElement("style");

        style.id = styleId;

        style.textContent = `

            .sidebar nav {

                display: flex !important;

                flex-direction: column !important;

                gap: 14px !important;

                width: 100% !important;

            }



            .sidebar nav a {

                display: block !important;

                width: 100% !important;

                padding: 13px 16px !important;

                margin: 0 !important;

                border-radius: 10px !important;

                color: #cbd5e1 !important;

                background: transparent !important;

                text-decoration: none !important;

                line-height: 1.25 !important;

                font-size: 1rem !important;

                box-sizing: border-box !important;

            }



            .sidebar nav a.active {

                background: #374151 !important;

                color: #ffffff !important;

                font-weight: 800 !important;

            }



            .sidebar nav a:hover {

                background: #374151 !important;

                color: #ffffff !important;

            }

        `;



        document.head.appendChild(style);

    }



    document.addEventListener("DOMContentLoaded", fixSidebarSpacing);

})();

