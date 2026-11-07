// ============================================================================
// Vidhi Modular Practice CMS — Legal, Company (OCR), IRD Tax & Audit
// Supports 1-Click English <-> Nepali Language Switch & Plug-and-Play Modules
// ============================================================================

let currentUser = null;
let currentLang = localStorage.getItem("vidhi_lang") || "en";
let activeTab = "dashboard";
let selectedComplianceCategory = "";

let cachedClients = [];
let cachedCases = [];
let cachedStaff = [];
let cachedCompanies = [];
let cachedModules = [];
let currentBsDate = "2083-07-21";

// ============================================================================
// BILINGUAL DICTIONARY (ENGLISH <-> NEPALI)
// ============================================================================
const I18N = {
  en: {
    app_title: "Vidhi Law, Company (OCR), Tax & Audit CMS",
    app_subtitle: "Modular Practice Management — Legal, OCR, IRD Tax & Audit",
    lbl_username: "Username",
    lbl_password: "Password",
    btn_signin: "Sign In →",
    demo_accounts: "Quick Demo Accounts:",
    brand_name: "Vidhi Practice CMS",
    brand_tag: "LEGAL • OCR • IRD TAX • AUDIT",
    lbl_today_date: "Today's Date:",
    sec_core: "Core Workspace",
    nav_dashboard: "Dashboard & Reminders",
    nav_clients: "Clients Directory",
    sec_legal_module: "⚖️ Legal & Litigation Module",
    nav_cases: "Court Cases (Mudda)",
    nav_hearings: "Hearings (Peshi/Tarekh)",
    nav_finance: "Fee Deal & Receipts",
    nav_documents: "Case Documents",
    sec_company_module: "🏢 Company (OCR, Tax & Audit)",
    nav_companies: "Companies (OCR & PAN/VAT)",
    nav_compliance: "OCR, IRD Tax & Audit Tasks",
    sec_admin: "Firm & Module Settings",
    nav_staff: "Advocates, Auditors & Staff",
    nav_tools: "Conflict & BS/AD Converter",
    nav_modules: "Plug & Play Modules",
    btn_logout: "Logout",
    btn_new_client: "+ Client",
    btn_new_case: "+ Case",
    btn_new_company: "+ Company (OCR/PAN)",
    btn_new_compliance: "+ OCR/Tax/Audit Task",
    kpi_clients_lbl: "Clients & Companies",
    kpi_cases_lbl: "Court Cases (Litigation)",
    kpi_compliance_lbl: "Pending OCR / Tax / Audit",
    kpi_compliance_sub: "Periodic Filings, VAT, D-03 & AGM",
    kpi_due_lbl: "Collected / Balance Due",
    dash_comp_reminders_title: "🏢 Upcoming Company (OCR), IRD Tax & Audit Compliance Deadlines",
    dash_comp_reminders_sub: "Section 78 Annual Returns, Monthly VAT/e-TDS (25th), Estimated Tax, Tax Clearance & UDIN Audits",
    btn_view_all_compliance: "Open Compliance Tracker →",
    dash_causelist_title: "🏛️ Upcoming Court Cause List (Peshi & Tarekh Schedule)",
    dash_causelist_sub: "Scheduled court hearings, lead advocates, and assigned paralegal staff",
    btn_view_all_hearings: "View All Hearings →",
    th_due_date: "Due Date (BS)",
    th_category: "Authority / Pillar",
    th_company: "Company Name",
    th_activity: "Periodic Activity / Filing",
    th_fy: "Fiscal Year",
    th_status: "Status",
    th_hearing_date: "Hearing Date (BS)",
    th_case_no: "Case No. & Type",
    th_court: "Court / Bench",
    th_parties: "Client vs Opponent",
    th_advocate: "Advocate / Staff",
    th_actions: "Actions",
    btn_add_client: "+ Register New Client",
    btn_register_case: "+ Register New Case",
    btn_add_hearing: "+ Add Hearing (Peshi)",
    btn_record_payment: "+ Record Payment & Issue Receipt",
    btn_add_document: "+ Add / Upload Document",
    btn_register_company: "+ Register Company (OCR / IRD / Audit)",
    comp_kpi_total: "Registered Companies (OCR)",
    comp_kpi_ocr: "Pending OCR Filings",
    comp_kpi_ird: "Pending IRD Tax & Clearance",
    comp_kpi_audit: "Pending Statutory Audits / AGM",
  },
  ne: {
    app_title: "विधि ल फर्म, कम्पनी (OCR), कर तथा लेखापरीक्षण प्रणाली",
    app_subtitle: "मोड्युलर व्यवस्थापन — कानूनी मुद्दा, OCR, आन्तरिक राजस्व कर र लेखापरीक्षण",
    lbl_username: "प्रयोगकर्ता नाम (Username)",
    lbl_password: "पासवर्ड (Password)",
    btn_signin: "लगइन गर्नुहोस् (Sign In) →",
    demo_accounts: "डेमो लगइन खाताहरू:",
    brand_name: "विधि व्यवस्थापन प्रणाली",
    brand_tag: "मुद्दा • कम्पनी (OCR) • कर (IRD) • लेखापरीक्षण",
    lbl_today_date: "आजको मिति:",
    sec_core: "मुख्य कार्यक्षेत्र",
    nav_dashboard: "ड्यासबोर्ड र म्याद अनुस्मारक",
    nav_clients: "क्लाइन्टको विवरण",
    sec_legal_module: "⚖️ मुद्दा तथा कानूनी मोड्युल",
    nav_cases: "मुद्दाको विवरण (Cases)",
    nav_hearings: "पेशी तथा तारेख विवरण",
    nav_finance: "आर्थिक तथा रसिद विवरण",
    nav_documents: "कागजात सम्बन्धी विवरण",
    sec_company_module: "🏢 कम्पनी, OCR, कर र लेखापरीक्षण",
    nav_companies: "कम्पनी दर्ता (OCR र PAN/VAT)",
    nav_compliance: "OCR, कर (IRD) र लेखापरीक्षण कार्य",
    sec_admin: "फर्म र मोड्युल सेटिङ",
    nav_staff: "वकिल, लेखापरीक्षक र कर्मचारी",
    nav_tools: "द्वन्द्व जाँच र मिति रूपान्तरण",
    nav_modules: "प्लग-एण्ड-प्ले मोड्युल (Modules)",
    btn_logout: "लगआउट",
    btn_new_client: "+ नयाँ क्लाइन्ट",
    btn_new_case: "+ नयाँ मुद्दा",
    btn_new_company: "+ नयाँ कम्पनी (OCR)",
    btn_new_compliance: "+ OCR/कर/अडिट कार्य",
    kpi_clients_lbl: "कुल क्लाइन्ट र कम्पनीहरू",
    kpi_cases_lbl: "अदालती मुद्दाहरू (Cases)",
    kpi_compliance_lbl: "बाँकी OCR / कर / लेखापरीक्षण",
    kpi_compliance_sub: "दफा ७८, मासिक भ्याट, आयकर D-03 र साधारण सभा",
    kpi_due_lbl: "प्राप्त शुल्क र बाँकी रकम",
    dash_comp_reminders_title: "🏢 आगामी कम्पनी रजिष्ट्रार (OCR), आन्तरिक राजस्व (IRD) र लेखापरीक्षण म्याद",
    dash_comp_reminders_sub: "दफा ७८ वार्षिक विवरण, मासिक भ्याट/ई-टीडीएस (२५ गते), अनुमानित कर, कर चुक्ता र UDIN",
    btn_view_all_compliance: "सबै विवरण हेर्नुहोस् →",
    dash_causelist_title: "🏛️ आजको तथा आगामी अदालती पेशी र तारेख सूची (Cause List)",
    dash_causelist_sub: "अदालतमा उपस्थित हुनुपर्ने मुद्दा, जिम्मेवार अधिवक्ता र सहायक कर्मचारी",
    btn_view_all_hearings: "सबै पेशी हेर्नुहोस् →",
    th_due_date: "म्याद मिति (वि.सं.)",
    th_category: "निकाय / क्षेत्र",
    th_company: "कम्पनीको नाम",
    th_activity: "आवधिक कार्य / विवरण",
    th_fy: "आर्थिक वर्ष",
    th_status: "अवस्था",
    th_hearing_date: "पेशी मिति (वि.सं.)",
    th_case_no: "मुद्दा नं. र प्रकार",
    th_court: "अदालत / इजलास",
    th_parties: "क्लाइन्ट वि. विपक्षी",
    th_advocate: "अधिवक्ता / सहायक",
    th_actions: "कार्य",
    btn_add_client: "+ नयाँ क्लाइन्ट दर्ता गर्नुहोस्",
    btn_register_case: "+ नयाँ मुद्दा दर्ता गर्नुहोस्",
    btn_add_hearing: "+ नयाँ पेशी थप्नुहोस्",
    btn_record_payment: "+ भुक्तानी र रसिद काट्नुहोस्",
    btn_add_document: "+ कागजात दर्ता / अपलोड",
    btn_register_company: "+ नयाँ कम्पनी दर्ता (OCR / PAN / Audit)",
    comp_kpi_total: "दर्ता भएका कम्पनीहरू (OCR)",
    comp_kpi_ocr: "बाँकी OCR अद्यावधिक कार्य",
    comp_kpi_ird: "बाँकी आन्तरिक राजस्व (IRD) कर कार्य",
    comp_kpi_audit: "बाँकी वैधानिक लेखापरीक्षण / AGM",
  },
};

const TAB_TITLES = {
  en: {
    dashboard: ["📊 Dashboard & Compliance Reminders", "Unified overview of Court Hearings, OCR Filings, IRD Tax Returns & Audits"],
    clients: ["👥 Clients Directory", "Client Name, Address, Contact, Email, Citizenship & Linked Cases"],
    cases: ["📁 Court Cases (Litigation Management)", "Case No., Court, Case Type, Opponent, Registration Date & Assigned Counsel"],
    hearings: ["🏛️ Court Hearings (Peshi & Tarekh)", "Hearing Dates, Status (Tarekh, Arguments, Verdict, Postponed), Next Date & Outcome"],
    finance: ["💰 Financials, Fee Deals & Official Receipts", "Agreed Deal Amount, Paid Amount, Balance Due, Payment Method & Printable Receipts"],
    documents: ["📄 Case Documents & Handover Registry", "Document Checklist, Original vs Copy, Received/Returned Dates & Scanned Uploads"],
    companies: ["🏢 Company Management (OCR, IRD PAN/VAT & Audit)", "Corporate Registry, Share Capital, Directors, Tax Clearance Status & Statutory Auditors"],
    compliance: ["📋 Periodic OCR, IRD Tax & Audit Compliance Tracker", "Section 78/51 Filings, Monthly VAT/e-TDS, Estimated Tax, Tax Clearance, UDIN & Reminders"],
    staff: ["👨‍⚖️ Advocates, Auditors & Support Staff", "Nepal Bar Council License, ICAN COP No., Specialization & Contact Details"],
    tools: ["🔍 Conflict of Interest Check & BS/AD Date Converter", "Search across all Clients/Opponents and convert Bikram Sambat ↔ Gregorian dates"],
    modules: ["🔌 Plug & Play Module Subscription Manager", "Configure subscribed modules (Legal Litigation, OCR, IRD Tax & Statutory Audit)"],
  },
  ne: {
    dashboard: ["📊 समग्र ड्यासबोर्ड र म्याद अनुस्मारक (Dashboard)", "अदालती पेशी, कम्पनी रजिष्ट्रार (OCR), आन्तरिक राजस्व कर र लेखापरीक्षणको एकीकृत विवरण"],
    clients: ["👥 क्लाइन्टको विवरण (Client Management)", "नाम, थर, ठेगाना, सम्पर्क नम्बर, इमेल र नागरिकता नम्बरको अभिलेख"],
    cases: ["📁 मुद्दाको विवरण (Case Management)", "मुद्दा नं., अदालतको नाम, मुद्दाको प्रकार, विपक्षी र दर्ता मितिको अभिलेख"],
    hearings: ["🏛️ पेशी तथा तारेख विवरण (Hearings & Tarekh)", "पेशी मिति, पेशीको अवस्था (तारेख, बहस, फैसला, स्थगित), अर्को पेशी र नतिजा"],
    finance: ["💰 आर्थिक तथा रसिद विवरण (Financials & Receipts)", "सहमति शुल्क (Deal), प्राप्त रकम (Paid), बाँकी रकम (Due), माध्यम र रसिद नम्बर"],
    documents: ["📄 कागजात सम्बन्धी विवरण (Documents & Handover)", "प्राप्त कागजातहरूको सूची, मूल वा प्रतिलिपि, र बुझाएको/फिर्ता गरेको मिति"],
    companies: ["🏢 कम्पनी व्यवस्थापन (OCR, PAN/VAT र लेखापरीक्षण)", "कम्पनी दर्ता नं., पूँजी, सञ्चालक, कर चुक्ता आ.व. र लेखापरीक्षकको पूर्ण विवरण"],
    compliance: ["📋 आवधिक OCR, आन्तरिक राजस्व (IRD) कर र लेखापरीक्षण ट्र्याकर", "दफा ७८/५१ विवरण, मासिक भ्याट/ई-टीडीएस, अनुमानित आयकर, कर चुक्ता, UDIN र म्याद अनुस्मारक"],
    staff: ["👨‍⚖️ वकिल, लेखापरीक्षक तथा कर्मचारी विवरण", "नेपाल बार काउन्सिल नं., ICAN दर्ता नं., विशेषज्ञता र सम्पर्क विवरण"],
    tools: ["🔍 विपक्षी द्वन्द्व जाँच र वि.सं. ↔ ई.सं. मिति रूपान्तरण", "क्लाइन्ट/विपक्षी द्वन्द्व जाँच र विक्रम संवत् रूपान्तरण"],
    modules: ["🔌 प्लग-एण्ड-प्ले मोड्युल व्यवस्थापन (Module Subscriptions)", "फर्मको आवश्यकता अनुसार कानूनी मुद्दा, OCR, कर र लेखापरीक्षण मोड्युल सुचारु वा बन्द गर्नुहोस्"],
  },
};

