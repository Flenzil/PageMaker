function updateSliderDisplay(slider) {
  const display = document.getElementById(slider.dataset.display);
  const precision = slider.step.toString().split('.')[1].length
  display.textContent = `${parseFloat(slider.value).toFixed(precision)}`;
}

function getSplittableSlidersInfo() {
  const names = Array.from(document.querySelectorAll('[data-splits]'))
    .map(el => el.getAttribute('data-splits'));


  return names.map(name => ({
    splitter: document.getElementById(`separate-${name}`),

    combinedContainer: document.getElementById(`${name}-combined-container`),
    separatedContainer: document.getElementById(`${name}-separated-container`),

    combinedSlider: document.getElementById(`${name}-slider`),
    xSlider: document.getElementById(`${name}-x-slider`),
    ySlider: document.getElementById(`${name}-y-slider`),
  }));
}


function splitSliders(splittableSlider) {
  function toggleSplit() {
    if (splittableSlider.splitter.checked) {
      splittableSlider.combinedContainer.style.display = "none";
      if (document.readyState === 'complete') {
        splittableSlider.xSlider.value = splittableSlider.combinedSlider.value;
        splittableSlider.ySlider.value = splittableSlider.combinedSlider.value;
        updateSliderDisplay(splittableSlider.xSlider);
        updateSliderDisplay(splittableSlider.ySlider);
      }
      splittableSlider.separatedContainer.style.display = "block";
    } else {
      splittableSlider.combinedContainer.style.display = "block";
      splittableSlider.separatedContainer.style.display = "none";
      if (document.readyState === 'complete') {
        splittableSlider.combinedSlider.value = (+splittableSlider.xSlider.value + +splittableSlider.ySlider.value) / 2;
        splittableSlider.xSlider.value = "";
        splittableSlider.ySlider.value = "";

        updateSliderDisplay(splittableSlider.combinedSlider);
      }
    }
  }

  toggleSplit();
  splittableSlider.splitter.addEventListener("change", toggleSplit);
}

getSplittableSlidersInfo()
  .forEach((splittableSlider) => {
    splitSliders(splittableSlider);
  })

