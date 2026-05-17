// UI controller — wires buttons to the API client and renders recommendations.

const els = {
  loginBtn: document.getElementById("login-btn"),
  syncBtn: document.getElementById("sync-btn"),
  userInfo: document.getElementById("user-info"),
  status: document.getElementById("status"),
  recs: document.getElementById("recommendations"),
};

els.loginBtn.addEventListener("click", () => {
  window.location.href = Api.loginUrl();
});

els.syncBtn.addEventListener("click", async () => {
  setStatus("Syncing your AniList...");
  els.syncBtn.disabled = true;
  try {
    const result = await Api.sync();
    setStatus(`Synced ${result.synced} interactions. Recommendations refresh hourly.`);
    await loadRecommendations();
  } catch (err) {
    setStatus(err instanceof AuthError ? "Please log in first." : `Error: ${err.message}`);
  } finally {
    els.syncBtn.disabled = false;
  }
});

async function loadRecommendations() {
  setStatus("Loading recommendations...");
  try {
    const data = await Api.recommendations();
    renderRecommendations(data.recommendations || []);
    els.userInfo.classList.remove("hidden");
    els.loginBtn.classList.add("hidden");
    if ((data.recommendations || []).length === 0) {
      setStatus("No recommendations yet. Click 'Sync my list' and check back next hour.");
    } else {
      hideStatus();
    }
  } catch (err) {
    if (err instanceof AuthError) {
      // Not logged in — landing state
      hideStatus();
    } else {
      setStatus(`Error: ${err.message}`);
    }
  }
}

function renderRecommendations(recs) {
  if (recs.length === 0) {
    els.recs.innerHTML = "";
    return;
  }
  els.recs.innerHTML = recs
    .map(
      (r) => `
      <article class="recommendation-item">
        ${r.cover_image_large ? `<img src="${escapeHtml(r.cover_image_large)}" alt="">` : ""}
        <div class="recommendation-body">
          <h3>${escapeHtml(r.title_english || r.title_romaji || "Untitled")}</h3>
          <p class="genres">${escapeHtml(r.genres || "")}</p>
          <p class="score">
            score <strong>${(r.score || 0).toFixed(3)}</strong>
            <span class="breakdown">
              (content ${(r.content_score || 0).toFixed(2)} ·
              collaborative ${(r.collaborative_score || 0).toFixed(2)})
            </span>
          </p>
        </div>
      </article>`
    )
    .join("");
}

function setStatus(msg) {
  els.status.textContent = msg;
  els.status.classList.remove("hidden");
}

function hideStatus() {
  els.status.classList.add("hidden");
}

function escapeHtml(s) {
  return String(s)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

// Try loading on page open — succeeds if session cookie is valid, no-ops otherwise.
loadRecommendations();
