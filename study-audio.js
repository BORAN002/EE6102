/** A click-to-play queue. No playback happens until the user asks for it. */
export class StudyAudio {
  constructor(media, onChange = () => {}) {
    this.media = media;
    this.onChange = onChange;
    this.queue = [];
    this.index = 0;
    this.revision = 0;
    this.rate = 1;
    this.status = 'idle';
    media.preload = 'none';
    media.addEventListener('playing', () => { if (this.queue.length) this.update('playing'); });
    media.addEventListener('pause', () => { if (this.queue.length && !media.ended) this.update('paused'); });
    media.addEventListener('ended', () => {
      if (!this.queue.length) return;
      if (this.index + 1 < this.queue.length) { this.index++; this.start(); }
      else this.update('ended');
    });
    media.addEventListener('error', () => { if (this.queue.length) this.update('error'); });
  }
  update(status) {
    this.status = status;
    this.onChange({ status, current: this.queue[this.index] || null, index: this.index, total: this.queue.length });
  }
  setRate(rate) {
    if (![.75, 1, 1.25].includes(Number(rate))) return;
    this.rate = Number(rate);
    this.media.playbackRate = this.rate;
  }
  play(items) {
    this.stop();
    this.queue = items.filter(item => item && /^audio\/en\/[a-f0-9]+\.m4a$/.test(item.src));
    if (this.queue.length) this.start();
  }
  async start() {
    const revision = ++this.revision;
    this.media.src = this.queue[this.index].src;
    this.media.playbackRate = this.rate;
    this.update('loading');
    try { await this.media.play(); }
    catch { if (revision === this.revision && this.queue.length) this.update('error'); }
  }
  stop() {
    this.revision++;
    this.queue = [];
    this.index = 0;
    this.media.pause();
    this.media.removeAttribute('src');
    this.media.load();
    this.update('idle');
  }
}