function t(key) {
  return (I18N[currentLang] && I18N[currentLang][key]) || I18N.en[key] || key;
}

function setLanguage(lang) {
  currentLang = lang === "ne" ? "ne" : "en";
  localStorage.setItem("vidhi_lang", currentLang);

  // Highlight active language buttons
  ["hdr-lang-en", "login-lang-en"].forEach((id) => {
    const el = document.getElementById(id);
    if (el) {
      el.className =
        currentLang === "en"
          ? "px-3 py-1 rounded-lg text-xs font-extrabold bg-amber-600 text-white shadow"
          : "px-3 py-1 rounded-lg text-xs font-semibold text-slate-500 hover:text-slate-900";
    }
  });
  ["hdr-lang-ne", "login-lang-ne"].forEach((id) => {
    const el = document.getElementById(id);
    if (el) {
      el.className =
        currentLang === "ne"
          ? "px-3 py-1 rounded-lg text-xs font-extrabold bg-amber-600 text-white shadow"
          : "px-3 py-1 rounded-lg text-xs font-semibold text-slate-500 hover:text-slate-900";
    }
  });

  // Translate all static [data-i18n] nodes
  document.querySelectorAll("[data-i18n]").forEach((el) => {
    const key = el.getAttribute("data-i18n");
    if (I18N[currentLang][key]) {
      el.textContent = I18N[currentLang][key];
    }
  });

  // Update current page header
  const titles = TAB_TITLES[currentLang][activeTab] || TAB_TITLES.en[activeTab];
  if (titles) {
    document.getElementById("page-title").textContent = titles[0];
    document.getElementById("page-subtitle").textContent = titles[1];
  }

  // Re-render current active tab if logged in
  if (currentUser) {
    switchTab(activeTab, false);
  }
}

const COURT_SUGGESTIONS = [
  "सर्वोच्च अदालत (Supreme Court of Nepal)",
  "उच्च अदालत पाटन (High Court Patan)",
  "काठमाडौँ जिल्ला अदालत (Kathmandu District Court)",
  "ललितपुर जिल्ला अदालत (Lalitpur District Court)",
  "भक्तपुर जिल्ला अदालत (Bhaktapur District Court)",
  "विशेष अदालत, काठमाडौँ (Special Court)",
  "श्रम अदालत, काठमाडौँ (Labour Court)",
  "राजस्व न्यायाधिकरण (Revenue Tribunal)"
];

const CASE_TYPES = [
  "अंशबण्डा (Partition of Property)",
  "लेनदेन (Loan / Recovery)",
  "सम्बन्ध विच्छेद र अंश (Divorce & Alimony)",
  "चेक अनादर / लेनदेन (Cheque Bounce & Recovery)",
  "दूषित लिखत बदर र जालसाजी (Deed Cancellation & Fraud)",
  "जग्गा खिचलो (Land Dispute)",
  "रिट निवेदन (Writ Petition)",
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
  "ConnectIPS"
];

const COMPLIANCE_TEMPLATES = {
  OCR: [
    "New Company Registration - Name Reservation, MOA/AOA & Certificate (नयाँ कम्पनी दर्ता)",
    "Section 78 Annual Return & AGM Minutes Filing - Poush End (दफा ७८ वार्षिक विवरण र साधारण सभा)",
    "Section 51 Shareholding & Capital Lagat Report (दफा ५१ शेयर लगत विवरण)",
    "Share Transfer / Purchase-Sale Nam-sari (शेयर खरिद-बिक्री तथा नामसारी)",
    "Board of Directors (BOD) Lagat Update (सञ्चालक समिति लगत अद्यावधिक)",
    "Capital Increase / Objective / Address 3-Mahale Amendment (पूँजी/उद्देश्य/ठेगाना ३ महले संशोधन)",
    "Auditor Appointment Filing under Sec 111 (लेखापरीक्षक नियुक्ति जानकारी)",
    "Company Liquidation / De-registration (कम्पनी खारेजी प्रक्रिया)"
  ],
  IRD_TAX: [
    "Monthly VAT Return & Purchase/Sales Register Filing - 25th (मासिक मु.अ.कर विवरण)",
    "Monthly e-TDS Filing & Verification - 25th (मासिक अग्रिम कर कट्टी ई-टीडीएस)",
    "Estimated Income Tax Return & 1st Installment 40% - Poush End (अनुमानित आयकर प्रथम किस्ता - पुस)",
    "Estimated Income Tax 2nd Installment 70% - Chaitra End (अनुमानित आयकर दोस्रो किस्ता - चैत)",
    "Estimated Income Tax 3rd Installment 100% - Ashadh End (अनुमानित आयकर तेस्रो किस्ता - असार)",
    "Annual Income Tax Return D-01 / D-02 / D-03 Filing (वार्षिक आयकर विवरण दाखिला)",
    "Tax Clearance Certificate Issuance (कर चुक्ता प्रमाणपत्र)",
    "Ward / Municipal Business Tax & Firm Renewal (वडा व्यवसाय कर तथा फर्म नवीकरण)",
    "Social Security Fund (SSF) Monthly Contribution (सामाजिक सुरक्षा कोष दाखिला)"
  ],
  AUDIT: [
    "Auditor Appointment & Consent Letter (लेखापरीक्षक नियुक्ति र सहमति पत्र)",
    "Trial Balance & Books of Account Review (लेखा तथा ट्रायल ब्यालेन्स रुजु)",
    "Statutory Audit Report & Financial Statements Sign-off (वैधानिक लेखापरीक्षण प्रतिवेदन)",
    "ICAN UDIN Generation & Tax Audit Certification (ICAN UDIN जारी र प्रमाणीकरण)",
    "Annual General Meeting (AGM) Notice & Minutes (वार्षिक साधारण सभा सम्पन्न)"
  ]
};

function fmtNPR(num) {
  const n = Number(num || 0);
  const prefix = currentLang === "ne" ? "रु. " : "NPR ";
  return prefix + n.toLocaleString("en-IN", { minimumFractionDigits: 0, maximumFractionDigits: 2 });
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
    throw new Error("Session expired. Please sign in again.");
  }
  const data = await resp.json().catch(() => ({}));
  if (!resp.ok) {
    throw new Error(data.detail || "Request failed");
  }
  return data;
}

// ============================================================================
// AUTHENTICATION & MODULE VISIBILITY
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
    if (!res.ok) throw new Error(data.detail || "Login failed");
    localStorage.setItem("vidhi_token", data.access_token);
    currentUser = data.user;
    enterApp();
  } catch (err) {
    errBox.textContent = err.message;
    errBox.classList.remove("hidden");
  }
});

async function checkSessionOnLoad() {
  setLanguage(currentLang);
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
  applyModuleVisibility();
  await switchTab("dashboard");
}

async function refreshReferenceLists() {
  try {
    const [clients, cases, staff, companies, modules] = await Promise.all([
      apiFetch("/api/clients"),
      apiFetch("/api/cases"),
      apiFetch("/api/staff"),
      apiFetch("/api/company/entities"),
      apiFetch("/api/modules"),
    ]);
    cachedClients = clients;
    cachedCases = cases;
    cachedStaff = staff;
    cachedCompanies = companies;
    cachedModules = modules;
  } catch (e) {
    console.warn("Could not preload reference lists:", e);
  }
}

function isModuleEnabled(key) {
  const m = cachedModules.find((x) => x.module_key === key);
  return m ? m.is_enabled : true;
}

function applyModuleVisibility() {
  const legalOn = isModuleEnabled("legal");
  const companyOn = isModuleEnabled("company_management");

  const legalGroup = document.getElementById("sidebar-group-legal");
  const compGroup = document.getElementById("sidebar-group-company");
  if (legalGroup) legalGroup.classList.toggle("hidden", !legalOn);
  if (compGroup) compGroup.classList.toggle("hidden", !companyOn);

  const qaCase = document.getElementById("qa-case");
  const qaComp = document.getElementById("qa-company");
  const qaTask = document.getElementById("qa-compliance");
  if (qaCase) qaCase.classList.toggle("hidden", !legalOn);
  if (qaComp) qaComp.classList.toggle("hidden", !companyOn);
  if (qaTask) qaTask.classList.toggle("hidden", !companyOn);

  const dashLegal = document.getElementById("dash-legal-causelist-card");
  const dashComp = document.getElementById("dash-company-reminders-card");
  if (dashLegal) dashLegal.classList.toggle("hidden", !legalOn);
  if (dashComp) dashComp.classList.toggle("hidden", !companyOn);
}

// ============================================================================
// NAVIGATION
// ============================================================================
async function switchTab(tabName) {
  activeTab = tabName;
  document.querySelectorAll(".tab-view").forEach((el) => el.classList.add("hidden"));
  document.querySelectorAll(".nav-btn").forEach((el) => el.classList.remove("nav-active"));

  const view = document.getElementById(`view-${tabName}`);
  const nav = document.getElementById(`nav-${tabName}`);
  if (view) view.classList.remove("hidden");
  if (nav) nav.classList.add("nav-active");

  const titles = (TAB_TITLES[currentLang] && TAB_TITLES[currentLang][tabName]) || TAB_TITLES.en[tabName];
  if (titles) {
    document.getElementById("page-title").textContent = titles[0];
    document.getElementById("page-subtitle").textContent = titles[1];
  }

  if (tabName === "dashboard") await loadDashboard();
  if (tabName === "clients") await loadClients();
  if (tabName === "cases") await loadCases();
  if (tabName === "hearings") await loadHearings();
  if (tabName === "finance") await loadFinance();
  if (tabName === "documents") await loadDocuments();
  if (tabName === "companies") await loadCompanies();
  if (tabName === "compliance") await loadComplianceActivities();
  if (tabName === "staff") await loadStaff();
  if (tabName === "modules") await loadModulesView();
}

