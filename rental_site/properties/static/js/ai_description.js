const generateButton = document.getElementById("generate-description");

if (generateButton) {
  generateButton.addEventListener("click", async function () {
    const title = document.getElementById("id_title").value;
    const city = document.getElementById("id_city").value;
    const address = document.getElementById("id_address").value;
    const rent = document.getElementById("id_monthly_rent").value;

    const descriptionField = document.getElementById("id_desc");
    const status = document.getElementById("ai-description-status");

    const csrfToken = document.querySelector(
      "[name=csrfmiddlewaretoken]",
    ).value;

    if (!title || !city || !address || !rent) {
      status.textContent =
        "Please fill in the title, city, address, and rent first.";
      return;
    }

    const formData = new FormData();

    formData.append("title", title);
    formData.append("city", city);
    formData.append("address", address);
    formData.append("monthly_rent", rent);

    generateButton.disabled = true;
    status.textContent = "Generating your description...";

    try {
      const response = await fetch("/generate-description/", {
        method: "POST",
        headers: {
          "X-CSRFToken": csrfToken,
        },
        body: formData,
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || "Something went wrong.");
      }

      descriptionField.value = data.description;
      status.textContent =
        "Description generated! Review and edit it before publishing.";
    } catch (error) {
      status.textContent = error.message;
    } finally {
      generateButton.disabled = false;
    }
  });
}
