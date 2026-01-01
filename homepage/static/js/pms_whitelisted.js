/* =====================================================
   PMS WHITELISTED PAGE SCRIPT
   ===================================================== */

let ALL_SCHEMES = [];
let CURRENT_FILTER = "all";
let CURRENT_SORT = "returns";

/* =====================================================
   INIT
   ===================================================== */
document.addEventListener("DOMContentLoaded", () => {
  fetchSchemes();
  bindUIEvents();
});

/* =====================================================
   FETCH DATA
   ===================================================== */
function fetchSchemes() {
  fetch(window.PMS_DATA_URL)
    .then(res => res.json())
    .then(data => {
      ALL_SCHEMES = data.schemes || [];
      renderMostWatched();
      renderTable();
    })
    .catch(err => {
      console.error("Failed to load PMS data", err);
    });
}

/* =====================================================
   EVENT BINDINGS
   ===================================================== */
function bindUIEvents() {
  // Search
  document.getElementById("search-input").addEventListener("input", renderTable);

  // Sort
  document.getElementById("sort-select").addEventListener("change", e => {
    CURRENT_SORT = e.target.value;
    renderTable();
  });

  // Category filters
  document.querySelectorAll(".pms-watched-filters button").forEach(btn => {
    btn.addEventListener("click", () => {
      document.querySelectorAll(".pms-watched-filters button")
        .forEach(b => b.classList.remove("active"));

      btn.classList.add("active");
      CURRENT_FILTER = btn.dataset.filter.toLowerCase();
      renderTable();
    });
  });
}

/* =====================================================
   MOST WATCHED SCHEMES (TOP 6)
   ===================================================== */
function renderMostWatched() {
  const grid = document.getElementById("pms-watched-grid");
  grid.innerHTML = "";

  const topSchemes = [...ALL_SCHEMES]
    .sort((a, b) => (b.one_year_return || 0) - (a.one_year_return || 0))
    .slice(0, 6);

  topSchemes.forEach(s => {
    grid.innerHTML += `
      <div class="pms-watched-card" onclick="openModal('${s.name}', '${s.provider}')">
        <h4>${s.name || "—"}</h4>
        <p>${s.provider}</p>
        <span class="pms-return">
          ${s.one_year_return ?? "—"}%
        </span>
      </div>
    `;
  });
}

/* =====================================================
   TABLE RENDER
   ===================================================== */
function renderTable() {
  const tbody = document.getElementById("schemes-list");
  const thead = document.getElementById("schemes-head");

  thead.innerHTML = `
    <tr>
      <th>Scheme</th>
      <th>Provider</th>
      <th>Category</th>
      <th>1Y Return</th>
      <th>3Y Return</th>
      <th>Min Investment</th>
    </tr>
  `;

  tbody.innerHTML = "";

  let filtered = filterSchemes();
  filtered = sortSchemes(filtered);

  if (filtered.length === 0) {
    tbody.innerHTML = `
      <tr>
        <td colspan="6" class="pms-empty">No schemes found</td>
      </tr>
    `;
    return;
  }

  filtered.forEach(s => {
    tbody.innerHTML += `
      <tr onclick="openModal('${s.name}', '${s.provider}')">
        <td>${s.name || "—"}</td>
        <td>${s.provider}</td>
        <td>${s.category || "—"}</td>
        <td>${formatReturn(s.one_year_return)}</td>
        <td>${formatReturn(s.three_year_return)}</td>
        <td>${s.min_inv || "—"}</td>
      </tr>
    `;
  });
}

/* =====================================================
   FILTER & SORT
   ===================================================== */
function filterSchemes() {
  const query = document.getElementById("search-input").value.toLowerCase();

  return ALL_SCHEMES.filter(s => {
    const matchesSearch =
      (s.name || "").toLowerCase().includes(query) ||
      (s.provider || "").toLowerCase().includes(query);

    const matchesCategory =
      CURRENT_FILTER === "all" ||
      (s.category || "").toLowerCase() === CURRENT_FILTER;

    return matchesSearch && matchesCategory;
  });
}

function sortSchemes(data) {
  if (CURRENT_SORT === "name") {
    return data.sort((a, b) => (a.name || "").localeCompare(b.name || ""));
  }

  // Default: sort by returns
  return data.sort(
    (a, b) => (b.one_year_return || 0) - (a.one_year_return || 0)
  );
}

/* =====================================================
   MODAL
   ===================================================== */
function openModal(title, provider) {
  document.getElementById("modal-title").innerText = title;
  document.getElementById("modal-content").innerHTML = `
    <p><strong>Provider:</strong> ${provider}</p>
    <p>This is a placeholder for full scheme details.</p>
  `;
  document.getElementById("modal").classList.add("active");
}

function closeModal() {
  document.getElementById("modal").classList.remove("active");
}

/* =====================================================
   HELPERS
   ===================================================== */
function formatReturn(val) {
  return val !== null && val !== undefined ? `${val}%` : "—";
}