// ============================================================================
// 1. DASHBOARD
// ============================================================================
async function loadDashboard() {
  try {
    const data = await apiFetch("/api/dashboard/stats");
    currentBsDate = data.today_bs || currentBsDate;
    document.getElementById("sidebar-date-bs").textContent = `BS: ${data.today_bs} (${data.today_bs_human})`;
    document.getElementById("sidebar-date-ad").textContent = `AD: ${data.today_ad}`;

    document.getElementById("kpi-clients").textContent = `${data.counts.total_clients} / ${data.counts.total_companies}`;
    document.getElementById("kpi-companies-sub").textContent =
      currentLang === "ne"
        ? `क्लाइन्ट: ${data.counts.total_clients} | दर्ता कम्पनी: ${data.counts.total_companies}`
        : `Individual Clients: ${data.counts.total_clients} | Companies: ${data.counts.total_companies}`;

    document.getElementById("kpi-cases").textContent = data.counts.total_cases;
    document.getElementById("kpi-cases-sub").textContent =
      currentLang === "ne"
        ? `विचाराधीन: ${data.counts.active_cases} | फैसला: ${data.counts.decided_cases}`
        : `Active: ${data.counts.active_cases} | Decided: ${data.counts.decided_cases}`;

    document.getElementById("kpi-compliance").textContent = data.counts.pending_compliance_count;
    document.getElementById("kpi-paid").textContent = fmtNPR(data.financials.total_paid_amount);
    document.getElementById("kpi-due").textContent =
      (currentLang === "ne" ? "उठाउन बाँकी: " : "Balance Due: ") + fmtNPR(data.financials.total_due_amount);

    // Render Upcoming Company (OCR, IRD Tax & Audit) Deadlines
    const compBody = document.getElementById("dashboard-compliance-body");
    const compItems = data.upcoming_compliance || [];
    if (!compItems.length) {
      compBody.innerHTML = `<tr><td colspan="6" class="p-5 text-center text-slate-400">No pending OCR/Tax/Audit tasks</td></tr>`;
    } else {
      compBody.innerHTML = compItems
        .map((a) => {
          const badgeColor =
            a.category === "OCR"
              ? "bg-amber-100 text-amber-900"
              : a.category === "IRD_TAX"
              ? "bg-blue-100 text-blue-900"
              : "bg-purple-100 text-purple-900";
          const compName = currentLang === "ne" ? a.company_name_np || a.company_name_en : a.company_name_en;
          return `
          <tr class="hover:bg-slate-50 transition">
            <td class="py-3 px-4 font-bold text-slate-900">📅 ${a.due_date_bs}</td>
            <td class="py-3 px-4"><span class="px-2.5 py-0.5 rounded-full text-xs font-bold ${badgeColor}">${a.category}</span></td>
            <td class="py-3 px-4 font-bold text-slate-800">
              <button onclick="openCompanyDetailModal(${a.company_id})" class="hover:underline text-blue-700">${compName}</button>
            </td>
            <td class="py-3 px-4 text-xs font-semibold text-slate-800">${a.activity_type}</td>
            <td class="py-3 px-4 text-xs font-mono">${a.fiscal_year}</td>
            <td class="py-3 px-4"><span class="px-2 py-0.5 rounded bg-slate-100 text-slate-700 text-xs font-semibold">${a.status}</span></td>
          </tr>`;
        })
        .join("");
    }

    // Render Court Cause List
    const clBody = document.getElementById("dashboard-causelist-body");
    if (!data.cause_list.length) {
      clBody.innerHTML = `<tr><td colspan="7" class="p-6 text-center text-slate-400">No upcoming court hearings</td></tr>`;
    } else {
      clBody.innerHTML = data.cause_list
        .map(
          (c) => `
        <tr class="hover:bg-amber-50/40 transition ${c.is_today ? "bg-amber-50/80" : ""}">
          <td class="py-3 px-4 font-bold">
            <span class="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg text-xs font-bold ${
              c.is_today ? "bg-red-600 text-white" : "bg-amber-100 text-amber-900"
            }">📅 ${c.next_hearing_date_bs}</span>
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
            <div class="text-xs text-rose-700">vs. ${c.opponent_name}</div>
          </td>
          <td class="py-3 px-4">
            <div class="font-medium text-slate-800">👨‍⚖️ ${c.advocate_name}</div>
            ${c.assistant_name ? `<div class="text-xs text-slate-500">${c.assistant_name}</div>` : ""}
          </td>
          <td class="py-3 px-4"><span class="px-2.5 py-1 rounded-full text-xs font-semibold bg-blue-50 text-blue-700">${c.status}</span></td>
          <td class="py-3 px-4 text-right space-x-1">
            <button onclick="openCaseDetailModal(${c.case_id})" class="px-2.5 py-1 bg-slate-100 hover:bg-slate-200 rounded text-xs font-semibold">View</button>
            <button onclick="openHearingModal(${c.case_id})" class="px-2.5 py-1 bg-blue-600 text-white rounded text-xs font-semibold">+ Peshi</button>
          </td>
        </tr>`
        )
        .join("");
    }
  } catch (err) {
    showToast(err.message, true);
  }
}

// ============================================================================
// 2. CLIENTS
// ============================================================================
async function loadClients() {
  const q = document.getElementById("client-search")?.value || "";
  const clients = await apiFetch(`/api/clients?search=${encodeURIComponent(q)}`);
  cachedClients = clients;
  const tbody = document.getElementById("clients-table-body");
  if (!clients.length) {
    tbody.innerHTML = `<tr><td colspan="7" class="p-8 text-center text-slate-400">No client records found</td></tr>`;
    return;
  }
  tbody.innerHTML = clients
    .map(
      (c, idx) => `
    <tr class="hover:bg-slate-50 transition">
      <td class="py-3.5 px-4 font-bold text-slate-500">${idx + 1}</td>
      <td class="py-3.5 px-4">
        <div class="font-bold text-slate-900 text-base">${c.full_name}</div>
        ${c.father_or_spouse_name ? `<div class="text-xs text-slate-500">Father/Spouse: ${c.father_or_spouse_name}</div>` : ""}
      </td>
      <td class="py-3.5 px-4">
        <div class="font-medium text-slate-800">${c.address}</div>
        ${c.district ? `<div class="text-xs text-slate-500">${c.district}</div>` : ""}
      </td>
      <td class="py-3.5 px-4">
        <div class="font-bold text-slate-800">📞 ${c.phone}</div>
        ${c.email ? `<div class="text-xs text-blue-600">✉️ ${c.email}</div>` : `<div class="text-xs text-slate-400">-</div>`}
      </td>
      <td class="py-3.5 px-4">
        <span class="px-2.5 py-1 bg-slate-100 border border-slate-300 rounded font-mono text-xs font-bold text-slate-900">🪪 ${c.citizenship_no}</span>
        <div class="text-xs text-slate-500 mt-1">${c.citizenship_district || ""} ${c.citizenship_issue_date_bs ? `(${c.citizenship_issue_date_bs})` : ""}</div>
      </td>
      <td class="py-3.5 px-4">
        <div class="font-bold text-slate-800">${c.case_count} Cases</div>
        <div class="text-xs text-emerald-700">Paid: ${fmtNPR(c.total_paid)}</div>
        <div class="text-xs text-rose-600">Due: ${fmtNPR(c.total_due)}</div>
      </td>
      <td class="py-3.5 px-4 text-right space-x-1">
        <button onclick='openClientModal(${JSON.stringify(c).replace(/'/g, "&#39;")})' class="px-2.5 py-1 bg-slate-100 hover:bg-slate-200 rounded text-xs font-semibold">Edit</button>
        <button onclick="deleteClient(${c.id})" class="px-2.5 py-1 bg-rose-50 hover:bg-rose-100 text-rose-600 rounded text-xs font-semibold">Delete</button>
      </td>
    </tr>`
    )
    .join("");
}

function openClientModal(client = null) {
  const isEdit = !!client;
  openModal(
    isEdit ? "👥 Edit Client Details (क्लाइन्ट सम्पादन)" : "👥 Register New Client (नयाँ क्लाइन्ट दर्ता)",
    `
    <form id="client-form" class="space-y-4">
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label class="block text-xs font-bold text-slate-700 mb-1">First Name (नाम) *</label>
          <input type="text" name="first_name" required value="${client?.first_name || ""}" class="w-full px-3 py-2 border rounded-lg" />
        </div>
        <div>
          <label class="block text-xs font-bold text-slate-700 mb-1">Last Name / Surname (थर) *</label>
          <input type="text" name="last_name" required value="${client?.last_name || ""}" class="w-full px-3 py-2 border rounded-lg" />
        </div>
        <div>
          <label class="block text-xs font-bold text-slate-700 mb-1">Address (ठेगाना) *</label>
          <input type="text" name="address" required value="${client?.address || ""}" class="w-full px-3 py-2 border rounded-lg" />
        </div>
        <div>
          <label class="block text-xs font-bold text-slate-700 mb-1">District (जिल्ला)</label>
          <input type="text" name="district" value="${client?.district || ""}" class="w-full px-3 py-2 border rounded-lg" />
        </div>
        <div>
          <label class="block text-xs font-bold text-slate-700 mb-1">Contact Number (सम्पर्क नम्बर) *</label>
          <input type="text" name="phone" required value="${client?.phone || ""}" class="w-full px-3 py-2 border rounded-lg" />
        </div>
        <div>
          <label class="block text-xs font-bold text-slate-700 mb-1">Email (इमेल - भएमा)</label>
          <input type="email" name="email" value="${client?.email || ""}" class="w-full px-3 py-2 border rounded-lg" />
        </div>
        <div>
          <label class="block text-xs font-bold text-slate-700 mb-1">Citizenship Number (नागरिकता नम्बर) *</label>
          <input type="text" name="citizenship_no" required value="${client?.citizenship_no || ""}" class="w-full px-3 py-2 border rounded-lg" />
        </div>
        <div>
          <label class="block text-xs font-bold text-slate-700 mb-1">Issue District & Date BS (जारी जिल्ला र मिति)</label>
          <div class="flex gap-2">
            <input type="text" name="citizenship_district" value="${client?.citizenship_district || ""}" placeholder="District" class="w-1/2 px-3 py-2 border rounded-lg" />
            <input type="text" name="citizenship_issue_date_bs" value="${client?.citizenship_issue_date_bs || ""}" placeholder="2072-05-10" class="w-1/2 px-3 py-2 border rounded-lg" />
          </div>
        </div>
        <div>
          <label class="block text-xs font-bold text-slate-700 mb-1">Father / Spouse Name (बाबु/पति/पत्नीको नाम)</label>
          <input type="text" name="father_or_spouse_name" value="${client?.father_or_spouse_name || ""}" class="w-full px-3 py-2 border rounded-lg" />
        </div>
        <div>
          <label class="block text-xs font-bold text-slate-700 mb-1">Occupation (पेशा)</label>
          <input type="text" name="occupation" value="${client?.occupation || ""}" class="w-full px-3 py-2 border rounded-lg" />
        </div>
      </div>
      <div class="flex justify-end gap-2 pt-3 border-t">
        <button type="button" onclick="closeModal()" class="px-4 py-2 bg-slate-200 rounded-lg font-semibold">Cancel</button>
        <button type="submit" class="px-5 py-2 bg-amber-600 hover:bg-amber-700 text-white rounded-lg font-bold shadow">Save Client</button>
      </div>
    </form>`
  );

  document.getElementById("client-form").onsubmit = async (e) => {
    e.preventDefault();
    const payload = Object.fromEntries(new FormData(e.target).entries());
    try {
      if (isEdit) {
        await apiFetch(`/api/clients/${client.id}`, { method: "PUT", body: JSON.stringify(payload) });
      } else {
        await apiFetch("/api/clients", { method: "POST", body: JSON.stringify(payload) });
      }
      showToast("Client saved successfully");
      closeModal();
      await refreshReferenceLists();
      await loadClients();
    } catch (err) {
      showToast(err.message, true);
    }
  };
}

async function deleteClient(id) {
  if (!confirm("Delete this client record?")) return;
  try {
    await apiFetch(`/api/clients/${id}`, { method: "DELETE" });
    showToast("Client deleted");
    await refreshReferenceLists();
    await loadClients();
  } catch (err) {
    showToast(err.message, true);
  }
}

