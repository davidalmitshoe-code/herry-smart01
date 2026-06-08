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

// Load saved data from localStorage memory or initialize empty if first time
let savedCart = localStorage.getItem("herry_cart");
let savedTotal = localStorage.getItem("herry_total");

let cart = savedCart ? JSON.parse(savedCart) : {};
let total = savedTotal ? parseInt(savedTotal) : 0;

function initHerryStoreGrid() {
  const productsDiv = document.getElementById("products");
  const orderBtn = document.getElementById("orderBtn");

  if (!productsDiv || !orderBtn) return;

  productsDiv.innerHTML = "";

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
      if (cart[product.name]) {
        cart[product.name].quantity += 1;
      } else {
        cart[product.name] = {
          name: product.name,
          price: product.price,
          quantity: 1
        };
      }

      total += product.price;
      
      // Save changes to device storage instantly
      saveCartToStorage();
      updateCartUI();
    });

    productsDiv.appendChild(div);
  });

  // Re-bind click listener safely
  const newOrderBtn = orderBtn.cloneNode(true);
  orderBtn.parentNode.replaceChild(newOrderBtn, orderBtn);

  newOrderBtn.addEventListener("click", () => {
    const tg = window.Telegram?.WebApp;
    const finalizedCartArray = Object.values(cart);

    if (finalizedCartArray.length === 0) {
      if (tg && typeof tg.showAlert === 'function') {
        tg.showAlert("Your cart is empty! Please add some items first. 🛒");
      } else {
        alert("Your cart is empty! Please add some items first. 🛒");
      }
      return;
    }

    if (tg && typeof tg.sendData === 'function') {
      tg.sendData(JSON.stringify({
        cart: finalizedCartArray,
        total: total
      }));
      
      // Clear storage after successful order so old items disappear
      localStorage.removeItem("herry_cart");
      localStorage.removeItem("herry_total");
      
      tg.close();
    } else {
      alert("Order simulated! (Testing mode)");
    }
  });

  updateCartUI();
}

// Save engine state values to client memory database
function saveCartToStorage() {
  localStorage.setItem("herry_cart", JSON.stringify(cart));
  localStorage.setItem("herry_total", total.toString());
}

function updateCartUI() {
  const totalDisplay = document.getElementById("total");
  const cartList = document.getElementById("cart");

  if (totalDisplay) totalDisplay.innerText = total;
  if (!cartList) return;

  cartList.innerHTML = ""; 

  Object.values(cart).forEach(item => {
    const li = document.createElement("li");
    li.innerText = `${item.name} (x${item.quantity}) — ${item.price * item.quantity} ETB`;
    cartList.appendChild(li);
  });
}

document.addEventListener("DOMContentLoaded", initHerryStoreGrid);
window.refreshStoreListeners = initHerryStoreGrid;
