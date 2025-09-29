function updateSliderDisplay(slider) {
  const display = document.getElementById(slider.dataset.display);
  const precision = slider.step.toString().split('.')[1].length
  display.textContent = `${parseFloat(slider.value).toFixed(precision)}`;
}

function dynamicSliderDisplay() {
  document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll('input[type="range"][data-display]').forEach(slider => {
      updateSliderDisplay(slider);

      slider.addEventListener('input', () => {
        updateSliderDisplay(slider);
      });
    });
  });
}

function getSplittableSliders(name) {
  return {
    combinedContainer: document.getElementById(`${name}-combined-container`),
    separatedContainer: document.getElementById(`${name}-separated-container`),

    combinedSlider: document.getElementById(`${name}-slider`),
    xSlider: document.getElementById(`${name}-x-slider`),
    ySlider: document.getElementById(`${name}-y-slider`),
  };
}

function splitSliders(sliderSplitter, splittableSlider) {
  sliderSplitter.addEventListener("change", function() {
    if (this.checked) {
      splittableSlider.combinedContainer.style.display = "none";
      splittableSlider.xSlider.value = splittableSlider.combinedSlider.value
      splittableSlider.ySlider.value = splittableSlider.combinedSlider.value
      updateSliderDisplay(splittableSlider.xSlider);
      updateSliderDisplay(splittableSlider.ySlider);
      splittableSlider.separatedContainer.style.display = "block";
    } else {
      splittableSlider.combinedSlider.value = (+splittableSlider.xSlider.value + +splittableSlider.ySlider.value) / 2;
      splittableSlider.xSlider.value = "";
      splittableSlider.ySlider.value = "";
      
      updateSliderDisplay(splittableSlider.combinedSlider);
      splittableSlider.combinedContainer.style.display = "block";
      splittableSlider.separatedContainer.style.display = "none";
    }
  });
}

const spacingSliders = getSplittableSliders("spacing");
const spacingSliderSplitter = document.getElementById(`separate-spacing`);

const bleedSliders = getSplittableSliders("bleed");
const bleedSliderSplitter = document.getElementById(`separate-bleed`);

splitSliders(spacingSliderSplitter, spacingSliders);
splitSliders(bleedSliderSplitter, bleedSliders);

dynamicSliderDisplay();
