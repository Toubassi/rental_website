const reviewForm = document.getElementById("review-form");

if (reviewForm) {
  reviewForm.addEventListener("submit", async function (event) {
    event.preventDefault();

    const status = document.getElementById("review-status");
    const formData = new FormData(reviewForm);

    try {
      const response = await fetch(reviewForm.dataset.url, {
        method: "POST",
        headers: {
          "X-CSRFToken": formData.get("csrfmiddlewaretoken"),
        },
        body: formData,
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error);
      }

      status.textContent = data.message;

      const reviewCard = document.createElement("article");
      const emptyMessage = document.getElementById("no-reviews");

      if (emptyMessage) {
        emptyMessage.remove();
      }

      const username = document.createElement("h4");
      username.textContent = data.username;

      const stars = document.createElement("p");
      stars.classList.add("review-stars");
      stars.textContent = "★".repeat(data.rating) + "☆".repeat(5 - data.rating);

      const comment = document.createElement("p");
      comment.textContent = data.review;

      const date = document.createElement("small");
      date.textContent = data.created_at;

      reviewCard.append(username, stars, comment, date);

      const reviewsList = document.getElementById("reviews-list");
      reviewsList.prepend(reviewCard);

      reviewForm.reset();

      reviewForm.style.display = "none";
    } catch (error) {
      status.textContent = error.message || "Something went wrong.";
    }
  });
}
