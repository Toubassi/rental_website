// =====================================================
// ADD ACCOMMODATION PAGE - properties/static/js/add_accommodation.js
// 1) choose photos, show previews, remove a photo
// 2) "Publishing..." state on the button
// (The server checks everything again. This file only makes the page nicer to use.)
// =====================================================


// ---------- 1) Photos ----------
var MAX_PHOTOS = 8;
var MAX_MB = 5;
var ALLOWED_TYPES = ['image/jpeg', 'image/png', 'image/webp'];

var photoInput = document.querySelector('#photos');
var chooseButton = document.querySelector('#choose-photos');
var previewBox = document.querySelector('#photo-previews');
var photoMessage = document.querySelector('#photos-error');

var chosenFiles = [];      // the photos picked so far
var previewUrls = [];      // temporary addresses used to show the previews

// the visible "Choose Photos" button opens the hidden file input
chooseButton.addEventListener('click', function () {
  photoInput.click();
});

// show a message under the upload box (or hide it when the text is empty)
function showPhotoMessage(text) {
  photoMessage.textContent = text;
  photoMessage.hidden = (text === '');
}

// when the person picks photos
photoInput.addEventListener('change', function () {
  var problem = '';
  var picked = Array.from(photoInput.files);

  picked.forEach(function (file) {
    var alreadyChosen = chosenFiles.some(function (other) {
      return other.name === file.name && other.size === file.size;
    });

    if (alreadyChosen) {
      return;                                            // same photo twice: ignore it
    }
    if (ALLOWED_TYPES.indexOf(file.type) === -1) {
      problem = '"' + file.name + '" is not a JPG, PNG or WebP photo.';
    } else if (file.size > MAX_MB * 1024 * 1024) {
      problem = '"' + file.name + '" is bigger than ' + MAX_MB + ' MB.';
    } else if (chosenFiles.length >= MAX_PHOTOS) {
      problem = 'You can add up to ' + MAX_PHOTOS + ' photos.';
    } else {
      chosenFiles.push(file);
    }
  });

  showPhotoMessage(problem);
  refreshPhotos();
});

// draw the previews and give the form the right list of files
function refreshPhotos() {
  // free the old preview addresses
  previewUrls.forEach(function (url) {
    URL.revokeObjectURL(url);
  });
  previewUrls = [];
  previewBox.innerHTML = '';

  chosenFiles.forEach(function (file, index) {
    var url = URL.createObjectURL(file);
    previewUrls.push(url);

    var box = document.createElement('div');
    box.className = 'aa-thumb';

    var img = document.createElement('img');
    img.src = url;
    img.alt = 'Selected photo ' + (index + 1);

    var removeButton = document.createElement('button');
    removeButton.type = 'button';
    removeButton.className = 'aa-thumb-remove';
    removeButton.setAttribute('aria-label', 'Remove photo ' + (index + 1));
    removeButton.innerHTML = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M6 6l12 12"/><path d="M18 6 6 18"/></svg>';
    removeButton.addEventListener('click', function () {
      chosenFiles.splice(index, 1);                      // take this photo out of the list
      showPhotoMessage('');
      refreshPhotos();
    });

    box.appendChild(img);
    box.appendChild(removeButton);
    previewBox.appendChild(box);
  });

  // ADVANCED (outside the course): a file input can not be edited directly,
  // so we build a new list of files with DataTransfer and give it to the input.
  var list = new DataTransfer();
  chosenFiles.forEach(function (file) {
    list.items.add(file);
  });
  photoInput.files = list.files;
}


// ---------- 2) The Publish button: "Publishing..." while the form is being sent ----------
var form = document.querySelector('#add-form');
var publishButton = document.querySelector('#publish-button');
var publishLabel = document.querySelector('#publish-label');

form.addEventListener('submit', function () {
  publishButton.disabled = true;                         // stops a second click (no double listing)
  publishLabel.textContent = 'Publishing...';
});

// if the person comes back with the browser's Back button, make the button normal again
window.addEventListener('pageshow', function () {
  publishButton.disabled = false;
  publishLabel.textContent = 'Publish Accommodation';
});