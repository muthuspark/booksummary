(() => {
  const index = document.querySelector('[data-author-index]');
  if (!index) return;

  const form = index.querySelector('.author-search');
  const input = index.querySelector('#author-query');
  const clear = index.querySelector('[data-clear-authors]');
  const status = index.querySelector('#author-results');
  const empty = index.querySelector('.author-empty');
  const alphabet = index.querySelector('.author-alphabet');
  const groups = [...index.querySelectorAll('.author-group')];
  const normalize = value => value.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLocaleLowerCase('en').trim();
  const rows = [...index.querySelectorAll('.author-list li')].map(row => ({
    row,
    name: normalize(row.querySelector('.term-name').textContent),
  }));

  const update = () => {
    if (history.state?.authorQuery !== input.value) {
      history.replaceState({ ...history.state, authorQuery: input.value }, '');
    }
    const query = normalize(input.value);
    let count = 0;
    for (const { row, name } of rows) {
      row.hidden = !name.includes(query);
      if (!row.hidden) count++;
    }
    for (const group of groups) {
      group.hidden = !group.querySelector('li:not([hidden])');
    }
    alphabet.hidden = Boolean(query);
    empty.hidden = count !== 0;
    clear.disabled = input.value.length === 0;
    status.textContent = query
      ? `${count} ${count === 1 ? 'author' : 'authors'} found`
      : `${status.dataset.total} authors · A–Z by displayed name`;
  };

  form.addEventListener('submit', event => event.preventDefault());
  input.addEventListener('input', update);
  clear.addEventListener('click', () => {
    input.value = '';
    update();
    input.focus();
  });
  alphabet.addEventListener('click', event => {
    const link = event.target.closest('a');
    if (link) document.getElementById(link.hash.slice(1))?.focus({ preventScroll: true });
  });
  const restore = () => {
    if (typeof history.state?.authorQuery === 'string') input.value = history.state.authorQuery;
    update();
  };
  window.addEventListener('pageshow', restore);
  restore();
  form.hidden = false;
})();
