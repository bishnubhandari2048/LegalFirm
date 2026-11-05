// ============================================================================
// विधि ल फर्म व्यवस्थापन प्रणाली (Vidhi Law Firm Management System) - Frontend JS
// ============================================================================

let currentUser = null;
let cachedClients = [];
let cachedCases = [];
let cachedStaff = [];
let currentBsDate = "2083-07-18";

const COURT_SUGGESTIONS = [
  "सर्वोच्च अदालत (Supreme Court of Nepal)",
  "उच्च अदालत पाटन (High Court Patan)",
  "काठमाडौँ जिल्ला अदालत (Kathmandu District Court)",
  "ललितपुर जिल्ला अदालत (Lalitpur District Court)",
  "भक्तपुर जिल्ला अदालत (Bhaktapur District Court)",
  "विशेष अदालत, काठमाडौँ (Special Court)",
  "श्रम अदालत, काठमाडौँ (Labour Court)",
  "राजस्व न्यायाधिकरण (Revenue Tribunal)",
  "ऋण असुली न्यायाधिकरण (Debt Recovery Tribunal)"
];

const CASE_TYPES = [
  "अंशबण्डा (Partition of Property)",
  "लेनदेन (Loan / Recovery)",
  "सम्बन्ध विच्छेद र अंश (Divorce & Alimony)",
  "चेक अनादर / लेनदेन (Cheque Bounce & Recovery)",
  "दूषित लिखत बदर र जालसाजी (Deed Cancellation & Fraud)",
  "जग्गा खिचलो (Land Dispute)",
  "रिट निवेदन (Writ Petition)",
  "मानाचामल (Alimony / Maintenance)",
  "घरेलु हिंसा (Domestic Violence)",
  "बैंकिङ कसूर (Banking Offense)",
  "फौजदारी (Criminal Defense)",
  "कर्पोरेट तथा करार (Corporate & Contract)"
];

const HEARING_STATUS_OPTIONS = [
  "तारेख (Tarekh)",
  "साधारण तारेख (General Tarekh)",
  "बहस / पेशी तोकिएको (Scheduled for Arguments)",
  "आदेश (Court Order)",
  "प्रमाण बुझ्ने / साक्षी बकपत्र (Witness / Evidence)",
  "स्थगित (Postponed)",
  "हेर्न नभ्याइने (Not Reached)",
  "हेर्दाहेर्दै (Part Heard)",
  "मिलापत्र (Settlement / Mediation)",
  "फैसला (Final Verdict)"
];

const PAYMENT_METHODS = [
  "नगद (Cash)",
  "बैंक ट्रान्सफर (Bank Transfer)",
  "चेक (Cheque)",
  "eSewa",
  "Khalti",
  "ConnectIPS",
  "मोबाइल बैंकिङ (Mobile Banking)"
];

function fmtNPR(num) {
  const n = Number(num || 0);
  return "रु. " + n.toLocaleString("en-IN", { minimumFractionDigits: 0, maximumFractionDigits: 2 });
}

function showToast(msg, isError = false) {
  const el = document.getElementById("toast");
  el.textContent = msg;
  el.className = `fixed bottom-5 right-5 z-50 px-5 py-3 rounded-xl shadow-2xl text-white font-semibold text-sm transition ${
    isError ? "bg-rose-600" : "bg-emerald-700"
  }`;
  el.classList.remove("hidden");
  setTimeout(() => el.classList.add("hidden"), 3500);
}

async function apiFetch(url, options = {}) {
  const token = localStorage.getItem("vidhi_token");
  const headers = options.headers || {};
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }
  if (!(options.body instanceof FormData) && !headers["Content-Type"]) {
    headers["Content-Type"] = "application/json";
  }
  const resp = await fetch(url, { ...options, headers });
  if (resp.status === 401) {
    localStorage.removeItem("vidhi_token");
    document.getElementById("login-screen").classList.remove("hidden");
    document.getElementById("app-shell").classList.add("hidden");
    throw new Error("कृपया पुनः लगइन गर्नुहोस् (Session expired)");
  }
  const data = await resp.json().catch(() => ({}));
  if (!resp.ok) {
    throw new Error(data.detail || "प्रक्रिया सफल हुन सकेन (Request failed)");
  }
  return data;
}

// ============================================================================
// AUTHENTICATION
// ============================================================================
function fillLogin(u, p) {
  document.getElementById("login-username").value = u;
  document.getElementById("login-password").value = p;
}

document.getElementById("login-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const errBox = document.getElementById("login-error");
  errBox.classList.add("hidden");
  const username = document.getElementById("login-username").value.trim();
  const password = document.getElementById("login-password").value;

  try {
    const res = await fetch("/api/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password }),
    });
    const data = await res.json();
    if (!res.ok) {
      throw new Error(data.detail || "लगइन असफल भयो");
    }
    localStorage.setItem("vidhi_token", data.access_token);
    currentUser = data.user;
    enterApp();
  } catch (err) {
    errBox.textContent = err.message;
    errBox.classList.remove("hidden");
  }
});

async function checkSessionOnLoad() {
  const token = localStorage.getItem("vidhi_token");
  if (!token) return;
  try {
    currentUser = await apiFetch("/api/auth/me");
    enterApp();
  } catch (_) {
    localStorage.removeItem("vidhi_token");
  }
}

async function handleLogout() {
  try {
    await fetch("/api/auth/logout", { method: "POST" });
  } catch (_) {}
  localStorage.removeItem("vidhi_token");
  currentUser = null;
  document.getElementById("app-shell").classList.add("hidden");
  document.getElementById("login-screen").classList.remove("hidden");
}

async function enterApp() {
  document.getElementById("login-screen").classList.add("hidden");
  document.getElementById("app-shell").classList.remove("hidden");
  if (currentUser) {
    document.getElementById("user-display-name").textContent = currentUser.full_name;
    document.getElementById("user-display-role").textContent = `${currentUser.designation} (${currentUser.role})`;
  }
  await refreshReferenceLists();
  await switchTab("dashboard");
}

async function refreshReferenceLists() {
  try {
    const [clients, cases, staff] = await Promise.all([
      apiFetch("/api/clients"),
      apiFetch("/api/cases"),
      apiFetch("/api/staff"),
    ]);
    cachedClients = clients;
    cachedCases = cases;
    cachedStaff = staff;
  } catch (e) {
    console.warn("Could not preload reference lists:", e);
  }
}

// ============================================================================
// TAB NAVIGATION
// ============================================================================
const TAB_TITLES = {
  dashboard: ["📊 समग्र ड्यासबोर्ड र दैनिक पेशी सूची (Dashboard)", "आजको र आगामी पेशी, मुद्दाको संक्षिप्त तथ्याङ्क र आर्थिक सारांश"],
  clients: ["👥 क्लाइन्टको विवरण (Client Management)", "नाम, थर, ठेगाना, सम्पर्क नम्बर, इमेल र नागरिकता नम्बरको अभिलेख"],
  cases: ["📁 मुद्दाको विवरण (Case Management)", "मुद्दा नं., अदालतको नाम, मुद्दाको प्रकार, विपक्षी र दर्ता मितिको अभिलेख"],
  hearings: ["🏛️ पेशी तथा तारेख विवरण (Hearings & Tarekh)", "पेशी मिति, पेशीको अवस्था (तारेख, बहस, फैसला, स्थगित), अर्को पेशी र नतिजा"],
  finance: ["💰 आर्थिक तथा रसिद विवरण (Financials & Receipts)", "सहमति शुल्क (Deal), प्राप्त रकम (Paid), बाँकी रकम (Due), माध्यम र रसिद नम्बर"],
  documents: ["📄 कागजात सम्बन्धी विवरण (Documents & Handover)", "प्राप्त कागजातहरूको सूची, मूल वा प्रतिलिपि, र बुझाएको/फिर्ता गरेको मिति"],
  staff: ["👨‍⚖️ वकिल तथा कर्मचारी विवरण (Advocates & Staff)", "जिम्मेवार अधिवक्ताको नाम, सहायक कर्मचारी र सम्पर्क विवरण"],
  tools: ["🔍 द्वन्द्व जाँच र मिति रूपान्तरण (Legal Utilities)", "विपक्षी द्वन्द्व जाँच (Conflict Check) र विक्रम संवत् ↔ ई.सं. रूपान्तरण"],
};

async function switchTab(tabName) {
  document.querySelectorAll(".tab-view").forEach((el) => el.classList.add("hidden"));
  document.querySelectorAll(".nav-btn").forEach((el) => el.classList.remove("nav-active"));

  const view = document.getElementById(`view-${tabName}`);
  const nav = document.getElementById(`nav-${tabName}`);
  if (view) view.classList.remove("hidden");
  if (nav) nav.classList.add("nav-active");

  if (TAB_TITLES[tabName]) {
    document.getElementById("page-title").textContent = TAB_TITLES[tabName][0];
    document.getElementById("page-subtitle").textContent = TAB_TITLES[tabName][1];
  }

  if (tabName === "dashboard") await loadDashboard();
  if (tabName === "clients") await loadClients();
  if (tabName === "cases") await loadCases();
  if (tabName === "hearings") await loadHearings();
  if (tabName === "finance") await loadFinance();
  if (tabName === "documents") await loadDocuments();
  if (tabName === "staff") await loadStaff();
}