// ============================================================================
// 3. CASES (LEGAL MODULE)
// ============================================================================
async function loadCases() {
  const search = document.getElementById("case-search")?.value || "";
  const caseType = document.getElementById("case-type-filter")?.value || "";
  const cases = await apiFetch(`/api/cases?search=${encodeURIComponent(search)}&case_type=${encodeURIComponent(caseType)}`);
  cachedCases = cases;

  const tbody = document.getElementById("cases-table-body");
  if (!cases.length) {
    tbody.innerHTML = `<tr><td colspan="7" class="p-8 text-center text-slate-400">No court cases found</td></tr>`;
    return;
  }
  tbody.innerHTML = cases
    .map(
      (c) => `
    <tr class="hover:bg-slate-50 transition">
      <td class="py-3.5 px-4">
        <button onclick="openCaseDetailModal(${c.id})" class="font-extrabold text-blue-700 hover:underline text-base">${c.case_number}</button>
        <div class="text-xs text-slate-500">Reg: <strong>${c.registration_date_bs}</strong></div>
      </td>
      <td class="py-3.5 px-4">
        <div class="font-bold text-slate-900">${c.court_name}</div>
        <span class="inline-block mt-1 px-2 py-0.5 bg-amber-100 text-amber-900 rounded text-xs font-semibold">${c.case_type}</span>
      </td>
      <td class="py-3.5 px-4">
        <div class="font-bold text-slate-900">${c.client_name} <span class="text-xs font-normal text-slate-500">(${c.client_party_role})</span></div>
        <div class="text-xs font-semibold text-rose-700 mt-0.5">vs. ${c.opponent_name}</div>
      </td>
      <td class="py-3.5 px-4">
        <div class="font-semibold text-slate-800">👨‍⚖️ ${c.advocate_name}</div>
        <div class="text-xs text-slate-500">Staff: ${c.assistant_name}</div>
      </td>
      <td class="py-3.5 px-4">
        <div class="text-xs font-bold text-amber-800">Next: ${c.next_hearing_date_bs || "-"}</div>
        <span class="inline-block mt-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-blue-50 text-blue-800">${c.status}</span>
      </td>
      <td class="py-3.5 px-4 text-xs">
        <div>Deal: <strong>${fmtNPR(c.deal_amount)}</strong></div>
        <div class="text-emerald-700">Paid: <strong>${fmtNPR(c.paid_amount)}</strong></div>
        <div class="text-rose-600">Due: <strong>${fmtNPR(c.due_amount)}</strong></div>
      </td>
      <td class="py-3.5 px-4 text-right space-x-1">
        <button onclick="openCaseDetailModal(${c.id})" class="px-2.5 py-1 bg-slate-900 text-amber-400 rounded text-xs font-bold">File</button>
        <a href="/print/case/${c.id}" target="_blank" class="inline-block px-2 py-1 bg-slate-100 hover:bg-slate-200 rounded text-xs font-semibold">🖨️</a>
        <button onclick='openCaseModal(${JSON.stringify(c).replace(/'/g, "&#39;")})' class="px-2 py-1 bg-slate-100 hover:bg-slate-200 rounded text-xs">Edit</button>
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
  const advOpts = `<option value="">-- Select Advocate --</option>` + advocates
    .map((a) => `<option value="${a.id}" ${caseObj?.advocate_id === a.id ? "selected" : ""}>${a.full_name}</option>`)
    .join("");
  const asstOpts = `<option value="">-- Select Staff --</option>` + cachedStaff
    .map((s) => `<option value="${s.id}" ${caseObj?.assistant_id === s.id ? "selected" : ""}>${s.full_name}</option>`)
    .join("");

  openModal(
    isEdit ? "📁 Edit Court Case (मुद्दा सम्पादन)" : "📁 Register Court Case (नयाँ मुद्दा दर्ता)",
    `
    <form id="case-form" class="space-y-4">
      <div class="grid grid-cols-1 md:grid-cols-3 gap-3">
        <div>
          <label class="block text-xs font-bold text-slate-700 mb-1">Case No. (मुद्दा नम्बर) *</label>
          <input type="text" name="case_number" required value="${caseObj?.case_number || ""}" placeholder="083-CP-0501" class="w-full px-3 py-2 border rounded-lg" />
        </div>
        <div>
          <label class="block text-xs font-bold text-slate-700 mb-1">Filing No. (दर्ता नं.)</label>
          <input type="text" name="filing_number" value="${caseObj?.filing_number || ""}" class="w-full px-3 py-2 border rounded-lg" />
        </div>
        <div>
          <label class="block text-xs font-bold text-slate-700 mb-1">Registration Date BS (दर्ता मिति) *</label>
          <input type="text" name="registration_date_bs" required value="${caseObj?.registration_date_bs || currentBsDate}" class="w-full px-3 py-2 border rounded-lg" />
        </div>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
        <div>
          <label class="block text-xs font-bold text-slate-700 mb-1">Court Name (अदालतको नाम) *</label>
          <input list="court-list" name="court_name" required value="${caseObj?.court_name || ""}" class="w-full px-3 py-2 border rounded-lg" />
          <datalist id="court-list">${COURT_SUGGESTIONS.map((ct) => `<option value="${ct}">`).join("")}</datalist>
        </div>
        <div>
          <label class="block text-xs font-bold text-slate-700 mb-1">Case Type (मुद्दाको प्रकार) *</label>
          <input list="casetype-list" name="case_type" required value="${caseObj?.case_type || ""}" class="w-full px-3 py-2 border rounded-lg" />
          <datalist id="casetype-list">${CASE_TYPES.map((t) => `<option value="${t}">`).join("")}</datalist>
        </div>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-3 gap-3">
        <div class="md:col-span-2">
          <label class="block text-xs font-bold text-slate-700 mb-1">Client (क्लाइन्ट) *</label>
          <select name="client_id" required class="w-full px-3 py-2 border rounded-lg bg-white">${clientOpts}</select>
        </div>
        <div>
          <label class="block text-xs font-bold text-slate-700 mb-1">Party Role (पक्षको हैसियत)</label>
          <select name="client_party_role" class="w-full px-3 py-2 border rounded-lg bg-white">
            <option value="वादी (Plaintiff)">वादी (Plaintiff)</option>
            <option value="प्रतिवादी (Defendant)">प्रतिवादी (Defendant)</option>
            <option value="निवेदक (Petitioner)">निवेदक (Petitioner)</option>
            <option value="पुनरावेदक (Appellant)">पुनरावेदक (Appellant)</option>
          </select>
        </div>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-3 gap-3 bg-rose-50/50 p-3 rounded-xl border border-rose-100">
        <div>
          <label class="block text-xs font-bold text-rose-900 mb-1">Opponent Name (विपक्षीको नाम) *</label>
          <input type="text" name="opponent_name" required value="${caseObj?.opponent_name || ""}" class="w-full px-3 py-2 border rounded-lg bg-white" />
        </div>
        <div>
          <label class="block text-xs font-bold text-rose-900 mb-1">Opponent Address/Phone</label>
          <input type="text" name="opponent_address" value="${caseObj?.opponent_address || ""}" class="w-full px-3 py-2 border rounded-lg bg-white" />
        </div>
        <div>
          <label class="block text-xs font-bold text-rose-900 mb-1">Opponent Counsel (विपक्षी वकिल)</label>
          <input type="text" name="opponent_counsel" value="${caseObj?.opponent_counsel || ""}" class="w-full px-3 py-2 border rounded-lg bg-white" />
        </div>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-3 gap-3">
        <div>
          <label class="block text-xs font-bold text-slate-700 mb-1">Lead Advocate (जिम्मेवार अधिवक्ता)</label>
          <select name="advocate_id" class="w-full px-3 py-2 border rounded-lg bg-white">${advOpts}</select>
        </div>
        <div>
          <label class="block text-xs font-bold text-slate-700 mb-1">Assistant Staff (सहायक कर्मचारी)</label>
          <select name="assistant_id" class="w-full px-3 py-2 border rounded-lg bg-white">${asstOpts}</select>
        </div>
        <div>
          <label class="block text-xs font-bold text-slate-700 mb-1">Next Hearing Date BS (अर्को पेशी)</label>
          <input type="text" name="next_hearing_date_bs" value="${caseObj?.next_hearing_date_bs || ""}" class="w-full px-3 py-2 border rounded-lg" />
        </div>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-3 gap-3 bg-emerald-50/60 p-3 rounded-xl border border-emerald-200">
        <div>
          <label class="block text-xs font-bold text-emerald-900 mb-1">Agreed Deal Amount (NPR) *</label>
          <input type="number" step="0.01" name="deal_amount" required value="${caseObj?.deal_amount ?? 50000}" class="w-full px-3 py-2 border rounded-lg bg-white" />
        </div>
        ${
          !isEdit
            ? `
        <div>
          <label class="block text-xs font-bold text-emerald-900 mb-1">Initial Paid Advance (NPR)</label>
          <input type="number" step="0.01" name="initial_paid_amount" value="0" class="w-full px-3 py-2 border rounded-lg bg-white" />
        </div>
        <div>
          <label class="block text-xs font-bold text-emerald-900 mb-1">Payment Method</label>
          <select name="initial_payment_method" class="w-full px-3 py-2 border rounded-lg bg-white">
            ${PAYMENT_METHODS.map((m) => `<option value="${m}">${m}</option>`).join("")}
          </select>
        </div>`
            : `
        <div>
          <label class="block text-xs font-bold text-slate-700 mb-1">Status</label>
          <input type="text" name="status" value="${caseObj?.status || "विचाराधीन (Active)"}" class="w-full px-3 py-2 border rounded-lg bg-white" />
        </div>`
        }
      </div>

      <div>
        <label class="block text-xs font-bold text-slate-700 mb-1">Case Summary / Claims (संक्षिप्त विवरण)</label>
        <textarea name="summary" rows="2" class="w-full px-3 py-2 border rounded-lg">${caseObj?.summary || ""}</textarea>
      </div>

      <div class="flex justify-end gap-2 pt-3 border-t">
        <button type="button" onclick="closeModal()" class="px-4 py-2 bg-slate-200 rounded-lg font-semibold">Cancel</button>
        <button type="submit" class="px-5 py-2 bg-amber-600 hover:bg-amber-700 text-white rounded-lg font-bold shadow">Save Case</button>
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
    if (!isEdit) payload.initial_paid_amount = Number(raw.initial_paid_amount || 0);
    try {
      if (isEdit) {
        await apiFetch(`/api/cases/${caseObj.id}`, { method: "PUT", body: JSON.stringify(payload) });
      } else {
        await apiFetch("/api/cases", { method: "POST", body: JSON.stringify(payload) });
      }
      showToast("Case saved successfully");
      closeModal();
      await refreshReferenceLists();
      await loadCases();
    } catch (err) {
      showToast(err.message, true);
    }
  };
}

async function openCaseDetailModal(caseId) {
  try {
    const c = await apiFetch(`/api/cases/${caseId}`);
    openModal(
      `📁 Case File: ${c.case_number} — ${c.case_type}`,
      `
      <div class="space-y-4">
        <div class="flex flex-wrap justify-between items-center gap-2 bg-slate-100 p-3.5 rounded-xl border">
          <div>
            <div class="font-extrabold text-slate-900 text-base">${c.case_title}</div>
            <div class="text-xs text-slate-600">${c.court_name} | Reg: <strong>${c.registration_date_bs}</strong> | Status: <strong>${c.status}</strong></div>
          </div>
          <a href="/print/case/${c.id}" target="_blank" class="px-3.5 py-1.5 bg-amber-600 text-white rounded-lg text-xs font-bold shadow">
            🖨️ Print Case Dossier
          </a>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-3 text-xs">
          <div class="p-3 border rounded-xl bg-slate-50">
            <div class="font-bold text-slate-700 mb-1">👥 Client & Opponent</div>
            <p>Client: <strong>${c.client_name}</strong> (${c.client_phone})</p>
            <p class="text-rose-700 font-semibold mt-1">Opponent: ${c.opponent_name}</p>
          </div>
          <div class="p-3 border rounded-xl bg-slate-50">
            <div class="font-bold text-slate-700 mb-1">👨‍⚖️ Assigned Team</div>
            <p>Advocate: <strong>${c.advocate_name}</strong></p>
            <p>Assistant: <strong>${c.assistant_name}</strong></p>
            <p class="text-amber-800 font-bold mt-1">Next Hearing: ${c.next_hearing_date_bs || "-"}</p>
          </div>
          <div class="p-3 border rounded-xl bg-emerald-50 border-emerald-200">
            <div class="font-bold text-emerald-900 mb-1">💰 Fee Summary</div>
            <p>Deal: <strong>${fmtNPR(c.deal_amount)}</strong></p>
            <p class="text-emerald-700">Paid: <strong>${fmtNPR(c.paid_amount)}</strong></p>
            <p class="text-rose-700">Due: <strong>${fmtNPR(c.due_amount)}</strong></p>
          </div>
        </div>
      </div>`
    );
  } catch (err) {
    showToast(err.message, true);
  }
}

// ============================================================================
// 4. HEARINGS (PESHI)
// ============================================================================
async function loadHearings() {
  const search = document.getElementById("hearing-search")?.value || "";
  const list = await apiFetch(`/api/hearings?search=${encodeURIComponent(search)}`);
  const tbody = document.getElementById("hearings-table-body");
  if (!list.length) {
    tbody.innerHTML = `<tr><td colspan="7" class="p-8 text-center text-slate-400">No hearing records found</td></tr>`;
    return;
  }
  tbody.innerHTML = list
    .map(
      (h) => `
    <tr class="hover:bg-slate-50 transition">
      <td class="py-3.5 px-4 font-extrabold text-slate-900">📅 ${h.hearing_date_bs}</td>
      <td class="py-3.5 px-4">
        <button onclick="openCaseDetailModal(${h.case_id})" class="font-bold text-blue-700 hover:underline">${h.case_number}</button>
        <div class="text-xs text-slate-600">${h.court_name}</div>
      </td>
      <td class="py-3.5 px-4">
        <div class="font-semibold text-slate-800">${h.client_name}</div>
        <div class="text-xs text-rose-700">vs. ${h.opponent_name}</div>
      </td>
      <td class="py-3.5 px-4"><span class="px-2.5 py-1 rounded-full text-xs font-bold bg-amber-100 text-amber-900">${h.hearing_status}</span></td>
      <td class="py-3.5 px-4 max-w-xs text-xs text-slate-800">${h.outcome || "-"}</td>
      <td class="py-3.5 px-4 font-bold text-blue-800">${h.next_hearing_date_bs || "-"}</td>
      <td class="py-3.5 px-4 text-right">
        <button onclick="deleteHearing(${h.id})" class="px-2.5 py-1 bg-rose-50 hover:bg-rose-100 text-rose-600 rounded text-xs font-semibold">Delete</button>
      </td>
    </tr>`
    )
    .join("");
}

