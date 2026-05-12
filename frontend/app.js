const API_BASE = new URLSearchParams(window.location.search).get("api")
  || localStorage.getItem("farmaexpresApiBase")
  || "http://localhost:8000";

localStorage.setItem("farmaexpresApiBase", API_BASE);

const elements = {
  status: document.querySelector("#service-status"),
  rawCount: document.querySelector("#raw-count"),
  cleanCount: document.querySelector("#clean-count"),
  predictionCount: document.querySelector("#prediction-count"),
  highRiskCount: document.querySelector("#high-risk-count"),
  lastTrained: document.querySelector("#last-trained"),
  chart: document.querySelector("#demand-chart"),
  topList: document.querySelector("#top-list"),
  tableBody: document.querySelector("#predictions-body"),
  tableState: document.querySelector("#table-state"),
  message: document.querySelector("#message"),
  buttons: Array.from(document.querySelectorAll("button")),
};

function setBusy(isBusy) {
  elements.buttons.forEach((button) => {
    button.disabled = isBusy;
  });
}

function setMessage(text, isError = false) {
  elements.message.textContent = text;
  elements.message.style.color = isError ? "#b91c1c" : "#697773";
}

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(data.detail || data.message || "Request failed");
  }
  return data;
}

function updateCounts(counts = {}) {
  elements.rawCount.textContent = counts.raw_data ?? 0;
  elements.cleanCount.textContent = counts.cleaned_data ?? 0;
  elements.predictionCount.textContent = counts.predictions ?? 0;
}

async function loadHealth() {
  const data = await request("/health");
  elements.status.textContent = data.status === "ok" ? "Servicio activo" : "Servicio degradado";
  elements.status.className = `service-chip ${data.status === "ok" ? "ok" : "bad"}`;
  updateCounts(data.counts);
  return data;
}

function renderChart(predictions) {
  const top = predictions.slice(0, 8);
  const maxDemand = Math.max(1, ...top.map((item) => item.predicted_demand_units || 0));
  elements.chart.innerHTML = top.length
    ? top.map((item) => {
        const width = Math.max(3, Math.round(((item.predicted_demand_units || 0) / maxDemand) * 100));
        return `
          <div class="bar-row">
            <span class="bar-label" title="${item.product_name}">${item.product_name}</span>
            <span class="bar-track"><span class="bar-fill" style="width:${width}%"></span></span>
            <span class="bar-value">${item.predicted_demand_units}</span>
          </div>
        `;
      }).join("")
    : "<span class=\"bar-label\">Sin predicciones generadas</span>";
}

function renderTopList(predictions) {
  elements.topList.innerHTML = predictions.slice(0, 5).map((item) => `
    <div class="top-item">
      <div>
        <strong>${item.product_name}</strong>
        <span>${item.category || "Sin categoria"} · stock ${item.current_stock}</span>
      </div>
      <span>${item.predicted_demand_units} uds</span>
    </div>
  `).join("") || "<span class=\"bar-label\">Ejecuta la prediccion para ver resultados</span>";
}

function renderTable(predictions) {
  elements.highRiskCount.textContent = predictions
    .filter((item) => ["HIGH", "OUT_OF_STOCK"].includes(item.risk_level))
    .length;
  elements.tableState.textContent = `${predictions.length} registros`;
  elements.tableBody.innerHTML = predictions.map((item) => `
    <tr>
      <td>${item.product_name}</td>
      <td>${item.product_code || item.product_id}</td>
      <td>${item.current_stock}</td>
      <td>${item.predicted_demand_units}</td>
      <td>${item.estimated_stockout_days ?? "Sin dato"}</td>
      <td><span class="risk ${item.risk_level}">${item.risk_level}</span></td>
    </tr>
  `).join("");
}

async function loadMetrics() {
  const data = await request("/metrics");
  if (data.trained_at) {
    elements.lastTrained.textContent = new Date(data.trained_at).toLocaleString();
  }
}

async function loadPredictions() {
  const predictions = await request("/predictions");
  renderChart(predictions);
  renderTopList(predictions);
  renderTable(predictions);
  await loadMetrics().catch(() => {});
}

async function runAction(label, path, body = {}) {
  setBusy(true);
  setMessage(`${label}...`);
  try {
    await request(path, {
      method: "POST",
      body: JSON.stringify(body),
    });
    await loadHealth();
    await loadPredictions().catch(() => {});
    setMessage(`${label} finalizado.`);
  } catch (error) {
    setMessage(error.message, true);
  } finally {
    setBusy(false);
  }
}

document.querySelector("#health-btn").addEventListener("click", async () => {
  setBusy(true);
  try {
    await loadHealth();
    setMessage("Estado actualizado.");
  } catch (error) {
    elements.status.textContent = "Servicio no disponible";
    elements.status.className = "service-chip bad";
    setMessage(error.message, true);
  } finally {
    setBusy(false);
  }
});

document.querySelector("#seed-btn").addEventListener("click", () => {
  runAction("Carga de datos", "/seed-test-data", { source: "generated", product_count: 15, days: 120 });
});

document.querySelector("#clean-btn").addEventListener("click", () => {
  runAction("Limpieza", "/clean");
});

document.querySelector("#train-btn").addEventListener("click", () => {
  runAction("Prediccion", "/train", { horizon_days: 7 });
});

document.querySelector("#refresh-btn").addEventListener("click", async () => {
  setBusy(true);
  try {
    await loadHealth();
    await loadPredictions();
    setMessage("Datos actualizados.");
  } catch (error) {
    setMessage(error.message, true);
  } finally {
    setBusy(false);
  }
});

loadHealth()
  .then(() => loadPredictions())
  .catch((error) => {
    elements.status.textContent = "Servicio no disponible";
    elements.status.className = "service-chip bad";
    setMessage(`${error.message}. API: ${API_BASE}`, true);
  });
