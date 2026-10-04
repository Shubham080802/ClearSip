function waitForEvent(video, eventName, timeoutMs, start = () => {}) {
  return new Promise((resolve, reject) => {
    let timer;
    const cleanup = () => {
      clearTimeout(timer);
      video.removeEventListener(eventName, onReady);
      video.removeEventListener("error", onError);
    };
    const onReady = () => { cleanup(); resolve(); };
    const onError = () => { cleanup(); reject(new Error("Video could not be decoded.")); };
    video.addEventListener(eventName, onReady);
    video.addEventListener("error", onError);
    timer = setTimeout(() => { cleanup(); reject(new Error("Video frame loading timed out.")); }, timeoutMs);
    try { start(); } catch (error) { cleanup(); reject(error); }
  });
}

export function waitForVideoMetadata(video, url, timeoutMs = 10_000) {
  return waitForEvent(video, "loadedmetadata", timeoutMs, () => { video.src = url; });
}

export function seekReadableVideoFrame(video, timeoutMs = 10_000) {
  const duration = Number.isFinite(video.duration) ? video.duration : 0;
  const target = Math.min(Math.max(duration / 2, 0), 2);
  if (target > 0 && Math.abs(video.currentTime - target) > 0.01) {
    return waitForEvent(video, "seeked", timeoutMs, () => { video.currentTime = target; });
  }
  if (video.readyState >= 2) return Promise.resolve();
  return waitForEvent(video, "loadeddata", timeoutMs);
}
