function pageSizeInMm(pageSize) {
  const pageWidths = { "a": 210, "b": 250, "c": 229 };
  const series = pageSize[0].toLowerCase();
  const stepFromBase = 4 - parseInt(pageSize[1]);
  const pageWidthInMm = Math.round(pageWidths[series] * Math.pow(Math.pow(2, 0.5), stepFromBase));
  const pageHeightInMm = Math.round(Math.sqrt(2) * pageWidthInMm);


  return {
    pageWidthInMm: pageWidthInMm,
    pageHeightInMm: pageHeightInMm
  };
}

function drawCards() {

  const grid = document.getElementById("preview");
  grid.innerHTML = "";

  const page = document.getElementById("preview");

  const pageSize = document.getElementById("page-size").value;

  const { pageWidthInMm, pageHeightInMm } = pageSizeInMm(pageSize);

  console.log(pageWidthInMm, pageHeightInMm);

  const pageWidth = +page.clientWidth;
  const pageHeight = +page.clientHeight;

  const PixelsPerMm = pageHeight / pageHeightInMm;
  const MmPerPixel = pageWidthInMm / pageWidth;

  const spacing = +document.getElementById("spacing-slider").value * PixelsPerMm;
  const neverUseBleed = document.getElementById("never-use-bleed");
  let bleed = +document.getElementById("bleed-slider").value * PixelsPerMm;


  if (neverUseBleed.checked) {
    bleed = 0;
  }

  const cardWidth = 63 * PixelsPerMm;
  const cardHeight = 89 * PixelsPerMm;

  const cardWidthWithBleed = cardWidth + 2 * bleed;
  const cardHeightWithBleed = cardHeight + 2 * bleed;

  const cols = Math.floor(pageWidth / (cardWidthWithBleed + spacing));
  const rows = Math.floor(pageHeight / (cardHeightWithBleed + spacing));

  const totalWidth = cols * cardWidthWithBleed + (cols - 1) * spacing;
  const totalHeight = rows * cardHeightWithBleed + (rows - 1) * spacing;

  const marginXBleed = (pageWidth - totalWidth) / 2;
  const marginYBleed = (pageHeight - totalHeight) / 2;


  for (let i = 0; i < cols; i++) {
    for (let j = 0; j < rows; j++) {
      const x = marginXBleed + i * (cardWidthWithBleed + spacing);
      const y = marginYBleed + j * (cardHeightWithBleed + spacing);

      const cardContainer = document.createElement("div");
      cardContainer.className = "card-container";
      cardContainer.style.left = x + "px";
      cardContainer.style.top = y + "px";
      cardContainer.style.width = cardWidthWithBleed + "px";
      cardContainer.style.height = cardHeightWithBleed + "px";

      const bleedDiv = document.createElement("div");
      bleedDiv.className = "card-bleed";
      bleedDiv.style.width = cardWidthWithBleed + "px";
      bleedDiv.style.height = cardHeightWithBleed + "px";

      const cardDiv = document.createElement("div");
      cardDiv.className = "card";
      cardDiv.img
      cardDiv.style.width = cardWidth + "px";
      cardDiv.style.height = cardHeight + "px";
      cardDiv.style.margin = bleed + "px";

      const cardImg = document.createElement("img");
      cardImg.src = 'static/vma-4-black-lotus.png';
      cardImg.className = "card-image";


      cardDiv.appendChild(cardImg);
      bleedDiv.appendChild(cardDiv);
      cardContainer.appendChild(bleedDiv);
      grid.appendChild(cardContainer);

    }
  }
}


window.addEventListener("resize", drawCards);
document.getElementById("spacing-slider").addEventListener("input", drawCards);
document.getElementById("bleed-slider").addEventListener("input", drawCards);
document.getElementById("never-use-bleed").addEventListener("change", drawCards);
document.getElementById("page-size").addEventListener("change", drawCards);
document.addEventListener("DOMContentLoaded", drawCards);
