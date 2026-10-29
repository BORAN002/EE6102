import test from 'node:test';
import assert from 'node:assert/strict';
import { StudyAudio } from '../study-audio.js';

class Media extends EventTarget {
  constructor() { super(); this.src = ''; this.ended = false; this.plays = []; this.playbackRate = 1; }
  play() {
    this.ended = false;
    this.plays.push(this.src);
    this.dispatchEvent(new Event('playing'));
    return this.pending || Promise.resolve();
  }
  pause() { this.dispatchEvent(new Event('pause')); }
  load() {}
  removeAttribute() { this.src = ''; }
  finish() { this.ended = true; this.dispatchEvent(new Event('ended')); }
}
const clips = ['a', 'b', 'c'].map(id => ({ src: `audio/en/${id.repeat(20)}.m4a`, label: id }));

test('a sentence queue advances once per ended event and stops after its last clip', () => {
  const media = new Media();
  const player = new StudyAudio(media);
  player.setRate(.75);
  player.play(clips);
  assert.equal(media.playbackRate, .75);
  media.finish();
  assert.equal(player.index, 1);
  assert.equal(media.src, clips[1].src);
  assert.equal(media.playbackRate, .75);
  media.finish(); media.finish();
  assert.equal(player.status, 'ended');
  assert.deepEqual(media.plays, clips.map(c => c.src));
});

test('switching to a word cancels the prior queue; closing prevents later advancement', () => {
  const media = new Media();
  const player = new StudyAudio(media);
  player.play(clips);
  player.play([clips[2]]);
  media.finish();
  assert.equal(player.status, 'ended');
  assert.deepEqual(media.plays, [clips[0].src, clips[2].src]);
  player.stop(); media.finish();
  assert.equal(player.status, 'idle');
  assert.equal(media.src, '');
  assert.equal(player.queue.length, 0);
});

test('a rejected old playback request cannot overwrite the next clip status', async () => {
  const media = new Media();
  let reject;
  media.pending = new Promise((_, fail) => { reject = fail; });
  const player = new StudyAudio(media);
  player.play([clips[0]]);
  media.pending = null;
  player.play([clips[1]]);
  reject(new Error('Aborted by another clip'));
  await Promise.resolve();
  assert.equal(player.status, 'playing');
  assert.equal(media.src, clips[1].src);
});

test('a playback failure is exposed and the next user attempt can recover', async () => {
  const media = new Media();
  media.pending = Promise.reject(new Error('No media support'));
  const player = new StudyAudio(media);
  player.play([clips[0]]);
  await Promise.resolve();
  assert.equal(player.status, 'error');
  media.pending = null;
  player.play([clips[0]]);
  assert.equal(player.status, 'playing');
});

test('unrecognized audio locations and unsupported playback rates are ignored', () => {
  const media = new Media();
  const player = new StudyAudio(media);
  player.play([{ src: 'https://example.com/speech.m4a' }]);
  assert.equal(media.plays.length, 0);
  player.setRate(0);
  assert.equal(player.rate, 1);
  player.setRate(1.25);
  assert.equal(media.playbackRate, 1.25);
});
