const providerFilter = document.querySelector("#provider-filter");
const categoryFilter = document.querySelector("#category-filter");
const searchInput = document.querySelector("#search-input");
const scanButton = document.querySelector("#scan-button");
const findingDialog = document.querySelector("#finding-dialog");
const toast = document.querySelector("#toast");

let findings = [];
let toastTimer;

// View switching - MUST BE AT TOP
function switchView(viewName) {
  const dashboardView = document.getElementById("dashboard-view");
  const infrastructureView = document.getElementById("infrastructure-view");
  
  if (viewName === "dashboard") {
    dashboardView.style.display = "block";
    infrastructureView.style.display = "none";
  } else if (viewName === "infrastructure") {
    dashboardView.style.display = "none";
    infrastructureView.style.display = "block";
  }
}

// Setup nav links
document.querySelectorAll(".nav-item").forEach(link => {
  link.addEventListener("click", (e) => {
    e.preventDefault();
    const view = link.dataset.view;
    
    // Update active state
    document.querySelectorAll(".nav-item").forEach(l => l.classList.remove("active"));
    link.classList.add("active");
    
    // Switch view
    switchView(view);
  });
});

function escapeHtml(value) {
  return String(value ?? "").replace(/[&<>"']/g, (character) => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#39;",
  })[character]);
}

function money(value) {
  return value == null ? "—" : new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 0,
  }).format(value);
}

function providerName(provider) {
  return ({ aws: "AWS", azure: "Azure", gcp: "Google Cloud" })[provider] || provider;
}

// Get API base URL from config (set by config.js)
const API_BASE = window.API_BASE_URL || '';

async function requestJson(url, options) {
  // Prepend API base URL if not already absolute
  const fullUrl = url.startsWith('http') ? url : `${API_BASE}${url}`;
  const response = await fetch(fullUrl, options);
  const body = await response.json();
  if (!response.ok) throw new Error(body.error || `Request failed (${response.status})`);
  return body;
}

function showToast(message, isError = false) {
  window.clearTimeout(toastTimer);
  toast.textContent = message;
  toast.classList.toggle("error", isError);
  toast.classList.add("visible");
  toastTimer = window.setTimeout(() => toast.classList.remove("visible"), 4000);
}

function filters() {
  return new URLSearchParams({
    provider: providerFilter.value,
    category: categoryFilter.value,
  });
}

function renderDashboard(summary) {
  document.querySelector("#total-findings").textContent = summary.total_findings;
  document.querySelector("#monthly-waste").textContent = money(summary.estimated_monthly_waste_usd);
  document.querySelector("#high-risk").textContent = summary.high_risk_findings;
  document.querySelector("#provider-count").textContent = Object.values(summary.by_provider)
    .filter((count) => count > 0).length;

  const names = ["aws", "azure", "gcp"];
  const maxCount = Math.max(1, ...names.map((name) => summary.by_provider[name] || 0));
  document.querySelector("#provider-chart").innerHTML = names.map((name) => {
    const count = summary.by_provider[name] || 0;
    const label = name === "gcp" ? "Google Cloud" : name === "aws" ? "AWS" : "Azure";
    return `<div class="provider-row">
      <span class="provider-name"><span class="provider-symbol">${name === "aws" ? "A" : name === "azure" ? "M" : "G"}</span>${label}</span>
      <span class="bar-track"><span class="bar-fill" style="width:${(count / maxCount) * 100}%"></span></span>
      <span class="provider-total">${count}</span>
    </div>`;
  }).join("");

  const largest = [...findings]
    .filter((finding) => finding.estimated_monthly_cost_usd != null)
    .sort((left, right) => right.estimated_monthly_cost_usd - left.estimated_monthly_cost_usd)
    .slice(0, 3);
  const opportunities = document.querySelector("#top-opportunities");
  opportunities.innerHTML = largest.length
    ? largest.map((finding) => `<div class="opportunity-row">
      <span class="opportunity-icon">↗</span>
      <span class="opportunity-info"><strong>${escapeHtml(finding.title)}</strong><span>${escapeHtml(providerName(finding.provider))} · ${escapeHtml(finding.region || "Global")}</span></span>
      <span class="opportunity-cost">${money(finding.estimated_monthly_cost_usd)}<small>/mo</small></span>
    </div>`).join("")
    : '<p class="empty-state">No costed findings in this sample.</p>';
}

