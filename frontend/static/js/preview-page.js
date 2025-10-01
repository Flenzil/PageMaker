function drawCards() {

  const canvas = document.getElementById("preview");
  const ctx = canvas.getContext("2d");
  ctx.clearRect(0, 0, canvas.width, canvas.height);

  const pageWidth = +canvas.getBoundingClientRect().width;
  const pageHeight = +canvas.getBoundingClientRect().height;

  const PixelsPerMm = pageWidth / 210;
  const MmPerPixel = 210 / pageWidth;

  const spacing = +document.getElementById("spacing-slider").value * PixelsPerMm;
  const bleed = +document.getElementById("bleed-slider").value * PixelsPerMm;

  const cardWidth = 63 * PixelsPerMm;
  const cardHeight = 89 * PixelsPerMm;

  const cardWidthWithBleed = cardWidth + 2 * bleed;
  const cardHeightWithBleed = cardHeight + 2 * bleed;

  const totalWidth = 3 * cardWidthWithBleed + 2 * spacing;
  const totalHeight = 3 * cardHeightWithBleed + 2 * spacing;

  const marginXBleed = (pageWidth - totalWidth) / 2 + bleed /2;
  const marginYBleed = (pageHeight - totalHeight) / 2 + bleed / 2;

  const marginX = marginXBleed + bleed;
  const marginY = marginYBleed + bleed;

  console.log(pageWidth);

  ctx.beginPath();

  for (let i = 0; i < 3; i++){
    for (let j = 0; j < 3; j++){
      ctx.rect(
        marginXBleed + i * (cardWidthWithBleed + spacing),
        marginYBleed + j * (cardHeightWithBleed + spacing),
        cardWidthWithBleed,
        cardHeightWithBleed
      );
      ctx.rect(
        marginX + i * (cardWidthWithBleed + spacing),
        marginY + j * (cardHeightWithBleed + spacing),
        cardWidth,
        cardHeight
      );
    }
  }
  ctx.stroke();
}


function resizeCanvas() {
  const canvas = document.querySelector("#preview");
  const rect = canvas.getBoundingClientRect();
  const dpr = window.devicePixelRatio || 1;

  const width = Math.min(canvas.clientWidth, window.innerWidth);
  const height = Math.min(canvas.clientHeight, window.innerHeight);

  canvas.style.width = width + "px";
  canvas.style.height = height + "px";

  // Set the canvas pixel size to match its CSS size * devicePixelRatio
  canvas.width = rect.width * dpr;
  canvas.height = rect.height * dpr;

  const ctx = canvas.getContext("2d");
  ctx.resetTransform && ctx.resetTransform();
  ctx.scale(dpr, dpr);  // scale drawings so 1 unit = 1 CSS pixel

  drawCards();
}

// Call once at load and again if the window resizes
document.addEventListener("DOMContentLoaded", () => {
  resizeCanvas();
});

window.addEventListener("resize", resizeCanvas);

document.getElementById("spacing-slider").addEventListener("input", drawCards);
document.getElementById("bleed-slider").addEventListener("input", drawCards);
