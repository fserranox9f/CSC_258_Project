//-----------------------------------------------------
// Dashboard script for showing live trend snapshots.
//
// Reads the latest trend data from the storage API and updates the page.
//
//   -- Open Design --
//   Dashboard only talks to the storage API. It does not know about Kafka,
//   Bluesky raw events, or database details.
//
//   -- Transparency --
//   Shows status text so users can see if data loaded or if the API failed.
//
//   -- Availability --
//   Refreshes every few seconds so the dashboard keeps updating as new
//   snapshots are saved.
//
//   -- Security --
//   Escapes user-generated post text before adding it to the HTML.
//-----------------------------------------------------

// storage API endpoint. Can be changed by setting window.DASHBOARD_API_BASE_URL.
const API_BASE_URL = window.DASHBOARD_API_BASE_URL || "http://localhost:5001";
const TREND_DATA_URL = `${API_BASE_URL}/api/latest-trends`;
const EXAMPLE_POSTS_URL = `${API_BASE_URL}/api/latest-examples`;

// refresh time for the dashboard
const REFRESH_MS = 5000;

// load the newest trend data from the storage service
async function loadTrends() {
  const status = document.getElementById("status");

  try {
    // request trends and example posts at the same time
    const [trendResponse, exampleResponse] = await Promise.all([
      fetch(`${TREND_DATA_URL}?t=${Date.now()}`),
      fetch(`${EXAMPLE_POSTS_URL}?t=${Date.now()}`),
    ]);

    // if either API call fails, show it in the dashboard status
    if (!trendResponse.ok) {
      throw new Error(`trends HTTP ${trendResponse.status}`);
    }

    if (!exampleResponse.ok) {
      throw new Error(`examples HTTP ${exampleResponse.status}`);
    }

    const trendPayload = await trendResponse.json();
    const examplePayload = await exampleResponse.json();

    // support both an array of snapshots and a single latest snapshot object
    const latest = latestSnapshotFrom(trendPayload);
    const latestExamples = latestSnapshotFrom(examplePayload);

    if (!latest) {
      status.textContent = "No trend snapshots saved yet.";
      return;
    }

    renderSnapshot(latest);
    renderExamples(latestExamples);

    status.textContent = "Live";
  } catch (error) {
    console.error(error);
    status.textContent = `Could not load trend data: ${error.message}`;
  }
}

// get the newest snapshot from the API response
function latestSnapshotFrom(payload) {
  if (Array.isArray(payload)) {
    return payload.length > 0 ? payload[payload.length - 1] : null;
  }

  if (payload && typeof payload === "object") {
    return payload;
  }

  return null;
}

// render posts processed, last update time, and top trend rows
function renderSnapshot(snapshot) {
  document.getElementById("postsProcessed").textContent =
    snapshot.posts_processed ?? 0;

  document.getElementById("lastUpdated").textContent =
    formatTimestamp(snapshot.timestamp);

  const trends = Array.isArray(snapshot.trends) ? snapshot.trends : [];
  const maxCount = Math.max(...trends.map((trend) => trend.count || 0), 1);
  const trendList = document.getElementById("trendList");
  trendList.innerHTML = "";

  if (trends.length === 0) {
    trendList.innerHTML = `<div class="empty-state">No trending words yet.</div>`;
    return;
  }

  // build one row per trend term
  for (let index = 0; index < trends.length; index++) {
    const trend = trends[index];
    const row = document.createElement("div");
    row.className = "trend-row";

    // scale the bar relative to the top trend count
    const count = trend.count ?? 0;
    const width = Math.max((count / maxCount) * 100, 4);

    row.innerHTML = `
      <div class="rank">${index + 1}</div>
      <div class="term">${escapeHtml(trend.term)}</div>
      <div class="bar-wrap">
        <div class="bar" style="width: ${width}%"></div>
      </div>
      <div class="count">${count}</div>
    `;

    trendList.appendChild(row);
  }
}

// render example posts for the top trending terms
function renderExamples(snapshot) {
  const exampleList = document.getElementById("exampleList");
  exampleList.innerHTML = "";

  // show a clear empty state if no examples have been saved yet
  if (!snapshot || !Array.isArray(snapshot.examples) || snapshot.examples.length === 0) {
    exampleList.innerHTML = `<div class="empty-state">No example posts saved yet.</div>`;
    return;
  }

  // build one card per example post
  for (const item of snapshot.examples) {
    const examplePost = item.example_post || {};
    const card = document.createElement("article");
    card.className = "example-card";

    card.innerHTML = `
      <div class="example-header">
        <span class="example-term">${escapeHtml(item.term)}</span>
        <span class="example-count">${escapeHtml(item.count ?? 0)}</span>
      </div>
      <p class="example-text">${escapeHtml(
        examplePost.text || "No post text saved."
      )}</p>
      <div class="example-meta">
        <span>${escapeHtml(examplePost.author || "unknown author")}</span>
        <span>${escapeHtml(formatTimestamp(examplePost.timestamp))}</span>
      </div>
    `;

    exampleList.appendChild(card);
  }
}

// convert API timestamps to a local readable time
function formatTimestamp(timestamp) {
  if (!timestamp) {
    return "Unknown";
  }

  const date = new Date(timestamp);
  if (Number.isNaN(date.getTime())) {
    return "Invalid date";
  }

  return date.toLocaleString();
}

// escape user text before inserting it into the page
function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

// load immediately, then keep refreshing for new snapshots
loadTrends();
setInterval(loadTrends, REFRESH_MS);
