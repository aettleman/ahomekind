// Small status readout for the toolbar popup: how many brands are cached,
// when they were last refreshed, and a manual refresh button for anyone
// who doesn't want to wait for the once-a-day automatic refresh.

(function () {
  "use strict";

  var CACHE_META_KEY = "ahk_brands_cache_meta";
  var statusEl = document.getElementById("status");
  var refreshBtn = document.getElementById("refresh");

  function formatAgo(ts) {
    var mins = Math.round((Date.now() - ts) / 60000);
    if (mins < 1) return "just now";
    if (mins < 60) return mins + " minute" + (mins === 1 ? "" : "s") + " ago";
    var hrs = Math.round(mins / 60);
    if (hrs < 24) return hrs + " hour" + (hrs === 1 ? "" : "s") + " ago";
    var days = Math.round(hrs / 24);
    return days + " day" + (days === 1 ? "" : "s") + " ago";
  }

  function render() {
    chrome.storage.local.get(CACHE_META_KEY).then(function (data) {
      var meta = data[CACHE_META_KEY];
      if (!meta) {
        statusEl.innerHTML = "<strong>Not loaded yet</strong>Brand list hasn't been fetched yet — try refreshing.";
        return;
      }
      if (meta.ok === false) {
        statusEl.innerHTML = "<strong>Last refresh failed</strong>Using whatever was cached before. Check your connection and try again.";
        return;
      }
      statusEl.innerHTML =
        "<strong>" + (meta.count || 0) + " brands loaded</strong>Last refreshed " + formatAgo(meta.fetchedAt) + ".";
    });
  }

  refreshBtn.addEventListener("click", function () {
    refreshBtn.disabled = true;
    refreshBtn.textContent = "Refreshing…";
    chrome.runtime.sendMessage({ type: "ahk-refresh-now" }, function () {
      render();
      refreshBtn.disabled = false;
      refreshBtn.textContent = "Refresh brand list now";
    });
  });

  render();
})();
