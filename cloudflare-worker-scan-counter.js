// Cloudflare Worker: daily scan counter for ahomekind.com
//
// Purpose: answer "how many scans happened today" without ever exposing
// the PostHog dashboard or API key to site visitors. The site's front
// end (see the counter code in js/nav.js) only ever talks to this
// Worker's own URL and gets back a small JSON number.
//
// Setup (done once, in the Cloudflare dashboard -- see the message this
// file was sent alongside for the exact click-by-click steps):
//   1. Create a new Worker, paste this whole file in as its code.
//   2. Add one secret to the Worker: POSTHOG_KEY = your PostHog
//      Personal API Key (the phx_... one, read-only, scoped to this
//      one project). Never hardcode it here -- Worker secrets are
//      encrypted and never shown again once saved, which is the point.
//   3. Deploy. Cloudflare gives you a worker.dev URL -- that's what
//      gets pasted into js/nav.js as WORKER_URL.
//
// This Worker holds no other secrets, touches no other data, and
// only ever answers with a single count -- nothing about individual
// visitors or events is exposed.

const PROJECT_ID = "268720";
const POSTHOG_HOST = "https://eu.posthog.com"; // EU data region, matching the account setup

export default {
  async fetch(request, env, ctx) {
    // Simple, permissive CORS: this Worker only ever returns a
    // non-sensitive count, so there's no risk in any site embedding it.
    const corsHeaders = {
      "Access-Control-Allow-Origin": "*",
      "Access-Control-Allow-Methods": "GET, OPTIONS",
      "Content-Type": "application/json",
    };

    if (request.method === "OPTIONS") {
      return new Response(null, { headers: corsHeaders });
    }

    try {
      const query = {
        query: {
          kind: "HogQLQuery",
          query:
            "select count() from events where event = 'scan_completed' and timestamp >= toStartOfDay(now())",
        },
      };

      const resp = await fetch(
        `${POSTHOG_HOST}/api/projects/${PROJECT_ID}/query/`,
        {
          method: "POST",
          headers: {
            Authorization: `Bearer ${env.POSTHOG_KEY}`,
            "Content-Type": "application/json",
          },
          body: JSON.stringify(query),
        }
      );

      if (!resp.ok) {
        return new Response(JSON.stringify({ count: null }), {
          status: 200,
          headers: corsHeaders,
        });
      }

      const data = await resp.json();
      const count =
        data && data.results && data.results[0] ? data.results[0][0] : 0;

      return new Response(JSON.stringify({ count: count }), {
        headers: corsHeaders,
        // Cache for 1 minute at Cloudflare's edge -- close to real-time
        // while still keeping the Worker (and PostHog) from being hit
        // on every single page load site-wide.
        cf: { cacheTtl: 60, cacheEverything: true },
      });
    } catch (err) {
      return new Response(JSON.stringify({ count: null }), {
        status: 200,
        headers: corsHeaders,
      });
    }
  },
};
