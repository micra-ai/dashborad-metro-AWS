/* Gallery follows the selected record; independently retries pending evidence. */
(() => {
  const root = document.getElementById('cycle-evidence');
  if (!root) return;
  const h = value => String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const clock = seconds => {
    const n = Math.max(0, Math.floor(Number(seconds)||0));
    return [Math.floor(n/3600),Math.floor(n%3600/60),n%60].map(v=>String(v).padStart(2,'0')).join(':');
  };
  let busy = false, shown = '', recordKey = '';
  const selected = () => typeof appState === 'undefined' ? null : appState.selectedRecord;
  async function refresh() {
    const record = selected();
    const key = record?.analysis_id || '';
    if (key !== recordKey) {
      root.replaceChildren(); shown = ''; recordKey = key;
    }
    if (record?.source !== 'VIDEO_PROCESADO') {
      root.hidden = true; return;
    }
    root.hidden = false;
    const stages = (record.stages || []).filter(s => s.observation !== 'UNOBSERVED');
    if (busy) return;
    busy = true;
    try {
      const ids = [...new Set(stages.map(s=>String(s.id).split(':')[0]))].filter(id=>/^[a-f0-9]{64}$/.test(id));
      const photos = new Map();
      let failed = false;
      await Promise.all(ids.map(async id => {
        try {
          const data = await fetchAPI(`/video-analyses/${id}/evidence`, {signal:AbortSignal.timeout(15000)});
          if (!data) throw new Error('Sin respuesta');
          for (const item of data.items || []) photos.set(`${id}:${item.segment_index}`,item);
        } catch (_) { failed = true; }
      }));
      // Discard response if the operator switched video during the request.
      if (selected()?.analysis_id !== key) return;
      const html = `<h3>Fotos de los intervalos detectados</h3><p class="cycle-evidence-note">${h(record.video_original)} · Una captura por intervalo. Haz clic para ampliar.</p>` +
        (failed ? '<p class="cycle-evidence-note">No se pudo consultar todas las fotos; se reintentará automáticamente.</p>' : '') +
        `<div class="cycle-evidence-grid">${stages.map(stage => {
          const photo = photos.get(String(stage.id));
          const safeURL = photo && /^\/api\/video-analyses\/[a-f0-9]{64}\/evidence\/\d+\/image\?v=[a-f0-9]{64}$/.test(photo.image_url) ? photo.image_url : null;
          const name = stage.video_original || record.video_original;
          return `<article class="cycle-evidence-card">${safeURL
            ? `<a href="${h(safeURL)}" target="_blank" rel="noopener"><img loading="lazy" src="${h(safeURL)}" alt="${h(stage.stage_name)} · ${h(name)} · ${clock(photo.timestamp_seconds)}"></a>`
            : '<div class="cycle-evidence-pending">Foto pendiente de procesamiento o envío</div>'}
            <div class="cycle-evidence-body"><span class="cycle-evidence-tag">${stage.observation==='OBJECT_PRESENT'?'Presencia de objeto':'Etapa candidata'}</span>
            <h4>${h(stage.stage_name)}</h4><p>${clock(stage.start_seconds)} – ${clock(stage.end_seconds)}</p>
            <small>${h(name)}</small>${photo?`<p>Captura en video: ${clock(photo.timestamp_seconds)} · confianza ${(100*photo.confidence).toFixed(1)}%</p>`:''}</div></article>`;
        }).join('')}</div>` + (!stages.length?'<p>Sin intervalos detectados en este registro.</p>':'');
      if (html !== shown) {root.innerHTML = html; shown = html;}
    } finally {busy = false;}
  }
  document.getElementById('cycle-select')?.addEventListener('change', refresh);
  document.getElementById('refresh')?.addEventListener('click', refresh);
  setInterval(refresh,5000);
  refresh();
})();
