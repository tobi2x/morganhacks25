// static/script.js

// 1) Handle profile form submission (on index.html)
const profileForm = document.getElementById('profile-form');
if (profileForm) {
  profileForm.addEventListener('submit', async function(e) {
    e.preventDefault();
    const profile = {
      first_name: document.getElementById('fname').value,
      last_name:  document.getElementById('lname').value,
      email:      document.getElementById('email').value,
      career_goals: document.getElementById('career').value,
      lifestyle:  document.getElementById('lifestyle').value,
    };
    const res = await fetch('/save_profile', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(profile),
    });
    const data = await res.json();
    if (data.message) alert(data.message);
  });
}

// 2) Handle community post form submission (on community.html)
const postForm = document.getElementById('post-form');
if (postForm) {
  postForm.addEventListener('submit', async function(e) {
    e.preventDefault();
    const content = document.getElementById('content').value;
    await fetch('/post', {
      method: 'POST',
      body: new URLSearchParams({ content })
    });
    window.location.reload();  // refresh to show new post
  });
}

// 3) Send user message to Flask /chat and display conversation
async function sendMessage() {
  const inputEl = document.getElementById('user-input');
  const chatWindow = document.getElementById('chat-window');
  const userMessage = inputEl.value.trim();
  if (!userMessage) return;

  // Show user message immediately
  addMessage(userMessage, 'user');
  inputEl.value = '';

  // Call backend
  try {
    const res = await fetch('/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: userMessage })
    });
    const data = await res.json();
    if (data.reply) {
      addMessage(data.reply, 'bot');
    } else {
      addMessage('Sorry, something went wrong on the server.', 'bot');
    }
  } catch (err) {
    console.error(err);
    addMessage('Network error — please check your connection.', 'bot');
  }
}

// 4) Utility to append a message bubble
function addMessage(text, sender) {
  const chatWindow = document.getElementById('chat-window');
  const container = document.createElement('div');
  container.classList.add('container', sender);

  const messageP = document.createElement('p');
  messageP.textContent = text;

  const timeSpan = document.createElement('span');
  timeSpan.classList.add(sender === 'user' ? 'time-right' : 'time-left');
  timeSpan.textContent = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

  container.appendChild(messageP);
  container.appendChild(timeSpan);
  chatWindow.appendChild(container);

  // auto-scroll
  chatWindow.scrollTop = chatWindow.scrollHeight;
}

// 5) Wire up any <button onclick="sendMessage()"> to also use our function
document.querySelectorAll('button[onclick="sendMessage()"]').forEach(btn =>
  btn.addEventListener('click', sendMessage)
);



// // Function to send user message and get Gemini's response
// async function sendMessage() {
//     const userMessage = document.getElementById('user-input').value;

//     if (userMessage.trim() === "") return;

//     // Add user message to chat
//     addMessage(userMessage, 'user');

//     // Send the message to the Flask backend and get the response
//     const response = await fetch('http://localhost:5500/get_gemini_response', {
//         method: 'POST',
//         headers: {
//             'Content-Type': 'application/json',
//         },
//         body: JSON.stringify({ message: userMessage }),
//     });

//     const data = await response.json();

//     if (data.response) {
//         addMessage(data.response, 'gemini');
//     } else {
//         addMessage("Sorry, there was an error. Please try again.", 'gemini');
//     }

//     // Clear the input field after sending the message
//     document.getElementById('user-input').value = '';
// }

// // Function to add a message to the chat box
// function addMessage(message, sender) {
//     const messageContainer = document.createElement('div');
//     messageContainer.classList.add('container', sender);

//     // const avatar = document.createElement('img');
//     // avatar.src = sender === 'user' ? '/w3images/bandmember.jpg' : '/w3images/avatar_g2.jpg';
//     // avatar.alt = 'Avatar';

//     const messageText = document.createElement('p');
//     messageText.textContent = message;

//     const time = document.createElement('span');
//     time.classList.add(sender === 'user' ? 'time-right' : 'time-left');
//     // time.textContent = new Date().toLocaleTimeString();
    
//     // changing to hours and minutes only
//     const options = { hour: '2-digit', minute: '2-digit' };
//     time.textContent = new Date().toLocaleTimeString([], options);


//     // messageContainer.appendChild(avatar);
//     messageContainer.appendChild(messageText);
//     messageContainer.appendChild(time);
    
//     document.getElementById('chat-box').appendChild(messageContainer);
    
//     // Auto-scroll to the latest message
//     document.getElementById('chat-box').scrollTop = document.getElementById('chat-box').scrollHeight;
// }
