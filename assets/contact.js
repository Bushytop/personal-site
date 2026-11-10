// Address is assembled here so it never appears in page source for scrapers.
document.querySelectorAll("a.email").forEach(function (a) {
  var addr = a.dataset.u + "@" + a.dataset.d;
  a.href = "mailto:" + addr;
  if (a.textContent.trim() === "email") a.textContent = addr;
});