// ============================================================================
// 1. DASHBOARD LOADER
// ============================================================================
async function loadDashboard() {
  try {
    const data = await apiFetch("/api/dashboard/stats");
    currentBsDate = data.today_bs || currentBsDate;
    document.getElementById("sidebar-date-bs").textContent = `वि.सं. ${data.today_bs} (${data.today_bs_human})`;
    document.getElementById("sidebar-date-ad").textContent = `ई.सं. (AD): ${data.today_ad}`;

    document.getElementById("kpi-clients").textContent = data.counts.total_clients;
    document.getElementById("kpi-cases").textContent = data.counts.total_cases;
    document.getElementById("kpi-cases-sub").textContent = `विचाराधीन: ${data.counts.active_cases} | फैसला/सम्पन्न: ${data.counts.decided_cases}`;
    document.getElementById("kpi-paid").textContent = fmtNPR(data.financials.total_paid_amount);
    document.getElementById("kpi-deal-sub").textContent = `कुल सहमति शुल्क: ${fmtNPR(data.financials.total_deal_amount)} (${data.financials.collection_rate}% असुली)`;
    document.getElementById("kpi-due").textContent = fmtNPR(data.financials.total_due_amount);
    document.getElementById("kpi-docs-sub").textContent = `कार्यालयमा सुरक्षित मूल कागजात: ${data.counts.original_docs_held} थान`;

    const clBody = document.getElementById("dashboard-causelist-body");
    if (!data.cause_list.length) {
      clBody.innerHTML = `<tr><td colspan="7" class="p-6 text-center text-slate-400">कुनै आगामी पेशी तोकिएको छैन</td></tr>`;
    } else {
      clBody.innerHTML = data.cause_list
        .map(
          (c) => `
        <tr class="hover:bg-amber-50/40 transition ${c.is_today ? "bg-amber-50/80" : ""}">
          <td class="py-3 px-4 font-bold text-slate-900">
            <span class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs font-bold ${
              c.is_today ? "bg-red-600 text-white" : "bg-amber-100 text-amber-900"
            }">
              📅 ${c.next_hearing_date_bs} ${c.is_today ? "(आज)" : ""}
            </span>
          </td>
          <td class="py-3 px-4">
            <button onclick="openCaseDetailModal(${c.case_id})" class="font-bold text-blue-700 hover:underline">${c.case_number}</button>
            <div class="text-xs text-slate-500">${c.case_type}</div>
          </td>
          <td class="py-3 px-4">
            <div class="font-medium text-slate-800">${c.court_name}</div>
            <div class="text-xs text-slate-500">${c.bench_section || ""}</div>
          </td>
          <td class="py-3 px-4">
            <div class="font-semibold text-slate-900">${c.client_name}</div>
            <div class="text-xs text-rose-700">वि. ${c.opponent_name}</div>
          </td>
          <td class="py-3 px-4">
            <div class="font-medium text-slate-800">👨‍⚖️ ${c.advocate_name}</div>
            ${c.assistant_name ? `<div class="text-xs text-slate-500">सहायक: ${c.assistant_name}</div>` : ""}
          </td>
          <td class="py-3 px-4">
            <span class="px-2.5 py-1 rounded-full text-xs font-semibold bg-blue-50 text-blue-700 border border-blue-200">${c.status}</span>
          </td>
          <td class="py-3 px-4 text-right space-x-1">
            <button onclick="openCaseDetailModal(${c.case_id})" class="px-2.5 py-1 bg-slate-100 hover:bg-slate-200 rounded text-xs font-semibold">फाइल</button>
            <button onclick="openHearingModal(${c.case_id})" class="px-2.5 py-1 bg-blue-600 text-white rounded text-xs font-semibold">+ पेशी</button>
          </td>
        </tr>`
        )
        .join("");
    }

    // Case type breakdown
    const typesEl = document.getElementById("dashboard-case-types");
    const entries = Object.entries(data.case_type_distribution || {});
    typesEl.innerHTML = entries.length
      ? entries
          .map(
            ([t, cnt]) => `
        <div class="flex justify-between items-center p-2.5 bg-slate-50 rounded-xl border border-slate-200">
          <span class="font-semibold text-slate-800">${t}</span>
          <span class="px-3 py-0.5 bg-slate-900 text-amber-400 rounded-full text-xs font-bold">${cnt} मुद्दा</span>
        </div>`
          )
          .join("")
      : `<p class="text-slate-400 text-xs">कुनै विवरण छैन</p>`;

    // Recent hearings
    const recEl = document.getElementById("dashboard-recent-hearings");
    recEl.innerHTML = (data.recent_hearings || []).length
      ? data.recent_hearings
          .map(
            (h) => `
        <div class="p-3 bg-slate-50 rounded-xl border border-slate-200">
          <div class="flex justify-between items-center">
            <span class="font-bold text-slate-900">${h.case_number} — ${h.hearing_status}</span>
            <span class="text-xs font-semibold text-amber-800 bg-amber-100 px-2 py-0.5 rounded">पेशी: ${h.hearing_date_bs}</span>
          </div>
          <p class="text-xs text-slate-600 mt-1">${h.outcome || "-"}</p>
          ${h.next_hearing_date_bs ? `<p class="text-[11px] text-blue-700 font-semibold mt-1">अर्को पेशी मिति: ${h.next_hearing_date_bs}</p>` : ""}
        </div>`
          )
          .join("")
      : `<p class="text-slate-400 text-xs">कुनै पेशी विवरण छैन</p>`;
  } catch (err) {
    showToast(err.message, true);
  }
}

// ============================================================================
// 2. CLIENTS (क्लाइन्टको विवरण)
// ============================================================================
async function loadClients() {
  const q = document.getElementById("client-search")?.value || "";
  const clients = await apiFetch(`/api/clients?search=${encodeURIComponent(q)}`);
  cachedClients = clients;
  const tbody = document.getElementById("clients-table-body");
  if (!clients.length) {
    tbody.innerHTML = `<tr><td colspan="7" class="p-8 text-center text-slate-400">कुनै क्लाइन्ट भेटिएन</td></tr>`;
    return;
  }
  tbody.innerHTML = clients
    .map(
      (c, idx) => `
    <tr class="hover:bg-slate-50 transition">
      <td class="py-3.5 px-4 font-bold text-slate-500">${idx + 1}</td>
      <td class="py-3.5 px-4">
        <div class="font-bold text-slate-900 text-base">${c.full_name}</div>
        <div class="text-xs text-slate-500">नाम: ${c.first_name} | थर: ${c.last_name}</div>
        ${c.father_or_spouse_name ? `<div class="text-xs text-slate-500">बाबु/पति/पत्नी: ${c.father_or_spouse_name}</div>` : ""}
      </td>
      <td class="py-3.5 px-4">
        <div class="font-medium text-slate-800">${c.address}</div>
        ${c.district ? `<div class="text-xs text-slate-500">जिल्ला: ${c.district}</div>` : ""}
      </td>
      <td class="py-3.5 px-4">
        <div class="font-bold text-slate-800">📞 ${c.phone}</div>
        ${c.alt_phone ? `<div class="text-xs text-slate-500">वैकल्पिक: ${c.alt_phone}</div>` : ""}
        ${c.email ? `<div class="text-xs text-blue-600">✉️ ${c.email}</div>` : `<div class="text-xs text-slate-400">इमेल: -</div>`}
      </td>
      <td class="py-3.5 px-4">
        <span class="px-2.5 py-1 bg-slate-100 border border-slate-300 rounded font-mono text-xs font-bold text-slate-900">🪪 ${c.citizenship_no}</span>
        <div class="text-xs text-slate-500 mt-1">${c.citizenship_district || ""} ${c.citizenship_issue_date_bs ? `(${c.citizenship_issue_date_bs})` : ""}</div>
      </td>
      <td class="py-3.5 px-4">
        <div class="font-bold text-slate-800">${c.case_count} मुद्दा</div>
        <div class="text-xs text-emerald-700">प्राप्त: ${fmtNPR(c.total_paid)}</div>
        <div class="text-xs text-rose-600">बाँकी: ${fmtNPR(c.total_due)}</div>
      </td>
      <td class="py-3.5 px-4 text-right space-x-1">
        <button onclick='openClientModal(${JSON.stringify(c).replace(/'/g, "&#39;")})' class="px-2.5 py-1 bg-slate-100 hover:bg-slate-200 rounded text-xs font-semibold">सम्पादन</button>
        <button onclick="deleteClient(${c.id})" class="px-2.5 py-1 bg-rose-50 hover:bg-rose-100 text-rose-600 rounded text-xs font-semibold">हटाउनुहोस्</button>
      </td>
    </tr>`
    )
    .join("");
}

