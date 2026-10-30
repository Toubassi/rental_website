/* ==========================================================
   HomeFinder - Explore Accommodation page behavior
   Loaded by explore.html. No Django template tags in here:
   anything the page needs from Django is read from the HTML.
   ========================================================== */
 
(() => {
  const $ = (sel, root = document) => root.querySelector(sel);
  const form = $("#filters");
  const searchBtn = $("#searchBtn");
  const searchLabel = $(".btn-label", searchBtn);
  const quickType = $("#quick_type");
  const typeBoxes = [...form.querySelectorAll('input[name="type"]')];
  const maxTop = $("#max_top");
  const minPrice = $("#min_price");
  const maxPrice = $("#max_price");
  const rangeMin = $("#rangeMin");
  const rangeMax = $("#rangeMax");
  const rangeFill = $("#rangeFill");
  const budgetError = $("#budget-error");
  const sort = $("#sort");
  const cardGrid = $("#cardGrid");
  const emptyState = $("#emptyState");
  const resultsCount = $("#resultsCount");
  const pagination = $("#pagination");
  const resultsMeta = $(".results-meta");
  const skeletonGrid = $("#skeletonGrid");
  const loadingStatus = $("#loadingStatus");
 
  /* ---- Mobile menu ---- */
  const nav = $("#nav");
  const navToggle = $("#navToggle");
  if (nav && navToggle) {
    navToggle.addEventListener("click", () => {
      const open = nav.classList.toggle("is-open");
      navToggle.setAttribute("aria-expanded", String(open));
      navToggle.setAttribute("aria-label", open ? "Close menu" : "Open menu");
    });
  }
 
  /* ---- User dropdown ---- */
  const userChip = $("#userChip");
  const userDropdown = $("#userDropdown");
  if (userChip) {
    const setMenu = (open) => {
      userDropdown.hidden = !open;
      userChip.setAttribute("aria-expanded", String(open));
    };
    userChip.addEventListener("click", () => setMenu(userDropdown.hidden));
    document.addEventListener("click", (e) => {
      if (!userDropdown.hidden && !e.target.closest("#userMenu")) setMenu(false);
    });
    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape" && !userDropdown.hidden) { setMenu(false); userChip.focus(); }
    });
  }
 
  /* ---- Filters on small screens ---- */
  const filterToggle = $("#filterToggle");
  filterToggle.addEventListener("click", () => {
    const open = $("#sidebar").classList.toggle("is-open");
    filterToggle.setAttribute("aria-expanded", String(open));
  });
 
  /* ---- Keep the search bar and the sidebar in step ---- */
  quickType.addEventListener("change", () => {
    typeBoxes.forEach((b) => (b.checked = quickType.value !== "" && b.value === quickType.value));
  });
  typeBoxes.forEach((b) => b.addEventListener("change", () => {
    const on = typeBoxes.filter((x) => x.checked);
    quickType.value = on.length === 1 ? on[0].value : "";
  }));
 
  const limit = Number(rangeMax.max) || 1000;
  function paintRange() {
    const a = (Number(rangeMin.value) / limit) * 100;
    const b = (Number(rangeMax.value) / limit) * 100;
    rangeFill.style.left = Math.min(a, b) + "%";
    rangeFill.style.right = 100 - Math.max(a, b) + "%";
  }
  function syncRangeFromInputs() {
    rangeMin.value = minPrice.value === "" ? 0 : Math.min(Number(minPrice.value), limit);
    rangeMax.value = maxPrice.value === "" ? limit : Math.min(Number(maxPrice.value), limit);
    paintRange();
  }
  rangeMin.addEventListener("input", () => {
    if (Number(rangeMin.value) > Number(rangeMax.value)) rangeMin.value = rangeMax.value;
    minPrice.value = Number(rangeMin.value) > 0 ? rangeMin.value : "";
    paintRange();
  });
  rangeMax.addEventListener("input", () => {
    if (Number(rangeMax.value) < Number(rangeMin.value)) rangeMax.value = rangeMin.value;
    maxPrice.value = Number(rangeMax.value) < limit ? rangeMax.value : "";
    maxTop.value = maxPrice.value;
    paintRange();
  });
  minPrice.addEventListener("input", syncRangeFromInputs);
  maxPrice.addEventListener("input", () => { maxTop.value = maxPrice.value; syncRangeFromInputs(); });
  maxTop.addEventListener("input", () => { maxPrice.value = maxTop.value; syncRangeFromInputs(); });
  syncRangeFromInputs();
 
  /* ---- Loading skeletons ---- */
  const skeletonTpl = $("#skeletonTpl");
  for (let i = 0; i < 6; i++) skeletonGrid.appendChild(skeletonTpl.content.cloneNode(true));
 
  function setLoading(on) {
    searchBtn.classList.toggle("is-loading", on);
    searchBtn.setAttribute("aria-disabled", String(on));
    searchLabel.textContent = on ? "Searching…" : "Search";
    form.setAttribute("aria-busy", String(on));
    [cardGrid, emptyState, resultsCount, pagination, resultsMeta].forEach((el) => el && (el.hidden = on));
    skeletonGrid.hidden = !on;
    loadingStatus.textContent = on ? "Loading accommodation…" : "";
  }
 
  /* ---- Submit ---- */
  const skipped = [];
  function skipField(el) {
    if (!el.name) return;
    skipped.push([el, el.name]);
    el.removeAttribute("name");
  }
 
  function submitForm() {
    if (searchBtn.getAttribute("aria-disabled") === "true") return false;
 
    if (minPrice.value && maxPrice.value && Number(minPrice.value) > Number(maxPrice.value)) {
      budgetError.textContent = "The minimum budget is higher than the maximum.";
      budgetError.hidden = false;
      if (!$("#sidebar").classList.contains("is-open") && getComputedStyle(filterToggle).display !== "none") filterToggle.click();
      minPrice.focus();
      return false;
    }
    budgetError.hidden = true;
 
    // The search bar controls are mirrored in the sidebar, so only the sidebar copies are sent.
    // Empty fields are skipped too, which keeps the URL tidy. (A field without a name is not submitted.)
    skipField(quickType);
    skipField(maxTop);
    [...form.elements].forEach((el) => {
      if (el.name && el.type !== "checkbox" && !el.value) skipField(el);
    });
    setLoading(true);
    return true;
  }
 
  form.addEventListener("submit", (e) => {
    if (!submitForm()) e.preventDefault();
  });
 
  sort && sort.addEventListener("change", () => form.requestSubmit());
 
  /* ---- Opening a card ---- */
  document.querySelectorAll(".card-link").forEach((link) => {
    link.addEventListener("click", (e) => {
      if (e.button !== 0 || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return; // new tab/window
      link.closest(".card").classList.add("is-opening");
      link.setAttribute("aria-busy", "true");
      $(".btn-label", link).textContent = "Opening…";
    });
  });
 
  /* ---- Saved places (kept in this browser until a Favorites feature exists) ---- */
  const KEY = "homefinder-saved";
  const readSaved = () => { try { return JSON.parse(localStorage.getItem(KEY)) || []; } catch (e) { return []; } };
  const writeSaved = (list) => { try { localStorage.setItem(KEY, JSON.stringify(list)); } catch (e) {} };
  const saved = new Set(readSaved().map(String));
 
  document.querySelectorAll(".fav").forEach((btn) => {
    const title = btn.getAttribute("aria-label").replace(/^Save /, "");
    const paint = () => {
      const on = saved.has(btn.dataset.id);
      btn.setAttribute("aria-pressed", String(on));
      btn.setAttribute("aria-label", (on ? "Remove from saved: " : "Save ") + title);
    };
    paint();
    btn.addEventListener("click", () => {
      saved.has(btn.dataset.id) ? saved.delete(btn.dataset.id) : saved.add(btn.dataset.id);
      writeSaved([...saved]);
      paint();
    });
  });
 
  /* ---- Back button: restore the page from the browser cache cleanly ---- */
  window.addEventListener("pageshow", (e) => {
    if (!e.persisted) return;
    skipped.forEach(([el, name]) => el.setAttribute("name", name));
    skipped.length = 0;
    setLoading(false);
    document.querySelectorAll(".card.is-opening").forEach((card) => {
      card.classList.remove("is-opening");
      const link = $(".card-link", card);
      link.removeAttribute("aria-busy");
      $(".btn-label", link).textContent = "View Details";
    });
  });
})();
 