/* a home kind - "Instead" swap finder
 * Drops a swap panel under a scan result.
 *
 * Usage:
 *   AHK.swaps.load('/data/swaps.json').then(function () {
 *     AHK.swaps.render(document.getElementById('instead'), {
 *       product:  'Garnier Micellar Cleansing Water',
 *       brand:    'Garnier',
 *       owner:    "L'Oreal",
 *       verdict:  'bad',                 // good | check | warn | bad | unverified
 *       categories: ['en:micellar-waters']   // optional, from Open Beauty Facts
 *     });
 *   });
 *
 * Nothing renders unless a product type is recognised, so an unmatched scan
 * looks exactly as it does today.
 */
(function (w) {
  'use strict';
  var AHK = w.AHK = w.AHK || {};
  var DATA = null;

  function norm(s) {
    s = (s || '').normalize('NFKD').replace(/[̀-ͯ]/g, '').toLowerCase();
    s = s.replace(/[^a-z0-9]+/g, ' ');
    s = s.replace(/([a-z])(?=[0-9])|([0-9])(?=[a-z])/g, '$1$2 ');
    return s.replace(/ +/g, ' ').trim();
  }

  function esc(s) {
    return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }

  /* Name keywords beat category tags: crowdsourced tags are unreliable.
     Types are tested in file order, so "dry shampoo" sits above "shampoo". */
  function matchType(product, categories, brand) {
    if (!DATA) return null;
    var n = norm(product);
    if (brand) {
      var b = norm(brand);
      if (b && n.indexOf(b) === 0) n = n.slice(b.length).trim();
    }
    var i, j, t, k;
    for (i = 0; i < DATA.types.length; i++) {
      t = DATA.types[i];
      for (j = 0; j < t.match.length; j++) {
        k = norm(t.match[j]);
        if (k && new RegExp('(^| )' + k.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + '( |$)').test(n)) return t;
      }
    }
    var tags = (categories || []).map(function (c) {
      return norm(String(c).split(':').pop()).replace(/ /g, '-');
    });
    if (!tags.length) return null;
    for (i = 0; i < DATA.types.length; i++) {
      t = DATA.types[i];
      for (j = 0; j < (t.obf || []).length; j++) {
        if (tags.indexOf(t.obf[j]) !== -1) return t;
      }
    }
    return null;
  }

  var CERT = {
    'leaping-bunny': 'Leaping Bunny',
    'peta': 'PETA',
    'both': 'Leaping Bunny &amp; PETA'
  };

  function pickHTML(p) {
    var where = (p.where || []).map(esc).join(' &middot; ');
    return '<li class="ahk-sw">' +
      '<div class="ahk-sw-top">' +
        '<a class="ahk-sw-nm" href="/brands/' + esc(p.slug) + '/">' + esc(p.brand) + '</a>' +
        (p.cert ? '<span class="ahk-cert">' + (CERT[p.cert] || esc(p.cert)) + '</span>' : '') +
        (p.price ? '<span class="ahk-sw-pr">' + esc(p.price) + '</span>' : '') +
      '</div>' +
      (p.note ? '<p class="ahk-sw-d">' + esc(p.note) + '</p>' : '') +
      (where ? '<p class="ahk-sw-where">' + where + '</p>' : '') +
    '</li>';
  }

  function noneHTML(type) {
    var n = type.none || {};
    var body = n.note ? esc(n.note)
      : 'Nothing certified does the same job at a similar price yet.';
    return '<div class="ahk-none">' +
      '<h3>I haven&rsquo;t found a good swap for this yet.</h3>' +
      '<p>' + body + '</p>' +
      '<span class="ahk-hand">still looking.</span>' +
      '<button type="button" class="ahk-tell" data-type="' + esc(type.id) + '">Tell me if you find one</button>' +
    '</div>';
  }

  /* Only offer swaps when the scan is actually a problem. A certified result
     gets a short "nothing needed" line instead of a shopping list. */
  function render(el, o) {
    if (!el) return null;
    el.innerHTML = '';
    var type = matchType(o.product, o.categories, o.brand);
    if (!type) return null;

    var fine = o.verdict === 'good' || o.verdict === 'check';
    var head = '<div class="ahk-ihd"><h2>Instead</h2><span>' +
      (fine ? 'nothing needed'
            : (type.picks.length ? type.picks.length + ' ' + esc(type.label.toLowerCase())
                                 : esc(type.label.toLowerCase()))) +
      '</span></div>';

    if (fine) {
      el.innerHTML = head + '<p class="ahk-isub">You&rsquo;re already fine here. Keep using it.</p>';
      el.hidden = false;
      return type;
    }

    el.innerHTML = head +
      (type.picks.length
        ? '<p class="ahk-isub">Certified, and close enough to swap without thinking about it.</p>' +
          '<ul class="ahk-swl">' + type.picks.map(pickHTML).join('') + '</ul>' +
          '<p class="ahk-ifoot">Prices are bands, not promises.' +
            (DATA.updated ? ' Last checked ' + esc(DATA.updated) + '.' : '') + '</p>'
        : noneHTML(type));

    el.hidden = false;
    return type;
  }

  /* "Tell me if you find one" -> the same Cloudflare Worker queue the barcode
     form uses, so suggestions land in the review page alongside barcodes.
     Honeypot field `website` must stay empty, as on the barcode form. */
  var ENDPOINT = 'https://barcode-inbox.ettlemanash.workers.dev/submit';

  function tell(typeId, text) {
    return fetch(ENDPOINT, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ kind: 'swap', type: typeId, brand: text, website: '' })
    }).then(function (r) { return r.ok; }).catch(function () { return false; });
  }

  function onTell(e) {
    var btn = e.target.closest ? e.target.closest('.ahk-tell') : null;
    if (!btn || btn.disabled) return;
    var box = btn.parentNode;
    if (!box.querySelector('.ahk-tellbox')) {
      var f = document.createElement('div');
      f.className = 'ahk-tellbox';
      f.innerHTML = '<input type="text" class="ahk-tellin" maxlength="80" ' +
        'placeholder="Which brand should I look at?" aria-label="Brand name">';
      box.insertBefore(f, btn);
      btn.textContent = 'Send';
      f.querySelector('input').focus();
      return;
    }
    var input = box.querySelector('.ahk-tellin');
    var val = (input.value || '').trim();
    if (!val) { input.focus(); return; }
    btn.disabled = true;
    btn.textContent = 'Sending...';
    tell(btn.getAttribute('data-type'), val).then(function (ok) {
      btn.textContent = ok ? 'Thank you. Sent.' : 'Could not send. Try again later.';
      if (ok) input.remove();
      else btn.disabled = false;
    });
  }

  document.addEventListener('click', onTell);

  function load(url) {
    return fetch(url, { cache: 'no-cache' })
      .then(function (r) { return r.json(); })
      .then(function (d) { DATA = d; return d; })
      .catch(function () { DATA = null; return null; });   // stay silent, never break the scan
  }

  AHK.swaps = {
    load: load,
    render: render,
    matchType: matchType,
    tell: tell,
    get data() { return DATA; },
    set data(d) { DATA = d; }
  };
})(window);
