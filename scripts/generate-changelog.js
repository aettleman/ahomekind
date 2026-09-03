#!/usr/bin/env node
// Generates data/changelog.json -- a "brand watch" feed of real changes to
// data/brands.json over time, built entirely from git history. This is not
// hand-maintained: every time this script runs (as part of shipping a
// brands.json change), it walks every commit that touched data/brands.json,
// diffs each snapshot against the one before it, and records what actually
// changed -- a brand added, a tier changing, or a note being rewritten.
// That means the brand-watch page stays accurate with zero extra manual
// work, and nobody has to remember to log an entry by hand.
//
// Usage: node scripts/generate-changelog.js

var { execSync } = require('child_process');
var fs = require('fs');
var path = require('path');

var ROOT = path.join(__dirname, '..');
var OUT = path.join(ROOT, 'data', 'changelog.json');
var MAX_ENTRIES = 200;

function sh(cmd) {
  return execSync(cmd, { cwd: ROOT, maxBuffer: 1024 * 1024 * 64 }).toString();
}

// All commits touching data/brands.json, oldest first.
var log = sh('git log --format="%H|%ad" --date=format:%Y-%m-%d --follow --reverse -- data/brands.json')
  .split('\n')
  .filter(Boolean)
  .map(function (line) {
    var parts = line.split('|');
    return { sha: parts[0], date: parts[1] };
  });

function snapshotAt(sha) {
  var raw;
  try {
    raw = sh('git show ' + sha + ':data/brands.json 2>/dev/null');
  } catch (e) {
    return null;
  }
  try {
    var arr = JSON.parse(raw);
    var map = {};
    arr.forEach(function (b) {
      if (b && b.slug) map[b.slug] = b;
    });
    return map;
  } catch (e) {
    return null; // malformed JSON at that point in history -- skip it
  }
}

var events = [];
var prev = null;

log.forEach(function (commit) {
  var snap = snapshotAt(commit.sha);
  if (!snap) return;
  if (prev) {
    Object.keys(snap).forEach(function (slug) {
      var now = snap[slug];
      var before = prev[slug];
      if (!before) {
        events.push({
          date: commit.date,
          type: 'added',
          slug: slug,
          name: now.name,
          summary: now.name + ' was added' + (now.tier ? ' (' + tierLabel(now.tier) + ')' : '') + '.'
        });
      } else if (before.tier !== now.tier) {
        events.push({
          date: commit.date,
          type: 'tier-change',
          slug: slug,
          name: now.name,
          summary: now.name + ' moved from ' + tierLabel(before.tier) + ' to ' + tierLabel(now.tier) + '.'
        });
      } else if ((before.note || '') !== (now.note || '') && now.note) {
        events.push({
          date: commit.date,
          type: 'note-update',
          slug: slug,
          name: now.name,
          summary: now.name + '’s listing was updated: “' + truncate(now.note, 140) + '”'
        });
      }
    });
  }
  prev = snap;
});

function tierLabel(tier) {
  return {
    good: 'fully cruelty-free & vegan',
    check: 'worth a closer look',
    warn: 'cruelty-free itself, parent company isn’t',
    bad: 'tested on animals',
    unverified: 'unverified'
  }[tier] || tier;
}

function truncate(str, n) {
  if (!str || str.length <= n) return str;
  return str.slice(0, n - 1).trim() + '…';
}

// Newest first, capped.
events.sort(function (a, b) { return a.date < b.date ? 1 : a.date > b.date ? -1 : 0; });
events = events.slice(0, MAX_ENTRIES);

fs.writeFileSync(OUT, JSON.stringify(events, null, 2) + '\n');
console.log('Done. ' + events.length + ' changelog entries written to data/changelog.json.');
