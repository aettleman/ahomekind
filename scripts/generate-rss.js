// generate-rss.js
// Builds journal/rss.xml from every post in journal/*.html (except index.html),
// so Buttondown's "RSS to email" automation can watch it and auto-send new
// journal posts to the mailing list.
//
// Publish dates come from each file's earliest git commit (its "added" date) —
// there's no separate CMS/date field on this static site, so git history is
// the most honest source of truth available. Run this again any time a new
// journal post is added:
//
//   node scripts/generate-rss.js

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const ROOT = path.join(__dirname, '..');
const JOURNAL_DIR = path.join(ROOT, 'journal');
const SITE_URL = 'https://ahomekind.com';
const OUT_PATH = path.join(JOURNAL_DIR, 'rss.xml');

function escapeXml(str) {
  if (!str) return '';
  return String(str)
    .split('&').join('&amp;')
    .split('<').join('&lt;')
    .split('>').join('&gt;')
    .split('"').join('&quot;')
    .split("'").join('&apos;');
}

function extractTag(html, re, fallback) {
  const m = html.match(re);
  return m ? m[1].trim() : fallback;
}

function firstAddedDate(filePath) {
  try {
    const rel = path.relative(ROOT, filePath);
    const out = execSync(`git log --follow --diff-filter=A --format=%aI -- "${rel}"`, {
      cwd: ROOT,
      encoding: 'utf8'
    }).trim();
    const lines = out.split('\n').filter(Boolean);
    if (lines.length) return new Date(lines[lines.length - 1]);
  } catch (e) {
    // not tracked yet, or git unavailable — fall through
  }
  return new Date();
}

function buildItem(file) {
  const filePath = path.join(JOURNAL_DIR, file);
  const html = fs.readFileSync(filePath, 'utf8');

  let title = extractTag(html, /<title>([^<]*)<\/title>/i, file);
  title = title.replace(/\s*[–-]\s*a home kind\s*$/i, '').trim();

  const description = extractTag(
    html,
    /<meta name="description" content="([^"]*)"/i,
    ''
  );

  const link = `${SITE_URL}/journal/${file}`;
  const pubDate = firstAddedDate(filePath);

  return {
    title,
    description,
    link,
    guid: link,
    pubDate
  };
}

function main() {
  const files = fs.readdirSync(JOURNAL_DIR)
    .filter(f => f.endsWith('.html') && f !== 'index.html');

  const items = files.map(buildItem)
    .sort((a, b) => b.pubDate - a.pubDate);

  const itemsXml = items.map(function (item) {
    return [
      '  <item>',
      '    <title>' + escapeXml(item.title) + '</title>',
      '    <link>' + escapeXml(item.link) + '</link>',
      '    <guid isPermaLink="true">' + escapeXml(item.guid) + '</guid>',
      '    <pubDate>' + item.pubDate.toUTCString() + '</pubDate>',
      '    <description>' + escapeXml(item.description) + '</description>',
      '  </item>'
    ].join('\n');
  }).join('\n');

  const lastBuild = items.length ? items[0].pubDate.toUTCString() : new Date().toUTCString();

  const xml = [
    '<?xml version="1.0" encoding="UTF-8"?>',
    '<rss version="2.0">',
    '<channel>',
    '  <title>a home kind — journal</title>',
    '  <link>' + SITE_URL + '/journal/</link>',
    '  <description>Swaps, ratings, and honest takes on cruelty-free and vegan living.</description>',
    '  <language>en-gb</language>',
    '  <lastBuildDate>' + lastBuild + '</lastBuildDate>',
    itemsXml,
    '</channel>',
    '</rss>',
    ''
  ].join('\n');

  fs.writeFileSync(OUT_PATH, xml, 'utf8');
  console.log('Wrote journal/rss.xml with ' + items.length + ' item(s).');
  items.forEach(function (i) { console.log(' -', i.pubDate.toISOString().slice(0, 10), i.title); });
}

main();
