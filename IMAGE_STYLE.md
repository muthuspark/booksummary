# Shared image style

Style identifier: `warm-gouache-v1`.

Use this style for every newly generated hero image, inline illustration, and
illustrated example across the site. Use the same style when editing or replacing
an image. Keep the subject specific to the book and the surrounding explanation.

## Reusable prompt prefix

Include this entire prefix in each image-generation prompt, followed by the
article-specific subject, scene, composition, and factual constraints:

> Create a finished illustration for a public book-summary library for adult
> readers. Use a calm, contemporary illustrated-book style: hand-painted gouache,
> soft matte pigment, restrained pencil details, and a subtle warm ivory paper
> texture. Use a consistent palette of muted sage and olive green, warm ochre,
> natural wood brown, and warm ivory, with dark brown or charcoal details. Keep
> saturation restrained and lighting soft and natural. Give the scene generous
> breathing room, a clear focal point, and simple, recognizable forms that remain
> readable on a phone. When people are relevant, depict believable adults with
> natural proportions, respectful expressions, and ordinary clothing. Use the same
> medium, palette, texture, and level of detail across the illustration. Avoid
> photorealism, glossy 3D, neon colors, cinematic effects, heavy black outlines,
> childish clipart, ornamental clutter, and a different art style in each panel.
> No readable text, captions, logos, watermarks, fake book covers, or invented
> author portraits. Keep all explanations and essential labels outside the
> generated image.

## Reference images

The approved visual references are:

- `content/posts/decision_making_and_critical_thinking/a-mind-for-numbers/spaced-review.webp`
- `content/posts/decision_making_and_critical_thinking/a-mind-for-numbers/starting-small.webp`

Inspect at least one reference before generating images. When the tool supports
reference images, provide one as a style reference and identify its role explicitly.
Follow the image-generation skill's reference-image workflow. Match the medium,
palette, lighting, texture, and visual density. Create a new subject and composition
for each article. Do not repeat the same student, desk, or setting across unrelated
books. Within a multi-panel illustration, keep recurring people and objects
consistent. Representation can vary across books without changing the art style.

## Composition and delivery

- Hero images: use a balanced square composition with one clear scene or visual
  metaphor. Save the finished image as `image.png`, at least 512px in each dimension.
  Keep important elements away from the edges so thumbnails remain understandable.
- Inline images: prefer landscape 3:2 compositions. Use one concrete scene, or at
  most three simple vignettes if the comparison needs them. Place images where they
  clarify the text. Do not add decorative images just to fill space.
- Keep subjects, objects, and historical details appropriate to the book. An
  illustrative example must not imply a documented event, scientific measurement,
  or real person's likeness. Explain illustrative examples in captions when needed.
- Keep numbers, equations, instructional labels, and essential distinctions in
  article text or editable SVG text. Do not rely on generated lettering for meaning.
- Save generated assets inside the article bundle. Inline WebP copies are suitable
  for smaller downloads. Supply dimensions, descriptive alt text, and useful captions.
- Record the tool, the exact final prompt including the shared prefix, the style
  identifier, any reference image used, and asset filenames in `image-source.md`
  for the hero or `illustration-sources.md` for inline images. Preserve earlier
  provenance when adding new images.
- Store long prompts or prompts containing source markup as JSON data in
  `image-generation.json`, linked from `image-source.md` or `illustration-sources.md`.
  Keep exact prompt text and previous provenance in that record. Do not paste raw
  template markup into Markdown provenance, where Hugo can execute it as a shortcode.
- Inspect every result before use. Regenerate if the medium, palette, lighting,
  texture, or complexity drifts from the references. Check the subject is clear at
  mobile width and the image contains no misleading details or broken anatomy.

## Diagrams and licensed fallbacks

Reader-friendly diagrams remain editable standalone SVG. Use warm ivory, sage,
and ochre accents, a quiet layout, and readable serif labels to fit this visual
family. Keep the SVG text crisp rather than painting a texture over it. Use the
diagram guidance in the generation prompts for structure and accessibility.

When generation is unavailable, prefer a suitably licensed illustration that fits
this visual style. Verify its license and retain any required attribution. Do not
claim a downloaded asset was generated, or that its source matches the style if it
does not. If no appropriate asset is available, report the incomplete visual.
