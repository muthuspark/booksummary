const test = require('node:test');
const assert = require('node:assert/strict');
const vm = require('node:vm');
const fs = require('node:fs');
const path = require('node:path');
const output = path.resolve(process.env.HUGO_TEST_OUTPUT || 'docs');
const source = fs.readFileSync('static/js/search-worker.js', 'utf8');

function workerHarness(failFirst = false) {
  const requested = [];
  let response;
  const context = vm.createContext({
    self: { postMessage: value => { response = value; } },
    fetch: async url => {
      requested.push(url);
      if (failFirst) { failFirst = false; return { ok: false }; }
      return { ok: true, json: async () => JSON.parse(fs.readFileSync(path.join(output, url), 'utf8')) };
    },
  });
  vm.runInContext(source, context);
  return {
    requested,
    async search(overrides = {}) {
      await context.self.onmessage({ data: { id: 1, indexURL: '/search.json', query: '', category: '', fullText: false, ...overrides } });
      return response;
    },
  };
}

test('title and category searches do not fetch full text; metadata is cached', async () => {
  const worker = workerHarness();
  let result = await worker.search({ query: 'Atomic Habits' });
  assert.equal(result.books[0].title, 'Atomic Habits by James Clear');
  result = await worker.search({ category: 'Productivity And Habits' });
  assert.equal(result.books.length, 52);
  assert.deepEqual(worker.requested, ['/search.json']);
});

test('full-text search loads only the selected category and retains body-only matches', async () => {
  const worker = workerHarness();
  const query = { category: 'Productivity And Habits', query: 'cueing' };
  const metadata = await worker.search(query);
  assert.equal(metadata.books.length, 0);
  const full = await worker.search({ ...query, fullText: true });
  assert.ok(full.books.some(book => book.title === 'Atomic Habits by James Clear'));
  assert.deepEqual(worker.requested, ['/search.json', '/search-content/productivity_and_habits.json']);
  await worker.search({ ...query, fullText: true });
  assert.equal(worker.requested.length, 2);
});

test('empty queries do not download body text even with full-text enabled', async () => {
  const worker = workerHarness();
  const result = await worker.search({ fullText: true });
  assert.equal(result.books.length, 830);
  assert.deepEqual(worker.requested, ['/search.json']);
});

test('index failures can be retried without reloading the page', async () => {
  const worker = workerHarness(true);
  assert.equal((await worker.search()).error, true);
  assert.equal((await worker.search()).books.length, 830);
});
