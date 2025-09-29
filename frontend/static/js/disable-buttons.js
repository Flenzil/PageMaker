function linkCheckboxes(dependantId, controllerId, reverse = false) {
  // Disable dependant checkbox if controller checkbox is ticked.
  // If reverse is true, disable dependant checkbox unless controller checkbox is ticked.
  //
  const dependant = document.getElementById(dependantId);
  const dependantContainer = document.getElementById(`${dependantId}-container`);

  const controller = document.getElementById(controllerId);

  const updateState = () => {
    const shouldDisable = reverse ? !controller.checked : controller.checked;
    dependant.disabled = shouldDisable;
    dependantContainer.classList.toggle("muted", shouldDisable);
  };

  updateState();

  controller.addEventListener("change", updateState);
}

linkCheckboxes("never-use-bleed", "always-use-bleed");
linkCheckboxes("always-use-bleed", "never-use-bleed");
linkCheckboxes("collate-back-pages", "save-as-pdf", true);
