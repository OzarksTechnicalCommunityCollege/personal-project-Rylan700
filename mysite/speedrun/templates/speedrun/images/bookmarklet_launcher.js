
// added this to prove understanding
// (function(){
//     if(!window.bookmarklet){
//         bookmarklet_js = document.body.appendChild(document.createElement('script'));
//         bookmarklet_js.src =  '//127.0.0.1:8000/static/js/bookmarklet.js?r='+Math.floor(Math.random()*9999999999999999);
//         window.bookmarklet = true
//     }
//     else{
//         bookmarkletLaunch();
//     }
// })();


// function bookmarkletLaunch() {
//   bookmarklet = document.getElementById('bookmarklet');
//   var imagesFound = bookmarklet.querySelector('.images');
//   // clear images found
//   imagesFound.innerHTML = '';
//   // display bookmarklet
//   bookmarklet.style.display = 'block';
//   // close event
//   bookmarklet.querySelector('#close')
//              .addEventListener('click', function(){
//                bookmarklet.style.display = 'none'
//              });
//   // find images in the DOM with the minimum dimensions
//   images = document.querySelectorAll('img[src$=".jpg"], img[src$=".jpeg"], img[src$=".png"]');
//   images.forEach(image => {
//     if(image.naturalWidth >= minWidth
//        && image.naturalHeight >= minHeight)
//     {
//       var imageFound = document.createElement('img');
//       imageFound.src = image.src;
//       imagesFound.append(imageFound);
//     }
//   })
// }
// // launch the bookmkarklet
// bookmarkletLaunch();
