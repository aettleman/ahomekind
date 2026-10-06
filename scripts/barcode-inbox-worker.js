// Cloudflare Worker: barcode-inbox for ahomekind.com
// - POST /submit        : visitors send a barcode + brand (saved for review, never live)
// - GET  /approved      : public list of barcodes Ash has approved (scanner reads this)
// - GET  /review?key=.. : Ash's private review page (needs ADMIN_KEY)
// Needs: KV binding named SUBMISSIONS, and a secret named ADMIN_KEY.

const ORIGINS = ["https://ahomekind.com", "https://www.ahomekind.com"];
const J = (o, status = 200, h = {}) =>
  new Response(JSON.stringify(o), { status, headers: { "Content-Type": "application/json", ...h } });
const norm = (s) => String(s || "").normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase().replace(/[^a-z0-9]/g, "");

async function brandsList() {
  const r = await fetch("https://ahomekind.com/data/brands.json", { cf: { cacheTtl: 300 } });
  return r.ok ? r.json() : [];
}

export default {
  async fetch(req, env) {
    const url = new URL(req.url);
    const origin = req.headers.get("Origin") || "";
    const cors = ORIGINS.includes(origin)
      ? { "Access-Control-Allow-Origin": origin, Vary: "Origin", "Access-Control-Allow-Methods": "GET, POST, OPTIONS", "Access-Control-Allow-Headers": "Content-Type" }
      : {};
    if (req.method === "OPTIONS") return new Response(null, { headers: cors });

    // ---------- public: approved barcodes ----------
    if (url.pathname === "/approved" && req.method === "GET") {
      const v = await env.SUBMISSIONS.get("approved");
      return new Response(v || "{}", {
        headers: { "Content-Type": "application/json", "Cache-Control": "public, max-age=60", "Access-Control-Allow-Origin": "*" },
      });
    }

    // ---------- public: submit ----------
    if (url.pathname === "/submit" && req.method === "POST") {
      if (!ORIGINS.includes(origin)) return J({ error: "not allowed" }, 403, cors);
      let b;
      try { b = await req.json(); } catch (e) { return J({ error: "bad request" }, 400, cors); }
      if (b.website) return J({ ok: true }, 200, cors); // hidden field: bots fill it in
      const barcode = String(b.barcode || "").replace(/\D/g, "");
      const brand = String(b.brand || "").trim().slice(0, 80);
      const product = String(b.product || "").trim().slice(0, 120);
      if (barcode.length < 6 || barcode.length > 14) return J({ error: "barcode" }, 400, cors);
      if (!brand && !product) return J({ error: "brand" }, 400, cors);
      const ip = req.headers.get("CF-Connecting-IP") || "x";
      const rk = "rl:" + ip + ":" + Math.floor(Date.now() / 3600000);
      const n = parseInt((await env.SUBMISSIONS.get(rk)) || "0", 10);
      if (n >= 10) return J({ error: "slow down" }, 429, cors);
      await env.SUBMISSIONS.put(rk, String(n + 1), { expirationTtl: 7200 });
      const id = Date.now() + "-" + Math.random().toString(36).slice(2, 7);
      const rec = {
        id, barcode, brand, product,
        noBrand: !!b.noBrand,
        brandOnList: !!b.brandOnList,
        matchedBrand: String(b.matchedBrand || "").slice(0, 80),
        at: new Date().toISOString(),
      };
      await env.SUBMISSIONS.put("sub:" + id, JSON.stringify(rec));
      return J({ ok: true }, 200, cors);
    }

    // ---------- private: Ash's review page ----------
    const key = url.searchParams.get("key") || "";
    const isAdmin = !!env.ADMIN_KEY && key === env.ADMIN_KEY;

    if (url.pathname === "/review" && req.method === "GET") {
      if (!isAdmin) return new Response("Not found", { status: 404 });
      return new Response(REVIEW_HTML, { headers: { "Content-Type": "text/html;charset=utf-8", "X-Robots-Tag": "noindex", "Cache-Control": "no-store" } });
    }
    if (url.pathname === "/admin/list" && req.method === "GET") {
      if (!isAdmin) return J({ error: "no" }, 404);
      const l = await env.SUBMISSIONS.list({ prefix: "sub:", limit: 500 });
      const subs = (await Promise.all(l.keys.map((k) => env.SUBMISSIONS.get(k.name)))).filter(Boolean).map((x) => JSON.parse(x));
      subs.sort((a, c) => (a.at < c.at ? 1 : -1));
      const approved = JSON.parse((await env.SUBMISSIONS.get("approved")) || "{}");
      return J({ subs, approvedCount: Object.keys(approved).length });
    }
    if (url.pathname === "/admin/approve" && req.method === "POST") {
      if (!isAdmin) return J({ error: "no" }, 404);
      const b = await req.json();
      const brands = await brandsList();
      const hit = brands.find((x) => norm(x.name) === norm(b.brand));
      if (!hit) return J({ error: "That brand isn't on your list yet. Add the brand first, or reject this one." }, 400);
      const approved = JSON.parse((await env.SUBMISSIONS.get("approved")) || "{}");
      approved[String(b.barcode).replace(/\D/g, "")] = { brand: hit.name, product: String(b.product || "").slice(0, 120), tier: hit.tier, note: hit.note || "" };
      await env.SUBMISSIONS.put("approved", JSON.stringify(approved));
      await env.SUBMISSIONS.delete("sub:" + b.id);
      return J({ ok: true, brand: hit.name, tier: hit.tier });
    }
    if (url.pathname === "/admin/reject" && req.method === "POST") {
      if (!isAdmin) return J({ error: "no" }, 404);
      const b = await req.json();
      await env.SUBMISSIONS.delete("sub:" + b.id);
      return J({ ok: true });
    }
    return new Response("Not found", { status: 404 });
  },
};

