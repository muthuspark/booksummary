(() => {
  const posts = {{ . | jsonify | safeJS }};
  const link = document.querySelector('[data-random-post]');
  if (!link) return;

  const currentPath = window.location.pathname.replace(/index\.html$/, '');
  const alternatives = posts.filter(url => url !== currentPath);
  const candidates = alternatives.length ? alternatives : posts;
  if (!candidates.length) return;

  function choosePost() {
    link.href = candidates[Math.floor(Math.random() * candidates.length)];
  }

  choosePost();
  link.addEventListener('click', choosePost);
  link.addEventListener('auxclick', choosePost);
})();
