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

dynamicSliderDisplay();
