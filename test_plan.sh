#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
node --input-type=module <<'JS'
import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
const source = readFileSync('frontend/src/App.jsx', 'utf8');
const component = source.split('function CopyButton(')[1]?.split('// ─── Login Page')[0];
assert.ok(component, 'CopyButton must exist');
const handler = component.match(/const handleCopy = async \(\) => \{([\s\S]*?)\n  \};/)?.[1];
assert.ok(handler, 'Copy handler must await clipboard completion');
const AsyncFunction = Object.getPrototypeOf(async function () {}).constructor;
function harness(navigator) {
  const state = { copied: false, error: false };
  const run = new AsyncFunction('navigator', 'textToCopy', 'setCopied', 'setCopyError', handler);
  return { state, click: () => run(navigator, 'Verified insight', x => state.copied = x, x => state.error = x) };
}
test('does not claim success until clipboard resolves', async () => {
  let resolve;
  let received;
  const h = harness({ clipboard: { writeText: text => { received = text; return new Promise(r => resolve = r); } } });
  const pending = h.click();
  assert.equal(h.state.copied, false);
  assert.equal(received, 'Verified insight');
  resolve();
  await pending;
  assert.equal(h.state.copied, true);
  assert.equal(h.state.error, false);
});
test('rejected clipboard writes show failure, never success', async () => {
  const h = harness({ clipboard: { writeText: async () => { throw new Error('permission denied'); } } });
  await h.click();
  assert.deepEqual(h.state, { copied: false, error: true });
});
test('unavailable clipboard is handled without an unhandled rejection', async () => {
  const h = harness({});
  await h.click();
  assert.deepEqual(h.state, { copied: false, error: true });
});
test('retry clears old error and succeeds only after the next write', async () => {
  let fail = true;
  const h = harness({ clipboard: { writeText: async () => { if (fail) throw new Error('denied'); } } });
  await h.click();
  fail = false;
  await h.click();
  assert.deepEqual(h.state, { copied: true, error: false });
});
test('feedback timer is cleaned up on effect cleanup', () => {
  const effect = component.match(/useEffect\(\(\) => \{([\s\S]*?)\n  \}, \[copied\]\);/)?.[1];
  assert.ok(effect, 'Copy feedback must have a cleanup effect');
  let cleanupTimer;
  let scheduled;
  const callback = new Function('copied', 'setTimeout', 'clearTimeout', 'setCopied', effect);
  const cleanup = callback(true, (fn, ms) => { scheduled = { fn, ms }; return 123; }, id => cleanupTimer = id, () => {});
  assert.equal(scheduled.ms, 2000);
  cleanup();
  assert.equal(cleanupTimer, 123);
  assert.equal(callback(false, () => assert.fail('must not schedule'), () => {}, () => {}), undefined);
});
test('copy failure has an honest accessible label', () => {
  assert.match(component, /aria-label=\{copyError \? "Copy failed\. Select and copy the text manually\."/);
});
JS
