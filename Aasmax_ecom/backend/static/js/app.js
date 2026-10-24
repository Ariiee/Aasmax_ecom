async function postJSON(url, payload, method = "POST") {
  const res = await fetch(url, {
    method,
    headers: {
      "Content-Type": "application/json",
      "X-Requested-With": "XMLHttpRequest",
    },
    credentials: "same-origin",
    body: method === "GET" ? undefined : JSON.stringify(payload),
  });

  let data = null;
  try {
    data = await res.json();
  } catch (e) {
    throw new Error("Server returned an invalid response.");
  }

  if (!res.ok || data?.success === false) {
    throw new Error(data?.message || "Request failed.");
  }
  return data;
}

function flashMessage(message, kind = "success") {
  const existing = document.querySelector(".js-floating-message");
  if (existing) existing.remove();

  const el = document.createElement("div");
  el.className = `js-floating-message alert alert-${kind} position-fixed top-0 end-0 m-3 shadow-lg border-0`;
  el.style.zIndex = "2000";
  el.style.maxWidth = "min(420px, calc(100vw - 2rem))";
  el.textContent = message;
  document.body.appendChild(el);

  setTimeout(() => {
    el.classList.add("fade");
    el.style.opacity = "0";
    setTimeout(() => el.remove(), 300);
  }, 2200);
}

function setButtonLoading(button, loading, label = "Processing...") {
  if (!button) return;
  if (loading) {
    button.dataset.originalText = button.innerHTML;
    button.disabled = true;
    button.innerHTML = `<span class="spinner-border spinner-border-sm me-2" aria-hidden="true"></span>${label}`;
  } else {
    button.disabled = false;
    if (button.dataset.originalText) button.innerHTML = button.dataset.originalText;
  }
}

function getTheme() {
  return localStorage.getItem("aasmax-theme") || "dark";
}

function applyTheme(theme) {
  document.documentElement.setAttribute("data-bs-theme", theme);
  localStorage.setItem("aasmax-theme", theme);
  const toggle = document.querySelector("[data-theme-toggle]");
  if (toggle) {
    toggle.innerHTML = theme === "dark" ? "<span>Dark</span>" : "<span>Light</span>";
  }
}

document.addEventListener("DOMContentLoaded", () => {
  applyTheme(getTheme());
});

document.addEventListener("click", async (event) => {
  const cartBtn = event.target.closest(".js-add-to-cart");
  const wishlistBtn = event.target.closest(".js-add-to-wishlist");
  const moveBtn = event.target.closest(".js-move-to-cart");
  const removeBtn = event.target.closest(".js-remove-wishlist");
  const qtyBtn = event.target.closest(".js-qty-btn");
  const themeBtn = event.target.closest("[data-theme-toggle]");
  const removeCartBtn = event.target.closest(".js-remove-cart-item");
  const saveProfileBtn = event.target.closest("[data-save-profile]");
  const saveAddressBtn = event.target.closest("[data-save-address]");
  const removeAddressBtn = event.target.closest(".js-remove-address");

  try {
    if (themeBtn) {
      const nextTheme = getTheme() === "dark" ? "light" : "dark";
      applyTheme(nextTheme);
      return;
    }

    if (saveProfileBtn) {
      const form = document.getElementById("profileForm");
      const payload = Object.fromEntries(new FormData(form).entries());
      setButtonLoading(saveProfileBtn, true, "Saving...");
      await postJSON("/api/profile", payload, "PUT");
      flashMessage("Profile updated");
      return;
    }

    if (saveAddressBtn) {
      const form = document.getElementById("addressForm");
      const payload = Object.fromEntries(new FormData(form).entries());
      payload.is_default = form.querySelector("[name=is_default]")?.checked ? "1" : "";
      setButtonLoading(saveAddressBtn, true, "Saving...");
      await postJSON("/api/addresses", payload, "POST");
      flashMessage("Address saved");
      setTimeout(() => window.location.reload(), 500);
      return;
    }

    if (removeAddressBtn) {
      setButtonLoading(removeAddressBtn, true, "Removing...");
      await postJSON(`/api/addresses/${removeAddressBtn.dataset.addressId}`, {}, "DELETE");
      flashMessage("Address removed");
      setTimeout(() => window.location.reload(), 500);
      return;
    }

    if (removeCartBtn) {
      setButtonLoading(removeCartBtn, true, "Removing...");
      await postJSON(`/api/cart/items/${removeCartBtn.dataset.itemId}`, {}, "DELETE");
      flashMessage("Item removed from cart");
      setTimeout(() => window.location.reload(), 500);
      return;
    }

    if (cartBtn) {
      setButtonLoading(cartBtn, true, "Adding...");
      await postJSON("/api/cart/items", {
        product_id: cartBtn.dataset.productId,
        quantity: Number(cartBtn.dataset.quantity || 1),
      });
      flashMessage(`${cartBtn.dataset.productName} added to cart`);
      setTimeout(() => window.location.reload(), 300);
      return;
    }

    if (wishlistBtn) {
      setButtonLoading(wishlistBtn, true, "Saving...");
      await postJSON("/api/wishlist", {
        product_id: wishlistBtn.dataset.productId,
      });
      flashMessage(`${wishlistBtn.dataset.productName} added to wishlist`);
      return;
    }

    if (moveBtn) {
      setButtonLoading(moveBtn, true, "Moving...");
      await postJSON("/api/wishlist/move-to-cart", {
        product_id: moveBtn.dataset.productId,
      });
      flashMessage("Moved to cart");
      setTimeout(() => window.location.reload(), 500);
      return;
    }

    if (removeBtn) {
      setButtonLoading(removeBtn, true, "Removing...");
      await postJSON("/api/wishlist", {
        product_id: removeBtn.dataset.productId,
      }, "DELETE");
      flashMessage("Removed from wishlist");
      setTimeout(() => window.location.reload(), 500);
      return;
    }

    if (qtyBtn) {
      const itemId = qtyBtn.dataset.itemId;
      const delta = Number(qtyBtn.dataset.delta || 0);
      const input = document.querySelector(`[data-qty-input="${itemId}"]`);
      if (!input) return;
      const nextValue = Math.max(1, Number(input.value || 1) + delta);
      input.value = nextValue;
      await postJSON(`/api/cart/items/${itemId}`, { quantity: nextValue }, "PUT");
      window.location.reload();
    }
  } catch (error) {
    flashMessage(error.message || "Something went wrong.", "danger");
  } finally {
    [cartBtn, wishlistBtn, moveBtn, removeBtn, qtyBtn, saveProfileBtn, saveAddressBtn, removeCartBtn, removeAddressBtn].forEach((button) => {
      if (button && button.disabled) setButtonLoading(button, false);
    });
  }
});
