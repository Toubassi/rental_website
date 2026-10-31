/* ==========================================================
   HomeFinder - Sign In page behavior
   Loaded by login.html.
   ========================================================== */
 
(() => {
  const form = document.getElementById("signin-form");
  const username = document.getElementById("username");
  const password = document.getElementById("password");
  const submitBtn = document.getElementById("signin-btn");
  const btnLabel = submitBtn.querySelector(".btn-label");
  const pwToggle = document.getElementById("togglePassword");
  const nav = document.getElementById("nav");
  const navToggle = document.getElementById("navToggle");
 
  /* ---- Mobile menu ---- */
  if (nav && navToggle) {
    navToggle.addEventListener("click", () => {
      const open = nav.classList.toggle("is-open");
      navToggle.setAttribute("aria-expanded", String(open));
      navToggle.setAttribute("aria-label", open ? "Close menu" : "Open menu");
    });
  }
 
  /* ---- Show / hide password ---- */
  pwToggle.addEventListener("click", () => {
    const show = password.type === "password";
    password.type = show ? "text" : "password";
    pwToggle.classList.toggle("is-visible", show);
    pwToggle.setAttribute("aria-pressed", String(show));
    pwToggle.setAttribute("aria-label", show ? "Hide password" : "Show password");
  });
 
  /* ---- Inline validation ---- */
  const checks = [
    { input: username, empty: (v) => v.trim() === "", message: "Enter your email or username." },
    { input: password, empty: (v) => v === "", message: "Enter your password." },
  ];
 
  function setError(input, message) {
    const field = input.closest(".field");
    const err = document.getElementById(input.id + "-error");
    field.classList.add("has-error");
    input.setAttribute("aria-invalid", "true");
    err.textContent = message;
    err.hidden = false;
  }
 
  function clearError(input) {
    const field = input.closest(".field");
    const err = document.getElementById(input.id + "-error");
    field.classList.remove("has-error");
    input.removeAttribute("aria-invalid");
    err.textContent = "";
    err.hidden = true;
  }
 
  checks.forEach(({ input }) => {
    input.addEventListener("input", () => {
      if (form.dataset.serverError) {
        // the server message covers both fields, so clear both together
        checks.forEach((c) => clearError(c.input));
        delete form.dataset.serverError;
      } else {
        clearError(input);
      }
    });
  });
 
  /* ---- Loading state ---- */
  function setLoading(on) {
    submitBtn.classList.toggle("is-loading", on);
    submitBtn.setAttribute("aria-disabled", String(on));
    submitBtn.setAttribute("aria-busy", String(on));
    btnLabel.textContent = on ? "Signing in…" : "Sign In";
  }
 
  form.addEventListener("submit", (e) => {
    if (submitBtn.getAttribute("aria-disabled") === "true") {
      e.preventDefault(); // ignore double clicks while signing in
      return;
    }
 
    let firstInvalid = null;
    checks.forEach(({ input, empty, message }) => {
      if (empty(input.value)) {
        setError(input, message);
        firstInvalid = firstInvalid || input;
      } else {
        clearError(input);
      }
    });
 
    if (firstInvalid) {
      e.preventDefault();
      firstInvalid.focus();
      return;
    }
 
    setLoading(true);
  });
 
  // Coming back with the browser's back button should not leave the button stuck
  window.addEventListener("pageshow", (e) => {
    if (e.persisted && !submitBtn.classList.contains("is-success")) setLoading(false);
  });
})();
 