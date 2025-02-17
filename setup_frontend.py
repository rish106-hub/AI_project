#!/usr/bin/env python3
import os

def create_folders():
    """Creates the frontend folder structure."""
    folders = [
        'frontend',
        os.path.join('frontend', 'static'),
        os.path.join('frontend', 'css'),
        os.path.join('frontend', 'js')
    ]
    for folder in folders:
        if not os.path.exists(folder):
            os.makedirs(folder)
            print(f"Created folder: {folder}")

def create_index_html():
    """Creates the index.html file inside the static folder with complete frontend code."""
    index_path = os.path.join('frontend', 'static', 'index.html')
    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>AI Habit Tracker</title>
  <style>
    body { font-family: Arial, sans-serif; margin: 20px; }
    .container { max-width: 800px; margin: 0 auto; }
    h1, h2 { text-align: center; }
    form { margin-bottom: 20px; text-align: center; }
    input, button { padding: 8px; margin: 5px; }
    ul { list-style-type: none; padding: 0; }
    li { border: 1px solid #ddd; padding: 10px; margin-bottom: 10px; }
    .recommendations { background-color: #f9f9f9; padding: 10px; border: 1px solid #ccc; }
  </style>
</head>
<body>
  <div class="container">
    <h1>AI Habit Tracker</h1>
    
    <section>
      <h2>Create New Habit</h2>
      <form id="createHabitForm">
        <input type="text" id="habitName" placeholder="Habit Name" required>
        <input type="text" id="habitDescription" placeholder="Description">
        <input type="text" id="habitFrequency" placeholder="Frequency (e.g., daily)">
        <input type="text" id="habitCategory" placeholder="Category">
        <button type="submit">Add Habit</button>
      </form>
    </section>
    
    <section>
      <h2>Habit List</h2>
      <ul id="habitList">
        <!-- Habits will be loaded here -->
      </ul>
    </section>
    
    <section>
      <h2>Recommendations</h2>
      <div id="recommendations" class="recommendations">
        <!-- Recommendations will appear here -->
      </div>
    </section>
  </div>
  
  <script>
    // Base URL for API endpoints (adjust if your backend is hosted elsewhere)
    const BASE_URL = '';

    // Fetch and display all habits
    async function fetchHabits() {
      const response = await fetch(`${BASE_URL}/api/habits`);
      const habits = await response.json();
      const habitList = document.getElementById('habitList');
      habitList.innerHTML = '';
      habits.forEach(habit => {
        const li = document.createElement('li');
        li.innerHTML = `<strong>${habit.name}</strong> - ${habit.description} (Category: ${habit.category}, Frequency: ${habit.frequency})
          <button onclick="logHabit(${habit.id})">Log Completion</button>`;
        habitList.appendChild(li);
      });
    }

    // Handle habit creation form submission
    document.getElementById('createHabitForm').addEventListener('submit', async function(event) {
      event.preventDefault();
      const name = document.getElementById('habitName').value;
      const description = document.getElementById('habitDescription').value;
      const frequency = document.getElementById('habitFrequency').value;
      const category = document.getElementById('habitCategory').value;
      
      const response = await fetch(`${BASE_URL}/api/habits`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, description, frequency, category })
      });
      if (response.status === 201) {
        alert('Habit created successfully!');
        fetchHabits();
      } else {
        alert('Error creating habit.');
      }
    });

    // Log habit completion for a given habit
    async function logHabit(habitId) {
      const response = await fetch(`${BASE_URL}/api/habits/${habitId}/log`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status: 'completed' })
      });
      if (response.status === 201) {
        alert('Habit logged successfully!');
        fetchRecommendations();
      } else {
        alert('Error logging habit.');
      }
    }

    // Fetch and display AI recommendations
    async function fetchRecommendations() {
      const response = await fetch(`${BASE_URL}/api/recommendations`);
      const recs = await response.json();
      const recDiv = document.getElementById('recommendations');
      recDiv.innerHTML = '';
      if (recs.length === 0) {
        recDiv.innerHTML = '<p>All habits are up-to-date!</p>';
      } else {
        recs.forEach(rec => {
          const p = document.createElement('p');
          p.textContent = rec.recommendation;
          recDiv.appendChild(p);
        });
      }
    }

    // Initial data fetch
    fetchHabits();
    fetchRecommendations();
  </script>
</body>
</html>
"""
    with open(index_path, "w") as f:
        f.write(html_content)
    print(f"Created index.html in: {index_path}")

def main():
    print("Setting up frontend...")
    create_folders()
    create_index_html()
    print("Frontend setup complete.")

if __name__ == '__main__':
    main()
