const MILESTONES = [10, 25, 50, 100, 250, 500, 1000];
const DATA_URL = "data/milestones.json";

const el = (id) => document.getElementById(id);
let runners = [];

function nextMilestone(total) {
  return MILESTONES.find((m) => m > total) ?? null;
}
function achieved(total) {
  return MILESTONES.filter((m) => total >= m);
}
function escapeHtml(value) {
  return String(value ?? "").replace(/[&<>"']/g, c => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"
  })[c]);
}
function render() {
  const query = el("search").value.trim().toLowerCase();
  const filter = el("filter").value;
  const filtered = runners.filter(r => {
    const total = Number(r.total_runs) || 0;
    const next = nextMilestone(total);
    const matches = `${r.name} ${r.athlete_id}`.toLowerCase().includes(query);
    const milestoneFilter = filter !== "milestone" || achieved(total).length > 0;
    const closeFilter = filter !== "close" || (next !== null && next - total <= 5);
    return matches && milestoneFilter && closeFilter;
  }).sort((a, b) => (Number(b.total_runs) || 0) - (Number(a.total_runs) || 0));

  el("results").innerHTML = filtered.length ? filtered.map(r => {
    const total = Number(r.total_runs) || 0;
    const done = achieved(total);
    const next = nextMilestone(total);
    const previous = [...MILESTONES].reverse().find(m => m <= total) || 0;
    const target = next || MILESTONES[MILESTONES.length - 1];
    const progress = next === null ? 100 : Math.max(0, Math.min(100, ((total - previous) / (target - previous)) * 100));
    const badges = done.length ? done.map(m => `<span class="pill ${m >= 250 ? "gold" : ""}">${m}</span>`).join("") : '<span class="sub">Not yet</span>';
    const nextText = next === null ? "All listed milestones" : `${next} (${next - total} to go)`;
    const profile = `https://www.parkrun.com.au/parkrunner/${encodeURIComponent(r.athlete_id)}/`;
    return `<tr>
      <td><span class="runner">${escapeHtml(r.name)}</span><span class="sub"><a href="${profile}" target="_blank" rel="noopener">ID ${escapeHtml(r.athlete_id)} · parkrun profile ↗</a></span></td>
      <td><strong>${total}</strong></td>
      <td><div class="pills">${badges}</div></td>
      <td>${nextText}</td>
      <td><div class="progress-wrap"><div class="progress-track"><div class="progress-bar" style="width:${progress}%"></div></div><span class="progress-label">${next === null ? "Complete" : `${Math.round(progress)}% to ${next}`}</span></div></td>
    </tr>`;
  }).join("") : '<tr><td colspan="5">No parkrunners match this filter.</td></tr>';

  el("runnerCount").textContent = runners.length;
  el("milestoneCount").textContent = runners.reduce((n, r) => n + achieved(Number(r.total_runs) || 0).length, 0);
  const closest = runners.filter(r => nextMilestone(Number(r.total_runs) || 0) !== null)
    .sort((a, b) => (nextMilestone(Number(a.total_runs)) - Number(a.total_runs)) - (nextMilestone(Number(b.total_runs)) - Number(b.total_runs)))[0];
  el("closestRunner").textContent = closest ? `${closest.name} · ${nextMilestone(Number(closest.total_runs)) - Number(closest.total_runs)} to go` : "—";
}
async function load() {
  try {
    const response = await fetch(`${DATA_URL}?v=${Date.now()}`, { cache: "no-store" });
    if (!response.ok) throw new Error(`Could not load data (${response.status})`);
    const data = await response.json();
    runners = Array.isArray(data.runners) ? data.runners : [];
    const date = data.updated_at ? new Date(data.updated_at).toLocaleString() : "date unavailable";
    el("updated").textContent = `Last updated: ${date}`;
    el("message").textContent = data.note || "Milestone totals are calculated from each athlete’s recorded parkrun finishes.";
    render();
  } catch (error) {
    el("updated").textContent = "Results data is not available yet.";
    el("message").textContent = `${error.message}. Run the GitHub Actions workflow after adding athlete IDs.`;
    el("results").innerHTML = '<tr><td colspan="5">No results data found.</td></tr>';
  }
}
el("search").addEventListener("input", render);
el("filter").addEventListener("change", render);
load();