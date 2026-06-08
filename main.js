const products = [
  { name: "Eye Gelass", price: 1000, image: "eyegalss_a.jpg" },
  { name: "iPhone 14 pro max", price: 650, image: "iphone14.jpg" },
  { name: "phone suction stickers", price: 300, image: "phone.jpg" },
  { name: "New Stylish EyeGlasses", price: 1000, image: "eye_galss_b.jpg" },
  { name: "New Stylish EyeGlasses", price: 1000, image: "eyegalssd.jpg" },
  { name: "New Stylish EyeGlasses", price: 1000, image: "eyegalssc.jpg" },
  { name: "Galaxy a56", price: 899, image: "galaxya56.jpg" },
  { name: "Galaxy S23", price: 899, image: "galaxys23.jpg" },
  { name: "Galaxy 12 pro", price: 899, image: "galxy12pro.jpg" },
  { name: "iphone 11", price: 999, image: "iphone11.jpg" },
  { name: "galaxy cover", price: 1000, image: "galaxy.jpg" }
];

// Persistent variables saved globally so items aren't deleted when viewing contact page
if (!window.cartStorage) window.cartStorage = {};
if (!window.totalStorage) window.totalStorage = 0;

// 1. Core Render and Bind Engine Function
function initHerryStoreGrid() {
  const productsDiv = document.getElementById("products");
  const orderBtn = document.getElementById("orderBtn");

  // If we aren't currently viewing the main storefront HTML layout page, exit safely
  if (!productsDiv || !orderBtn) return;

  // Clear existing items grid layout to prevent rendering duplicates
  productsDiv.innerHTML = "";

  // Render items to the Home Page interface grid
  products.forEach(product => {
    const div = document.createElement("div");
    div.className = "product";
    div.innerHTML = `
      <img src="${product.image}" alt="${product.name}" style="width:100%; max-width:150px; object-fit:cover;">
      <h3>${product.name}</h3>
      <p>${product.price} ETB</p>
      <button class="add-btn">Add To Cart</button>
    `;

    div.querySelector(".add-btn").addEventListener("click", () => {
      if (window.cartStorage[product.name]) {
        window.cartStorage[product.name].quantity += 1;
      } else {
        window.cartStorage[product.name] = {
          name: product.name,
          price: product.price,
          quantity: 1
        };
      }

      window.totalStorage += product.price;
      updateCartUI();
    });

    productsDiv.appendChild(div);
  });

  // 2. Clear old event links and cleanly re-attach the active listener to your Order button
  const newOrderBtn = orderBtn.cloneNode(true);
  orderBtn.parentNode.replaceChild(newOrderBtn, orderBtn);

  newOrderBtn.addEventListener("click", () => {
    const tg = window.Telegram?.WebApp;
    const finalizedCartArray = Object.values(window.cartStorage);

    if (finalizedCartArray.length === 0) {
      if (tg && typeof tg.showAlert === 'function') {
        tg.showAlert("Your cart is empty! Please add some items first. 🛒");
      } else {
        alert("Your cart is empty! Please add some items first. 🛒");
      }
      return;
    }

    // Pass the finalized data package directly back to your Python Flask Telegram Bot
    if (tg && typeof tg.sendData === 'function') {
      tg.sendData(JSON.stringify({
        cart: finalizedCartArray,
        total: window.totalStorage
      }));
      tg.close();
    } else {
      console.log("Data packet simulation package:", { cart: finalizedCartArray, total: window.totalStorage });
      alert("Order sent to bot! (Testing mode outside Telegram)");
    }
  });

  // Keep the visual item list and price total correct after switching pages
  updateCartUI();
}

// 3. Refresh and Render Cart Layout Text views
function updateCartUI() {
  const totalDisplay = document.getElementById("total");
  const cartList = document.getElementById("cart");

  if (totalDisplay) totalDisplay.innerText = window.totalStorage;
  if (!cartList) return;

  cartList.innerHTML = ""; 

  Object.values(window.cartStorage).forEach(item => {
    const li = document.createElement("li");
    li.innerText = `${item.name} (x${item.quantity}) — ${item.price * item.quantity} ETB`;
    cartList.appendChild(li);
  });
}

// Run the script instantly when loading up for the first time
document.addEventListener("DOMContentLoaded", initHerryStoreGrid);

// 🛠️ MAGIC TRICK: Expose this function globally to your template navigation setup
window.refreshStoreListeners = initHerryStoreGrid;
