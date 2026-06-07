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

// Cart structured as an object to handle item quantities properly
let cart = {}; 
let total = 0;

const productsDiv = document.getElementById("products");

// 1. Render Products to UI
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
    // If item already exists in cart, increase quantity, otherwise initialize it
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
    updateCartUI();
  });

  productsDiv.appendChild(div);
});

// 2. Refresh and Render Cart List Layout
function updateCartUI() {
  // Update total price element
  document.getElementById("total").innerText = total;
  
  const cartList = document.getElementById("cart");
  cartList.innerHTML = ""; // Clear existing UI list elements safely

  // Loop through grouped cart items
  Object.values(cart).forEach(item => {
    const li = document.createElement("li");
    li.innerText = `${item.name} (x${item.quantity}) — ${item.price * item.quantity} ETB`;
    cartList.appendChild(li);
  });
}

// 3. Dispatch Formatted Order Packet back to Flask Bot Server
document.getElementById("orderBtn").addEventListener("click", () => {
  const tg = window.Telegram.WebApp;

  // Convert our cart object into a clean array for your Python backend loop
  const finalizedCartArray = Object.values(cart);

  if (finalizedCartArray.length === 0) {
    tg.showAlert("Your cart is empty! Please add some items first. 🛒");
    return;
  }

  // Safely stringify and pass directly to your telegram bot environment
  tg.sendData(JSON.stringify({
    cart: finalizedCartArray,
    total: total
  }));
  
  // Close the Mini App window automatically after submission
  tg.close();
});
