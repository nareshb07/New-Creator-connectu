const id = JSON.parse(document.getElementById('json-username').textContent);
const message_username = JSON.parse(document.getElementById('json-message-username').textContent);
const receiver = JSON.parse(document.getElementById('json-username-receiver').textContent);

const socket = new WebSocket(
  'ws://' + window.location.host + '/ws/' + id + '/'
);

socket.onopen = function() {
  console.log("CONNECTION ESTABLISHED");
};

socket.onclose = function() {
  console.log("CONNECTION LOST");
};

socket.onerror = function() {
  console.log("ERROR OCCURRED");
};

function escapeHTML(html) {
  return document.createElement('div').appendChild(document.createTextNode(html)).parentNode.innerHTML;
}


document.querySelector('#chat-message-submit').onclick = function() {
  const messageInput = document.querySelector('#message_input');
  const fileInput = document.querySelector('#fileInput');
  const fileNameElement = document.getElementById('file-name');
 
  const message = messageInput.value;
  const file = fileInput.files[0];

  // Check if message input or file is not empty
  if (message.trim() !== '' || file) {
    const formData = new FormData();

    if (file) {
      formData.append('fileInput', file);
      
      fetch(`/chat/${id}/`, {
        method: 'POST',
        body: formData
      })
        .then(response => response.json())
        .then(data => {
          if (data.success) {
            socket.send(JSON.stringify({
              'file_url': data.file_url,
              'file_name': data.file_name,
              'message': message,
              'username': message_username,
              'receiver': receiver,
            }));
            fileInput.value = '';
            fileNameElement.classList.add("hidden")
            console.log("File uploaded successfully:", data.file_url);
          } else {
            fileInput.value = '';
            fileNameElement.classList.add("hidden")
            const message = document.querySelector('#message-body');

            // Create a new div element
            const newElement = document.createElement("div");
            newElement.className = "bg-black h-10 min-w-full absolute bottom-20 text-white py-2 px-4";
            newElement.innerHTML = data.message;

            // Append the new element to the message container
            message.appendChild(newElement);

            // Hide the element after 5 seconds (5000 milliseconds)
            setTimeout(function() {
            newElement.style.display = "none";
            }, 2000);

            console.log("File upload failed:", data.message);

          }
        })
        .catch(error => {
          console.log("An error occurred during file upload:", error);
        });
    } else {
      socket.send(JSON.stringify({
        'message': message,
        'username': message_username,
        'receiver': receiver
      }));
    }

    messageInput.value = '';
  }
};

