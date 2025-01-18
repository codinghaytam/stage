const button = document.querySelector("#menu-button");
const button2 = document.querySelector("#menu-button2");

const sidebar = document.querySelector(".sidebar");

function draw(timePassed) {
  sidebar.style.left = -timePassed / 5 + 'px';
}
button.addEventListener("click",(e)=>{
    sidebar.style.display = "flex"
     sidebar.style.transform ="translateX(0px)";
    sidebar.style.transitionDuration = "1s";

});

button2.addEventListener("click",()=>{
    sidebar.style.transform ="translateX(-300px)";
    sidebar.style.transitionDuration = "1s";


});