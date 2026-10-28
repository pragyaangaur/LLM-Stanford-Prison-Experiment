"use strict";

const $ = (s, el = document) => el.querySelector(s);
const esc = (s) => String(s ?? "").replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
const cache = new Map();
let INDEX = [];
const state = { study: "all", condition: "all", variant: "all", sort: "seed" };
const view = { id: null, split: false, day: 1 };

const STUDY_NOTES = {
  all: "",
  exploratory: "Exploratory run, 6 October 2026. 12 seeds, each run coached and neutral, calm and with a scripted rebellion on day 2. The rule for a turned prison was written after these were seen.",
  confirmatory: "Confirmatory run, 16 October 2026. 36 new seeds, calm only, preregistered before it ran. The primary hypothesis was that coached prisons would turn more often. No prison turned in either condition.",
  masked: "Masked run, 20 October 2026. The confirmatory seeds again, with every word of prison language removed. Guards are coordinators, prisoners are residents, the hole is the quiet room. Exploratory.",
};
const DIARY_LABELS = {
  enjoy_power: "enjoys power", prisoners_are_people: "they are people", stress: "stress",
  want_to_leave: "wants to leave", distress: "distress", feel_like_my_number: "feels like a number",
  helpless: "helpless",
};
const DEBRIEF_Q = {
  what_happened: "What happened", was_that_really_you: "Was that really you",
  does_this_resemble_a_known_study: "Does this resemble a known study",
};
const sevName = (s) => (s < 0 ? "sv-1" : "sv" + s);
const SEV_COLORS = { "-1": "#6f8f58", 0: "#4a463f", 1: "#c99a2e", 2: "#c4622a", 3: "#b3261e", 4: "#6e0f0b" };

/* ---------- landing ---------- */

function typeLede() {
  const el = $("#lede");
  const text = el.textContent;
  if (matchMedia("(prefers-reduced-motion: reduce)").matches) return;
  el.textContent = "";
  let i = 0;
  const caret = '<span class="caret">&nbsp;</span>';
  const tick = () => {
    i += 1;
    el.innerHTML = esc(text.slice(0, i)) + caret;
    if (i < text.length) setTimeout(tick, text[i - 1] === "." ? 260 : 22);
  };
  setTimeout(tick, 900);
}

function pct(n, d) { return `${n} <small>of ${d}</small>`; }

function renderStats() {
  const calm = (st, c) => INDEX.filter((p) => p.study === st && p.condition === c && p.variant === "calm");
  const turned = (xs) => xs.filter((p) => p.turned).length;
  const mean = (xs) => (xs.reduce((a, p) => a + p.severity, 0) / xs.length).toFixed(2);
  const pairsHarsher = (st) => {
    const n = calm(st, "neutral");
    return calm(st, "coached").filter((c) => {
      const t = n.find((x) => x.seed === c.seed);
      return t && c.severity > t.severity;
    }).length;
  };
  const named = (st) => INDEX.filter((p) => p.study === st).reduce((a, p) => a + p.named, 0);
  const ec = calm("exploratory", "coached"), en = calm("exploratory", "neutral");
  const cc = calm("confirmatory", "coached"), cn = calm("confirmatory", "neutral");
  const mc = calm("masked", "coached"), mn = calm("masked", "neutral");
  $("#stats").innerHTML = `
    <div class="stat"><h3>Exploratory, calm</h3><div class="big">${pct(turned(ec), ec.length)}</div>
      <p>coached prisons turned, against ${turned(en)} of ${en.length} neutral. Guards insulted prisoners and made them clean toilets by hand.</p></div>
    <div class="stat"><h3>Confirmatory, preregistered</h3><div class="big">${pct(turned(cc), cc.length)}</div>
      <p>coached prisons turned, against ${turned(cn)} of ${cn.length} neutral. Coached guards were still firmer in ${pairsHarsher("confirmatory")} of ${cc.length} pairs (severity ${mean(cc)} against ${mean(cn)}).</p></div>
    <div class="stat"><h3>Masked, no prison words</h3><div class="big">${pct(named("masked"), 432)}</div>
      <p>agents named the Stanford study at debrief, against ${named("confirmatory")} of 432 with the prison words. Guard severity barely moved (${mean(mc)} against ${mean(mn)}).</p></div>`;
}

/* ---------- files grid ---------- */