function openHearingModal(preselectedCaseId = null) {
  const caseOpts = cachedCases
    .map((c) => `<option value="${c.id}" ${preselectedCaseId === c.id ? "selected" : ""}>${c.case_number} — ${c.client_name}</option>`)
    .join("");
  openModal(
    "🏛️ Add Court Hearing / Peshi (पेशी विवरण थप्नुहोस्)",
    `
    <form id="hearing-form" class="space-y-4">
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div class="md:col-span-2">
          <label class="block text-xs font-bold text-slate-700 mb-1">Select Case *</label>
          <select name="case_id" required class="w-full px-3 py-2 border rounded-lg bg-white">${caseOpts}</select>
        </div>
        <div>
          <label class="block text-xs font-bold text-slate-700 mb-1">Hearing Date BS (पेशी मिति) *</label>
          <input type="text" name="hearing_date_bs" required value="${currentBsDate}" class="w-full px-3 py-2 border rounded-lg" />
        </div>
        <div>
          <label class="block text-xs font-bold text-slate-700 mb-1">Status (तारेख, बहस, फैसला, स्थगित) *</label>
          <input list="hstatus-list" name="hearing_status" required class="w-full px-3 py-2 border rounded-lg" />
          <datalist id="hstatus-list">${HEARING_STATUS_OPTIONS.map((s) => `<option value="${s}">`).join("")}</datalist>
        </div>
        <div>
          <label class="block text-xs font-bold text-slate-700 mb-1">Bench / Judge</label>
          <input type="text" name="bench_or_judge" class="w-full px-3 py-2 border rounded-lg" />
        </div>
        <div>
          <label class="block text-xs font-bold text-slate-700 mb-1">Next Hearing Date BS (अर्को पेशी)</label>
          <input type="text" name="next_hearing_date_bs" placeholder="2083-08-15" class="w-full px-3 py-2 border rounded-lg" />
        </div>
      </div>
      <div>
        <label class="block text-xs font-bold text-slate-700 mb-1">Hearing Outcome / Order (पेशीको नतिजा) *</label>
        <textarea name="outcome" rows="3" required class="w-full px-3 py-2 border rounded-lg"></textarea>
      </div>
      <div class="flex justify-end gap-2 pt-3 border-t">
        <button type="button" onclick="closeModal()" class="px-4 py-2 bg-slate-200 rounded-lg font-semibold">Cancel</button>
        <button type="submit" class="px-5 py-2 bg-blue-600 text-white rounded-lg font-bold shadow">Save Hearing</button>
      </div>
    </form>`
  );

  document.getElementById("hearing-form").onsubmit = async (e) => {
    e.preventDefault();
    const raw = Object.fromEntries(new FormData(e.target).entries());
    try {
      await apiFetch("/api/hearings", { method: "POST", body: JSON.stringify({ ...raw, case_id: Number(raw.case_id) }) });
      showToast("Hearing saved");
      closeModal();
      await loadHearings();
    } catch (err) {
      showToast(err.message, true);
    }
  };
}

async function deleteHearing(id) {
  if (!confirm("Delete this hearing?")) return;
  await apiFetch(`/api/hearings/${id}`, { method: "DELETE" });
  await loadHearings();
}

// ============================================================================
// 5. FINANCE & RECEIPTS
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

  document.getElementById("finance-ledger-body").innerHTML = (summary.case_ledgers || [])
    .map(
      (row) => `
    <tr class="hover:bg-slate-50">
      <td class="py-3 px-4 font-bold text-blue-700">${row.case_number}</td>
      <td class="py-3 px-4 font-semibold">${row.client_name}</td>
      <td class="py-3 px-4 text-right font-bold">${fmtNPR(row.deal_amount)}</td>
      <td class="py-3 px-4 text-right font-bold text-emerald-700">${fmtNPR(row.paid_amount)}</td>
      <td class="py-3 px-4 text-right font-bold text-rose-600">${fmtNPR(row.due_amount)}</td>
      <td class="py-3 px-4 text-center"><span class="px-2.5 py-0.5 rounded-full text-xs font-bold bg-amber-100 text-amber-900">${row.payment_status}</span></td>
      <td class="py-3 px-4 text-right">
        <button onclick="openPaymentModal(${row.case_id})" class="px-3 py-1 bg-emerald-600 text-white rounded-lg text-xs font-bold">+ Pay</button>
      </td>
    </tr>`
    )
    .join("");

  document.getElementById("payments-table-body").innerHTML = payments
    .map(
      (p) => `
    <tr class="hover:bg-slate-50">
      <td class="py-3 px-4 font-mono font-bold text-red-700">${p.receipt_number}</td>
      <td class="py-3 px-4 font-semibold">${p.payment_date_bs}</td>
      <td class="py-3 px-4"><div class="font-bold">${p.client_name}</div><div class="text-xs text-slate-500">${p.case_number}</div></td>
      <td class="py-3 px-4 text-xs font-semibold">${p.purpose}</td>
      <td class="py-3 px-4"><span class="px-2.5 py-1 bg-slate-100 border rounded text-xs font-semibold">${p.payment_method}</span></td>
      <td class="py-3 px-4 text-right font-extrabold text-emerald-700">${fmtNPR(p.amount)}</td>
      <td class="py-3 px-4 text-right">
        <a href="/print/receipt/${p.id}" target="_blank" class="inline-block px-3 py-1 bg-amber-600 text-white rounded text-xs font-bold">🖨️ Print</a>
      </td>
    </tr>`
    )
    .join("");
}

function openPaymentModal(preselectedCaseId = null) {
  const caseOpts = cachedCases
    .map((c) => `<option value="${c.id}" ${preselectedCaseId === c.id ? "selected" : ""}>${c.case_number} — ${c.client_name} (Due: ${fmtNPR(c.due_amount)})</option>`)
    .join("");
  openModal(
    "💰 Record Payment & Issue Receipt (भुक्तानी रसिद)",
    `
    <form id="payment-form" class="space-y-4">
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div class="md:col-span-2">
          <label class="block text-xs font-bold text-slate-700 mb-1">Select Case *</label>
          <select name="case_id" required class="w-full px-3 py-2 border rounded-lg bg-white">${caseOpts}</select>
        </div>
        <div>
          <label class="block text-xs font-bold text-slate-700 mb-1">Amount Paid (NPR) *</label>
          <input type="number" step="0.01" name="amount" required class="w-full px-3 py-2 border rounded-lg" />
        </div>
        <div>
          <label class="block text-xs font-bold text-slate-700 mb-1">Payment Date BS *</label>
          <input type="text" name="payment_date_bs" required value="${currentBsDate}" class="w-full px-3 py-2 border rounded-lg" />
        </div>
        <div>
          <label class="block text-xs font-bold text-slate-700 mb-1">Payment Method *</label>
          <select name="payment_method" class="w-full px-3 py-2 border rounded-lg bg-white">
            ${PAYMENT_METHODS.map((m) => `<option value="${m}">${m}</option>`).join("")}
          </select>
        </div>
        <div>
          <label class="block text-xs font-bold text-slate-700 mb-1">Receipt No. (Auto if blank)</label>
          <input type="text" name="receipt_number" placeholder="RCP-2083-XXXX" class="w-full px-3 py-2 border rounded-lg" />
        </div>
      </div>
      <div class="flex justify-end gap-2 pt-3 border-t">
        <button type="button" onclick="closeModal()" class="px-4 py-2 bg-slate-200 rounded-lg font-semibold">Cancel</button>
        <button type="submit" class="px-5 py-2 bg-emerald-600 text-white rounded-lg font-bold shadow">Issue Receipt</button>
      </div>
    </form>`
  );

  document.getElementById("payment-form").onsubmit = async (e) => {
    e.preventDefault();
    const raw = Object.fromEntries(new FormData(e.target).entries());
    try {
      await apiFetch("/api/finance/payments", {
        method: "POST",
        body: JSON.stringify({ ...raw, case_id: Number(raw.case_id), amount: Number(raw.amount) }),
      });
      showToast("Receipt recorded");
      closeModal();
      await refreshReferenceLists();
      await loadFinance();
    } catch (err) {
      showToast(err.message, true);
    }
  };
}

// ============================================================================
// 6. DOCUMENTS
// ============================================================================
async function loadDocuments() {
  const search = document.getElementById("doc-search")?.value || "";
  const dtype = document.getElementById("doc-type-filter")?.value || "";
  const docs = await apiFetch(`/api/documents?search=${encodeURIComponent(search)}&document_type=${encodeURIComponent(dtype)}`);
  const tbody = document.getElementById("documents-table-body");
  if (!docs.length) {
    tbody.innerHTML = `<tr><td colspan="7" class="p-8 text-center text-slate-400">No documents found</td></tr>`;
    return;
  }
  tbody.innerHTML = docs
    .map(
      (d) => `
    <tr class="hover:bg-slate-50 transition">
      <td class="py-3.5 px-4 font-bold text-slate-900">📄 ${d.document_name}</td>
      <td class="py-3.5 px-4"><div class="font-bold text-blue-700">${d.case_number}</div><div class="text-xs text-slate-500">${d.client_name}</div></td>
      <td class="py-3.5 px-4"><span class="px-2.5 py-1 rounded text-xs font-bold bg-slate-100">${d.document_type}</span></td>
      <td class="py-3.5 px-4 font-semibold">${d.received_date_bs}</td>
      <td class="py-3.5 px-4">
        ${
          d.returned_date_bs
            ? `<span class="text-emerald-700 font-bold">✓ ${d.returned_date_bs}</span>`
            : `<button onclick="markDocumentReturned(${d.id})" class="px-2 py-0.5 bg-amber-100 text-amber-900 rounded text-xs font-semibold">Set Return Date</button>`
        }
      </td>
      <td class="py-3.5 px-4 text-xs">
        <div class="font-semibold">${d.status}</div>
        ${d.file_path ? `<a href="${d.file_path}" target="_blank" class="text-blue-600 underline font-bold">📎 Download</a>` : ""}
      </td>
      <td class="py-3.5 px-4 text-right">
        <button onclick="deleteDocument(${d.id})" class="px-2.5 py-1 bg-rose-50 text-rose-600 rounded text-xs font-semibold">Delete</button>
      </td>
    </tr>`
    )
    .join("");
}

function openDocumentModal(preselectedCaseId = null) {
  const caseOpts = cachedCases
    .map((c) => `<option value="${c.id}" ${preselectedCaseId === c.id ? "selected" : ""}>${c.case_number} — ${c.client_name}</option>`)
    .join("");
  openModal(
    "📄 Add / Upload Case Document (कागजात दर्ता)",
    `
    <form id="doc-form" class="space-y-4">
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div class="md:col-span-2">
          <label class="block text-xs font-bold text-slate-700 mb-1">Select Case *</label>
          <select name="case_id" required class="w-full px-3 py-2 border rounded-lg bg-white">${caseOpts}</select>
        </div>
        <div class="md:col-span-2">
          <label class="block text-xs font-bold text-slate-700 mb-1">Document Name *</label>
          <input type="text" name="document_name" required placeholder="e.g., Land Ownership Certificate (Lalpurja), Citizenship..." class="w-full px-3 py-2 border rounded-lg" />
        </div>
        <div>
          <label class="block text-xs font-bold text-slate-700 mb-1">Original vs Copy *</label>
          <select name="document_type" class="w-full px-3 py-2 border rounded-lg bg-white">
            <option value="मूल कागजात (Original)">Original (मूल कागजात)</option>
            <option value="प्रतिलिपि (Copy)">Copy (प्रतिलिपि)</option>
            <option value="प्रमाणित प्रतिलिपि (Certified Copy)">Certified Copy (प्रमाणित प्रतिलिपि)</option>
          </select>
        </div>
        <div>
          <label class="block text-xs font-bold text-slate-700 mb-1">Received Date BS *</label>
          <input type="text" name="received_date_bs" required value="${currentBsDate}" class="w-full px-3 py-2 border rounded-lg" />
        </div>
        <div>
          <label class="block text-xs font-bold text-slate-700 mb-1">Returned Date BS (Optional)</label>
          <input type="text" name="returned_date_bs" class="w-full px-3 py-2 border rounded-lg" />
        </div>
        <div>
          <label class="block text-xs font-bold text-slate-700 mb-1">Upload File (Optional)</label>
          <input type="file" name="file" class="w-full text-xs border rounded-lg p-1.5" />
        </div>
      </div>
      <div class="flex justify-end gap-2 pt-3 border-t">
        <button type="button" onclick="closeModal()" class="px-4 py-2 bg-slate-200 rounded-lg font-semibold">Cancel</button>
        <button type="submit" class="px-5 py-2 bg-amber-600 text-white rounded-lg font-bold shadow">Save Document</button>
      </div>
    </form>`
  );

  document.getElementById("doc-form").onsubmit = async (e) => {
    e.preventDefault();
    const formData = new FormData(e.target);
    try {
      await apiFetch("/api/documents/upload", { method: "POST", body: formData });
      showToast("Document saved");
      closeModal();
      await loadDocuments();
    } catch (err) {
      showToast(err.message, true);
    }
  };
}

