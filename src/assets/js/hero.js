/* hero font cycler — pulls from /hero-fonts.json, rotates infinitely,
 * lets the user blocklist fonts they don't like (localStorage). */

(function () {
  const HERO = document.getElementById("hero");
  if (!HERO) return;

  const PRE = HERO.querySelector("pre");
  const NAME = HERO.querySelector(".hero-name");
  const HIDE = HERO.querySelector(".hero-hide");
  const RESET = HERO.querySelector(".hero-reset");
  const COUNT = HERO.querySelector(".hero-count");
  const PAUSE = HERO.querySelector(".hero-pause");

  const STORE_KEY = "hero.blocklist.v1";
  const INTERVAL = 4200;

  let fonts = [];
  let blocked = new Set(load());
  let current = null;
  let timer = null;
  let paused = false;

  function load() {
    try { return JSON.parse(localStorage.getItem(STORE_KEY) || "[]"); }
    catch { return []; }
  }
  function save() {
    try { localStorage.setItem(STORE_KEY, JSON.stringify([...blocked])); } catch {}
  }

  function available() {
    return fonts.filter((f) => !blocked.has(f.name));
  }

  function fit(rec) {
    // pick a font-size so the art fits the hero box in both axes
    const containerW = HERO.clientWidth || window.innerWidth;
    const containerH = HERO.clientHeight || 200;
    const targetW = Math.min(containerW, window.innerWidth * 0.65, 820);
    const targetH = containerH - 12;            // small breathing room
    const fsW = targetW / (rec.w * 0.61);       // mono char ≈ 0.61em wide
    const fsH = targetH / (rec.h * 1.02);       // line-height 1.0 + a hair
    return Math.max(6, Math.min(fsW, fsH, 22));
  }

  function render(rec) {
    current = rec;
    PRE.textContent = rec.art;
    PRE.style.fontSize = fit(rec).toFixed(2) + "px";
    // re-trigger the css enter animation
    PRE.style.animation = "none";
    void PRE.offsetHeight;
    PRE.style.animation = "";
    NAME.textContent = rec.name;
    const total = fonts.length, on = available().length;
    COUNT.textContent = on + "/" + total;
  }

  function next() {
    const pool = available();
    if (!pool.length) {
      PRE.textContent = "(all fonts blocked — reset to continue)";
      PRE.style.fontSize = "0.85rem";
      NAME.textContent = "—";
      return;
    }
    let pick;
    do { pick = pool[Math.floor(Math.random() * pool.length)]; }
    while (pool.length > 1 && current && pick.name === current.name);
    render(pick);
  }

  function start() {
    stop();
    if (paused) return;
    timer = setInterval(next, INTERVAL);
  }
  function stop() {
    if (timer) { clearInterval(timer); timer = null; }
  }

  HIDE.addEventListener("click", function (e) {
    e.preventDefault();
    if (!current) return;
    blocked.add(current.name);
    save();
    next();
  });

  RESET.addEventListener("click", function (e) {
    e.preventDefault();
    if (!blocked.size) return;
    if (!confirm("clear " + blocked.size + " blocked font(s)?")) return;
    blocked = new Set();
    save();
    const pool = available();
    const total = fonts.length;
    COUNT.textContent = pool.length + "/" + total;
  });

  PAUSE.addEventListener("click", function (e) {
    e.preventDefault();
    paused = !paused;
    PAUSE.textContent = paused ? "[▶ play]" : "[❚❚ pause]";
    if (paused) stop(); else start();
  });

  PRE.addEventListener("click", next);

  window.addEventListener("resize", function () {
    if (current) PRE.style.fontSize = fit(current).toFixed(2) + "px";
  });

  fetch("/hero-fonts.json", { cache: "force-cache" })
    .then((r) => r.json())
    .then((data) => {
      fonts = data;
      HERO.classList.add("loaded");
      next();
      start();
    })
    .catch(() => {
      PRE.textContent = "daniel";
      PRE.style.fontSize = "3rem";
    });
})();