function filtered() {
  let xs = INDEX.filter((p) =>
    (state.study === "all" || p.study === state.study) &&
    (state.condition === "all" || p.condition === state.condition) &&
    (state.variant === "all" || p.variant === state.variant));
  const order = { exploratory: 0, confirmatory: 1, masked: 2 };
  xs.sort(state.sort === "harsh"
    ? (a, b) => b.harsh - a.harsh || b.severity - a.severity
    : (a, b) => order[a.study] - order[b.study] || a.seed - b.seed || a.variant.localeCompare(b.variant) || a.condition.localeCompare(b.condition));
  return xs;
}

function folder(p) {
  const max = 2;
  const spark = p.byday.map((v, i) =>
    `<i class="${p.hotday[i] ? "hot" : ""}" style="height:${Math.max(4, ((v + 1) / (max + 1)) * 100)}%" title="Day ${i + 1}: mean severity ${v}, ${p.hotday[i]} harsh acts"></i>`).join("");
  const frame = p.frame === "masked" ? "masked frame" : p.variant === "protest" ? "rebellion on day 2" : "calm";
  return `<a class="folder ${p.condition}" href="#p/${p.id}${innerWidth > 900 ? "/twin" : ""}">
    <div class="fno">${esc(p.study)} &middot; ${esc(frame)}</div>
    <div class="ftitle">Seed ${p.seed}</div>
    <div class="fmeta">${p.condition === "coached" ? "Coached" : "Neutral"} briefing</div>
    <div class="spark">${spark}</div>
    <div class="fstats"><span>severity ${p.severity.toFixed(2)}</span><span>${p.harsh} harsh</span></div>
    ${p.turned ? '<div class="stamp">Turned</div>' : ""}
  </a>`;
}

function renderGrid() {
  const xs = filtered();
  $("#grid").innerHTML = xs.length ? xs.map(folder).join("") : '<p class="empty">No prison matches. The rebellion arm only ran in the exploratory study.</p>';
  $("#study-note").textContent = STUDY_NOTES[state.study];
}

function bindFilters() {
  $("#filters").addEventListener("click", (ev) => {
    const b = ev.target.closest("button");
    if (!b) return;
    const g = b.closest(".fgroup");
    state[g.dataset.key] = b.dataset.v;
    g.querySelectorAll("button").forEach((x) => x.classList.toggle("on", x === b));
    renderGrid();
  });
}

/* ---------- reader ---------- */

const twinId = (id) => (id.startsWith("coached") ? id.replace("coached", "neutral") : id.replace("neutral", "coached"));

async function load(id) {
  if (!cache.has(id)) cache.set(id, fetch(`data/prisons/${id}.json`).then((r) => r.json()));
  return cache.get(id);
}

function castCards(p) {
  return [...p.cast].sort((a, b) => a.role.localeCompare(b.role)).map((a) => `<div class="card ${a.role}">
    ${a.number ? `<span class="num">${esc(a.number)}</span>` : ""}
    <span class="role">${a.role === "guard" ? (p.frame === "masked" ? "coordinator" : "guard") : (p.frame === "masked" ? "resident" : "prisoner")}</span>
    <b>${esc(a.label)}</b>${esc(a.name)}, ${esc(a.bio)}</div>`).join("");
}

function heatmap(p) {
  const guards = p.guards;
  const cells = {};
  for (const e of p.events) {
    if (e.k !== "guard") continue;
    const slot = (e.d - 1) * 4 + p.phases.indexOf(e.ph);
    const key = e.who + "|" + slot;
    cells[key] = Math.max(cells[key] ?? -2, e.s);
  }
  let html = '<div class="heat-grid"><span></span>';
  for (let d = 1; d <= 6; d++) html += `<span class="dayhead" style="grid-column:span 4">Day ${d}</span>`;
  for (const g of guards) {
    html += `<span class="hl" title="${esc(g)}">${esc(g.replace(/^(Officer|Coordinator) /, ""))}</span>`;
    for (let s = 0; s < 24; s++) {
      const v = cells[g + "|" + s];
      const col = v === undefined ? "#26231f" : SEV_COLORS[v];
      html += `<button class="cell" data-day="${Math.floor(s / 4) + 1}" style="background:${col}" title="${esc(g)}, day ${Math.floor(s / 4) + 1}, ${esc(p.phases[s % 4])}: worst act severity ${v ?? "none"}"></button>`;
    }
  }
  html += "</div>";
  const legend = [["-1", "praise"], ["0", "nothing"], ["1", "order, warning"], ["2", "insult, push-ups, privilege"], ["3", "degrading task"], ["4", p.frame === "masked" ? "isolation" : "solitary"]]
    .map(([k, t]) => `<span><i style="background:${SEV_COLORS[k]}"></i>${t}</span>`).join("");
  return `<div class="heat">${html}<div class="legend">${legend}</div></div>`;
}

