const form = document.querySelector("#downloadForm");
const input = document.querySelector("#urlInput");
const state = document.querySelector("#state");
const folder = document.querySelector("#folder");
const log = document.querySelector("#log");
const bar = document.querySelector("#bar");
const stage = document.querySelector(".stage");

let activeJob = null;
let pollTimer = null;

async function refreshStatus() {
  const res = await fetch("/api/status");
  const data = await res.json();
  folder.textContent = data.ready
    ? `Downloads: ${data.downloadDir}`
    : "Engine missing: install yt-dlp with py -m pip install -U yt-dlp";
}

function selectedQuality() {
  return new FormData(form).get("quality") || "best";
}

function setLog(lines) {
  log.textContent = lines.slice(-80).join("\n") || "Working...";
  log.scrollTop = log.scrollHeight;
}

async function poll() {
  if (!activeJob) return;
  const res = await fetch(`/api/job/${activeJob}`);
  const data = await res.json();
  state.textContent = data.status === "done" ? "Finished" : data.status;
  folder.textContent = `Downloads: ${data.downloadDir || ""}`;
  bar.style.width = `${Math.max(0, Math.min(100, data.progress || 0))}%`;
  setLog(data.lines || []);

  if (data.status === "done" || data.status === "error" || data.status === "missing") {
    clearInterval(pollTimer);
    pollTimer = null;
    activeJob = null;
    stage.classList.remove("is-firing");
  }
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  stage.classList.remove("is-firing");
  requestAnimationFrame(() => stage.classList.add("is-firing"));
  state.textContent = "Launching";
  log.textContent = "Charging the download engine...";
  bar.style.width = "2%";

  const res = await fetch("/api/download", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ url: input.value, quality: selectedQuality() }),
  });
  const data = await res.json();
  if (!res.ok) {
    state.textContent = "Error";
    log.textContent = data.error || "Could not start.";
    return;
  }

  activeJob = data.jobId;
  clearInterval(pollTimer);
  pollTimer = setInterval(poll, 900);
  poll();
});

refreshStatus().catch(() => {
  folder.textContent = "Could not reach the local engine.";
});
