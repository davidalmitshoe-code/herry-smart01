const products = [

{
name:"Eye Gelass",
price:1000,
image:"images/eyegalss_a.jpg"
},

{
name:"iPhone 14 pro max",
price:650,
image:"images/iphone14.jpg"
},

{
name:"phone suction stickers",
price:300,
image:"images/phone.jpg"
},

{
name:"New Stylish EyeGlasses",
price:1000,
image:"images/eye_galss_b.jpg"
},

{
name:"New Stylish EyeGlasses",
price:1000,
image:"images/eyegalssd.jpg"
},

{
name:"New Stylish EyeGlasses",
price:1000,
image:"images/eyegalssc.jpg"
},

{
name:"Galaxy a56",
price:899,
image:"images/galaxya56.jpg"
},

{
name:"Galaxy S23",
price:899,
image:"images/galaxys23.jpg"
},

{
name:"Galaxy 12 pro",
price:899,
image:"images/galxy12pro.jpg"
},

{
name:"iphone 11",
price:999,
image:"images/iphone11.jpg"
},

{
name:"galaxy cover",
price:1000,
image:"images/galaxy.jpg"
}

];

let cart = [];
let total = 0;

const productsDiv =
document.getElementById("products");

products.forEach(product=>{

const div=document.createElement("div");

div.className="product";

div.innerHTML=`
<img src="${product.image}">
<h3>${product.name}</h3>
<p>${product.price} ETB</p>

<button>
Add To Cart
</button>
`;

div.querySelector("button")
.addEventListener("click",()=>{

cart.push(product);

total += product.price;

document.getElementById("total")
.innerText = total;

const li=document.createElement("li");

li.innerText=
`${product.name} - ${product.price}`;

document.getElementById("cart")
.appendChild(li);

});

productsDiv.appendChild(div);

});

document.getElementById("orderBtn")
.addEventListener("click",()=>{

const tg = window.Telegram.WebApp;

tg.sendData(JSON.stringify({
cart,
total
}));

});