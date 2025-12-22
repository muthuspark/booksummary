-- Lua filter to inject Article schema.org structured data for SEO
-- This filter adds JSON-LD structured data for each book summary page

local function get_meta_string(meta, key)
  if meta[key] then
    if type(meta[key]) == "table" then
      return pandoc.utils.stringify(meta[key])
    else
      return tostring(meta[key])
    end
  end
  return nil
end

function Meta(meta)
  -- Only add article schema if we have a title and it looks like a book summary
  local title = get_meta_string(meta, "title")
  local description = get_meta_string(meta, "description")
  local author = get_meta_string(meta, "author")
  local image = get_meta_string(meta, "image")

  -- Skip if this is the homepage or no title
  if not title or title == "Summaries of 1000+ greatest books" then
    return meta
  end

  -- Get categories
  local categories = {}
  if meta.categories then
    for _, cat in ipairs(meta.categories) do
      table.insert(categories, pandoc.utils.stringify(cat))
    end
  end
  local category = categories[1] or "Books"

  -- Build the current URL path from categories and title slug
  local site_url = "https://summaries.muthu.co"

  -- Create Article schema JSON-LD
  local schema = string.format([[
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "%s",
  "description": "%s",
  "author": {
    "@type": "Person",
    "name": "%s"
  },
  "publisher": {
    "@type": "Organization",
    "name": "Book Summaries",
    "logo": {
      "@type": "ImageObject",
      "url": "%s/logo.png"
    }
  },
  "mainEntityOfPage": {
    "@type": "WebPage"
  },
  "articleSection": "%s",
  "inLanguage": "en-US"
}
</script>
]],
    title:gsub('"', '\\"'),
    (description or ""):gsub('"', '\\"'),
    (author or "Unknown"):gsub('"', '\\"'),
    site_url,
    category:gsub('"', '\\"')
  )

  -- Also create Book schema for richer results
  local book_schema = string.format([[
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Book",
  "name": "%s",
  "author": {
    "@type": "Person",
    "name": "%s"
  },
  "description": "%s",
  "genre": "%s",
  "inLanguage": "en"
}
</script>
]],
    title:gsub('"', '\\"'):gsub(" by .*$", ""),
    (author or "Unknown"):gsub('"', '\\"'),
    (description or ""):gsub('"', '\\"'),
    category:gsub('"', '\\"')
  )

  -- Inject into header-includes
  if not meta["header-includes"] then
    meta["header-includes"] = pandoc.MetaList({})
  end

  table.insert(meta["header-includes"], pandoc.MetaBlocks({pandoc.RawBlock("html", schema)}))
  table.insert(meta["header-includes"], pandoc.MetaBlocks({pandoc.RawBlock("html", book_schema)}))

  return meta
end
