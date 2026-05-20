const API_BASE = new URLSearchParams(window.location.search).get("api")
  || localStorage.getItem("farmaexpresApiBase")
  || "http://localhost:8085";

localStorage.setItem("farmaexpresApiBase", API_BASE);

const elements = {
  status: document.querySelector("#service-status"),
  pipelineState: document.querySelector("#pipeline-state"),
  statusDetail: document.querySelector("#status-detail"),
  apiLabel: document.querySelector("#api-label"),
  rawCount: document.querySelector("#raw-count"),
  cleanCount: document.querySelector("#clean-count"),
  predictionCount: document.querySelector("#prediction-count"),
  highRiskCount: document.querySelector("#high-risk-count"),
  maeValue: document.querySelector("#mae-value"),
  lastTrained: document.querySelector("#last-trained"),
  chart: document.querySelector("#demand-chart"),
  topList: document.querySelector("#top-list"),
  tableBody: document.querySelector("#predictions-body"),
  tableState: document.querySelector("#table-state"),
  message: document.querySelector("#message"),
  messageState: document.querySelector("#message-state"),
  activityLog: document.querySelector("#activity-log"),
  buttons: Array.from(document.querySelectorAll("button")),
  pipelineSteps: Array.from(document.querySelectorAll(".pipeline-step")),
};

let latestHealth = null;

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function setBusy(isBusy) {
  elements.buttons.forEach((button) => {
    button.disabled = isBusy;
  });
}

function addActivity(text, type = "info") {
  const item = document.createElement("li");
  item.className = type;
  item.textContent = text;
  elements.activityLog.prepend(item);
  while (elements.activityLog.children.length > 7) {
    elements.activityLog.lastElementChild.remove();
  }
}

function setMessage(text, isError = false) {
  elements.message.textContent = text;
  elements.message.className = `message ${isError ? "error" : "ok"}`;
  elements.messageState.textContent = isError ? "Revisar" : "OK";
}

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(data.detail || data.message || "La solicitud no se pudo completar.");
  }
  return data;
}

function updateCounts(counts = {}) {
  elements.rawCount.textContent = counts.raw_data ?? 0;
  elements.cleanCount.textContent = counts.cleaned_data ?? 0;
  elements.predictionCount.textContent = counts.predictions ?? 0;
}

function updatePipelineSteps(counts = {}) {
  const active = new Set(["postgres", "extract"]);
  if ((counts.raw_data || 0) > 0) active.add("raw");
  if ((counts.cleaned_data || 0) > 0) {
    active.add("raw");
    active.add("clean");
  }
  if ((counts.predictions || 0) > 0) {
    active.add("raw");
    active.add("clean");
    active.add("model");
    active.add("predict");
  }

  elements.pipelineSteps.forEach((step) => {
    const name = step.dataset.step;
    step.classList.toggle("active", active.has(name));
    step.classList.toggle("pending", !active.has(name));
  });
}

function describePipeline(health) {
  const counts = health.counts || {};
  if (!health.mongo) {
    return ["Servicio degradado", "MongoDB no respondió al chequeo del backend."];
  }
  if ((counts.raw_data || 0) === 0) {
    return ["Sin datos cargados", "Ejecuta Cargar datos de prueba o sincroniza una fuente local para llenar raw_data."];
  }
  if ((counts.cleaned_data || 0) === 0) {
    return ["Datos crudos disponibles", "raw_data ya tiene registros. El siguiente paso es limpiar datos."];
  }
  if ((counts.predictions || 0) === 0) {
    return ["Datos limpios listos", "cleaned_data ya está preparado. El siguiente paso es entrenar el modelo."];
  }
  return ["Predicción disponible", "MongoDB contiene datos crudos, datos limpios, métricas y predicciones."];
}

