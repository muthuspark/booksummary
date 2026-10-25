(() => {
  const catalog = document.querySelector('#library');
  if (!catalog) return;
  const search = document.querySelector('#book-search');
  const category = document.querySelector('#category-filter');
  const fullText = document.querySelector('#fulltext-search');
  const form = catalog.querySelector('form');
  const grid = document.querySelector('#book-grid');
  const count = document.querySelector('#result-count');
  const heading = document.querySelector('#library-heading');
  const pagination = document.querySelector('#pagination');
  const more = document.querySelector('#load-more');
  const original = { html: grid.innerHTML, count: count.textContent };
  const params = new URLSearchParams(location.search);
  search.value = params.get('q') || '';
  fullText.checked = params.get('fulltext') === '1';
  if (params.has('category')) category.value = params.get('category');
  let worker;
  let matches = [];
  let visible = 36;
  let request = 0;
  let timer;
  let focusResults = false;

  function element(tag, className, text) {
    const node = document.createElement(tag);
    if (className) node.className = className;
    if (text) node.textContent = text;
    return node;
  }
  function bookCard(book) {
    const card = element('article', 'book-card');
    const cover = element('a', 'book-image');
    cover.href = book.url;
    cover.tabIndex = -1;
    cover.setAttribute('aria-hidden', 'true');
    const image = element('img');
    image.src = book.image;
    image.srcset = book.imageSrcset;
    image.sizes = '(max-width: 600px) 60px, 80px';
    image.alt = '';
    image.width = image.height = 80;
    image.loading = 'lazy';
    image.decoding = 'async';
    cover.append(image);
    const details = element('div', 'book-details');
    const title = element('h3');
    const link = element('a', '', book.title);
    link.href = book.url;
    title.append(link);
    details.append(title, element('p', '', book.description), element('p', 'muted', `${book.author} · ${book.readingTime} min read`));
    card.append(cover, details);
    return card;
  }
  function render() {
    grid.replaceChildren(...matches.slice(0, visible).map(bookCard));
    count.textContent = matches.length ? `${matches.length} ${matches.length === 1 ? 'summary' : 'summaries'} found · Showing ${Math.min(matches.length, visible)}` : 'No summaries found. Try another title, author, or category.';
    more.hidden = visible >= matches.length;
    pagination.hidden = true;
  }
  function finish() {
    catalog.removeAttribute('aria-busy');
    if (focusResults) {
      heading.focus();
      focusResults = false;
    }
  }
  function showError() {
    count.textContent = 'Search could not load. Check your connection and try again. You can still browse the summaries and category links.';
    finish();
  }
  function getWorker() {
    if (!worker) {
      worker = new Worker(catalog.dataset.workerUrl);
      worker.onmessage = ({ data }) => {
        if (data.id !== request) return;
        if (data.error) { showError(); return; }
        matches = data.books;
        visible = 36;
        render();
        finish();
      };
      worker.onerror = () => {
        worker.terminate();
        worker = undefined;
        showError();
      };
    }
    return worker;
  }
  function filter(moveFocus = false) {
    const current = ++request;
    focusResults = moveFocus;
    const query = search.value.trim();
    const chosen = category.value;
    const url = new URL(location.href);
    if (query) url.searchParams.set('q', query); else url.searchParams.delete('q');
    if (chosen) url.searchParams.set('category', chosen); else url.searchParams.delete('category');
    if (fullText.checked) url.searchParams.set('fulltext', '1'); else url.searchParams.delete('fulltext');
    if (moveFocus) url.hash = 'library';
    history.replaceState(null, '', url);
    if (!query && chosen === catalog.dataset.defaultCategory) {
      grid.innerHTML = original.html;
      count.textContent = original.count;
      pagination.hidden = false;
      more.hidden = true;
      finish();
      return;
    }
    count.textContent = 'Searching the collection…';
    catalog.setAttribute('aria-busy', 'true');
    try {
      getWorker().postMessage({ id: current, indexURL: catalog.dataset.searchUrl, query, category: chosen, fullText: fullText.checked });
    } catch (_) { showError(); }
  }
  form.addEventListener('submit', event => { event.preventDefault(); clearTimeout(timer); filter(true); });
  search.addEventListener('input', () => { clearTimeout(timer); timer = setTimeout(() => filter(), 200); });
  category.addEventListener('change', () => { clearTimeout(timer); filter(); });
  fullText.addEventListener('change', () => { clearTimeout(timer); filter(); });
  more.addEventListener('click', () => {
    const previous = visible;
    visible += 36;
    render();
    grid.children[previous]?.querySelector('h3 a')?.focus();
  });
  if (search.value || params.has('category')) filter(location.hash === '#library');
})();