function openClientModal(client = null) {
  const isEdit = !!client;
  openModal(
    isEdit ? "👥 क्लाइन्टको विवरण सम्पादन गर्नुहोस् (Edit Client)" : "👥 नयाँ क्लाइन्ट दर्ता गर्नुहोस् (Add New Client)",
    `
    <form id="client-form" class="space-y-4">
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label class="block text-xs font-bold text-slate-700 mb-1">नाम (First Name) *</label>
          <input type="text" name="first_name" required value="${client?.first_name || ""}" placeholder="जस्तै: हरिबहादुर" class="w-full px-3 py-2 border rounded-lg" />
        </div>
        <div>
          <label class="block text-xs font-bold text-slate-700 mb-1">थर (Last Name / Surname) *</label>
          <input type="text" name="last_name" required value="${client?.last_name || ""}" placeholder="जस्तै: श्रेष्ठ" class="w-full px-3 py-2 border rounded-lg" />
        </div>
        <div>
          <label class="block text-xs font-bold text-slate-700 mb-1">ठेगाना (Full Address) *</label>
          <input type="text" name="address" required value="${client?.address || ""}" placeholder="काठमाडौँ म.न.पा.-१०, बानेश्वर" class="w-full px-3 py-2 border rounded-lg" />
        </div>
        <div>
          <label class="block text-xs font-bold text-slate-700 mb-1">जिल्ला (District)</label>
          <input type="text" name="district" value="${client?.district || ""}" placeholder="काठमाडौँ" class="w-full px-3 py-2 border rounded-lg" />
        </div>
        <div>
          <label class="block text-xs font-bold text-slate-700 mb-1">सम्पर्क नम्बर (Contact Phone) *</label>
          <input type="text" name="phone" required value="${client?.phone || ""}" placeholder="9851XXXXXX" class="w-full px-3 py-2 border rounded-lg" />
        </div>
        <div>
          <label class="block text-xs font-bold text-slate-700 mb-1">इमेल (Email - भएमा)</label>
          <input type="email" name="email" value="${client?.email || ""}" placeholder="client@example.com" class="w-full px-3 py-2 border rounded-lg" />
        </div>
        <div>
          <label class="block text-xs font-bold text-slate-700 mb-1">नागरिकता नम्बर (Citizenship No.) *</label>
          <input type="text" name="citizenship_no" required value="${client?.citizenship_no || ""}" placeholder="२७-०१-७१-०४५२१" class="w-full px-3 py-2 border rounded-lg" />
        </div>
        <div>
          <label class="block text-xs font-bold text-slate-700 mb-1">नागरिकता जारी जिल्ला र मिति (वि.सं.)</label>
          <div class="flex gap-2">
            <input type="text" name="citizenship_district" value="${client?.citizenship_district || ""}" placeholder="जिल्ला" class="w-1/2 px-3 py-2 border rounded-lg" />
            <input type="text" name="citizenship_issue_date_bs" value="${client?.citizenship_issue_date_bs || ""}" placeholder="2072-05-10" class="w-1/2 px-3 py-2 border rounded-lg" />
          </div>
        </div>
        <div>
          <label class="block text-xs font-bold text-slate-700 mb-1">बाबु / पति / पत्नीको नाम (तीनपुस्ते विवरण)</label>
          <input type="text" name="father_or_spouse_name" value="${client?.father_or_spouse_name || ""}" placeholder="वकालतनामाका लागि उपयोगी" class="w-full px-3 py-2 border rounded-lg" />
        </div>
        <div>
          <label class="block text-xs font-bold text-slate-700 mb-1">पेशा (Occupation)</label>
          <input type="text" name="occupation" value="${client?.occupation || ""}" placeholder="व्यापार / सेवा / कृषि" class="w-full px-3 py-2 border rounded-lg" />
        </div>
      </div>
      <div>
        <label class="block text-xs font-bold text-slate-700 mb-1">थप विवरण / कैफियत (Notes)</label>
        <textarea name="notes" rows="2" class="w-full px-3 py-2 border rounded-lg">${client?.notes || ""}</textarea>
      </div>
      <div class="flex justify-end gap-2 pt-3 border-t">
        <button type="button" onclick="closeModal()" class="px-4 py-2 bg-slate-200 rounded-lg font-semibold">रद्द गर्नुहोस्</button>
        <button type="submit" class="px-5 py-2 bg-amber-600 hover:bg-amber-700 text-white rounded-lg font-bold shadow">सुरक्षित गर्नुहोस् (Save Client)</button>
      </div>
    </form>`
  );

  document.getElementById("client-form").onsubmit = async (e) => {
    e.preventDefault();
    const payload = Object.fromEntries(new FormData(e.target).entries());
    try {
      if (isEdit) {
        await apiFetch(`/api/clients/${client.id}`, { method: "PUT", body: JSON.stringify(payload) });
        showToast("क्लाइन्टको विवरण अद्यावधिक गरियो");
      } else {
        await apiFetch("/api/clients", { method: "POST", body: JSON.stringify(payload) });
        showToast("नयाँ क्लाइन्ट सफलतापूर्वक दर्ता गरियो");
      }
      closeModal();
      await refreshReferenceLists();
      await loadClients();
      await loadDashboard();
    } catch (err) {
      showToast(err.message, true);
    }
  };
}

async function deleteClient(id) {
  if (!confirm("के तपाईं यो क्लाइन्ट र सम्बन्धित विवरण हटाउन चाहनुहुन्छ?")) return;
  try {
    await apiFetch(`/api/clients/${id}`, { method: "DELETE" });
    showToast("क्लाइन्ट विवरण हटाइयो");
    await refreshReferenceLists();
    await loadClients();
  } catch (err) {
    showToast(err.message, true);
  }
}

// ============================================================================
// 3. CASES (मुद्दाको विवरण) + 360 CASE FILE VIEW
// ============================================================================
async function loadCases() {
  const search = document.getElementById("case-search")?.value || "";
  const caseType = document.getElementById("case-type-filter")?.value || "";
  const url = `/api/cases?search=${encodeURIComponent(search)}&case_type=${encodeURIComponent(caseType)}`;
  const cases = await apiFetch(url);
  cachedCases = cases;

  const tbody = document.getElementById("cases-table-body");
  if (!cases.length) {
    tbody.innerHTML = `<tr><td colspan="7" class="p-8 text-center text-slate-400">कुनै मुद्दाको विवरण भेटिएन</td></tr>`;
    return;
  }
  tbody.innerHTML = cases
    .map(
      (c) => `
    <tr class="hover:bg-slate-50 transition">
      <td class="py-3.5 px-4">
        <button onclick="openCaseDetailModal(${c.id})" class="font-extrabold text-blue-700 hover:underline text-base">${c.case_number}</button>
        <div class="text-xs text-slate-500">दर्ता मिति: <strong>${c.registration_date_bs}</strong></div>
        ${c.filing_number ? `<div class="text-[11px] text-slate-400">${c.filing_number}</div>` : ""}
      </td>
      <td class="py-3.5 px-4">
        <div class="font-bold text-slate-900">${c.court_name}</div>
        <span class="inline-block mt-1 px-2 py-0.5 bg-amber-100 text-amber-900 rounded text-xs font-semibold">${c.case_type}</span>
        ${c.bench_section ? `<div class="text-xs text-slate-500 mt-0.5">${c.bench_section}</div>` : ""}
      </td>
      <td class="py-3.5 px-4">
        <div class="font-bold text-slate-900">पक्ष: ${c.client_name} <span class="text-xs font-normal text-slate-500">(${c.client_party_role})</span></div>
        <div class="text-xs font-semibold text-rose-700 mt-0.5">विपक्षी: ${c.opponent_name}</div>
        ${c.opponent_counsel ? `<div class="text-[11px] text-slate-500">विपक्षी वकिल: ${c.opponent_counsel}</div>` : ""}
      </td>
      <td class="py-3.5 px-4">
        <div class="font-semibold text-slate-800">👨‍⚖️ ${c.advocate_name}</div>
        <div class="text-xs text-slate-500">सहायक: ${c.assistant_name}</div>
      </td>
      <td class="py-3.5 px-4">
        <div class="text-xs font-bold text-amber-800">अर्को पेशी: ${c.next_hearing_date_bs || "-"}</div>
        <span class="inline-block mt-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-blue-50 text-blue-800 border border-blue-200">${c.status}</span>
      </td>
      <td class="py-3.5 px-4 text-xs">
        <div>सहमति: <strong>${fmtNPR(c.deal_amount)}</strong></div>
        <div class="text-emerald-700">प्राप्त: <strong>${fmtNPR(c.paid_amount)}</strong></div>
        <div class="text-rose-600">बाँकी: <strong>${fmtNPR(c.due_amount)}</strong></div>
      </td>
      <td class="py-3.5 px-4 text-right space-x-1">
        <button onclick="openCaseDetailModal(${c.id})" class="px-2.5 py-1 bg-slate-900 text-amber-400 rounded text-xs font-bold">पूर्ण फाइल</button>
        <a href="/print/case/${c.id}" target="_blank" class="inline-block px-2 py-1 bg-slate-100 hover:bg-slate-200 rounded text-xs font-semibold">🖨️</a>
        <button onclick='openCaseModal(${JSON.stringify(c).replace(/'/g, "&#39;")})' class="px-2 py-1 bg-slate-100 hover:bg-slate-200 rounded text-xs">सम्पादन</button>
      </td>
    </tr>`
    )
    .join("");
}