async function loadHealth(announce = false) {
  const data = await request("/health");
  latestHealth = data;
  const [state, detail] = describePipeline(data);
  elements.status.textContent = data.status === "ok" ? "Servicio activo" : "Servicio degradado";
  elements.status.className = `service-chip ${data.status === "ok" ? "ok" : "bad"}`;
  elements.pipelineState.textContent = state;
  elements.statusDetail.textContent = `${detail} Base NoSQL: ${data.database}.`;
  elements.apiLabel.textContent = API_BASE;
  updateCounts(data.counts);
  updatePipelineSteps(data.counts);
  if (announce) {
    addActivity(`Estado actualizado: ${state}.`, "success");
  }
  return data;
}

function riskLabel(riskLevel) {
  const labels = {
    OUT_OF_STOCK: "Sin stock",
    HIGH: "Alto",
    MEDIUM: "Medio",
    LOW: "Bajo",
  };
  return labels[riskLevel] || riskLevel || "Sin dato";
}

function renderChart(predictions) {
  const top = predictions.slice(0, 10);
  const maxDemand = Math.max(1, ...top.map((item) => item.predicted_demand_units || 0));
  elements.chart.innerHTML = top.length
    ? top.map((item) => {
        const width = Math.max(4, Math.round(((item.predicted_demand_units || 0) / maxDemand) * 100));
        return `
          <div class="bar-row">
            <span class="bar-label" title="${escapeHtml(item.product_name)}">${escapeHtml(item.product_name)}</span>
            <span class="bar-track"><span class="bar-fill" style="width:${width}%"></span></span>
            <span class="bar-value">${item.predicted_demand_units}</span>
          </div>
        `;
      }).join("")
    : "<span class=\"empty-state\">Aún no hay predicciones. Carga datos, limpia y entrena el modelo.</span>";
}

function renderTopList(predictions) {
  const priority = [...predictions]
    .sort((a, b) => {
      const riskOrder = { OUT_OF_STOCK: 0, HIGH: 1, MEDIUM: 2, LOW: 3 };
      return (riskOrder[a.risk_level] ?? 4) - (riskOrder[b.risk_level] ?? 4)
        || (b.predicted_demand_units || 0) - (a.predicted_demand_units || 0);
    })
    .slice(0, 6);

  elements.topList.innerHTML = priority.map((item) => `
    <div class="top-item">
      <div>
        <strong>${escapeHtml(item.product_name)}</strong>
        <span>${escapeHtml(item.category || "Sin categoría")} · demanda ${item.predicted_demand_units} uds · stock ${item.current_stock}</span>
      </div>
      <span class="risk ${item.risk_level}">${riskLabel(item.risk_level)}</span>
    </div>
  `).join("") || "<span class=\"empty-state\">Sin alertas. Entrena el modelo para priorizar reposición.</span>";
}

function renderTable(predictions) {
  const highRisk = predictions.filter((item) => ["HIGH", "OUT_OF_STOCK"].includes(item.risk_level)).length;
  elements.highRiskCount.textContent = highRisk;
  elements.tableState.textContent = predictions.length ? `${predictions.length} productos evaluados` : "Sin predicciones";
  elements.tableBody.innerHTML = predictions.map((item) => `
    <tr>
      <td>${escapeHtml(item.product_name)}</td>
      <td>${escapeHtml(item.product_code || item.product_id)}</td>
      <td>${item.current_stock}</td>
      <td>${item.predicted_demand_units}</td>
      <td>${item.estimated_stockout_days ?? "No estimado"}</td>
      <td><span class="risk ${item.risk_level}">${riskLabel(item.risk_level)}</span></td>
    </tr>
  `).join("");
}

async function loadMetrics() {
  const data = await request("/metrics");
  const training = data.latest_training || (data.latest?.type === "training" ? data.latest : null);
  if (training?.trained_at) {
    elements.lastTrained.textContent = `Entrenado: ${new Date(training.trained_at).toLocaleString()}`;
    elements.maeValue.textContent = training.average_mae ?? "--";
    return training;
  }
  elements.lastTrained.textContent = "Sin entrenamiento";
  elements.maeValue.textContent = "--";
  return null;
}