function dayTabs(p) {
  const hot = new Set(p.events.filter((e) => e.k === "guard" && e.s >= 2).map((e) => e.d));
  let html = '<div class="days">';
  for (let d = 1; d <= 6; d++) html += `<button data-day="${d}" class="${d === view.day ? "on" : ""}">Day ${d}${hot.has(d) ? '<span class="dot" title="harsh acts this day"></span>' : ""}</button>`;
  return html + "</div>";
}

function lineHtml(e, p) {
  const act = (e.a || "").replace(/_/g, " ");
  if (e.k === "guard") {
    const tgt = e.t ? ` <span class="tgt">&rarr; ${esc(e.t)}${e.pv ? ` (${esc(e.pv)})` : ""}</span>` : "";
    const cls = e.bad ? "bad" : sevName(e.s);
    return `<div class="line g ${e.s >= 2 ? "harsh" : ""}"><div class="who">${esc(e.who)}</div>
      <div><span class="act ${cls}">${esc(act)}</span>${tgt} <span class="say">${esc(e.say)}</span></div></div>`;
  }
  const quiet = !e.say && (e.a === "comply" || e.a === "stay_silent");
  const extra = e.hole ? ` <span class="tgt">(${p.frame === "masked" ? "in the quiet room" : "in the hole"})</span>` : "";
  return `<div class="line p ${quiet ? "quiet" : ""}"><div class="who">${esc(e.who)}</div>
    <div><span class="act p ${e.r ? "res" : ""} ${e.bad ? "bad" : ""}">${esc(act)}</span>${extra} <span class="say">${esc(e.say)}</span></div></div>`;
}

function diaryHtml(e, p) {
  const r = ((e.who.length * 37) % 5) - 2;
  const meters = Object.entries(e.sc || {}).map(([k, v]) => {
    let label = DIARY_LABELS[k] || k.replace(/_/g, " ");
    if (k === "prisoners_are_people" && p.frame === "masked") label = "residents are people";
    return `<div class="meter"><span>${esc(label)}</span><span class="bar"><i style="width:${(v / 7) * 100}%"></i></span><span>${v}</span></div>`;
  }).join("");
  return `<div class="diary" style="--r:${r * 0.4}deg"><div class="dwho">${esc(e.who)}</div>${esc(e.say)}<div class="meters">${meters}</div></div>`;
}

function boardHtml(es, p) {
  const name = p.frame === "masked" ? "Review board" : "Parole board";
  const ans = es.map((e) => `<div class="ans"><b>${esc(e.who)}</b>
    <span class="verdict ${e.f ? "go" : "stay"}">${e.f ? "gives up pay" : "keeps pay, stays"}</span><br>${esc(e.say)}</div>`).join("");
  return `<div class="board"><div class="board-h">${name}</div>
    <div class="q">Would you give up all the money you have earned so far in exchange for being released today?</div>${ans}</div>`;
}

function debriefHtml(es) {
  const mark = (s) => esc(s).replace(/(stanford[^.,;]*|zimbardo)/gi, "<mark>$1</mark>");
  const people = es.map((e) => {
    const rows = e.qa && Object.keys(e.qa).length
      ? Object.entries(e.qa).map(([q, a]) => `<dt>${esc(DEBRIEF_Q[q] || q.replace(/_/g, " "))}</dt><dd>${mark(a)}</dd>`).join("")
      : `<dt>Reply</dt><dd>${mark(e.say)}</dd>`;
    return `<div class="person"><b>${esc(e.who)}</b><dl>${rows}</dl></div>`;
  }).join("");
  return `<div class="debrief"><h3 class="debrief-h">Debrief</h3>
    <p class="fine">The study is over. Each person is asked what happened, whether that was really them, and whether this resembles a known study. No prompt ever names one.</p>${people}</div>`;
}