function openCaseModal(caseObj = null) {
  const isEdit = !!caseObj;
  const clientOpts = cachedClients
    .map((cl) => `<option value="${cl.id}" ${caseObj?.client_id === cl.id ? "selected" : ""}>${cl.full_name} (${cl.phone})</option>`)
    .join("");
  const advocates = cachedStaff.filter((s) => s.role === "advocate" || s.role === "admin");
  const staffList = cachedStaff;

  const advOpts = `<option value="">-- छान्नुहोस् --</option>` + advocates
    .map((a) => `<option value="${a.id}" ${caseObj?.advocate_id === a.id ? "selected" : ""}>${a.full_name}</option>`)
    .join("");
  const asstOpts = `<option value="">-- छान्नुहोस् --</option>` + staffList
    .map((s) => `<option value="${s.id}" ${caseObj?.assistant_id === s.id ? "selected" : ""}>${s.full_name} (${s.designation})</option>`)
    .join("");

  const courtDatalist = COURT_SUGGESTIONS.map((ct) => `<option value="${ct}">`).join("");
  const typeDatalist = CASE_TYPES.map((t) => `<option value="${t}">`).join("");

  openModal(
    isEdit ? "📁 मुद्दाको विवरण सम्पादन गर्नुहोस् (Edit Case)" : "📁 नयाँ मुद्दा दर्ता गर्नुहोस् (Register New Case)",
    `
    <form id="case-form" class="space-y-4">
      <div class="grid grid-cols-1 md:grid-cols-3 gap-3">
        <div>
          <label class="block text-xs font-bold text-slate-700 mb-1">मुद्दा नम्बर (Case No.) *</label>
          <input type="text" name="case_number" required value="${caseObj?.case_number || ""}" placeholder="०८३-CP-०५०१" class="w-full px-3 py-2 border rounded-lg" />
        </div>
        <div>
          <label class="block text-xs font-bold text-slate-700 mb-1">दर्ता / दायर नम्बर (Filing No.)</label>
          <input type="text" name="filing_number" value="${caseObj?.filing_number || ""}" placeholder="दर्ता नं. १२३४/०८३" class="w-full px-3 py-2 border rounded-lg" />
        </div>
        <div>
          <label class="block text-xs font-bold text-slate-700 mb-1">मुद्दा दर्ता मिति (वि.सं.) *</label>
          <input type="text" name="registration_date_bs" required value="${caseObj?.registration_date_bs || currentBsDate}" placeholder="2083-07-18" class="w-full px-3 py-2 border rounded-lg" />
        </div>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
        <div>
          <label class="block text-xs font-bold text-slate-700 mb-1">अदालतको नाम (Court Name) *</label>
          <input list="court-list" name="court_name" required value="${caseObj?.court_name || ""}" placeholder="काठमाडौँ जिल्ला अदालत" class="w-full px-3 py-2 border rounded-lg" />
          <datalist id="court-list">${courtDatalist}</datalist>
        </div>
        <div>
          <label class="block text-xs font-bold text-slate-700 mb-1">मुद्दाको प्रकार (अंशबण्डा, लेनदेन, सम्बन्ध विच्छेद आदि) *</label>
          <input list="casetype-list" name="case_type" required value="${caseObj?.case_type || ""}" placeholder="अंशबण्डा / लेनदेन / सम्बन्ध विच्छेद" class="w-full px-3 py-2 border rounded-lg" />
          <datalist id="casetype-list">${typeDatalist}</datalist>
        </div>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-3 gap-3">
        <div class="md:col-span-2">
          <label class="block text-xs font-bold text-slate-700 mb-1">क्लाइन्ट छान्नुहोस् (Client) *</label>
          <select name="client_id" required class="w-full px-3 py-2 border rounded-lg bg-white">${clientOpts}</select>
        </div>
        <div>
          <label class="block text-xs font-bold text-slate-700 mb-1">पक्षको हैसियत (Party Role)</label>
          <select name="client_party_role" class="w-full px-3 py-2 border rounded-lg bg-white">
            <option value="वादी (Plaintiff)" ${caseObj?.client_party_role === "वादी (Plaintiff)" ? "selected" : ""}>वादी (Plaintiff)</option>
            <option value="प्रतिवादी (Defendant)" ${caseObj?.client_party_role === "प्रतिवादी (Defendant)" ? "selected" : ""}>प्रतिवादी (Defendant)</option>
            <option value="निवेदक (Petitioner)" ${caseObj?.client_party_role === "निवेदक (Petitioner)" ? "selected" : ""}>निवेदक (Petitioner)</option>
            <option value="पुनरावेदक (Appellant)" ${caseObj?.client_party_role === "पुनरावेदक (Appellant)" ? "selected" : ""}>पुनरावेदक (Appellant)</option>
          </select>
        </div>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-3 gap-3 bg-rose-50/50 p-3 rounded-xl border border-rose-100">
        <div>
          <label class="block text-xs font-bold text-rose-900 mb-1">विपक्षीको नाम (Opponent Name) *</label>
          <input type="text" name="opponent_name" required value="${caseObj?.opponent_name || ""}" placeholder="विपक्षीको पूरा नाम" class="w-full px-3 py-2 border rounded-lg bg-white" />
        </div>
        <div>
          <label class="block text-xs font-bold text-rose-900 mb-1">विपक्षीको ठेगाना / सम्पर्क</label>
          <input type="text" name="opponent_address" value="${caseObj?.opponent_address || ""}" placeholder="ठेगाना वा फोन" class="w-full px-3 py-2 border rounded-lg bg-white" />
        </div>
        <div>
          <label class="block text-xs font-bold text-rose-900 mb-1">विपक्षीको वकिल (भएमा)</label>
          <input type="text" name="opponent_counsel" value="${caseObj?.opponent_counsel || ""}" placeholder="विपक्षी अधिवक्ता" class="w-full px-3 py-2 border rounded-lg bg-white" />
        </div>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-3 gap-3">
        <div>
          <label class="block text-xs font-bold text-slate-700 mb-1">जिम्मेवार अधिवक्ता (Lead Advocate)</label>
          <select name="advocate_id" class="w-full px-3 py-2 border rounded-lg bg-white">${advOpts}</select>
        </div>
        <div>
          <label class="block text-xs font-bold text-slate-700 mb-1">सहायक कर्मचारी (Assistant Staff)</label>
          <select name="assistant_id" class="w-full px-3 py-2 border rounded-lg bg-white">${asstOpts}</select>
        </div>
        <div>
          <label class="block text-xs font-bold text-slate-700 mb-1">अर्को पेशी मिति (वि.सं.)</label>
          <input type="text" name="next_hearing_date_bs" value="${caseObj?.next_hearing_date_bs || ""}" placeholder="2083-08-10" class="w-full px-3 py-2 border rounded-lg" />
        </div>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-3 gap-3 bg-emerald-50/60 p-3 rounded-xl border border-emerald-200">
        <div>
          <label class="block text-xs font-bold text-emerald-900 mb-1">सहमति भएको शुल्क (Deal Amount रु.) *</label>
          <input type="number" step="0.01" name="deal_amount" required value="${caseObj?.deal_amount ?? 50000}" class="w-full px-3 py-2 border rounded-lg bg-white" />
        </div>
        ${
          !isEdit
            ? `
        <div>
          <label class="block text-xs font-bold text-emerald-900 mb-1">शुरुमा प्राप्त पेश्की रकम (Paid Advance रु.)</label>
          <input type="number" step="0.01" name="initial_paid_amount" value="0" class="w-full px-3 py-2 border rounded-lg bg-white" />
        </div>
        <div>
          <label class="block text-xs font-bold text-emerald-900 mb-1">भुक्तानी माध्यम</label>
          <select name="initial_payment_method" class="w-full px-3 py-2 border rounded-lg bg-white">
            ${PAYMENT_METHODS.map((m) => `<option value="${m}">${m}</option>`).join("")}
          </select>
        </div>`
            : `
        <div>
          <label class="block text-xs font-bold text-slate-700 mb-1">मुद्दाको अवस्था (Case Status)</label>
          <select name="status" class="w-full px-3 py-2 border rounded-lg bg-white">
            <option value="विचाराधीन (Active)" ${caseObj?.status === "विचाराधीन (Active)" ? "selected" : ""}>विचाराधीन (Active)</option>
            <option value="तारेखमा / विचाराधीन (Active)" ${caseObj?.status === "तारेखमा / विचाराधीन (Active)" ? "selected" : ""}>तारेखमा (On Tarekh)</option>
            <option value="बहसको क्रममा (In Arguments)" ${caseObj?.status === "बहसको क्रममा (In Arguments)" ? "selected" : ""}>बहसको क्रममा</option>
            <option value="फैसला भएको (Decided)" ${caseObj?.status === "फैसला भएको (Decided)" ? "selected" : ""}>फैसला भएको (Decided)</option>
            <option value="मिलापत्र (Settled)" ${caseObj?.status === "मिलापत्र (Settled)" ? "selected" : ""}>मिलापत्र (Settled)</option>
            <option value="मुल्तबी (Stayed)" ${caseObj?.status === "मुल्तबी (Stayed)" ? "selected" : ""}>मुल्तबी (Stayed)</option>
          </select>
        </div>
        <div>
          <label class="block text-xs font-bold text-slate-700 mb-1">फाँट / इजलास</label>
          <input type="text" name="bench_section" value="${caseObj?.bench_section || ""}" placeholder="फाँट नं. ५" class="w-full px-3 py-2 border rounded-lg bg-white" />
        </div>`
        }
      </div>

      <div>
        <label class="block text-xs font-bold text-slate-700 mb-1">मुद्दाको संक्षिप्त व्यहोरा / फिराद मागदाबी (Case Summary)</label>
        <textarea name="summary" rows="2" class="w-full px-3 py-2 border rounded-lg">${caseObj?.summary || ""}</textarea>
      </div>

      <div class="flex justify-end gap-2 pt-3 border-t">
        <button type="button" onclick="closeModal()" class="px-4 py-2 bg-slate-200 rounded-lg font-semibold">रद्द गर्नुहोस्</button>
        <button type="submit" class="px-5 py-2 bg-amber-600 hover:bg-amber-700 text-white rounded-lg font-bold shadow">सुरक्षित गर्नुहोस् (Save Case)</button>
      </div>
    </form>`
  );

  document.getElementById("case-form").onsubmit = async (e) => {
    e.preventDefault();
    const raw = Object.fromEntries(new FormData(e.target).entries());
    const payload = {
      ...raw,
      client_id: Number(raw.client_id),
      deal_amount: Number(raw.deal_amount || 0),
      advocate_id: raw.advocate_id ? Number(raw.advocate_id) : null,
      assistant_id: raw.assistant_id ? Number(raw.assistant_id) : null,
    };
    if (!isEdit) {
      payload.initial_paid_amount = Number(raw.initial_paid_amount || 0);
    }
    try {
      if (isEdit) {
        await apiFetch(`/api/cases/${caseObj.id}`, { method: "PUT", body: JSON.stringify(payload) });
        showToast("मुद्दाको विवरण अद्यावधिक गरियो");
      } else {
        await apiFetch("/api/cases", { method: "POST", body: JSON.stringify(payload) });
        showToast("नयाँ मुद्दा सफलतापूर्वक दर्ता गरियो");
      }
      closeModal();
      await refreshReferenceLists();
      await loadCases();
      await loadDashboard();
    } catch (err) {
      showToast(err.message, true);
    }
  };
}