async function loadPredictions() {
  const predictions = await request("/predictions?limit=200");
  renderChart(predictions);
  renderTopList(predictions);
  renderTable(predictions);
  await loadMetrics().catch(() => {});
  return predictions;
}

async function refreshDashboard(announce = false) {
  await loadHealth(announce);
  const predictions = await loadPredictions().catch(() => []);
  if (announce) {
    addActivity(`Tablero actualizado con ${predictions.length} predicciones visibles.`, "success");
  }
}

async function runAction(label, path, body = {}, nextMessage = "") {
  setBusy(true);
  setMessage(`${label} en proceso...`);
  addActivity(`${label} iniciado.`, "info");
  try {
    const result = await request(path, {
      method: "POST",
      body: JSON.stringify(body),
    });
    await refreshDashboard(false);
    const detail = nextMessage || result.message || `${label} finalizado.`;
    setMessage(detail);
    addActivity(detail, "success");
  } catch (error) {
    setMessage(error.message, true);
    addActivity(error.message, "error");
  } finally {
    setBusy(false);
  }
}

document.querySelector("#health-btn").addEventListener("click", async () => {
  setBusy(true);
  try {
    await loadHealth(true);
    const counts = latestHealth?.counts || {};
    setMessage(`MongoDB conectado. Crudos: ${counts.raw_data || 0}, limpios: ${counts.cleaned_data || 0}, predicciones: ${counts.predictions || 0}.`);
  } catch (error) {
    elements.status.textContent = "Servicio no disponible";
    elements.status.className = "service-chip bad";
    elements.pipelineState.textContent = "Sin conexión";
    elements.statusDetail.textContent = `No se pudo contactar la API ${API_BASE}.`;
    setMessage(error.message, true);
    addActivity(`Error de estado: ${error.message}`, "error");
  } finally {
    setBusy(false);
  }
});

document.querySelector("#seed-btn").addEventListener("click", () => {
  runAction(
    "Carga de datos de prueba",
    "/seed-test-data",
    { source: "generated", product_count: 80, days: 180 },
    "Datos de prueba cargados en raw_data. Ahora limpia los registros para preparar el modelo."
  );
});

document.querySelector("#postgres-btn").addEventListener("click", () => {
  runAction(
    "Ingesta desde PostgreSQL",
    "/ingest",
    { source: "postgres", product_count: 80, days: 180 },
    "Ingesta terminada. Si RELATIONAL_DB_URL no está configurada, se usaron datos de prueba para no bloquear la validación local."
  );
});

document.querySelector("#clean-btn").addEventListener("click", () => {
  runAction(
    "Limpieza de datos",
    "/clean",
    {},
    "Datos limpios generados en cleaned_data. Ya puedes entrenar el promedio móvil."
  );
});

document.querySelector("#train-btn").addEventListener("click", () => {
  runAction(
    "Entrenamiento del modelo",
    "/train",
    { horizon_days: 7 },
    "Predicción lista: revisa demanda esperada, riesgo y días hasta agotamiento."
  );
});

document.querySelector("#refresh-btn").addEventListener("click", async () => {
  setBusy(true);
  try {
    await refreshDashboard(true);
    setMessage("Tablero actualizado.");
  } catch (error) {
    setMessage(error.message, true);
    addActivity(`Error al refrescar: ${error.message}`, "error");
  } finally {
    setBusy(false);
  }
});

refreshDashboard(false)
  .then(() => setMessage("Tablero conectado."))
  .catch((error) => {
    elements.status.textContent = "Servicio no disponible";
    elements.status.className = "service-chip bad";
    elements.pipelineState.textContent = "Sin conexión";
    elements.statusDetail.textContent = `No se pudo contactar la API ${API_BASE}.`;
    setMessage(`${error.message}. API: ${API_BASE}`, true);
    addActivity(`No se pudo iniciar el tablero: ${error.message}`, "error");
  });
