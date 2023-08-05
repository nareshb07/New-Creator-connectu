const messageInput = document.getElementById('message_input');
const submitButton = document.getElementById('chat-message-submit');





messageInput.addEventListener('keypress', function(event) {
    if (event.key === 'Enter') {
        console.log("entered ")
        event.preventDefault(); // Prevent the default form submission

        // Trigger the submit button click event
        submitButton.click();
    }
});



const fileInput = document.getElementById('fileInput');
const fileNameElement = document.getElementById('file-name');

const chatMessageSubmit = document.getElementById('chat-message-submit');



// Add event listener for change event on the file input
fileInput.addEventListener('change', function() {
  // Check if a file is selected
  if (fileInput.files.length > 0) {
    const fileName = fileInput.files[0].name;
    fileNameElement.classList.remove("hidden")
    fileNameElement.textContent = fileName;
    
  }
});






