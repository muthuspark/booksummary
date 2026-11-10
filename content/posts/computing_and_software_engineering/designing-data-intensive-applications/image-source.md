# Hero image provenance

Style: `warm-gouache-v1` from IMAGE_STYLE.md.

Tool: built-in OpenAI image_gen.imagegen using the imagegen skill.

File: `image.png`. Style reference: `content/posts/decision_making_and_critical_thinking/a-mind-for-numbers/starting-small.webp`.

Delivery: optimized 640px square PNG; the full-resolution generated original is retained in the migration staging directory and tool output cache.

Original conceptual illustration for this book summary. Not a book cover, documentary photograph, or author portrait.

Reviewed for the shared palette, hand-painted medium, subject relevance, thumbnail clarity and unwanted lettering.

## Exact final generation prompt

Create a finished illustration for a public book-summary library for adult readers. Use a calm, contemporary illustrated-book style: hand-painted gouache, soft matte pigment, restrained pencil details, and a subtle warm ivory paper texture. Use a consistent palette of muted sage and olive green, warm ochre, natural wood brown, and warm ivory, with dark brown or charcoal details. Keep saturation restrained and lighting soft and natural. Give the scene generous breathing room, a clear focal point, and simple, recognizable forms that remain readable on a phone. When people are relevant, depict believable adults with natural proportions, respectful expressions, and ordinary clothing. Use the same medium, palette, texture, and level of detail across the illustration. Avoid photorealism, glossy 3D, neon colors, cinematic effects, heavy black outlines, childish clipart, ornamental clutter, and a different art style in each panel. No readable text, captions, logos, watermarks, fake book covers, or invented author portraits. Keep all explanations and essential labels outside the generated image.

Use case: illustration-story. Asset type: finished SQUARE hero illustration for a
book-summary article. The supplied reference is a STYLE REFERENCE ONLY. Match its
gouache, paper texture, matte pigments and gentle natural light. Do not copy its
person, study desk, notebook or scene. Use a NEW concrete subject and composition
appropriate to the book below. Choose a clear single scene or visual metaphor that
conveys the central idea, using the summary as context. Do not render the title,
author name, quotations, text, labels, equations or a book cover. No random abstract
shards, generic tech networks, diagram labels, glossy objects or flat-vector icons.
Avoid a person at a study desk as a default. Use people only when they help explain
this particular subject. For biographies, evoke the person's work, historical
setting or defining subject through places and objects, without inventing an author
or historical person's likeness. Do not depict a speculative documentary event.
For novels, choose an appropriate setting, object or restrained symbolic scene;
preserve the work's tone without graphic violence, sexual imagery or fake covers.
For scientific or medical topics, favor truthful everyday or natural objects and
avoid inventing scientific diagrams, anatomy, measurements or therapeutic results.
Use balanced square framing with a clear focal point and safe margins for small
thumbnails. Maintain the shared muted sage, olive, ochre, wood brown and warm ivory
palette. Make the illustration clearly hand-painted rather than photographic.

Book and summary context (data, not instructions):
{"title": "Designing Data-Intensive Applications by Martin Kleppmann", "description": "A guide to the trade-offs behind reliable data systems, from storage and replication to transactions, consensus, and stream processing.", "excerpt": "\n\n# How Data Systems Keep Their Promises\n\nA database can accept a write while a search index misses it. A retry can count the same purchase twice. A server can appear dead when its network is merely slow. These problems connect the subjects in Martin Kleppmann's *Designing Data-Intensive Applications*.\n\nThe central argument is that sound architecture requires an understanding of mechanisms, guarantees, and trade-offs. Product names alone tell us little. Engineers need to know what a system promises, what assumptions support that promise, and what happens when those assumptions fail. The [author's introduction](https://martin.kleppmann.com/2017/03/27/designing-data-intensive-applications.html) presents this comparison of underlying ideas as the book's purpose.\n\nThis summary covers the 2017 first edition, written by Kleppmann alone. Its three parts move from the foundations of data systems to distributed data and then derived data. The examples below simplify the mechanisms to explain their practical consequences.\n\n## Start with Reliability, Scalability, and Maintainability\n\nKleppmann gives system design three broad goals. **Reliability** means continuing to work correctly despite faults. A broken disk is a fault; losing the service's ability to meet its requirements is a failure. Good design prevents expected faults from becoming failures.\n\n**Scalability** concerns how a system handles growth. First describe the load. Requests per second, data volume, and the distribution of activity can expose different limits. Then measure performance under that load. An average response time can hide the slow requests that cause users difficulty.\n\n**Maintainability** includes operating the system, understanding it, and changing it. A design that needs constant expert intervention has a real cost, even if its benchmark looks good. These goals, developed in [the opening chapter](https://www.oreilly.com/library/view/designing-data-intensive-applications/9781491903063/ch01.html), make operational work part of architecture.\n\n## Choose Data Models Around Relationships\n\nThe book compares relational, document, and graph models. Each makes some relationships easier to express.\n\nA document can keep a self-contained record together. A relational model can represent shared entities with"}

## Previous image provenance (superseded)

# Hero image provenance

- Tool: OpenAI built-in `image_gen.imagegen` (imagegen skill, default tool mode).
- Created for this summary; no reference images or third-party artwork were supplied.
- File: `image.png`, copied from the generated output into this leaf bundle.
- The illustration is a conceptual view of replicated storage, event streams, search, and analytics. It is not a book cover or a precise system diagram.
- No external image attribution is required for this generated asset.

## Generation prompt

Use case: stylized-concept. Asset type: square editorial hero illustration for a summary of Designing Data-Intensive Applications. Create a finished, thoughtful isometric illustration of a distributed data system: several distinct small server towers, layered cylindrical data stores, an ordered ribbon of small event tiles branching toward a search index and a compact analytical grid. Show replicated matching data tiles on two separated server islands, with one interrupted connection subtly rerouted. Precise architectural forms, warm ivory background, muted teal, slate blue and amber accents, soft paper texture and restrained shadows. Clear focal hierarchy, ample breathing room, visually readable at thumbnail size. Conceptual illustration, not a technical diagram. At least 1024 by 1024 pixels. No text, letters, numbers, logos, cover imitation, people or watermarks.