async function markDocumentReturned(docId) {
  const retDate = prompt("Enter Return Date (BS YYYY-MM-DD):", currentBsDate);
  if (!retDate) return;
  await apiFetch(`/api/documents/${docId}`, {
    method: "PUT",
    body: JSON.stringify({ returned_date_bs: retDate.trim(), status: "क्लाइन्टलाई फिर्ता (Returned to Client)" }),
  });
  await loadDocuments();
}

async function deleteDocument(id) {
  if (!confirm("Delete this document?")) return;
  await apiFetch(`/api/documents/${id}`, { method: "DELETE" });
  await loadDocuments();
}

// ============================================================================
// 7. COMPANY MANAGEMENT MODULE (OCR, IRD PAN/VAT & STATUTORY AUDIT)
// ============================================================================
async function loadCompanies() {
  const q = document.getElementById("company-search")?.value || "";
  const [summary, companies] = await Promise.all([
    apiFetch("/api/company/summary"),
    apiFetch(`/api/company/entities?search=${encodeURIComponent(q)}`),
  ]);
  cachedCompanies = companies;

  document.getElementById("comp-kpi-entities").textContent = summary.counts.total_companies;
  document.getElementById("comp-kpi-ocr-pending").textContent = summary.counts.ocr_pending;
  document.getElementById("comp-kpi-ird-pending").textContent = summary.counts.ird_tax_pending;
  document.getElementById("comp-kpi-audit-pending").textContent = summary.counts.audit_pending;

  const tbody = document.getElementById("companies-table-body");
  if (!companies.length) {
    tbody.innerHTML = `<tr><td colspan="7" class="p-8 text-center text-slate-400">No registered companies found</td></tr>`;
    return;
  }
  tbody.innerHTML = companies
    .map(
      (c) => `
    <tr class="hover:bg-slate-50 transition">
      <td class="py-3.5 px-4">
        <button onclick="openCompanyDetailModal(${c.id})" class="font-extrabold text-blue-700 hover:underline text-base">${c.company_name_en}</button>
        <div class="text-xs font-semibold text-slate-600">${c.company_name_np}</div>
        <span class="inline-block mt-1 px-2 py-0.5 bg-slate-100 rounded text-[11px] font-bold">${c.company_type}</span>
      </td>
      <td class="py-3.5 px-4">
        <div class="font-mono font-bold text-slate-900">OCR: ${c.ocr_registration_no}</div>
        <div class="text-xs text-slate-500">Reg Date: ${c.registration_date_bs}</div>
        ${c.camis_username ? `<div class="text-[11px] text-slate-400">CAMIS: ${c.camis_username}</div>` : ""}
      </td>
      <td class="py-3.5 px-4">
        <div class="font-mono font-bold text-indigo-800">${c.tax_registration_type}: ${c.pan_vat_no}</div>
        <div class="text-xs text-slate-600">${c.ird_office}</div>
      </td>
      <td class="py-3.5 px-4 text-xs">
        <div>Paid-up: <strong>${fmtNPR(c.paidup_capital)}</strong></div>
        <div class="text-slate-600 mt-0.5">Auditor: <strong>${c.current_auditor_name || "-"}</strong></div>
        ${c.auditor_ican_no ? `<div class="font-mono text-[11px] text-purple-700">${c.auditor_ican_no}</div>` : ""}
      </td>
      <td class="py-3.5 px-4 text-xs">
        <span class="inline-block px-2.5 py-0.5 rounded-full font-bold bg-emerald-100 text-emerald-800">
          ✓ Tax Clearance: FY ${c.tax_clearance_upto_fy || "-"}
        </span>
        <div class="text-slate-500 mt-1">OCR Sec 78 Filed: FY ${c.last_ocr_filed_fy || "-"}</div>
      </td>
      <td class="py-3.5 px-4">
        <div class="flex flex-wrap gap-1 text-xs">
          <span class="px-2 py-0.5 bg-amber-100 text-amber-900 rounded font-bold">OCR: ${c.pending_ocr_count}</span>
          <span class="px-2 py-0.5 bg-blue-100 text-blue-900 rounded font-bold">IRD: ${c.pending_ird_count}</span>
          <span class="px-2 py-0.5 bg-purple-100 text-purple-900 rounded font-bold">Audit: ${c.pending_audit_count}</span>
        </div>
        ${c.next_due_date_bs ? `<div class="text-[11px] text-rose-700 font-semibold mt-1">Next Due: ${c.next_due_date_bs}</div>` : ""}
      </td>
      <td class="py-3.5 px-4 text-right space-x-1">
        <button onclick="openCompanyDetailModal(${c.id})" class="px-2.5 py-1 bg-slate-900 text-emerald-400 rounded text-xs font-bold">360° File</button>
        <button onclick="openComplianceModal(${c.id})" class="px-2 py-1 bg-indigo-600 text-white rounded text-xs font-bold">+ Task</button>
        <button onclick='openCompanyModal(${JSON.stringify(c).replace(/'/g, "&#39;")})' class="px-2 py-1 bg-slate-100 rounded text-xs">Edit</button>
      </td>
    </tr>`
    )
    .join("");
}

function openCompanyModal(comp = null) {
  const isEdit = !!comp;
  const staffOpts = cachedStaff
    .map((s) => `<option value="${s.id}" ${comp?.assigned_officer_id === s.id ? "selected" : ""}>${s.full_name}</option>`)
    .join("");

  openModal(
    isEdit
      ? "🏢 Edit Company Profile (कम्पनी विवरण सम्पादन)"
      : "🏢 Register Company for OCR, IRD Tax & Audit Management (नयाँ कम्पनी दर्ता)",
    `
    <form id="company-form" class="space-y-4">
      <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
        <div>
          <label class="block text-xs font-bold text-slate-700 mb-1">Company Name (English) *</label>
          <input type="text" name="company_name_en" required value="${comp?.company_name_en || ""}" placeholder="Everest Trade & Logistics Pvt. Ltd." class="w-full px-3 py-2 border rounded-lg" />
        </div>
        <div>
          <label class="block text-xs font-bold text-slate-700 mb-1">Company Name (नेपालीमा)</label>
          <input type="text" name="company_name_np" value="${comp?.company_name_np || ""}" placeholder="एभरेष्ट ट्रेड एण्ड लजिस्टिक्स प्रा.लि." class="w-full px-3 py-2 border rounded-lg" />
        </div>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-3 gap-3 bg-amber-50/60 p-3 rounded-xl border border-amber-200">
        <div>
          <label class="block text-xs font-bold text-amber-900 mb-1">Company Type *</label>
          <select name="company_type" class="w-full px-3 py-2 border rounded-lg bg-white">
            <option value="Private Limited (प्रा.लि.)">Private Limited (प्रा.लि.)</option>
            <option value="Public Limited (लि.)">Public Limited (लि.)</option>
            <option value="Non-Profit (मुनाफा वितरण नगर्ने)">Non-Profit (मुनाफा वितरण नगर्ने)</option>
            <option value="Partnership / Firm (साझेदारी / फर्म)">Partnership / Firm</option>
          </select>
        </div>
        <div>
          <label class="block text-xs font-bold text-amber-900 mb-1">OCR Registration No. (दर्ता नं.) *</label>
          <input type="text" name="ocr_registration_no" required value="${comp?.ocr_registration_no || ""}" placeholder="284512/078/079" class="w-full px-3 py-2 border rounded-lg bg-white" />
        </div>
        <div>
          <label class="block text-xs font-bold text-amber-900 mb-1">Registration Date BS (दर्ता मिति) *</label>
          <input type="text" name="registration_date_bs" required value="${comp?.registration_date_bs || currentBsDate}" class="w-full px-3 py-2 border rounded-lg bg-white" />
        </div>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-3 gap-3 bg-blue-50/60 p-3 rounded-xl border border-blue-200">
        <div>
          <label class="block text-xs font-bold text-blue-900 mb-1">PAN / VAT Number (स्थायी लेखा नं.) *</label>
          <input type="text" name="pan_vat_no" required value="${comp?.pan_vat_no || ""}" placeholder="609845123" class="w-full px-3 py-2 border rounded-lg bg-white" />
        </div>
        <div>
          <label class="block text-xs font-bold text-blue-900 mb-1">Tax Type (PAN / VAT)</label>
          <select name="tax_registration_type" class="w-full px-3 py-2 border rounded-lg bg-white">
            <option value="VAT (मु.अ.कर)">VAT (मु.अ.कर)</option>
            <option value="PAN Only (प्यान मात्र)">PAN Only (प्यान मात्र)</option>
            <option value="VAT + Excise (अन्तःशुल्क)">VAT + Excise</option>
          </select>
        </div>
        <div>
          <label class="block text-xs font-bold text-blue-900 mb-1">IRD Tax Office (आन्तरिक राजस्व कार्यालय) *</label>
          <input type="text" name="ird_office" required value="${comp?.ird_office || "आन्तरिक राजस्व कार्यालय, बानेश्वर"}" class="w-full px-3 py-2 border rounded-lg bg-white" />
        </div>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-3 gap-3">
        <div>
          <label class="block text-xs font-bold text-slate-700 mb-1">Authorized Capital (अधिकृत पूँजी)</label>
          <input type="number" step="0.01" name="authorized_capital" value="${comp?.authorized_capital ?? 10000000}" class="w-full px-3 py-2 border rounded-lg" />
        </div>
        <div>
          <label class="block text-xs font-bold text-slate-700 mb-1">Paid-up Capital (चुक्ता पूँजी)</label>
          <input type="number" step="0.01" name="paidup_capital" value="${comp?.paidup_capital ?? 5000000}" class="w-full px-3 py-2 border rounded-lg" />
        </div>
        <div>
          <label class="block text-xs font-bold text-slate-700 mb-1">Tax Clearance Up To FY (कर चुक्ता आ.व.)</label>
          <input type="text" name="tax_clearance_upto_fy" value="${comp?.tax_clearance_upto_fy || "2081/82"}" class="w-full px-3 py-2 border rounded-lg" />
        </div>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-3 gap-3 bg-purple-50/50 p-3 rounded-xl border border-purple-200">
        <div>
          <label class="block text-xs font-bold text-purple-900 mb-1">Statutory Auditor Name (लेखापरीक्षक)</label>
          <input type="text" name="current_auditor_name" value="${comp?.current_auditor_name || ""}" placeholder="CA ..." class="w-full px-3 py-2 border rounded-lg bg-white" />
        </div>
        <div>
          <label class="block text-xs font-bold text-purple-900 mb-1">ICAN COP / Membership No.</label>
          <input type="text" name="auditor_ican_no" value="${comp?.auditor_ican_no || ""}" placeholder="ICAN-COP-XXXX" class="w-full px-3 py-2 border rounded-lg bg-white" />
        </div>
        <div>
          <label class="block text-xs font-bold text-purple-900 mb-1">Assigned Firm Officer</label>
          <select name="assigned_officer_id" class="w-full px-3 py-2 border rounded-lg bg-white">${staffOpts}</select>
        </div>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-3 gap-3">
        <div>
          <label class="block text-xs font-bold text-slate-700 mb-1">Registered Address (ठेगाना) *</label>
          <input type="text" name="registered_address" required value="${comp?.registered_address || ""}" class="w-full px-3 py-2 border rounded-lg" />
        </div>
        <div>
          <label class="block text-xs font-bold text-slate-700 mb-1">Contact Person (सम्पर्क व्यक्ति) *</label>
          <input type="text" name="contact_person" required value="${comp?.contact_person || ""}" class="w-full px-3 py-2 border rounded-lg" />
        </div>
        <div>
          <label class="block text-xs font-bold text-slate-700 mb-1">Contact Phone *</label>
          <input type="text" name="contact_phone" required value="${comp?.contact_phone || ""}" class="w-full px-3 py-2 border rounded-lg" />
        </div>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
        <div>
          <label class="block text-xs font-bold text-slate-700 mb-1">Directors & Shareholders Summary (सञ्चालक विवरण)</label>
          <input type="text" name="directors_summary" value="${comp?.directors_summary || ""}" class="w-full px-3 py-2 border rounded-lg" />
        </div>
        <div>
          <label class="block text-xs font-bold text-slate-700 mb-1">Annual Retainer Fee (वार्षिक रिटेनर शुल्क NPR)</label>
          <input type="number" step="0.01" name="annual_retainer_fee" value="${comp?.annual_retainer_fee ?? 120000}" class="w-full px-3 py-2 border rounded-lg" />
        </div>
      </div>

      ${
        !isEdit
          ? `
      <label class="flex items-center gap-2 p-3 bg-emerald-50 border border-emerald-200 rounded-xl text-xs font-bold text-emerald-900 cursor-pointer">
        <input type="checkbox" name="auto_generate_periodic_tasks" checked class="w-4 h-4 accent-emerald-600" />
        Automatically generate standard periodic compliance reminders (OCR Sec 78, Sec 51, Monthly VAT/e-TDS, Estimated Tax, D-03 & Statutory Audit)
      </label>`
          : ""
      }

      <div class="flex justify-end gap-2 pt-3 border-t">
        <button type="button" onclick="closeModal()" class="px-4 py-2 bg-slate-200 rounded-lg font-semibold">Cancel</button>
        <button type="submit" class="px-5 py-2 bg-emerald-700 hover:bg-emerald-800 text-white rounded-lg font-bold shadow">Save Company</button>
      </div>
    </form>`
  );

  document.getElementById("company-form").onsubmit = async (e) => {
    e.preventDefault();
    const formEl = e.target;
    const raw = Object.fromEntries(new FormData(formEl).entries());
    const payload = {
      ...raw,
      authorized_capital: Number(raw.authorized_capital || 0),
      paidup_capital: Number(raw.paidup_capital || 0),
      annual_retainer_fee: Number(raw.annual_retainer_fee || 0),
      assigned_officer_id: raw.assigned_officer_id ? Number(raw.assigned_officer_id) : null,
      auto_generate_periodic_tasks: formEl.querySelector('[name="auto_generate_periodic_tasks"]')?.checked ?? false,
    };
    try {
      if (isEdit) {
        await apiFetch(`/api/company/entities/${comp.id}`, { method: "PUT", body: JSON.stringify(payload) });
      } else {
        await apiFetch("/api/company/entities", { method: "POST", body: JSON.stringify(payload) });
      }
      showToast("Company profile saved");
      closeModal();
      await refreshReferenceLists();
      await loadCompanies();
    } catch (err) {
      showToast(err.message, true);
    }
  };
}

