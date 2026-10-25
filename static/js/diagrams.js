(() => {
  if (!window.mermaid) return;
  mermaid.initialize({ startOnLoad: false, securityLevel: 'strict', theme: 'neutral', suppressErrorRendering: true });
  let queue = Promise.resolve();
  function render(node) {
    const source = node.textContent;
    queue = queue.then(async () => {
      try {
        const id = `diagram-${++render.id}`;
        const result = await mermaid.render(id, source);
        node.innerHTML = result.svg;
        node.dataset.processed = 'true';
        result.bindFunctions?.(node);
      } catch (_) {
        node.textContent = source;
        const note = document.createElement('p');
        note.className = 'diagram-error';
        note.textContent = 'This diagram could not be displayed. The original diagram source is shown below.';
        node.before(note);
      }
    });
  }
  render.id = 0;
  const nodes = document.querySelectorAll('pre.mermaid');
  if ('IntersectionObserver' in window) {
    const observer = new IntersectionObserver(entries => {
      for (const entry of entries) if (entry.isIntersecting) {
        observer.unobserve(entry.target);
        render(entry.target);
      }
    }, { rootMargin: '300px' });
    nodes.forEach(node => observer.observe(node));
  } else nodes.forEach(render);
})();
