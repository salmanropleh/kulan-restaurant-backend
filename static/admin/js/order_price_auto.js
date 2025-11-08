// static/admin/js/order_price_auto.js
document.addEventListener("DOMContentLoaded", function () {
  console.log("Order price auto-fill script loaded!");

  function updatePrice(selectElement) {
    const selectedOption = selectElement.options[selectElement.selectedIndex];
    if (selectedOption && selectedOption.value) {
      // Extract price from the option text (format: "Item Name - $Price")
      const optionText = selectedOption.text;
      console.log("Option text:", optionText);

      const priceMatch = optionText.match(/\$([\d.]+)/);

      if (priceMatch) {
        const price = priceMatch[1];
        console.log("Extracted price:", price);

        // Find the closest table row
        const row = selectElement.closest("tr");
        if (row) {
          // Find the price input in this row - look for any input that contains "price" in its ID
          const inputs = row.querySelectorAll("input");
          let priceInput = null;

          inputs.forEach((input) => {
            if (input.id.includes("price") || input.name.includes("price")) {
              priceInput = input;
            }
          });

          if (priceInput) {
            priceInput.value = price;
            console.log(
              "Auto-filled price input:",
              priceInput.id,
              "with value:",
              price
            );

            // Trigger events to update the form
            priceInput.dispatchEvent(new Event("change", { bubbles: true }));
            priceInput.dispatchEvent(new Event("input", { bubbles: true }));
            priceInput.dispatchEvent(new Event("blur", { bubbles: true }));
          } else {
            console.log("Could not find price input in row");
          }
        }
      }
    }
  }

  // Listen for changes on menu item selects
  document.addEventListener("change", function (e) {
    if (e.target.matches("select")) {
      const select = e.target;
      if (
        select.id.includes("menu_item") ||
        select.name.includes("menu_item")
      ) {
        console.log("Menu item select changed:", select.value);
        updatePrice(select);
      }
    }
  });

  // Update prices for existing selects when page loads
  setTimeout(function () {
    const menuItemSelects = document.querySelectorAll("select");
    menuItemSelects.forEach(function (select) {
      if (
        (select.id.includes("menu_item") ||
          select.name.includes("menu_item")) &&
        select.value
      ) {
        console.log("Updating existing select:", select.value);
        updatePrice(select);
      }
    });
  }, 500);
});
