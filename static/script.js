// static/script.js

// 1) Handle profile form submission (on index.html)
const profileForm = document.getElementById('profile-form');
if (profileForm) {
  profileForm.addEventListener('submit', async function(e) {
    e.preventDefault();
    const profile = {
      username: document.getElementById('user').value,
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

    // — Allow Enter in any profile input to submit the form —
    profileForm.querySelectorAll('input').forEach(inputEl => {
        inputEl.addEventListener('keydown', function(e) {
          if (e.key === 'Enter') {
            e.preventDefault();          // prevent default form behavior
            profileForm.requestSubmit(); // trigger the form's submit handler
          }
        });
      });

}

// 2) Handle community post form submission (on community.html)
const postForm = document.getElementById('post-form');
if (postForm) {
  postForm.addEventListener('submit', async function(e) {
    e.preventDefault();
    const content = document.getElementById('content').value;
    const postAs = document.getElementById('post-as').value;  // <-- grab from post-as not username-select

    await fetch('/post', {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: new URLSearchParams({ content: content, post_as: postAs }) // <-- send post_as not username
    });

    window.location.reload();  // refresh to show new post
  });

  // Allow Enter in the textarea to submit the form too
  const contentEl = document.getElementById('content');
  if (contentEl) {
    contentEl.addEventListener('keydown', function(e) {
      if (e.key === 'Enter') {
        e.preventDefault();        // prevent newline
        postForm.requestSubmit();  // trigger the form's submit handler
      }
    });
  }
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

// Also trigger sendMessage when the user hits Enter in the chat input
const inputEl = document.getElementById('user-input');
if (inputEl) {
  inputEl.addEventListener('keydown', function(e) {
    if (e.key === 'Enter') {
      e.preventDefault();  // prevent any default form submission/reload
      sendMessage();
    }
  });
}

// 6) Load previous chat history on page load
async function loadChatHistory() {
  try {
    const res = await fetch('/chat_history');
    const data = await res.json();
    if (data.messages) {
      // Clear chat window before loading
      document.getElementById('chat-window').innerHTML = '';

      for (const msg of data.messages) {
        addMessage(msg.user, 'user');
        addMessage(msg.bot, 'bot');
      }
    }
  } catch (err) {
    console.error('Error loading chat history:', err);
  }
}

// Auto-load chat history when page loads
window.addEventListener('load', () => {
  loadChatHistory();
});



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