async function openCaseDetailModal(caseId) {
  try {
    const c = await apiFetch(`/api/cases/${caseId}`);
    openModal(
      `📁 मुद्दा फाइल: ${c.case_number} — ${c.case_type}`,
      `
      <div class="space-y-5">
        <div class="flex flex-wrap justify-between items-center gap-2 bg-slate-100 p-3.5 rounded-xl border">
          <div>
            <div class="font-extrabold text-slate-900 text-base">${c.case_title}</div>
            <div class="text-xs text-slate-600">${c.court_name} | दर्ता मिति: <strong>${c.registration_date_bs}</strong> | अवस्था: <strong>${c.status}</strong></div>
          </div>
          <a href="/print/case/${c.id}" target="_blank" class="px-3.5 py-1.5 bg-amber-600 text-white rounded-lg text-xs font-bold shadow">
            🖨️ पूर्ण फाइल प्रिन्ट (Print Dossier)
          </a>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-3 gap-3 text-xs">
          <div class="p-3 border rounded-xl bg-slate-50">
            <div class="font-bold text-slate-700 mb-1">👥 क्लाइन्ट र विपक्षी</div>
            <p>क्लाइन्ट: <strong>${c.client_name}</strong> (${c.client_phone})</p>
            <p>नागरिकता: ${c.client_citizenship}</p>
            <p class="text-rose-700 font-semibold mt-1">विपक्षी: ${c.opponent_name}</p>
            <p>विपक्षी वकिल: ${c.opponent_counsel || "-"}</p>
          </div>
          <div class="p-3 border rounded-xl bg-slate-50">
            <div class="font-bold text-slate-700 mb-1">👨‍⚖️ जिम्मेवार वकिल र कर्मचारी</div>
            <p>अधिवक्ता: <strong>${c.advocate_name}</strong> (${c.advocate_phone})</p>
            <p>सहायक: <strong>${c.assistant_name}</strong> (${c.assistant_phone})</p>
            <p>वारेस: ${c.waris_name || "-"}</p>
            <p class="text-amber-800 font-bold mt-1">अर्को पेशी: ${c.next_hearing_date_bs || "-"}</p>
          </div>
          <div class="p-3 border rounded-xl bg-emerald-50 border-emerald-200">
            <div class="font-bold text-emerald-900 mb-1">💰 आर्थिक विवरण</div>
            <p>सहमति शुल्क (Deal): <strong>${fmtNPR(c.deal_amount)}</strong></p>
            <p class="text-emerald-700">प्राप्त रकम (Paid): <strong>${fmtNPR(c.paid_amount)}</strong></p>
            <p class="text-rose-700">बाँकी रकम (Due): <strong>${fmtNPR(c.due_amount)}</strong></p>
          </div>
        </div>

        <!-- Hearings inside case -->
        <div>
          <div class="flex justify-between items-center mb-2">
            <h4 class="font-bold text-slate-800">🏛️ पेशी विवरण (${c.hearings.length})</h4>
            <button onclick="closeModal(); openHearingModal(${c.id})" class="px-2.5 py-1 bg-blue-600 text-white rounded text-xs font-bold">+ पेशी थप्नुहोस्</button>
          </div>
          <div class="border rounded-xl overflow-hidden">
            <table class="w-full text-xs">
              <thead class="bg-slate-800 text-white">
                <tr>
                  <th class="p-2 text-left">पेशी मिति</th>
                  <th class="p-2 text-left">अवस्था</th>
                  <th class="p-2 text-left">नतिजा / आदेश</th>
                  <th class="p-2 text-left">अर्को पेशी</th>
                </tr>
              </thead>
              <tbody class="divide-y">
                ${
                  c.hearings.length
                    ? c.hearings
                        .map(
                          (h) => `
                  <tr>
                    <td class="p-2 font-bold">${h.hearing_date_bs}</td>
                    <td class="p-2">${h.hearing_status}</td>
                    <td class="p-2">${h.outcome || "-"}</td>
                    <td class="p-2 font-semibold text-amber-800">${h.next_hearing_date_bs || "-"}</td>
                  </tr>`
                        )
                        .join("")
                    : `<tr><td colspan="4" class="p-3 text-center text-slate-400">कुनै पेशी विवरण छैन</td></tr>`
                }
              </tbody>
            </table>
          </div>
        </div>

        <!-- Documents inside case -->
        <div>
          <div class="flex justify-between items-center mb-2">
            <h4 class="font-bold text-slate-800">📄 कागजात सम्बन्धी विवरण (${c.documents.length})</h4>
            <button onclick="closeModal(); openDocumentModal(${c.id})" class="px-2.5 py-1 bg-amber-600 text-white rounded text-xs font-bold">+ कागजात थप्नुहोस्</button>
          </div>
          <div class="border rounded-xl overflow-hidden">
            <table class="w-full text-xs">
              <thead class="bg-slate-800 text-white">
                <tr>
                  <th class="p-2 text-left">कागजातको नाम</th>
                  <th class="p-2 text-left">प्रकार</th>
                  <th class="p-2 text-left">बुझाएको मिति</th>
                  <th class="p-2 text-left">फिर्ता मिति</th>
                  <th class="p-2 text-left">अवस्था</th>
                </tr>
              </thead>
              <tbody class="divide-y">
                ${
                  c.documents.length
                    ? c.documents
                        .map(
                          (d) => `
                  <tr>
                    <td class="p-2 font-semibold">${d.document_name}</td>
                    <td class="p-2">${d.document_type}</td>
                    <td class="p-2">${d.received_date_bs}</td>
                    <td class="p-2">${d.returned_date_bs || "-"}</td>
                    <td class="p-2">${d.status}</td>
                  </tr>`
                        )
                        .join("")
                    : `<tr><td colspan="5" class="p-3 text-center text-slate-400">कुनै कागजात दर्ता छैन</td></tr>`
                }
              </tbody>
            </table>
          </div>
        </div>
      </div>`
    );
  } catch (err) {
    showToast(err.message, true);
  }
}

// ============================================================================
// 4. HEARINGS / PESHI (पेशी विवरण)
// ============================================================================
async function loadHearings() {
  const search = document.getElementById("hearing-search")?.value || "";
  const status = document.getElementById("hearing-status-filter")?.value || "";
  const list = await apiFetch(`/api/hearings?search=${encodeURIComponent(search)}&hearing_status=${encodeURIComponent(status)}`);
  const tbody = document.getElementById("hearings-table-body");

  if (!list.length) {
    tbody.innerHTML = `<tr><td colspan="7" class="p-8 text-center text-slate-400">कुनै पेशी विवरण भेटिएन</td></tr>`;
    return;
  }

  tbody.innerHTML = list
    .map(
      (h) => `
    <tr class="hover:bg-slate-50 transition">
      <td class="py-3.5 px-4">
        <div class="font-extrabold text-slate-900">📅 ${h.hearing_date_bs}</div>
        <div class="text-xs text-slate-500">${h.hearing_date_bs_human}</div>
      </td>
      <td class="py-3.5 px-4">
        <button onclick="openCaseDetailModal(${h.case_id})" class="font-bold text-blue-700 hover:underline">${h.case_number}</button>
        <div class="text-xs text-slate-600">${h.court_name}</div>
        ${h.bench_or_judge ? `<div class="text-[11px] text-slate-500">${h.bench_or_judge}</div>` : ""}
      </td>
      <td class="py-3.5 px-4">
        <div class="font-semibold text-slate-800">${h.client_name}</div>
        <div class="text-xs text-rose-700">वि. ${h.opponent_name}</div>
      </td>
      <td class="py-3.5 px-4">
        <span class="px-2.5 py-1 rounded-full text-xs font-bold bg-amber-100 text-amber-900">${h.hearing_status}</span>
      </td>
      <td class="py-3.5 px-4 max-w-xs">
        <div class="text-xs text-slate-800 font-medium">${h.outcome || "-"}</div>
        ${h.attended_by_name ? `<div class="text-[11px] text-slate-500 mt-0.5">उपस्थित: ${h.attended_by_name}</div>` : ""}
      </td>
      <td class="py-3.5 px-4">
        <span class="font-bold text-blue-800">${h.next_hearing_date_bs || "-"}</span>
      </td>
      <td class="py-3.5 px-4 text-right">
        <button onclick="deleteHearing(${h.id})" class="px-2.5 py-1 bg-rose-50 hover:bg-rose-100 text-rose-600 rounded text-xs font-semibold">हटाउनुहोस्</button>
      </td>
    </tr>`
    )
    .join("");
}

function openHearingModal(preselectedCaseId = null) {
  const caseOpts = cachedCases
    .map(
      (c) =>
        `<option value="${c.id}" ${preselectedCaseId === c.id ? "selected" : ""}>${c.case_number} — ${c.client_name} वि. ${c.opponent_name}</option>`
    )
    .join("");
  const statusOpts = HEARING_STATUS_OPTIONS.map((s) => `<option value="${s}">${s}</option>`).join("");

  openModal(
    "🏛️ पेशी तथा तारेख विवरण थप्नुहोस् (Add Hearing / Peshi Record)",
    `
    <form id="hearing-form" class="space-y-4">
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div class="md:col-span-2">
          <label class="block text-xs font-bold text-slate-700 mb-1">सम्बन्धित मुद्दा छान्नुहोस् (Select Case) *</label>
          <select name="case_id" required class="w-full px-3 py-2 border rounded-lg bg-white">${caseOpts}</select>
        </div>
        <div>
          <label class="block text-xs font-bold text-slate-700 mb-1">पेशी मिति (वि.सं. BS Date) *</label>
          <input type="text" name="hearing_date_bs" required value="${currentBsDate}" placeholder="2083-07-18" class="w-full px-3 py-2 border rounded-lg" />
        </div>
        <div>
          <label class="block text-xs font-bold text-slate-700 mb-1">पेशीको अवस्था (तारेख, बहस, फैसला, स्थगित आदि) *</label>
          <input list="hstatus-list" name="hearing_status" required placeholder="तारेख / बहस / आदेश / फैसला / स्थगित" class="w-full px-3 py-2 border rounded-lg" />
          <datalist id="hstatus-list">${statusOpts}</datalist>
        </div>
        <div>
          <label class="block text-xs font-bold text-slate-700 mb-1">इजलास नं. / माननीय न्यायाधीशको नाम</label>
          <input type="text" name="bench_or_judge" placeholder="इजलास नं. ४" class="w-full px-3 py-2 border rounded-lg" />
        </div>
        <div>
          <label class="block text-xs font-bold text-slate-700 mb-1">अर्को पेशी वा तारेख मिति (वि.सं.)</label>
          <input type="text" name="next_hearing_date_bs" placeholder="2083-08-15" class="w-full px-3 py-2 border rounded-lg" />
        </div>
      </div>
      <div>
        <label class="block text-xs font-bold text-slate-700 mb-1">पेशीको नतिजा / आदेशको व्यहोरा (Hearing Outcome) *</label>
        <textarea name="outcome" rows="3" required placeholder="अदालतबाट भएको आदेश, प्रमाण बुझ्ने वा फैसलाको संक्षिप्त विवरण..." class="w-full px-3 py-2 border rounded-lg"></textarea>
      </div>
      <div class="flex justify-end gap-2 pt-3 border-t">
        <button type="button" onclick="closeModal()" class="px-4 py-2 bg-slate-200 rounded-lg font-semibold">रद्द गर्नुहोस्</button>
        <button type="submit" class="px-5 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-bold shadow">पेशी सुरक्षित गर्नुहोस्</button>
      </div>
    </form>`
  );

  document.getElementById("hearing-form").onsubmit = async (e) => {
    e.preventDefault();
    const raw = Object.fromEntries(new FormData(e.target).entries());
    const payload = { ...raw, case_id: Number(raw.case_id) };
    try {
      await apiFetch("/api/hearings", { method: "POST", body: JSON.stringify(payload) });
      showToast("पेशी विवरण सफलतापूर्वक थपियो");
      closeModal();
      await refreshReferenceLists();
      await loadHearings();
      await loadDashboard();
    } catch (err) {
      showToast(err.message, true);
    }
  };
}