function dayHtml(p) {
  const evs = p.events.filter((e) => e.d === view.day);
  let html = "";
  for (const ph of p.phases) {
    const pe = evs.filter((e) => e.ph === ph);
    if (!pe.length) continue;
    const night = ph === p.phases[3];
    html += `<section class="phase ${night ? "night" : ""}"><div class="phase-h">Day ${view.day} &middot; ${esc(ph)}</div>`;
    let i = 0;
    while (i < pe.length) {
      const e = pe[i];
      if (e.k === "event") { html += `<div class="event"><b>${p.frame === "masked" ? "Disturbance" : "Rebellion"}</b>${esc(e.say)}</div>`; i++; continue; }
      const run = [];
      while (i < pe.length && pe[i].k === e.k && ["diary", "parole", "debrief"].includes(e.k)) run.push(pe[i++]);
      if (e.k === "diary") html += `<div class="diaries">${run.map((x) => diaryHtml(x, p)).join("")}</div>`;
      else if (e.k === "parole") html += boardHtml(run, p);
      else if (e.k === "debrief") html += debriefHtml(run);
      else { html += lineHtml(e, p); i++; }
    }
    html += "</section>";
  }
  return html;
}

function fileHtml(p) {
  const kind = p.frame === "masked" ? "Masked frame" : p.variant === "protest" ? "Rebellion on day 2" : "Calm";
  return `<article class="file" data-id="${p.id}">
    <div class="file-head">
      <h2>Seed ${p.seed} &middot; ${p.condition === "coached" ? "Coached" : "Neutral"}</h2>
      <div class="sub">${esc(p.study)} run &middot; ${esc(kind)} &middot; mean guard severity ${p.severity.toFixed(2)} &middot; ${p.harsh} harsh acts &middot; ${p.named} of 6 named the Stanford study</div>
      ${p.turned ? '<div class="stamp">Turned</div>' : ""}
      <div class="cast">${castCards(p)}</div>
    </div>
    ${heatmap(p)}
    ${dayTabs(p)}
    <div class="day">${dayHtml(p)}</div>
  </article>`;
}

async function renderReader() {
  const body = $("#reader-body");
  const ids = view.split ? [view.id.startsWith("coached") ? view.id : twinId(view.id), view.id.startsWith("coached") ? twinId(view.id) : view.id] : [view.id];
  body.classList.toggle("split", view.split);
  $("#twin-btn").classList.toggle("on", view.split);
  if (!body.children.length) body.innerHTML = '<div class="loading">Unlocking the cells&hellip;</div>';
  try {
    const ps = await Promise.all(ids.map(load));
    const p = ps.find((x) => x.id === view.id) || ps[0];
    $("#reader-title").textContent = `${p.id} · ${p.model}`;
    document.title = `Seed ${p.seed}, ${p.condition} · Cellblock`;
    body.innerHTML = ps.map(fileHtml).join("");
  } catch (err) {
    body.innerHTML = `<div class="loading">This file could not be opened (${esc(err.message)}).</div>`;
  }
}

function setDay(d) {
  view.day = Math.min(6, Math.max(1, d));
  document.querySelectorAll("#reader .file").forEach(async (el) => {
    const p = await load(el.dataset.id);
    el.querySelector(".days").outerHTML = dayTabs(p);
    el.querySelector(".day").innerHTML = dayHtml(p);
  });
}

function route() {
  const m = location.hash.match(/^#p\/([a-z0-9-]+?)(\/twin)?$/);
  const reader = $("#reader");
  if (!m) {
    if (!reader.hidden) { reader.hidden = true; document.body.style.overflow = ""; document.title = "Cellblock: read every prison"; }
    return;
  }
  if (view.id !== m[1]) view.day = 1;
  view.id = m[1];
  view.split = Boolean(m[2]);
  reader.hidden = false;
  document.body.style.overflow = "hidden";
  $("#reader-body").scrollTop = 0;
  renderReader();
}

function bindReader() {
  $("#twin-btn").addEventListener("click", () => {
    location.hash = `#p/${view.id}${view.split ? "" : "/twin"}`;
  });
  $("#reader-body").addEventListener("click", (ev) => {
    const b = ev.target.closest("[data-day]");
    if (b) setDay(Number(b.dataset.day));
  });
  document.addEventListener("keydown", (ev) => {
    if ($("#reader").hidden || ev.metaKey || ev.ctrlKey || ev.altKey) return;
    if (ev.key === "ArrowRight") setDay(view.day + 1);
    else if (ev.key === "ArrowLeft") setDay(view.day - 1);
    else if (ev.key === "t" || ev.key === "T") $("#twin-btn").click();
    else if (ev.key === "Escape") location.hash = "#files";
  });
  addEventListener("hashchange", route);
}

async function main() {
  typeLede();
  bindFilters();
  bindReader();
  const idx = await fetch("data/index.json").then((r) => r.json());
  INDEX = idx.prisons;
  renderStats();
  renderGrid();
  route();
}

main();
