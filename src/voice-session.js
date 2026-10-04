export function createVoiceSession() {
  let revision = 0;
  let active = null;
  return {
    start(recognition) {
      this.cancel();
      active = recognition;
      return revision;
    },
    isCurrent(token) { return active !== null && token === revision; },
    finish(token) {
      if (this.isCurrent(token)) {
        active = null;
        revision++;
      }
    },
    cancel() {
      revision++;
      const previous = active;
      active = null;
      try { previous?.abort(); } catch { /* A browser may already have ended this session. */ }
    },
  };
}
