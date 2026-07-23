
window.openTunnelTab = async function () {
  window.currentDashboardTab = "tunnel";

  const main =

    document.querySelector(".main-content") ||

    document.querySelector(".content") ||

    document.querySelector(".dashboard") ||

    document.querySelector(".dashboard-page") ||

    document.querySelector(".app-content") ||

    document.querySelector("section") ||

    document.body.children[1];



  if (!main) {

    alert("No encontré el contenedor del dashboard");

    return false;

  }



  const pageTitle = document.querySelector("h1");
  if (pageTitle) pageTitle.style.display = "none";



  main.innerHTML = `

    <div style="font-size:36px;font-weight:800;margin-bottom:8px;color:white;">Túnel / LoRaWAN</div>

    <p style="color:#b8c7da;margin-bottom:30px;">Telemetría recibida desde Milesight UG65.</p>



    <section style="display:grid;grid-template-columns:repeat(3,1fr);gap:22px;">

      <div class="metric-card"><h3>Riesgo actual</h3><strong id="t-risk">-</strong></div>

      <div class="metric-card"><h3>Rocas detectadas</h3><strong id="t-rocks">0</strong></div>

      <div class="metric-card"><h3>Deslizamientos</h3><strong id="t-landslides">0</strong></div>

      <div class="metric-card"><h3>Avance estimado</h3><strong id="t-advance">0 m</strong></div>

      <div class="metric-card"><h3>Estado dispositivo</h3><strong id="t-status">-</strong></div>

      <div class="metric-card"><h3>Alarmas activadas</h3><strong id="t-alarms" style="color:#ef4444;">0</strong></div>

    </section>

  `;



  const style = document.createElement("style");

  style.textContent = `

    .metric-card{

      background:#202b3a;

      border:1px solid #334155;

      border-radius:16px;

      padding:28px;

    }

    .metric-card h3{

      color:#b8c7da;

      font-size:16px;

      margin:0 0 16px;

    }

    .metric-card strong{

      display:block;

      font-size:42px;

      color:white;

    }

  `;

  document.head.appendChild(style);



  const token = localStorage.getItem("token");



  const res = await fetch("/api/dashboard/excavation", {

    headers: { Authorization: `Bearer ${token}` }

  });



  if (!res.ok) {

    alert("No se pudieron cargar los datos LoRaWAN. Status: " + res.status);

    return false;

  }



  const d = await res.json();



  document.getElementById("t-risk").textContent = d.current_risk_level || "-";

  document.getElementById("t-risk").style.color =

    d.current_risk_level === "MEDIUM" ? "#f59e0b" :

    d.current_risk_level === "HIGH" ? "#ef4444" : "#22c55e";



  document.getElementById("t-rocks").textContent = d.rocas_detectadas ?? 0;

  document.getElementById("t-landslides").textContent = d.deslizamientos ?? 0;

  document.getElementById("t-advance").textContent = `${d.avance_metros ?? 0} m`;

  document.getElementById("t-status").textContent = d.device_status || "-";

  document.getElementById("t-alarms").textContent = d.total_alarms_triggered ?? 0;



  return false;

};







document.addEventListener("DOMContentLoaded", function () {

  if (window.location.search.includes("tunnel=1")) {

    setTimeout(function () {

      if (window.openTunnelTab) window.openTunnelTab();

    }, 500);

  }

});

