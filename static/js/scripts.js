document.getElementById('startRecording').addEventListener('click', async function() {
    const employeeId = "12345"; // Replace with dynamic employee ID if needed

    try {
        const response = await fetch('/start-recording', {
            method: 'POST'
        });
        const data = await response.json();
        console.log(data.message);
        document.getElementById('statusMessage').innerText = data.message; // Update status message

        // Wait for 60 seconds before fetching tracking data
        await new Promise(resolve => setTimeout(resolve, 60000));

        // Fetch tracking data after waiting for 60 seconds
        const trackingResponse = await fetch(`/tracking-data/${employeeId}`);
        if (!trackingResponse.ok) {
            throw new Error('Failed to fetch tracking data');
        }
        const trackingData = await trackingResponse.json();
        const absentTime = trackingData.total_absent_time;
        const phoneUsageTime = trackingData.total_phone_usage_time;

        // Display tracking data on UI
        document.getElementById('statusMessage').innerText += `\nTotal Absent Time: ${absentTime} seconds`;
        document.getElementById('statusMessage').innerText += `\nTotal Phone Usage Time: ${phoneUsageTime} seconds`;
    } catch (error) {
        console.error('Error:', error);
        document.getElementById('statusMessage').innerText += '\nError fetching tracking data.';
    }
});
