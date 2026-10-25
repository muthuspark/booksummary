/* Search runs off the main thread; full article text is loaded only on request. */
const normalize = text => String(text || '').normalize('NFKD').replace(/[\u0300-\u036f]/g, '').toLocaleLowerCase();
let indexPromise;
const chunks = new Map();
async function fetchJSON(url) {
  const response = await fetch(url);
  if (!response.ok) throw new Error('Search unavailable');
  return response.json();
}
async function loadIndex(url) {
  if (!indexPromise) {
    indexPromise = fetchJSON(url).then(books => books.map(book => ({
      ...book,
      terms: normalize([book.title, book.author, book.description, ...book.categories].join(' ')),
      titleTerms: normalize(book.title),
    }))).catch(error => { indexPromise = undefined; throw error; });
  }
  return indexPromise;
}
function loadChunk(url) {
  if (!chunks.has(url)) {
    chunks.set(url, fetchJSON(url).then(rows => new Map(rows.map(row => [row.url, normalize(row.content)])))
      .catch(error => { chunks.delete(url); throw error; }));
  }
  return chunks.get(url);
}
self.onmessage = async ({ data }) => {
  const { id, indexURL, query, category, fullText } = data;
  try {
    const books = await loadIndex(indexURL);
    const candidates = books.filter(book => !category || book.categories.includes(category));
    const normalizedQuery = normalize(query.trim());
    const tokens = normalizedQuery.split(/\s+/).filter(Boolean);
    const content = new Map();
    if (fullText && tokens.length) {
      const urls = [...new Set(candidates.map(book => book.contentURL))];
      const loaded = await Promise.all(urls.map(loadChunk));
      for (const chunk of loaded) for (const [url, text] of chunk) content.set(url, text);
    }
    const matches = candidates.filter(book => {
      const text = book.terms + ' ' + (content.get(book.url) || '');
      return tokens.every(token => text.includes(token));
    });
    if (normalizedQuery) matches.sort((a, b) => Number(b.titleTerms.includes(normalizedQuery)) - Number(a.titleTerms.includes(normalizedQuery)));
    self.postMessage({ id, books: matches.map(({ terms, titleTerms, ...book }) => book) });
  } catch (_) {
    self.postMessage({ id, error: true });
  }
};
