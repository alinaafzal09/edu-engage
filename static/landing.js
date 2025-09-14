window.addEventListener('DOMContentLoaded', () => {
  const logo = document.getElementById('logo');
  const welcomeText = document.getElementById('welcome-text');
  const loginBtn = document.getElementById('login-btn');

  // Step 1: after 5 sec, blur out logo
  setTimeout(() => {
    logo.style.opacity = '0';
    logo.style.filter = 'blur(5px)';
  }, 5000);

  // Step 2: show welcome text after logo fades
  setTimeout(() => {
    welcomeText.style.opacity = '1';
  }, 6000);

  // Step 3: show login button
  setTimeout(() => {
    loginBtn.style.opacity = '1';
  }, 7000);
});