async function openCompanyDetailModal(companyId) {
  try {
    const c = await apiFetch(`/api/company/entities/${companyId}`);
    openModal(
      `🏢 ${c.company_name_en} (${c.ocr_registration_no})`,
      `
      <div class="space-y-4">
        <div class="grid grid-cols-1 md:grid-cols-3 gap-3 text-xs">
          <div class="p-3 bg-amber-50 border border-amber-200 rounded-xl">
            <div class="font-bold text-amber-900 mb-1">🏛️ OCR Registration</div>
            <p>OCR No.: <strong>${c.ocr_registration_no}</strong></p>
            <p>Reg Date: ${c.registration_date_bs}</p>
            <p>Paid-up Capital: <strong>${fmtNPR(c.paidup_capital)}</strong></p>
            <p>Last Sec 78 Filed: <strong>FY ${c.last_ocr_filed_fy}</strong></p>
          </div>
          <div class="p-3 bg-blue-50 border border-blue-200 rounded-xl">
            <div class="font-bold text-blue-900 mb-1">🧾 IRD Tax & Clearance</div>
            <p>${c.tax_registration_type}: <strong>${c.pan_vat_no}</strong></p>
            <p>Office: ${c.ird_office}</p>
            <p class="text-emerald-700 font-bold mt-1">✓ Tax Clearance: FY ${c.tax_clearance_upto_fy}</p>
          </div>
          <div class="p-3 bg-purple-50 border border-purple-200 rounded-xl">
            <div class="font-bold text-purple-900 mb-1">📊 Statutory Audit & AGM</div>
            <p>Auditor: <strong>${c.current_auditor_name || "-"}</strong></p>
            <p>ICAN No.: ${c.auditor_ican_no || "-"}</p>
            <p>Last AGM Date: ${c.last_agm_date_bs || "-"}</p>
          </div>
        </div>

        <div class="text-xs bg-slate-50 p-3 rounded-xl border">
          <strong>Directors / Shareholders:</strong> ${c.directors_summary || "-"} |
          <strong>Contact:</strong> ${c.contact_person} (${c.contact_phone})
        </div>

        <div class="flex justify-between items-center">
          <h4 class="font-bold text-slate-900">📋 Periodic OCR, IRD Tax & Audit Activities (${c.activities.length})</h4>
          <button onclick="closeModal(); openComplianceModal(${c.id})" class="px-3 py-1 bg-indigo-600 text-white rounded-lg text-xs font-bold">+ Add Activity</button>
        </div>

        <div class="border rounded-xl overflow-hidden">
          <table class="w-full text-xs">
            <thead class="bg-slate-800 text-white">
              <tr>
                <th class="p-2 text-left">Due Date</th>
                <th class="p-2 text-left">Pillar</th>
                <th class="p-2 text-left">Activity</th>
                <th class="p-2 text-left">FY</th>
                <th class="p-2 text-left">Status</th>
              </tr>
            </thead>
            <tbody class="divide-y">
              ${c.activities
                .map(
                  (a) => `
                <tr>
                  <td class="p-2 font-bold">${a.due_date_bs}</td>
                  <td class="p-2 font-bold">${a.category}</td>
                  <td class="p-2">${a.activity_type}</td>
                  <td class="p-2">${a.fiscal_year}</td>
                  <td class="p-2 font-semibold">${a.status}</td>
                </tr>`
                )
                .join("")}
            </tbody>
          </table>
        </div>
      </div>`
    );
  } catch (err) {
    showToast(err.message, true);
  }
}

// ============================================================================
// 8. COMPLIANCE ACTIVITIES (OCR, IRD TAX & AUDIT TRACKER)
// ============================================================================
function filterComplianceCategory(cat) {
  selectedComplianceCategory = cat;
  loadComplianceActivities();
}

async function loadComplianceActivities() {
  const search = document.getElementById("compliance-search")?.value || "";
  const url = `/api/company/activities?category=${encodeURIComponent(selectedComplianceCategory)}&search=${encodeURIComponent(search)}`;
  const items = await apiFetch(url);
  const tbody = document.getElementById("compliance-table-body");

  if (!items.length) {
    tbody.innerHTML = `<tr><td colspan="8" class="p-8 text-center text-slate-400">No compliance activities found</td></tr>`;
    return;
  }

  tbody.innerHTML = items
    .map((a) => {
      const catBadge =
        a.category === "OCR"
          ? `<span class="px-2.5 py-1 rounded-full text-xs font-bold bg-amber-100 text-amber-900">🏛️ OCR</span>`
          : a.category === "IRD_TAX"
          ? `<span class="px-2.5 py-1 rounded-full text-xs font-bold bg-blue-100 text-blue-900">🧾 IRD Tax</span>`
          : `<span class="px-2.5 py-1 rounded-full text-xs font-bold bg-purple-100 text-purple-900">📊 Audit</span>`;

      const isDone = a.status.includes("Completed") || a.status.includes("सम्पन्न");
      return `
      <tr class="hover:bg-slate-50 transition">
        <td class="py-3.5 px-4">
          <div class="font-extrabold text-slate-900">📅 ${a.due_date_bs}</div>
          <div class="text-[11px] text-amber-800 font-semibold">🔔 Reminder: ${a.next_reminder_date_bs}</div>
        </td>
        <td class="py-3.5 px-4">${catBadge}</td>
        <td class="py-3.5 px-4">
          <button onclick="openCompanyDetailModal(${a.company_id})" class="font-bold text-blue-700 hover:underline">${a.company_name_en}</button>
          <div class="text-xs text-slate-500">OCR: ${a.ocr_registration_no} | PAN: ${a.pan_vat_no}</div>
        </td>
        <td class="py-3.5 px-4 max-w-sm">
          <div class="font-bold text-slate-900 text-xs">${a.activity_type}</div>
          ${a.remarks ? `<div class="text-[11px] text-slate-500 mt-0.5">${a.remarks}</div>` : ""}
        </td>
        <td class="py-3.5 px-4 text-xs">
          <div class="font-mono font-bold">FY ${a.fiscal_year}</div>
          <div class="text-slate-500">${a.period_label || ""}</div>
        </td>
        <td class="py-3.5 px-4 text-xs">
          ${a.reference_or_certificate_no ? `<div class="font-mono font-bold text-emerald-800">Ref: ${a.reference_or_certificate_no}</div>` : ""}
          ${a.udin_number ? `<div class="font-mono font-bold text-purple-800">UDIN: ${a.udin_number}</div>` : ""}
          ${a.auditor_or_officer_name ? `<div class="text-slate-600">${a.auditor_or_officer_name}</div>` : ""}
        </td>
        <td class="py-3.5 px-4">
          <span class="px-2.5 py-1 rounded-full text-xs font-bold ${
            isDone ? "bg-emerald-100 text-emerald-800" : "bg-amber-100 text-amber-900"
          }">${a.status}</span>
        </td>
        <td class="py-3.5 px-4 text-right space-x-1">
          ${
            !isDone
              ? `<button onclick="markComplianceDone(${a.id})" class="px-2.5 py-1 bg-emerald-600 hover:bg-emerald-700 text-white rounded text-xs font-bold">✓ Complete</button>`
              : ""
          }
          <button onclick="deleteCompliance(${a.id})" class="px-2 py-1 bg-rose-50 text-rose-600 rounded text-xs">✕</button>
        </td>
      </tr>`;
    })
    .join("");
}

function openComplianceModal(preselectedCompanyId = null) {
  const compOpts = cachedCompanies
    .map((c) => `<option value="${c.id}" ${preselectedCompanyId === c.id ? "selected" : ""}>${c.company_name_en} (PAN: ${c.pan_vat_no})</option>`)
    .join("");

  const allTemplates = [
    ...COMPLIANCE_TEMPLATES.OCR,
    ...COMPLIANCE_TEMPLATES.IRD_TAX,
    ...COMPLIANCE_TEMPLATES.AUDIT,
  ]
    .map((x) => `<option value="${x}">`)
    .join("");

  openModal(
    "📋 Add OCR, IRD Tax or Statutory Audit Activity & Reminder",
    `
    <form id="compliance-form" class="space-y-4">
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label class="block text-xs font-bold text-slate-700 mb-1">Select Company *</label>
          <select name="company_id" required class="w-full px-3 py-2 border rounded-lg bg-white">${compOpts}</select>
        </div>
        <div>
          <label class="block text-xs font-bold text-slate-700 mb-1">Pillar / Authority *</label>
          <select name="category" class="w-full px-3 py-2 border rounded-lg bg-white">
            <option value="OCR">🏛️ OCR (Office of the Company Registrar / कम्पनी रजिष्ट्रार)</option>
            <option value="IRD_TAX">🧾 IRD Tax & Clearance (आन्तरिक राजस्व विभाग / कर)</option>
            <option value="AUDIT">📊 Statutory Audit & AGM (वैधानिक लेखापरीक्षण / साधारण सभा)</option>
          </select>
        </div>
        <div class="md:col-span-2">
          <label class="block text-xs font-bold text-slate-700 mb-1">Activity / Filing Type (Select or Type) *</label>
          <input list="comp-act-list" name="activity_type" required placeholder="e.g. Section 78 Annual Return, Monthly VAT Return, Tax Clearance..." class="w-full px-3 py-2 border rounded-lg" />
          <datalist id="comp-act-list">${allTemplates}</datalist>
        </div>
        <div>
          <label class="block text-xs font-bold text-slate-700 mb-1">Fiscal Year (आर्थिक वर्ष) *</label>
          <input type="text" name="fiscal_year" required value="2082/83" class="w-full px-3 py-2 border rounded-lg" />
        </div>
        <div>
          <label class="block text-xs font-bold text-slate-700 mb-1">Period Label (मासिक / त्रैमासिक / वार्षिक)</label>
          <input type="text" name="period_label" placeholder="e.g. Kartik 25th / Poush End" class="w-full px-3 py-2 border rounded-lg" />
        </div>
        <div>
          <label class="block text-xs font-bold text-slate-700 mb-1">Statutory Due Date BS (म्याद मिति) *</label>
          <input type="text" name="due_date_bs" required value="2083-09-29" class="w-full px-3 py-2 border rounded-lg" />
        </div>
        <div>
          <label class="block text-xs font-bold text-slate-700 mb-1">Next Reminder Date BS (अनुस्मारक मिति)</label>
          <input type="text" name="next_reminder_date_bs" value="2083-09-15" class="w-full px-3 py-2 border rounded-lg" />
        </div>
        <div>
          <label class="block text-xs font-bold text-slate-700 mb-1">OCR Ref / Tax Clearance No.</label>
          <input type="text" name="reference_or_certificate_no" placeholder="CAMIS / IRD Submission No." class="w-full px-3 py-2 border rounded-lg" />
        </div>
        <div>
          <label class="block text-xs font-bold text-slate-700 mb-1">ICAN UDIN No. (For Audit)</label>
          <input type="text" name="udin_number" placeholder="UDIN Number" class="w-full px-3 py-2 border rounded-lg" />
        </div>
      </div>
      <div>
        <label class="block text-xs font-bold text-slate-700 mb-1">Remarks / Checklist Notes</label>
        <textarea name="remarks" rows="2" class="w-full px-3 py-2 border rounded-lg"></textarea>
      </div>
      <div class="flex justify-end gap-2 pt-3 border-t">
        <button type="button" onclick="closeModal()" class="px-4 py-2 bg-slate-200 rounded-lg font-semibold">Cancel</button>
        <button type="submit" class="px-5 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg font-bold shadow">Save Activity</button>
      </div>
    </form>`
  );

  document.getElementById("compliance-form").onsubmit = async (e) => {
    e.preventDefault();
    const raw = Object.fromEntries(new FormData(e.target).entries());
    try {
      await apiFetch("/api/company/activities", {
        method: "POST",
        body: JSON.stringify({ ...raw, company_id: Number(raw.company_id) }),
      });
      showToast("Compliance activity & reminder added");
      closeModal();
      await loadComplianceActivities();
      await loadDashboard();
    } catch (err) {
      showToast(err.message, true);
    }
  };
}

