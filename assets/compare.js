// Before/after slider for .compare blocks: a range input sets how much of the top layer shows;
// .layer-tabs buttons swap which product sits on top.
document.querySelectorAll(".compare").forEach((box) => {
  const range = box.querySelector("input[type=range]");
  const top = box.querySelector(".compare-top img");
  const caption = box.parentElement.querySelector(".layer-caption");
  const set = () => box.style.setProperty("--pos", range.value + "%");
  range.addEventListener("input", set);
  set();
  box.parentElement.querySelectorAll(".layer-tabs button").forEach((btn) => {
    btn.addEventListener("click", () => {
      box.parentElement.querySelectorAll(".layer-tabs button")
        .forEach((b) => b.setAttribute("aria-pressed", String(b === btn)));
      top.src = btn.dataset.src;
      top.alt = btn.dataset.alt;
      if (caption) caption.textContent = btn.dataset.caption;
    });
  });
});
