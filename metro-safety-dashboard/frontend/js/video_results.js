(() => {

  function tiempo(valor) {

    if (valor === null || valor === undefined) return "—";



    const numero = Number(valor);

    if (!Number.isFinite(numero) || numero < 0) return "—";



    const total = Math.round(numero);

    const horas = Math.floor(total / 3600);

    const minutos = Math.floor((total % 3600) / 60);

    const segundos = total % 60;



    return [horas, minutos, segundos]

      .map(n => String(n).padStart(2, "0"))

      .join(":");

  }



  function agregar(parent, etiqueta, texto) {

    const nodo = document.createElement(etiqueta);

    nodo.textContent = texto;

    parent.appendChild(nodo);

    return nodo;

  }



  function tabla(parent, encabezados, filas) {

    const contenedor = document.createElement("div");

    contenedor.style.overflowX = "auto";



    const elemento = document.createElement("table");

    elemento.style.width = "100%";



    const cabecera = elemento.createTHead().insertRow();

    encabezados.forEach(texto => agregar(cabecera, "th", texto));



    const cuerpo = elemento.createTBody();

    filas.forEach(valores => {

      const fila = cuerpo.insertRow();

      valores.forEach(valor => agregar(fila, "td", String(valor)));

    });



    contenedor.appendChild(elemento);

    parent.appendChild(contenedor);

  }



  async function iniciar() {

    const vista = document.getElementById("cycle");

    if (!vista || document.getElementById("video-results-panel")) return;



    const panel = document.createElement("article");

    panel.id = "video-results-panel";

    panel.className = "card";

    panel.style.marginTop = "24px";

    panel.style.padding = "20px";



    agregar(panel, "h2", "Videos procesados");

    agregar(

      panel,

      "p",

      "Segmentos observados en videos históricos. " +

      "Se muestran separados de los ciclos completos."

    );



    const boton = agregar(panel, "button", "Actualizar resultados");

    boton.type = "button";



    const estado = agregar(panel, "p", "");

    estado.setAttribute("role", "status");



    const contenido = document.createElement("div");

    panel.appendChild(contenido);

    vista.appendChild(panel);



    async function cargar() {

      boton.disabled = true;

      estado.textContent = "Cargando resultados…";



      try {

        const datos = await fetchAPI("/video-results");

        if (!datos) {

          estado.textContent = "Inicia sesión para consultar los resultados.";

          return;

        }



        if (!Array.isArray(datos.registros)) {

          throw new Error("Respuesta inesperada de la API");

        }



        contenido.replaceChildren();



        for (const registro of datos.registros) {

          const bloque = document.createElement("div");

          bloque.style.marginTop = "20px";

          contenido.appendChild(bloque);



          agregar(

            bloque,

            "h3",

            registro.video_original || registro.registro_id

          );



          agregar(

            bloque,

            "p",

            "Fuente: video procesado · " +

            (registro.ciclo_completo_verificado

              ? "Ciclo completo verificado"

              : "Segmento parcial")

          );



          agregar(

            bloque,

            "p",

            registro.fecha_grabacion

              ? `Fecha de grabación: ${registro.fecha_grabacion}`

              : "Fecha de grabación: pendiente de informar"

          );



          tabla(

            bloque,

            ["Medición", "Duración"],

            [

              [

                "Retro detectada visualmente",

                tiempo(registro.presencia_visible_segundos)

              ],

              [

                "Presencia estimada, incluyendo interrupciones breves",

                tiempo(registro.presencia_estimada_segundos)

              ]

            ]

          );



          agregar(bloque, "h4", "Tramos de presencia de la retro");



          tabla(

            bloque,

            ["Inicio", "Fin", "Presencia estimada", "Tiempo visible"],

            (registro.segmentos_retro || []).map(segmento => [

              tiempo(segmento.inicio_segundos),

              tiempo(segmento.fin_segundos),

              tiempo(segmento.duracion_segundos),

              tiempo(segmento.visible_segundos)

            ])

          );



          agregar(bloque, "h4", "Observaciones de revisión manual");



          tabla(

            bloque,

            ["Observación", "Inicio aproximado", "Fin aproximado", "Duración"],

            (registro.observaciones_manuales || []).map(observacion => [

              observacion.descripcion,

              tiempo(observacion.inicio_segundos),

              tiempo(observacion.fin_segundos),

              tiempo(observacion.duracion_segundos)

            ])

          );

        }



        estado.textContent = datos.registros.length

          ? `${datos.registros.length} registro(s) cargado(s).`

          : "Todavía no hay resultados de videos.";

      } catch (error) {

        console.error("Error al consultar videos procesados:", error);

        estado.textContent =

          "No se pudieron cargar los resultados. " +

          "Presiona Actualizar resultados para volver a intentar.";

      } finally {

        boton.disabled = false;

      }

    }



    boton.addEventListener("click", cargar);

    await cargar();

  }



  if (document.readyState === "loading") {

    document.addEventListener("DOMContentLoaded", iniciar);

  } else {

    iniciar();

  }

})();
