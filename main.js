const products = [

{
name:"Eye Gelass",
price:1000,
image:"eyegalss_a.jpg"
},

{
name:"iPhone 14 pro max",
price:650,
image:"iphone14.jpg"
},

{
name:"phone suction stickers",
price:300,
image:"phone.jpg"
},

{
name:"New Stylish EyeGlasses",
price:1000,
image:"eye_galss_b.jpg"
},

{
name:"New Stylish EyeGlasses",
price:1000,
image:"eyegalssd.jpg"
},

{
name:"New Stylish EyeGlasses",
price:1000,
image:"eyegalssc.jpg"
},

{
name:"Galaxy a56",
price:899,
image:"galaxya56.jpg"
},

{
name:"Galaxy S23",
price:899,
image:"galaxys23.jpg"
},

{
name:"Galaxy 12 pro",
price:899,
image:"galxy12pro.jpg"
},

{
name:"iphone 11",
price:999,
image:"iphone11.jpg"
},

{
name:"galaxy cover",
price:1000,
image:"galaxy.jpg"
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

  document.getElementById("orderBtn")
.addEventListener("click",()=>{

const tg = window.Telegram.WebApp;

tg.sendData(JSON.stringify({
cart,
total
}));

});

