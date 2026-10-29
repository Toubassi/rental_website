// ---------- 1) Show / hide a password. Uses only document.querySelector ----------
function setupToggle(buttonSelector, inputSelector) {
  var button = document.querySelector(buttonSelector);
  var input = document.querySelector(inputSelector);
 
  button.addEventListener('click', function () {
    var isHidden = input.type === 'password';
    if (isHidden) {
      input.type = 'text';
      button.classList.add('is-showing');
      button.setAttribute('aria-pressed', 'true');
      button.setAttribute('aria-label', 'Hide password');
    } else {
      input.type = 'password';
      button.classList.remove('is-showing');
      button.setAttribute('aria-pressed', 'false');
      button.setAttribute('aria-label', 'Show password');
    }
  });
}
 
setupToggle('#toggle-password', '#id_password');
setupToggle('#toggle-confirm', '#id_confirm_password');
 
 
// ---------- 2) Calendar button next to Date of Birth (optional extra: the box can also be typed in) ----------
// The visible box is a normal text box, so it always shows DD/MM/YYYY on every browser.
// The calendar icon opens the browser's own calendar (a hidden <input type="date">),
// and when you pick a day we write it into the text box as DD/MM/YYYY.
var dobInput = document.querySelector('#id_dob');
var calendarHelper = document.querySelector('#calendar-helper');
var calendarButton = document.querySelector('#open-calendar');
 
calendarButton.addEventListener('click', function () {
  try {
    calendarHelper.showPicker();      // opens the calendar pop-up
  } catch (error) {
    dobInput.focus();                 // very old browser: just let the person type the date
  }
});
 
calendarHelper.addEventListener('change', function () {
  var parts = calendarHelper.value.split('-');    // the helper gives "YYYY-MM-DD"
  if (parts.length === 3) {
    dobInput.value = parts[2] + '/' + parts[1] + '/' + parts[0];
  }
});