async function deleteHearing(id) {
  if (!confirm("यो पेशी विवरण हटाउने हो?")) return;
  try {
    await apiFetch(`/api/hearings/${id}`, { method: "DELETE" });
    showToast("पेशी विवरण हटाइयो");
    await loadHearings();
  } catch (err) {
    showToast(err.message, true);
  }
}

// ============================================================================
// 5. FINANCIALS & RECEIPTS (आर्थिक विवरण)
// ============================================================================
async function loadFinance() {
  const search = document.getElementById("payment-search")?.value || "";
  const [summary, payments] = await Promise.all([
    apiFetch("/api/finance/summary"),
    apiFetch(`/api/finance/payments?search=${encodeURIComponent(search)}`),
  ]);

  document.getElementById("fin-total-deal").textContent = fmtNPR(summary.total_deal_amount);
  document.getElementById("fin-total-paid").textContent = fmtNPR(summary.total_paid_amount);
  document.getElementById("fin-total-due").textContent = fmtNPR(summary.total_due_amount);

  const ledgerBody = document.getElementById("finance-ledger-body");
  ledgerBody.innerHTML = (summary.case_ledgers || [])
    .map(
      (row) => `
    <tr class="hover:bg-slate-50">
      <td class="py-3 px-4">
        <button onclick="openCaseDetailModal(${row.case_id})" class="font-bold text-blue-700 hover:underline">${row.case_number}</button>
        <div class="text-xs text-slate-500">${row.case_type}</div>
      </td>
      <td class="py-3 px-4 font-semibold">${row.client_name} <span class="text-xs text-slate-500">(${row.client_phone})</span></td>
      <td class="py-3 px-4 text-right font-bold">${fmtNPR(row.deal_amount)}</td>
      <td class="py-3 px-4 text-right font-bold text-emerald-700">${fmtNPR(row.paid_amount)}</td>
      <td class="py-3 px-4 text-right font-bold text-rose-600">${fmtNPR(row.due_amount)}</td>
      <td class="py-3 px-4 text-center">
        <span class="px-2.5 py-0.5 rounded-full text-xs font-bold ${
          row.due_amount <= 0 ? "bg-emerald-100 text-emerald-800" : "bg-amber-100 text-amber-900"
        }">${row.payment_status}</span>
      </td>
      <td class="py-3 px-4 text-right">
        <button onclick="openPaymentModal(${row.case_id})" class="px-3 py-1 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg text-xs font-bold">+ भुक्तानी थप्नुहोस्</button>
      </td>
    </tr>`
    )
    .join("");

  const payBody = document.getElementById("payments-table-body");
  payBody.innerHTML = payments.length
    ? payments
        .map(
          (p) => `
      <tr class="hover:bg-slate-50">
        <td class="py-3 px-4 font-mono font-bold text-red-700">${p.receipt_number}</td>
        <td class="py-3 px-4 font-semibold">${p.payment_date_bs}</td>
        <td class="py-3 px-4">
          <div class="font-bold text-slate-900">${p.client_name}</div>
          <div class="text-xs text-slate-500">मुद्दा नं.: ${p.case_number}</div>
        </td>
        <td class="py-3 px-4 text-xs">
          <div class="font-semibold text-slate-800">${p.purpose}</div>
          ${p.remarks ? `<div class="text-slate-500">${p.remarks}</div>` : ""}
        </td>
        <td class="py-3 px-4">
          <span class="px-2.5 py-1 bg-slate-100 border rounded text-xs font-semibold">${p.payment_method}</span>
          ${p.reference_no ? `<div class="text-[11px] font-mono text-slate-500 mt-0.5">${p.reference_no}</div>` : ""}
        </td>
        <td class="py-3 px-4 text-right font-extrabold text-emerald-700">${fmtNPR(p.amount)}</td>
        <td class="py-3 px-4 text-right space-x-1">
          <a href="/print/receipt/${p.id}" target="_blank" class="inline-block px-3 py-1 bg-amber-600 hover:bg-amber-700 text-white rounded text-xs font-bold">🖨️ रसिद प्रिन्ट</a>
          <button onclick="deletePayment(${p.id})" class="px-2 py-1 bg-rose-50 text-rose-600 rounded text-xs">✕</button>
        </td>
      </tr>`
        )
        .join("")
    : `<tr><td colspan="7" class="p-6 text-center text-slate-400">कुनै भुक्तानी अभिलेख छैन</td></tr>`;
}

function openPaymentModal(preselectedCaseId = null) {
  const caseOpts = cachedCases
    .map(
      (c) =>
        `<option value="${c.id}" ${preselectedCaseId === c.id ? "selected" : ""}>${c.case_number} — ${c.client_name} (बाँकी: ${fmtNPR(c.due_amount)})</option>`
    )
    .join("");
  const methodOpts = PAYMENT_METHODS.map((m) => `<option value="${m}">${m}</option>`).join("");

  openModal(
    "💰 भुक्तानी तथा रसिद दर्ता गर्नुहोस् (Record Payment & Issue Receipt)",
    `
    <form id="payment-form" class="space-y-4">
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div class="md:col-span-2">
          <label class="block text-xs font-bold text-slate-700 mb-1">मुद्दा र क्लाइन्ट छान्नुहोस् (Select Case) *</label>
          <select name="case_id" required class="w-full px-3 py-2 border rounded-lg bg-white">${caseOpts}</select>
        </div>
        <div>
          <label class="block text-xs font-bold text-slate-700 mb-1">प्राप्त रकम (Paid Amount NPR रु.) *</label>
          <input type="number" step="0.01" name="amount" required placeholder="25000" class="w-full px-3 py-2 border rounded-lg" />
        </div>
        <div>
          <label class="block text-xs font-bold text-slate-700 mb-1">भुक्तानी मिति (वि.सं.) *</label>
          <input type="text" name="payment_date_bs" required value="${currentBsDate}" placeholder="2083-07-18" class="w-full px-3 py-2 border rounded-lg" />
        </div>
        <div>
          <label class="block text-xs font-bold text-slate-700 mb-1">भुक्तानीको माध्यम (नगद, बैंक, चेक, eSewa आदि) *</label>
          <select name="payment_method" class="w-full px-3 py-2 border rounded-lg bg-white">${methodOpts}</select>
        </div>
        <div>
          <label class="block text-xs font-bold text-slate-700 mb-1">रसिद नम्बर (Receipt No. - खाली छोडेमा स्वतः बन्नेछ)</label>
          <input type="text" name="receipt_number" placeholder="RCP-2083-XXXX" class="w-full px-3 py-2 border rounded-lg" />
        </div>
        <div>
          <label class="block text-xs font-bold text-slate-700 mb-1">भुक्तानीको प्रयोजन (Purpose)</label>
          <input type="text" name="purpose" value="वकालत शुल्क (Legal Fee)" class="w-full px-3 py-2 border rounded-lg" />
        </div>
        <div>
          <label class="block text-xs font-bold text-slate-700 mb-1">चेक नं. / eSewa वा बैंक सन्दर्भ नं.</label>
          <input type="text" name="reference_no" placeholder="CHQ / TXN ID" class="w-full px-3 py-2 border rounded-lg" />
        </div>
      </div>
      <div>
        <label class="block text-xs font-bold text-slate-700 mb-1">कैफियत (Remarks)</label>
        <input type="text" name="remarks" placeholder="थप विवरण..." class="w-full px-3 py-2 border rounded-lg" />
      </div>
      <div class="flex justify-end gap-2 pt-3 border-t">
        <button type="button" onclick="closeModal()" class="px-4 py-2 bg-slate-200 rounded-lg font-semibold">रद्द गर्नुहोस्</button>
        <button type="submit" class="px-5 py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg font-bold shadow">रसिद जारी गर्नुहोस् (Save Receipt)</button>
      </div>
    </form>`
  );

  document.getElementById("payment-form").onsubmit = async (e) => {
    e.preventDefault();
    const raw = Object.fromEntries(new FormData(e.target).entries());
    const payload = {
      ...raw,
      case_id: Number(raw.case_id),
      amount: Number(raw.amount),
    };
    try {
      await apiFetch("/api/finance/payments", { method: "POST", body: JSON.stringify(payload) });
      showToast("भुक्तानी रसिद दर्ता गरियो र बाँकी रकम स्वतः अद्यावधिक भयो");
      closeModal();
      await refreshReferenceLists();
      await loadFinance();
      await loadDashboard();
    } catch (err) {
      showToast(err.message, true);
    }
  };
}

