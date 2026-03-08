const imgs = document.querySelectorAll('.data_src_img');

imgs.forEach(img => {
  img.src = img.dataset.src;
});
