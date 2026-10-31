/* ==========================================================
    HomeFinder - Accommodation Details page behavior
    Loaded by details.html. No Django template tags in here:
    anything the page needs from Django is read from the HTML.
    Everything is progressive enhancement: with JavaScript off,
    photos open as plain images and every link still works.
   ========================================================== */

(() => {
    const $ = (sel, root = document) => root.querySelector(sel);
    const $$ = (sel, root = document) => [...root.querySelectorAll(sel)];

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
    if (userChip && userDropdown) {
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
 
  /* ---- Photo gallery: mobile counter + full-screen viewer ---- */
    const track = $("#galleryTrack");
    const links = $$("[data-photo]");
    const photoCount = $("#photoCount");
    const viewAll = $("#viewAll");
    const lightbox = $("#lightbox");
 
  // Which photo is showing in the swipeable carousel (mobile)
    const currentSlide = () => {
    if (!track || !links.length) return 0;
    const items = $$(".g-item", track);
    let best = 0, bestDist = Infinity;
    items.forEach((item, i) => {
        const d = Math.abs(item.offsetLeft - track.scrollLeft);
        if (d < bestDist) { best = i; bestDist = d; }
    });
    return best;
    };
 
    if (track && photoCount) {
        let raf = 0;
    track.addEventListener("scroll", () => {
        cancelAnimationFrame(raf);
        raf = requestAnimationFrame(() => {
        photoCount.textContent = `${currentSlide() + 1} / ${links.length}`;
        });
    }, { passive: true });
    }
 
    if (lightbox && typeof lightbox.showModal === "function" && links.length) {
    const img = $("#lbImg");
    const count = $("#lbCount");
    const prev = $("#lbPrev");
    const next = $("#lbNext");
    const close = $("#lbClose");
    const photos = links.map((a) => ({
        src: a.getAttribute("href"),
        alt: $("img", a) ? $("img", a).alt : "",
    }));
    let index = 0;
 
    const show = (i) => {
        index = (i + photos.length) % photos.length;
        img.src = photos[index].src;
        img.alt = photos[index].alt;
        count.textContent = `Photo ${index + 1} of ${photos.length}`;
        const multiple = photos.length > 1;
        prev.hidden = next.hidden = !multiple;
      // warm the cache for the neighbours so arrows feel instant
        [index - 1, index + 1].forEach((n) => { if (multiple) new Image().src = photos[(n + photos.length) % photos.length].src; });
    };
 
    const open = (i) => { show(i); lightbox.showModal(); };
 
    links.forEach((a, i) => a.addEventListener("click", (e) => {
      if (e.metaKey || e.ctrlKey || e.shiftKey || e.button !== 0) return; // keep "open in new tab"
        e.preventDefault();
        open(i);
    }));
 
    if (viewAll) {
        viewAll.hidden = false; // the button only works with JS, so it is revealed by JS
        viewAll.addEventListener("click", () => open(0));
    }
 
    prev.addEventListener("click", () => show(index - 1));
    next.addEventListener("click", () => show(index + 1));
    close.addEventListener("click", () => lightbox.close());
 
    lightbox.addEventListener("keydown", (e) => {
        if (e.key === "ArrowLeft") { e.preventDefault(); show(index - 1); }
        if (e.key === "ArrowRight") { e.preventDefault(); show(index + 1); }
    });
 
    // Click on the dark area (not the photo or a button) closes the viewer
    lightbox.addEventListener("click", (e) => {
        if (e.target === lightbox || e.target.classList.contains("lb-figure")) lightbox.close();
    });
 
    // After closing, the mobile carousel jumps to the photo that was last viewed
    lightbox.addEventListener("close", () => {
        if (track && window.matchMedia("(max-width: 639px)").matches) {
        const item = $$(".g-item", track)[index];
        if (item) track.scrollTo({ left: item.offsetLeft, behavior: "auto" });
        }
    });
    }
 
  /* ---- Contact Provider: show that the action was picked ---- */
    const contactLinks = $$("[data-contact]");
    const resetContact = () => contactLinks.forEach((a) => {
    a.classList.remove("is-opening");
    a.removeAttribute("aria-disabled");
    a.removeAttribute("aria-busy");
    const label = $(".btn-label", a);
    if (label && label.dataset.label) label.textContent = label.dataset.label;
    });
 
    contactLinks.forEach((a) => a.addEventListener("click", (e) => {
    if (e.metaKey || e.ctrlKey || e.shiftKey || e.button !== 0) return; // new tab: leave this page alone
    if (a.getAttribute("href").startsWith("mailto:")) return; // email opens the mail app and the page stays, so no "Opening…"
    contactLinks.forEach((b) => {
        const label = $(".btn-label", b);
        if (label) { label.dataset.label = label.dataset.label || label.textContent; label.textContent = "Opening…"; }
        b.classList.add("is-opening");
        b.setAttribute("aria-disabled", "true");
        b.setAttribute("aria-busy", "true");
    });
    }));
 
  // Coming back with the browser's Back button must not leave the buttons stuck on "Opening…"
    window.addEventListener("pageshow", (e) => { if (e.persisted) resetContact(); });
 
  /* ---- Mobile bottom bar: appears when the rent/contact panel is out of view ---- */
    const bar = $("#mobileBar");
    const panel = $("#contactPanel");
    if (bar && panel && "IntersectionObserver" in window) {
    new IntersectionObserver(([entry]) => {
        bar.hidden = entry.isIntersecting;
    }).observe(panel);
    }
})();