async function deletePayment(id) {
  if (!confirm("यो भुक्तानी रसिद हटाउने हो?")) return;
  try {
    await apiFetch(`/api/finance/payments/${id}`, { method: "DELETE" });
    showToast("भुक्तानी विवरण हटाइयो");
    await refreshReferenceLists();
    await loadFinance();
  } catch (err) {
    showToast(err.message, true);
  }
}

// ============================================================================
// 6. DOCUMENTS (कागजात सम्बन्धी विवरण)
// ============================================================================
async function loadDocuments() {
  const search = document.getElementById("doc-search")?.value || "";
  const dtype = document.getElementById("doc-type-filter")?.value || "";
  const docs = await apiFetch(`/api/documents?search=${encodeURIComponent(search)}&document_type=${encodeURIComponent(dtype)}`);
  const tbody = document.getElementById("documents-table-body");

  if (!docs.length) {
    tbody.innerHTML = `<tr><td colspan="7" class="p-8 text-center text-slate-400">कुनै कागजात भेटिएन</td></tr>`;
    return;
  }

  tbody.innerHTML = docs
    .map(
      (d) => `
    <tr class="hover:bg-slate-50 transition">
      <td class="py-3.5 px-4">
        <div class="font-bold text-slate-900">📄 ${d.document_name}</div>
        ${d.remarks ? `<div class="text-xs text-slate-500 mt-0.5">${d.remarks}</div>` : ""}
      </td>
      <td class="py-3.5 px-4">
        <button onclick="openCaseDetailModal(${d.case_id})" class="font-bold text-blue-700 hover:underline">${d.case_number}</button>
        <div class="text-xs text-slate-600">${d.client_name}</div>
      </td>
      <td class="py-3.5 px-4">
        <span class="px-2.5 py-1 rounded text-xs font-bold ${
          d.document_type.includes("मूल") ? "bg-rose-100 text-rose-900 border border-rose-300" : "bg-slate-100 text-slate-800"
        }">${d.document_type}</span>
      </td>
      <td class="py-3.5 px-4 font-semibold">${d.received_date_bs}</td>
      <td class="py-3.5 px-4">
        ${
          d.returned_date_bs
            ? `<span class="text-emerald-700 font-bold">✓ ${d.returned_date_bs}</span>`
            : `<button onclick="markDocumentReturned(${d.id})" class="px-2 py-0.5 bg-amber-100 hover:bg-amber-200 text-amber-900 rounded text-xs font-semibold">फिर्ता मिति राख्नुहोस्</button>`
        }
      </td>
      <td class="py-3.5 px-4">
        <div class="text-xs font-semibold text-slate-800">${d.status}</div>
        ${
          d.file_path
            ? `<a href="${d.file_path}" target="_blank" class="inline-block mt-1 text-xs text-blue-600 hover:underline font-bold">📎 फाइल हेर्नुहोस् (${d.file_name || "Download"})</a>`
            : `<span class="text-[11px] text-slate-400">भौतिक फाइल मात्र</span>`
        }
      </td>
      <td class="py-3.5 px-4 text-right">
        <button onclick="deleteDocument(${d.id})" class="px-2.5 py-1 bg-rose-50 hover:bg-rose-100 text-rose-600 rounded text-xs font-semibold">हटाउनुहोस्</button>
      </td>
    </tr>`
    )
    .join("");
}

function openDocumentModal(preselectedCaseId = null) {
  const caseOpts = cachedCases
    .map(
      (c) =>
        `<option value="${c.id}" ${preselectedCaseId === c.id ? "selected" : ""}>${c.case_number} — ${c.client_name}</option>`
    )
    .join("");

  openModal(
    "📄 कागजात सम्बन्धी विवरण थप्नुहोस् (Add Document & File Upload)",
    `
    <form id="doc-form" class="space-y-4">
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div class="md:col-span-2">
          <label class="block text-xs font-bold text-slate-700 mb-1">सम्बन्धित मुद्दा छान्नुहोस् (Case) *</label>
          <select name="case_id" required class="w-full px-3 py-2 border rounded-lg bg-white">${caseOpts}</select>
        </div>
        <div class="md:col-span-2">
          <label class="block text-xs font-bold text-slate-700 mb-1">प्राप्त भएका कागजातको नाम (Document Name) *</label>
          <input type="text" name="document_name" required placeholder="जस्तै: जग्गाधनी लालपुर्जा, नागरिकता प्रतिलिपि, तमसुक, चेक स्लिप..." class="w-full px-3 py-2 border rounded-lg" />
        </div>
        <div>
          <label class="block text-xs font-bold text-slate-700 mb-1">मूल कागजात वा प्रतिलिपि *</label>
          <select name="document_type" class="w-full px-3 py-2 border rounded-lg bg-white">
            <option value="मूल कागजात (Original)">मूल कागजात (Original)</option>
            <option value="प्रतिलिपि (Copy)">प्रतिलिपि (Copy)</option>
            <option value="प्रमाणित प्रतिलिपि (Certified Copy)">प्रमाणित प्रतिलिपि (Certified Copy)</option>
          </select>
        </div>
        <div>
          <label class="block text-xs font-bold text-slate-700 mb-1">कागजातको अवस्था (Status)</label>
          <select name="status" class="w-full px-3 py-2 border rounded-lg bg-white">
            <option value="कार्यालयमा सुरक्षित (In Office)">कार्यालयमा सुरक्षित (In Office)</option>
            <option value="अदालतमा पेश (Submitted to Court)">अदालतमा पेश (Submitted to Court)</option>
            <option value="क्लाइन्टलाई फिर्ता (Returned to Client)">क्लाइन्टलाई फिर्ता (Returned to Client)</option>
          </select>
        </div>
        <div>
          <label class="block text-xs font-bold text-slate-700 mb-1">कागजात बुझाएको / प्राप्त मिति (वि.सं.) *</label>
          <input type="text" name="received_date_bs" required value="${currentBsDate}" class="w-full px-3 py-2 border rounded-lg" />
        </div>
        <div>
          <label class="block text-xs font-bold text-slate-700 mb-1">कागजात फिर्ता गरेको मिति (फिर्ता भएमा मात्र)</label>
          <input type="text" name="returned_date_bs" placeholder="2083-08-20" class="w-full px-3 py-2 border rounded-lg" />
        </div>
        <div>
          <label class="block text-xs font-bold text-slate-700 mb-1">बुझाउने वा बुझिलिने व्यक्तिको नाम</label>
          <input type="text" name="handover_person" placeholder="क्लाइन्ट वा वारेसको नाम" class="w-full px-3 py-2 border rounded-lg" />
        </div>
        <div>
          <label class="block text-xs font-bold text-slate-700 mb-1">डिजिटल स्क्यान फाइल अपलोड (PDF / फोटो - ऐच्छिक)</label>
          <input type="file" name="file" class="w-full text-xs border rounded-lg p-1.5" />
        </div>
      </div>
      <div>
        <label class="block text-xs font-bold text-slate-700 mb-1">कैफियत (Remarks)</label>
        <input type="text" name="remarks" placeholder="फाइल दराज नं. वा थप जानकारी..." class="w-full px-3 py-2 border rounded-lg" />
      </div>
      <div class="flex justify-end gap-2 pt-3 border-t">
        <button type="button" onclick="closeModal()" class="px-4 py-2 bg-slate-200 rounded-lg font-semibold">रद्द गर्नुहोस्</button>
        <button type="submit" class="px-5 py-2 bg-amber-600 hover:bg-amber-700 text-white rounded-lg font-bold shadow">कागजात सुरक्षित गर्नुहोस्</button>
      </div>
    </form>`
  );

  document.getElementById("doc-form").onsubmit = async (e) => {
    e.preventDefault();
    const formData = new FormData(e.target);
    try {
      await apiFetch("/api/documents/upload", { method: "POST", body: formData });
      showToast("कागजातको विवरण सफलतापूर्वक दर्ता गरियो");
      closeModal();
      await loadDocuments();
      await loadDashboard();
    } catch (err) {
      showToast(err.message, true);
    }
  };
}

async function markDocumentReturned(docId) {
  const retDate = prompt("कागजात फिर्ता गरेको मिति (वि.सं. YYYY-MM-DD) लेख्नुहोस्:", currentBsDate);
  if (!retDate) return;
  try {
    await apiFetch(`/api/documents/${docId}`, {
      method: "PUT",
      body: JSON.stringify({
        returned_date_bs: retDate.trim(),
        status: "क्लाइन्टलाई फिर्ता (Returned to Client)",
      }),
    });
    showToast("कागजात फिर्ता मिति अद्यावधिक गरियो");
    await loadDocuments();
    await loadDashboard();
  } catch (err) {
    showToast(err.message, true);
  }
}

async function deleteDocument(id) {
  if (!confirm("यो कागजात विवरण हटाउने हो?")) return;
  try {
    await apiFetch(`/api/documents/${id}`, { method: "DELETE" });
    showToast("कागजात विवरण हटाइयो");
    await loadDocuments();
  } catch (err) {
    showToast(err.message, true);
  }
}