async function markComplianceDone(actId) {
  const refNo = prompt("Enter OCR Filing No. / IRD Tax Clearance Certificate No. / UDIN (optional):", "");
  if (refNo === null) return;
  try {
    await apiFetch(`/api/company/activities/${actId}`, {
      method: "PUT",
      body: JSON.stringify({
        status: "Completed / Cleared (सम्पन्न / चुक्ता)",
        completed_date_bs: currentBsDate,
        reference_or_certificate_no: refNo || undefined,
      }),
    });
    showToast("Marked as Completed!");
    await loadComplianceActivities();
    await loadCompanies();
  } catch (err) {
    showToast(err.message, true);
  }
}

async function deleteCompliance(id) {
  if (!confirm("Delete this compliance activity?")) return;
  await apiFetch(`/api/company/activities/${id}`, { method: "DELETE" });
  await loadComplianceActivities();
}

// ============================================================================
// 9. STAFF & ADVOCATES / AUDITORS
// ============================================================================
async function loadStaff() {
  const list = await apiFetch("/api/staff");
  cachedStaff = list;
  document.getElementById("staff-table-body").innerHTML = list
    .map(
      (s) => `
    <tr class="hover:bg-slate-50 transition">
      <td class="py-3.5 px-4"><div class="font-bold text-slate-900">${s.full_name}</div><div class="text-xs text-slate-500">@${s.username}</div></td>
      <td class="py-3.5 px-4"><span class="px-2.5 py-0.5 rounded-full text-xs font-bold bg-amber-100 text-amber-900">${s.designation}</span></td>
      <td class="py-3.5 px-4"><div class="font-mono text-xs font-bold">${s.bar_council_no || "-"}</div><div class="text-xs text-slate-600">${s.specialization || "-"}</div></td>
      <td class="py-3.5 px-4"><div class="font-bold">📞 ${s.phone}</div><div class="text-xs text-blue-600">${s.email || ""}</div></td>
      <td class="py-3.5 px-4 text-xs">${s.address || "-"}</td>
      <td class="py-3.5 px-4 text-center"><span class="px-3 py-1 bg-slate-900 text-amber-400 rounded-lg text-xs font-bold">${s.total_cases_count}</span></td>
      <td class="py-3.5 px-4 text-right">
        <button onclick='openStaffModal(${JSON.stringify(s).replace(/'/g, "&#39;")})' class="px-2.5 py-1 bg-slate-100 rounded text-xs font-semibold">Edit</button>
      </td>
    </tr>`
    )
    .join("");
}

function openStaffModal(member = null) {
  const isEdit = !!member;
  openModal(
    isEdit ? "👨‍⚖️ Edit Advocate / Auditor / Staff" : "👨‍⚖️ Add Advocate / Auditor / Staff",
    `
    <form id="staff-form" class="space-y-4">
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label class="block text-xs font-bold text-slate-700 mb-1">Full Name *</label>
          <input type="text" name="full_name" required value="${member?.full_name || ""}" class="w-full px-3 py-2 border rounded-lg" />
        </div>
        <div>
          <label class="block text-xs font-bold text-slate-700 mb-1">Role *</label>
          <select name="role" class="w-full px-3 py-2 border rounded-lg bg-white">
            <option value="advocate">Advocate / Auditor (अधिवक्ता / लेखापरीक्षक)</option>
            <option value="staff">Assistant Staff (सहायक कर्मचारी)</option>
            <option value="admin">Managing Partner / Admin</option>
          </select>
        </div>
        <div>
          <label class="block text-xs font-bold text-slate-700 mb-1">Designation *</label>
          <input type="text" name="designation" required value="${member?.designation || "Advocate / Tax Advisor"}" class="w-full px-3 py-2 border rounded-lg" />
        </div>
        <div>
          <label class="block text-xs font-bold text-slate-700 mb-1">Bar Council / ICAN COP No.</label>
          <input type="text" name="bar_council_no" value="${member?.bar_council_no || ""}" class="w-full px-3 py-2 border rounded-lg" />
        </div>
        <div>
          <label class="block text-xs font-bold text-slate-700 mb-1">Phone *</label>
          <input type="text" name="phone" required value="${member?.phone || ""}" class="w-full px-3 py-2 border rounded-lg" />
        </div>
        <div>
          <label class="block text-xs font-bold text-slate-700 mb-1">Username *</label>
          <input type="text" name="username" required value="${member?.username || ""}" ${isEdit ? "readonly" : ""} class="w-full px-3 py-2 border rounded-lg" />
        </div>
      </div>
      <div class="flex justify-end gap-2 pt-3 border-t">
        <button type="button" onclick="closeModal()" class="px-4 py-2 bg-slate-200 rounded-lg font-semibold">Cancel</button>
        <button type="submit" class="px-5 py-2 bg-amber-600 text-white rounded-lg font-bold shadow">Save</button>
      </div>
    </form>`
  );

  document.getElementById("staff-form").onsubmit = async (e) => {
    e.preventDefault();
    const payload = Object.fromEntries(new FormData(e.target).entries());
    if (isEdit) {
      await apiFetch(`/api/staff/${member.id}`, { method: "PUT", body: JSON.stringify(payload) });
    } else {
      await apiFetch("/api/staff", { method: "POST", body: JSON.stringify(payload) });
    }
    closeModal();
    await loadStaff();
  };
}

// ============================================================================
// 10. PLUG & PLAY MODULE SUBSCRIPTION MANAGER
// ============================================================================
async function loadModulesView() {
  const modules = await apiFetch("/api/modules");
  cachedModules = modules;
  applyModuleVisibility();

  const container = document.getElementById("modules-cards-container");
  container.innerHTML = modules
    .map((m) => {
      const title = currentLang === "ne" ? m.name_np : m.name_en;
      const desc = currentLang === "ne" ? m.description_np : m.description_en;
      const isCompanyMod = m.module_key === "company_management";
      return `
      <div class="bg-white p-6 rounded-2xl border-2 ${
        m.is_enabled ? "border-emerald-500" : "border-slate-200 opacity-75"
      } shadow-sm flex flex-col justify-between space-y-4">
        <div>
          <div class="flex justify-between items-start gap-2">
            <div>
              <span class="px-2.5 py-0.5 rounded-full text-[11px] font-extrabold uppercase ${
                m.is_enabled ? "bg-emerald-100 text-emerald-800" : "bg-slate-200 text-slate-600"
              }">${m.is_enabled ? "✓ Active Subscription" : "Disabled"}</span>
              <h4 class="text-lg font-extrabold text-slate-900 mt-2">${title}</h4>
            </div>
            <label class="inline-flex items-center cursor-pointer">
              <input type="checkbox" ${m.is_enabled ? "checked" : ""}
                onchange="toggleModuleSubscription('${m.module_key}', this.checked)"
                class="w-6 h-6 accent-emerald-600 rounded cursor-pointer" />
            </label>
          </div>
          <p class="text-xs text-slate-600 mt-2">${desc}</p>

          ${
            isCompanyMod
              ? `
          <div class="mt-4 pt-4 border-t space-y-2 text-xs">
            <div class="font-bold text-slate-700">Included Sub-Modules (Plug & Play):</div>
            <div class="flex flex-wrap gap-2">
              <span class="px-3 py-1 bg-amber-50 border border-amber-200 rounded-lg font-semibold text-amber-900">🏛️ OCR (Company Registrar: Reg, Sec 78, Sec 51, Share Lagat)</span>
              <span class="px-3 py-1 bg-blue-50 border border-blue-200 rounded-lg font-semibold text-blue-900">🧾 IRD Tax (Monthly VAT, e-TDS, Est. Tax, D-03 & Tax Clearance)</span>
              <span class="px-3 py-1 bg-purple-50 border border-purple-200 rounded-lg font-semibold text-purple-900">📊 Statutory Audit (ICAN Auditor, UDIN & AGM)</span>
            </div>
          </div>`
              : `
          <div class="mt-4 pt-4 border-t space-y-2 text-xs">
            <div class="font-bold text-slate-700">Included Features:</div>
            <div class="flex flex-wrap gap-2">
              <span class="px-3 py-1 bg-slate-100 rounded-lg font-semibold">📁 Court Cases (Mudda)</span>
              <span class="px-3 py-1 bg-slate-100 rounded-lg font-semibold">🏛️ Daily Hearings (Peshi/Tarekh)</span>
              <span class="px-3 py-1 bg-slate-100 rounded-lg font-semibold">💰 Fee Deals & Receipts</span>
              <span class="px-3 py-1 bg-slate-100 rounded-lg font-semibold">📄 Original/Copy Document Vault</span>
            </div>
          </div>`
          }
        </div>
      </div>`;
    })
    .join("");
}

async function toggleModuleSubscription(moduleKey, isEnabled) {
  try {
    await apiFetch(`/api/modules/${moduleKey}`, {
      method: "PUT",
      body: JSON.stringify({ is_enabled: isEnabled }),
    });
    showToast(`Module '${moduleKey}' ${isEnabled ? "enabled" : "disabled"}!`);
    await loadModulesView();
  } catch (err) {
    showToast(err.message, true);
  }
}

// ============================================================================
// 11. TOOLS (CONFLICT CHECK & BS/AD CONVERTER)
// ============================================================================
async function runConflictCheck() {
  const q = document.getElementById("conflict-input").value.trim();
  if (!q) return;
  const res = await apiFetch(`/api/dashboard/conflict-check?q=${encodeURIComponent(q)}`);
  const box = document.getElementById("conflict-results");

  if (!res.has_conflict) {
    box.innerHTML = `<div class="p-3 bg-emerald-50 border border-emerald-200 text-emerald-800 rounded-xl font-semibold">✓ No Conflict Found for "${q}".</div>`;
    return;
  }

  let html = "";
  if (res.matched_as_client.length) {
    html += `<div class="p-3 bg-blue-50 border border-blue-200 rounded-xl"><div class="font-bold text-blue-900 mb-1">👥 Matched Clients (${res.matched_as_client.length}):</div>`;
    html += res.matched_as_client.map((c) => `<div>• <strong>${c.full_name}</strong> (${c.phone})</div>`).join("");
    html += `</div>`;
  }
  if (res.matched_in_cases_or_opponent.length) {
    html += `<div class="p-3 bg-rose-50 border border-rose-200 rounded-xl"><div class="font-bold text-rose-900 mb-1">⚠️ Matched in Cases / Opponents (${res.matched_in_cases_or_opponent.length}):</div>`;
    html += res.matched_in_cases_or_opponent
      .map((m) => `<div>• Case <strong>${m.case_number}</strong> — Client: ${m.client_name} | <strong>Opponent: ${m.opponent_name}</strong></div>`)
      .join("");
    html += `</div>`;
  }
  box.innerHTML = html;
}

async function convertBsToAd() {
  const bs = document.getElementById("conv-bs-input").value.trim();
  const data = await apiFetch(`/api/dashboard/date-convert?bs=${encodeURIComponent(bs)}`);
  const resBox = document.getElementById("conv-result");
  resBox.textContent = `BS ${data.bs} (${data.bs_human})  =  AD: ${data.ad || "Invalid"}`;
  resBox.classList.remove("hidden");
  if (data.ad) document.getElementById("conv-ad-input").value = data.ad;
}

async function convertAdToBs() {
  const ad = document.getElementById("conv-ad-input").value.trim();
  const data = await apiFetch(`/api/dashboard/date-convert?ad=${encodeURIComponent(ad)}`);
  const resBox = document.getElementById("conv-result");
  resBox.textContent = `AD ${data.ad}  =  BS: ${data.bs} (${data.bs_human})`;
  resBox.classList.remove("hidden");
  if (data.bs) document.getElementById("conv-bs-input").value = data.bs;
}

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
