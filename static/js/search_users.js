const searchInput = document.getElementById('searchInput');
const searchResults = document.getElementById('searchResults');
let timeoutId;

searchInput.addEventListener('input', function() {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(() => {
        const searchTerm = searchInput.value;
        if (searchTerm.trim() !== '') {
            fetchSearchResults(searchTerm);
        } else {
            searchResults.innerHTML = '';
        }
    }, 100);
});

function fetchSearchResults(searchTerm) {
    const url = '/search/?search=' + encodeURIComponent(searchTerm);
    fetch(url)
        .then(response => response.json())
        .then(data => {
            let searchResultsHTML = '';
            if (data.length > 0) {
                
                data.forEach(result => {
                    const imageUrl = result.image_url;
                    
                    searchResultsHTML += ` <a href="/Creator_profile/${result.id}">
                                                <li class=" px-4 py-4 rounded-2xl bg-slate-800 text-center hover:bg-slate-700">
                                                <div class="flex flex-row items-center">
                                                    <img src="${imageUrl}" class="ml-5 h-14 w-14 flex-none rounded-full bg-black" />
                                                    <div class="ml-5 text-start text-white">
                                                    <div class="flex flex-row">
                                                    <p class="text-sky-200 flex-none"><b class="text-sky-300 font-bold">${result.first_name} ${result.last_name}</b> @${result.username}</p>
                                                    </div>
                                                    ${result.profession ? `<h1 class = "font-semibold">${result.profession}</h1>`  : ''}
                                                </div>
                                                </div>
                                                </li>
                                                </a>`;
                                            });


                    
                                            
                                                           
                                         
                                  searchResultsHTML += '</ul>';
                                   } else {
                                  searchResultsHTML = '<p>No users found.</p>';
                                  }

                                   searchResults.innerHTML = searchResultsHTML;
                                  })
                                    .catch(error => {
                                  console.error('Error:', error);
                                      });
                                 }