// ============================================================================
// 7. ADVOCATES & STAFF (वकिल तथा कर्मचारी विवरण)
// ============================================================================
async function loadStaff() {
  const list = await apiFetch("/api/staff");
  cachedStaff = list;
  const tbody = document.getElementById("staff-table-body");

  tbody.innerHTML = list
    .map(
      (s) => `
    <tr class="hover:bg-slate-50 transition">
      <td class="py-3.5 px-4">
        <div class="font-bold text-slate-900 text-base">${s.full_name}</div>
        <div class="text-xs text-slate-500">प्रयोगकर्ता (Username): <span class="font-mono">${s.username}</span></div>
      </td>
      <td class="py-3.5 px-4">
        <span class="px-2.5 py-0.5 rounded-full text-xs font-bold ${
          s.role === "admin" || s.role === "advocate"
            ? "bg-amber-100 text-amber-900"
            : "bg-blue-100 text-blue-900"
        }">${s.designation}</span>
      </td>
      <td class="py-3.5 px-4">
        ${s.bar_council_no ? `<div class="font-mono text-xs font-bold text-slate-900">बार नं.: ${s.bar_council_no}</div>` : `<div class="text-xs text-slate-400">सहायक कर्मचारी</div>`}
        <div class="text-xs text-slate-600">${s.specialization || "-"}</div>
      </td>
      <td class="py-3.5 px-4">
        <div class="font-bold text-slate-800">📞 ${s.phone}</div>
        ${s.email ? `<div class="text-xs text-blue-600">✉️ ${s.email}</div>` : ""}
      </td>
      <td class="py-3.5 px-4 text-xs text-slate-700">${s.address || "-"}</td>
      <td class="py-3.5 px-4 text-center">
        <span class="px-3 py-1 bg-slate-900 text-amber-400 rounded-lg text-xs font-bold">
          वकालत: ${s.lead_cases_count} | सहायक: ${s.assisted_cases_count}
        </span>
      </td>
      <td class="py-3.5 px-4 text-right">
        <button onclick='openStaffModal(${JSON.stringify(s).replace(/'/g, "&#39;")})' class="px-2.5 py-1 bg-slate-100 hover:bg-slate-200 rounded text-xs font-semibold">सम्पादन</button>
      </td>
    </tr>`
    )
    .join("");
}

function openStaffModal(member = null) {
  const isEdit = !!member;
  openModal(
    isEdit ? "👨‍⚖️ वकिल तथा कर्मचारी विवरण सम्पादन" : "👨‍⚖️ नयाँ वकिल वा कर्मचारी थप्नुहोस्",
    `
    <form id="staff-form" class="space-y-4">
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label class="block text-xs font-bold text-slate-700 mb-1">पूरा नाम, थर (Full Name) *</label>
          <input type="text" name="full_name" required value="${member?.full_name || ""}" placeholder="अधिवक्ता ..." class="w-full px-3 py-2 border rounded-lg" />
        </div>
        <div>
          <label class="block text-xs font-bold text-slate-700 mb-1">भूमिका (System Role) *</label>
          <select name="role" class="w-full px-3 py-2 border rounded-lg bg-white">
            <option value="advocate" ${member?.role === "advocate" ? "selected" : ""}>जिम्मेवार अधिवक्ता (Advocate)</option>
            <option value="staff" ${member?.role === "staff" ? "selected" : ""}>सहायक कर्मचारी (Assistant Staff)</option>
            <option value="admin" ${member?.role === "admin" ? "selected" : ""}>प्रमुख / एडमिन (Managing Partner / Admin)</option>
          </select>
        </div>
        <div>
          <label class="block text-xs font-bold text-slate-700 mb-1">पद (Designation) *</label>
          <input type="text" name="designation" required value="${member?.designation || "अधिवक्ता (Advocate)"}" class="w-full px-3 py-2 border rounded-lg" />
        </div>
        <div>
          <label class="block text-xs font-bold text-slate-700 mb-1">नेपाल बार काउन्सिल नं. (अधिवक्ताको हकमा)</label>
          <input type="text" name="bar_council_no" value="${member?.bar_council_no || ""}" placeholder="NBC-XXXX" class="w-full px-3 py-2 border rounded-lg" />
        </div>
        <div>
          <label class="block text-xs font-bold text-slate-700 mb-1">सम्पर्क नम्बर (Phone) *</label>
          <input type="text" name="phone" required value="${member?.phone || ""}" placeholder="98XXXXXXXX" class="w-full px-3 py-2 border rounded-lg" />
        </div>
        <div>
          <label class="block text-xs font-bold text-slate-700 mb-1">इमेल (Email)</label>
          <input type="email" name="email" value="${member?.email || ""}" class="w-full px-3 py-2 border rounded-lg" />
        </div>
        <div>
          <label class="block text-xs font-bold text-slate-700 mb-1">विशेषज्ञता / कार्यक्षेत्र</label>
          <input type="text" name="specialization" value="${member?.specialization || ""}" placeholder="देवानी, फौजदारी, अदालती तारेख..." class="w-full px-3 py-2 border rounded-lg" />
        </div>
        <div>
          <label class="block text-xs font-bold text-slate-700 mb-1">ठेगाना (Address)</label>
          <input type="text" name="address" value="${member?.address || ""}" class="w-full px-3 py-2 border rounded-lg" />
        </div>
        <div>
          <label class="block text-xs font-bold text-slate-700 mb-1">लगइन प्रयोगकर्ता नाम (Username) *</label>
          <input type="text" name="username" required value="${member?.username || ""}" ${isEdit ? "readonly" : ""} class="w-full px-3 py-2 border rounded-lg bg-slate-50" />
        </div>
        <div>
          <label class="block text-xs font-bold text-slate-700 mb-1">${isEdit ? "नयाँ पासवर्ड (परिवर्तन गर्न चाहेमा)" : "पासवर्ड (Password) *"}</label>
          <input type="password" name="password" ${isEdit ? "" : 'value="lawfirm123" required'} class="w-full px-3 py-2 border rounded-lg" />
        </div>
      </div>
      <div class="flex justify-end gap-2 pt-3 border-t">
        <button type="button" onclick="closeModal()" class="px-4 py-2 bg-slate-200 rounded-lg font-semibold">रद्द गर्नुहोस्</button>
        <button type="submit" class="px-5 py-2 bg-amber-600 hover:bg-amber-700 text-white rounded-lg font-bold shadow">सुरक्षित गर्नुहोस्</button>
      </div>
    </form>`
  );

  document.getElementById("staff-form").onsubmit = async (e) => {
    e.preventDefault();
    const payload = Object.fromEntries(new FormData(e.target).entries());
    try {
      if (isEdit) {
        await apiFetch(`/api/staff/${member.id}`, { method: "PUT", body: JSON.stringify(payload) });
        showToast("वकिल/कर्मचारी विवरण अद्यावधिक गरियो");
      } else {
        await apiFetch("/api/staff", { method: "POST", body: JSON.stringify(payload) });
        showToast("नयाँ वकिल/कर्मचारी थपियो");
      }
      closeModal();
      await refreshReferenceLists();
      await loadStaff();
    } catch (err) {
      showToast(err.message, true);
    }
  };
}

// ============================================================================
// 8. TOOLS (द्वन्द्व जाँच र मिति रूपान्तरण)
// ============================================================================
async function runConflictCheck() {
  const q = document.getElementById("conflict-input").value.trim();
  if (!q) return;
  const res = await apiFetch(`/api/dashboard/conflict-check?q=${encodeURIComponent(q)}`);
  const box = document.getElementById("conflict-results");

  if (!res.has_conflict) {
    box.innerHTML = `<div class="p-3 bg-emerald-50 border border-emerald-200 text-emerald-800 rounded-xl font-semibold">✓ "${q}" सँग सम्बन्धित कुनै पनि विपक्षी वा क्लाइन्ट द्वन्द्व भेटिएन (No Conflict Found)।</div>`;
    return;
  }

  let html = "";
  if (res.matched_as_client.length) {
    html += `<div class="p-3 bg-blue-50 border border-blue-200 rounded-xl"><div class="font-bold text-blue-900 mb-1">👥 क्लाइन्टको सूचीमा भेटिएको (${res.matched_as_client.length}):</div>`;
    html += res.matched_as_client.map((c) => `<div>• <strong>${c.full_name}</strong> (${c.phone}, ना.प्र.नं.: ${c.citizenship_no})</div>`).join("");
    html += `</div>`;
  }
  if (res.matched_in_cases_or_opponent.length) {
    html += `<div class="p-3 bg-rose-50 border border-rose-200 rounded-xl"><div class="font-bold text-rose-900 mb-1">⚠️ मुद्दा / विपक्षीको सूचीमा भेटिएको (${res.matched_in_cases_or_opponent.length}):</div>`;
    html += res.matched_in_cases_or_opponent
      .map(
        (m) =>
          `<div>• मुद्दा नं. <strong>${m.case_number}</strong> (${m.case_type}) — क्लाइन्ट: ${m.client_name} | <strong>विपक्षी: ${m.opponent_name}</strong></div>`
      )
      .join("");
    html += `</div>`;
  }
  box.innerHTML = html;
}

async function convertBsToAd() {
  const bs = document.getElementById("conv-bs-input").value.trim();
  const data = await apiFetch(`/api/dashboard/date-convert?bs=${encodeURIComponent(bs)}`);
  const resBox = document.getElementById("conv-result");
  resBox.textContent = `वि.सं. ${data.bs} (${data.bs_human})  =  ई.सं. (AD): ${data.ad || "अमान्य मिति"}`;
  resBox.classList.remove("hidden");
  if (data.ad) document.getElementById("conv-ad-input").value = data.ad;
}

async function convertAdToBs() {
  const ad = document.getElementById("conv-ad-input").value.trim();
  const data = await apiFetch(`/api/dashboard/date-convert?ad=${encodeURIComponent(ad)}`);
  const resBox = document.getElementById("conv-result");
  resBox.textContent = `ई.सं. ${data.ad}  =  वि.सं. (BS): ${data.bs} (${data.bs_human})`;
  resBox.classList.remove("hidden");
  if (data.bs) document.getElementById("conv-bs-input").value = data.bs;
}

// ============================================================================
// MODAL HELPERS
// ============================================================================
function openModal(title, htmlContent) {
  document.getElementById("modal-title").textContent = title;
  document.getElementById("modal-body").innerHTML = htmlContent;
  document.getElementById("modal-container").classList.remove("hidden");
}

function closeModal() {
  document.getElementById("modal-container").classList.add("hidden");
  document.getElementById("modal-body").innerHTML = "";
}

window.addEventListener("DOMContentLoaded", checkSessionOnLoad);
