async function login(event) {
    event.preventDefault();
    const email = document.getElementById('login-email').value;
    const password = document.getElementById('login-password').value;
  
    const res = await fetch('/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: new URLSearchParams({ email, password })
    });
    const data = await res.json();
    if (data.message) {
      alert(data.message);
      window.location.href = "/profile"; // redirect to profile for more info
    } else {
      alert(data.error);
    }
  }
  
  async function register(event) {
    event.preventDefault();
    const email = document.getElementById('register-email').value;
    const password = document.getElementById('register-password').value;
  
    const res = await fetch('/signup', {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: new URLSearchParams({ email, password })
    });
    const data = await res.json();
    if (data.message) {
      alert(data.message);
      window.location.href = "/"; // redirect to index.html chatbot after signup
    } else {
      alert(data.error);
    }
  }
  