module.exports = function (eleventyConfig) {
  // Ignore non-content files (replaces .eleventyignore)
  eleventyConfig.ignores.add("README.md");
  eleventyConfig.ignores.add("PROCESS.md");
  eleventyConfig.ignores.add("SEARCH.md");
  eleventyConfig.ignores.add("node_modules");

  // Pass through static assets
  eleventyConfig.addPassthroughCopy("css");
  eleventyConfig.addPassthroughCopy("js");
  eleventyConfig.addPassthroughCopy("favicon.svg");
  eleventyConfig.addPassthroughCopy("robots.txt");

  // Date filter: "December 15, 1791"
  eleventyConfig.addFilter("formatDate", function (value) {
    if (!value) return "";
    const d = value instanceof Date ? value : new Date(value + "T00:00:00");
    if (isNaN(d)) return value;
    const months = ["January","February","March","April","May","June","July","August","September","October","November","December"];
    return `${months[d.getMonth()]} ${d.getDate()}, ${d.getFullYear()}`;
  });

  // Ordinal filter: 1 -> "1st", 22 -> "22nd"
  eleventyConfig.addFilter("ordinal", function (n) {
    n = parseInt(n, 10);
    if (11 <= (n % 100) && (n % 100) <= 13) return n + "th";
    const suffix = ({ 1: "st", 2: "nd", 3: "rd" })[n % 10] || "th";
    return n + suffix;
  });

  // Sections filter: split rendered HTML by <h2> tags into named sections
  eleventyConfig.addFilter("sections", function (content) {
    if (!content) return {};
    const sections = {};
    const slugify = (text) =>
      text.toLowerCase().replace(/[^\w\s-]/g, "").replace(/[\s_-]+/g, "_").replace(/^_|_$/g, "");

    // Split on <h2> tags — keeps the delimiter in the result
    const parts = content.split(/(?=<h2[ >])/);

    parts.forEach((part) => {
      const match = part.match(/^<h2[^>]*>(.*?)<\/h2>/);
      if (match) {
        const heading = match[1].trim();
        const key = slugify(heading);
        sections[key + "_heading"] = heading;
        // Everything after the </h2> closing tag is the section content
        sections[key] = part.replace(/^<h2[^>]*>.*?<\/h2>/, "").trim();
      }
    });
    return sections;
  });

  // Collections — sorted by number/title
  eleventyConfig.addCollection("amendments", function (api) {
    return api.getFilteredByGlob("content/amendments/*.md")
      .sort((a, b) => a.data.number - b.data.number);
  });
  eleventyConfig.addCollection("articles", function (api) {
    return api.getFilteredByGlob("content/articles/*.md")
      .sort((a, b) => a.data.number - b.data.number);
  });
  eleventyConfig.addCollection("situations", function (api) {
    return api.getFilteredByGlob("content/situations/*.md")
      .sort((a, b) => (a.data.title || "").localeCompare(b.data.title || ""));
  });

  return {
    dir: {
      input: ".",
      output: "_site",
      includes: "layouts",
      data: "data"
    },
    markdownTemplateEngine: "njk",
    htmlTemplateEngine: "njk",
    templateFormats: ["md", "njk", "html"]
  };
};
