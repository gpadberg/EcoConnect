document.addEventListener("DOMContentLoaded", function() {
    // Fetch user points from Flask backend
    fetch('/get_points')
        .then(response => response.json())
        .then(data => {
            const userPoints = data.points;

            // Update circle text and bonus points
            document.getElementById('pointsText').innerText = `${userPoints}/10 EcoPoints`;
            document.getElementById('bonusPoints').innerText = `+${10 - userPoints} points to next rank`;
            
            // Update total points
            document.getElementById('totalPoints').innerText = `Total Points: ${userPoints}`;

            // Additional logic, such as updating circle color based on points, can be added here.
        })
        .catch(error => {
            console.error('Error fetching user points:', error);
        });
});
