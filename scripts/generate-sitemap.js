#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

const brandsPath = path.join(__dirname, '../data/brands.json');
if (!fs.existsSync(brandsPath)) {
    console.error(`Error: ${brandsPath} not found`);
    process.exit(1);
}

let brands;
try {
    const brandsData = fs.readFileSync(brandsPath, 'utf8');
    brands = JSON.parse(brandsData);
} catch (err) {
    console.error(`Error reading/parsing brands.json:`, err);
    process.exit(1);
}

if (!Array.isArray(brands)) {
    console.error('Error: brands.json must contain an array of brands');
    process.exit(1);
}

const today = new Date().toISOString().split('T')[0];

let sitemapEntries = [];

const staticPages = [
  { url: '/', priority: '1.0', changefreq: 'weekly' },
  { url: '/brand-check', priority: '0.9', changefreq: 'weekly' },
  { url: '/scan', priority: '0.8', changefreq: 'monthly' },
  { url: '/shelf', priority: '0.8', changefreq: 'monthly' }
  ];

staticPages.forEach(page => {
    sitemapEntries.push(`  <url>\n    <loc>https://ahomekind.com${page.url}</loc>\n    <lastmod>${today}</lastmod>\n    <changefreq>${page.changefreq}</changefreq>\n    <priority>${page.priority}</priority>\n  </url>`);
});

brands.forEach(brand => {
    sitemapEntries.push(`  <url>\n    <loc>https://ahomekind.com/brands/${brand.slug}</loc>\n    <lastmod>${today}</lastmod>\n    <changefreq>monthly</changefreq>\n    <priority>0.7</priority>\n  </url>`);
});

const sitemapXml = `<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n${sitemapEntries.join('\n')}\n</urlset>`;

const sitemapPath = path.join(__dirname, '../sitemap.xml');
fs.writeFileSync(sitemapPath, sitemapXml, 'utf8');

console.log(`Generated sitemap.xml with ${staticPages.length + brands.length} entries`);
