// Dummy data - Replace with actual data from your Flask backend
const rankTitle = "Current Rank: Sustainability Starter";
const currentPoints = 3;
const bonusPoints = "+7 until next rank";

// Update content dynamically
document.getElementById("rank-title").textContent = rankTitle;
document.getElementById("current-points").textContent = currentPoints;
document.getElementById("bonus-points").textContent = bonusPoints;
document.getElementById("total-points").textContent = `Total points: ${currentPoints}`;