const REVIEW_HTML = `<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex"><title>Barcode review</title>
<style>
:root{--blush:#F4E6DE;--cream:#FBF4EF;--ink:#2A1630;--muted:#5A4550;--plum:#3A1F3D;--apricot:#E8804C;--sage:#7C9A78;--rose:#F5D3D6}
*{box-sizing:border-box}body{margin:0;background:var(--blush);color:var(--ink);font:16px/1.45 system-ui,sans-serif;padding:16px}
.w{max-width:640px;margin:0 auto}h1{font:400 28px Georgia,serif;color:var(--plum);margin:4px 0}
.s{color:var(--muted);margin:0 0 14px}.c{background:var(--cream);border-radius:16px;padding:14px 16px;margin:12px 0}
.bc{font:700 20px ui-monospace,monospace;letter-spacing:.04em}.tag{display:inline-block;font-size:12px;font-weight:700;padding:3px 10px;border-radius:99px;margin:6px 6px 6px 0}
.on{background:#DCE6D6;color:#33502f}.off{background:#FBE3D3;color:#A85523}
input{width:100%;font:inherit;padding:10px 12px;border:1px solid #D9C3B7;border-radius:10px;margin:4px 0 8px;background:#fff}
label{font-size:12px;letter-spacing:.06em;text-transform:uppercase;color:var(--muted)}
.row{display:flex;gap:8px}button{flex:1;font:inherit;font-weight:700;padding:12px;border:0;border-radius:99px;cursor:pointer}
.ok{background:var(--plum);color:var(--cream)}.no{background:#fff;color:var(--ink);border:1px solid #D9C3B7}.msg{color:#A8324E;font-size:14px;min-height:18px}
</style></head><body><div class="w"><h1>Barcode review</h1><p class="s" id="top">Loading...</p><div id="list"></div></div>
<script>
var KEY=new URLSearchParams(location.search).get("key");
function api(p,body){return fetch(p+(p.indexOf("?")<0?"?":"&")+"key="+encodeURIComponent(KEY),body?{method:"POST",body:JSON.stringify(body)}:{}).then(function(r){return r.json()})}
function el(t,c,x){var e=document.createElement(t);if(c)e.className=c;if(x!=null)e.textContent=x;return e}
function load(){api("/admin/list").then(function(d){
 var L=document.getElementById("list");L.innerHTML="";
 document.getElementById("top").textContent=d.subs.length+" waiting. "+d.approvedCount+" approved so far.";
 d.subs.forEach(function(s){
  var c=el("div","c");c.appendChild(el("div","bc",s.barcode));
  var t=el("span","tag "+(s.brandOnList?"on":"off"),s.brandOnList?"brand IS on your list"+(s.matchedBrand?": "+s.matchedBrand:""):"brand NOT on your list");c.appendChild(t);
  if(s.noBrand)c.appendChild(el("span","tag off","no brand on pack"));
  c.appendChild(el("div","s",new Date(s.at).toLocaleString()));
  c.appendChild(el("label",null,"Brand"));var b=el("input");b.value=s.matchedBrand||s.brand;c.appendChild(b);
  c.appendChild(el("label",null,"Product"));var p=el("input");p.value=s.product||"";c.appendChild(p);
  var m=el("div","msg");c.appendChild(m);var r=el("div","row");
  var a=el("button","ok","Approve");a.onclick=function(){m.textContent="";api("/admin/approve",{id:s.id,barcode:s.barcode,brand:b.value,product:p.value}).then(function(x){if(x.error){m.textContent=x.error}else{c.remove();load()}})};
  var d2=el("button","no","Reject");d2.onclick=function(){api("/admin/reject",{id:s.id}).then(function(){c.remove();load()})};
  r.appendChild(a);r.appendChild(d2);c.appendChild(r);L.appendChild(c)});
 if(!d.subs.length)L.appendChild(el("p","s","Nothing to review. All clear."));
}).catch(function(){document.getElementById("top").textContent="Could not load. Check the link has your key on the end."})}
load();
</script></body></html>`;