function renderFindings() {
  const body = document.querySelector("#findings-body");
  document.querySelector("#table-status").textContent = `${findings.length} sample finding${findings.length === 1 ? "" : "s"}`;
  body.innerHTML = findings.length ? findings.map((finding, index) => {
    const provider = escapeHtml(finding.provider);
    const initials = provider === "aws" ? "A" : provider === "azure" ? "M" : "G";
    return `<tr>
      <td><div class="resource-cell"><span class="resource-avatar">${initials}</span><div><span class="resource-title">${escapeHtml(finding.title)}</span><div class="resource-id">${escapeHtml(finding.resource_id)}</div></div></div></td>
      <td><span class="provider-pill ${provider}">${escapeHtml(providerName(provider))}</span></td>
      <td>${escapeHtml(finding.region || "Global")}</td>
      <td><span class="risk-pill ${escapeHtml(finding.risk)}">${escapeHtml(finding.risk)}</span></td>
      <td><span class="confidence-pill">${escapeHtml(finding.confidence)}</span></td>
      <td class="cost-cell">${money(finding.estimated_monthly_cost_usd)}</td>
      <td><button class="details-button" type="button" data-finding-index="${index}">Details</button></td>
    </tr>`;
  }).join("") : '<tr><td colspan="7" class="empty-state">No findings match these filters.</td></tr>';

  body.querySelectorAll("[data-finding-index]").forEach((button) => {
    button.addEventListener("click", () => showFinding(findings[Number(button.dataset.findingIndex)]));
  });
}

function showFinding(finding) {
  document.querySelector("#dialog-title").textContent = finding.title;
  document.querySelector("#dialog-summary").textContent = finding.summary;
  const detailRows = [
    ["Provider", providerName(finding.provider)],
    ["Resource ID", finding.resource_id],
    ["Resource type", finding.resource_type],
    ["Region", finding.region || "Global"],
    ["Why flagged", finding.reason],
    ["Matched rule", finding.rule_id],
    ["Confidence", finding.confidence],
    ["Evidence window", finding.evidence.time_window || "Not specified"],
  ];
  document.querySelector("#dialog-details").innerHTML = detailRows.map(([label, value]) =>
    `<dt>${escapeHtml(label)}</dt><dd>${escapeHtml(value)}</dd>`).join("");
  findingDialog.showModal();
}

async function loadDashboard() {
  const searchParams = filters();
  const [summary, result] = await Promise.all([
    requestJson(`/api/dashboard?${searchParams}`),
    requestJson(`/api/findings?${searchParams}`),
  ]);
  findings = result.findings;
  renderDashboard(summary);
  renderFindings();
}

providerFilter.addEventListener("change", () => loadDashboard().catch((error) => showToast(error.message, true)));
categoryFilter.addEventListener("change", () => loadDashboard().catch((error) => showToast(error.message, true)));

let searchTimer;
searchInput.addEventListener("input", () => {
  window.clearTimeout(searchTimer);
  searchTimer = window.setTimeout(async () => {
    try {
      const params = filters();
      if (searchInput.value.trim()) params.set("q", searchInput.value.trim());
      const result = await requestJson(`/api/findings?${params}`);
      findings = result.findings;
      renderFindings();
    } catch (error) {
      showToast(error.message, true);
    }
  }, 180);
});

scanButton.addEventListener("click", async () => {
  scanButton.disabled = true;
  scanButton.innerHTML = '<span aria-hidden="true">↻</span> Running demo…';
  try {
    const result = await requestJson("/api/scan", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ provider: providerFilter.value, category: categoryFilter.value }),
    });
    await loadDashboard();
    document.querySelector("#updated-label").textContent = `Updated ${new Date().toLocaleTimeString([], { hour: "numeric", minute: "2-digit" })}`;
    showToast(result.message);
  } catch (error) {
    showToast(error.message, true);
  } finally {
    scanButton.disabled = false;
    scanButton.innerHTML = '<span aria-hidden="true">↻</span> Run demo scan';
  }
});

// Real AWS scan button
const realScanButton = document.querySelector("#real-scan-button");
if (realScanButton) {
  realScanButton.addEventListener("click", async () => {
    realScanButton.disabled = true;
    realScanButton.innerHTML = '<span aria-hidden="true">☁</span> Scanning AWS...';
    try {
      const result = await requestJson("/api/scan", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ scan_type: "real" }),
      });
      
      if (result.error) {
        showToast(`Scan failed: ${result.message}`, true);
      } else {
        // Update findings with real data
        findings = result.findings || [];
        renderDashboard(result);
        renderFindings();
        document.querySelector("#updated-label").textContent = `Real AWS scan - ${new Date().toLocaleTimeString([], { hour: "numeric", minute: "2-digit" })}`;
        showToast(result.message || `Found ${result.total_findings} real wasteful resources!`);
      }
    } catch (error) {
      showToast(`AWS scan error: ${error.message}`, true);
    } finally {
      realScanButton.disabled = false;
      realScanButton.innerHTML = '<span aria-hidden="true">☁</span> Scan Real AWS';
    }
  });
}

loadDashboard().catch((error) => showToast(`Could not load dashboard: ${error.message}`, true));
