document.getElementById('checkStatus').addEventListener('click', function() {
    fetch('/api/check_status')  // Adjust the endpoint as necessary
        .then(response => response.json())
        .then(data => {
            console.log(data);
            // Update the UI based on the response data
        })
        .catch(error => console.error('Error:', error));
});