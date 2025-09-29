const darkModeButton = document.getElementById('dark-mode');

function updateDarkMode(){
  const darkModeOn = darkModeButton.checked;
  document.documentElement.classList.toggle('dark-mode', darkModeOn);
  localStorage.setItem("dark-mode", darkModeOn);
  document.cookie = "dark_mode=" + darkModeOn + "; path=/; max-age=31536000";
};

updateDarkMode();
darkModeButton.addEventListener("change", updateDarkMode);