socket.onmessage = function(event) {
  const data = JSON.parse(event.data);

  const chatBody = document.querySelector('#chat-body');
  const escapedMessage = escapeHTML(data.message);

  if (data.file_url) {
    const isSender = data.username === message_username;
    const svg_bg = isSender ? '#7dd3fc' : '#020617';
    let content;

    if (data.file_name.toLowerCase().match(/\.(jpg|jpeg|png)$/i)) {
        content = `<img class="object-cover max-w-[15rem] max-h-[16rem]  rounded-2xl sm:max-w-md" alt="image" src="${data.file_url}">`;
    } else if (data.file_name.toLowerCase().match(/\.(mp4|avi|mov)$/i)) { 
      
    const fileExtension = data.file_name.split('.').pop().toLowerCase();

    // Map the file extension to the corresponding MIME type
  let fileType;
  switch (fileExtension) {
      case 'mp4':
          fileType = 'video/mp4';
          break;
      case 'avi':
          fileType = 'video/x-msvideo';
          break;
      case 'mov':
          fileType = 'video/quicktime';
          break;
      default:
          fileType = ''; // Set an empty string if the file type is unknown
          break;
  }

    content = `<video class = " rounded-2xl max-w-xs max-h-xs sm:max-h-md sm:max-w-md bg-white" controls>
    <source src="${data.file_url}" type="${fileType}" >
    Your browser does not support the video tag.
    </video>`;
    } else if (data.file_name.toLowerCase().match(/\.(pdf|doc|docx)$/i)) {
        content = `<a href="${data.file_url}" target="_blank"><svg xmlns="http://www.w3.org/2000/svg" class="h-16 w-16 pt-10" viewBox="0 0 384 512"><path fill = '${svg_bg}' d="M0 64C0 28.7 28.7 0 64 0H224V128c0 17.7 14.3 32 32 32H384V448c0 35.3-28.7 64-64 64H64c-35.3 0-64-28.7-64-64V64zm384 64H256V0L384 128z"/></svg>${data.file_name}</a>`;
    } else if (data.file_name.toLowerCase().match(/\.(mp3|ogg)$/i)) {

    const fileExtension = data.file_name.split('.').pop().toLowerCase();

      // Map the file extension to the corresponding MIME type
    let fileType;
    switch (fileExtension) {
        case 'mp3':
            fileType = 'audio/mpeg';
            break;
        case 'ogg':
            fileType = 'audio/ogg';
            break;
        default:
            fileType = ''; // Set an empty string if the file type is unknown
            break;
    }
      content = ` <audio controls>
                    <source src="${data.file_url}" type="${fileType}">
                    Your browser does not support the audio tag.
                  </audio> `;
  } 
    else {
        content = `<a href="${data.file_url}" target="_blank"><svg xmlns="http://www.w3.org/2000/svg" class="h-16 w-16 pt-10" viewBox="0 0 384 512"><path fill = '${svg_bg}' d="M0 64C0 28.7 28.7 0 64 0H224V128c0 17.7 14.3 32 32 32H384V448c0 35.3-28.7 64-64 64H64c-35.3 0-64-28.7-64-64V64zm384 64H256V0L384 128z"/></svg>${data.file_name}</a>`;
    }

    
    const messageClass = isSender ?  'hover:bg-slate-950 bg-slate-900 text-sky-200 hover:text-sky-300' : 'hover:bg-sky-300 bg-sky-200 text-slate-900 hover:text-slate-950';
    const messageFloat = isSender ?  'flex justify-end mb-5 mr-5' :'flex justify-start mb-5 ml-5';
    const timeFloat = isSender ?  'justify-end' : '';

    const messageHTML = ` <div class="${messageFloat}">
                              <div class="flex flex-col max-w-[75%]">
                              <div class="${messageClass}  rounded-2xl ">${content}</div>
                              <code class="flex ${timeFloat} mr-5 text-[80%]  text-white"> just now </code>
                            </div>
                          </div>;`
    
    chatBody.innerHTML += messageHTML;
} else {
  
  
  if (data.username === message_username) {
    chatBody.innerHTML += `<div class="flex justify-end mb-5 ">
                            <div class="flex flex-col max-w-[80%]">
                              <p class="mr-6 rounded-s-3xl rounded-br-lg rounded-tr-3xl hover:bg-slate-950 hover:text-sky-300 bg-slate-900 px-4 py-2 text-sky-200">${escapedMessage}</p>
                              <code class="flex justify-end mr-8 text-[80%]  text-white">just now</code>
                            </div>
                          </div>`;

  } else {
    chatBody.innerHTML += `<div class="flex justify-start mb-5 ">
                            <div class= "flex flex-col max-w-[80%]">
                              <p class=" ml-6 rounded-e-3xl rounded-bl-lg rounded-tl-3xl hover:text-slate-900 hover:bg-sky-300 bg-sky-200 px-4 py-2 text-base text-slate-900">${escapedMessage}</p>
                              <code class="text-[80%] flex  ml-8 text-white">just now</code>
                            </div>
                          </div>`;
  }
};


const fileNameElement = document.getElementById('file-name');
const fileInput = document.getElementById('fileInput');
fileInput.addEventListener('change', function() {
  // Check if a file is selected
  if (fileInput.files.length > 0) {
    const fileName = fileInput.files[0].name;
    fileNameElement.classList.remove("hidden")
    fileNameElement.textContent = fileName;
    
  
}})};

