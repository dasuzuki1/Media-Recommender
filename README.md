<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Media Recommendation System</title>
    <link rel="stylesheet" href="styles.css"> <!-- Link to your CSS -->
    <!-- Add external font -->
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700&display=swap" rel="stylesheet">
    <style>
        body {
            font-family: 'Roboto', sans-serif;
            margin: 0;
            padding: 0;
            background-color: #f5f5f5;
            color: #333;
        }
        header {
            background-color: #6200ea;
            color: white;
            padding: 1rem 2rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        header h1 {
            margin: 0;
            font-size: 1.5rem;
        }
        nav {
            display: flex;
            gap: 1rem;
        }
        nav a {
            color: white;
            text-decoration: none;
            font-weight: 500;
        }
        nav a:hover {
            text-decoration: underline;
        }
        main {
            padding: 2rem;
        }
        .section {
            margin-bottom: 2rem;
        }
        .section h2 {
            font-size: 1.75rem;
            margin-bottom: 0.5rem;
        }
        .button {
            background-color: #6200ea;
            color: white;
            padding: 0.5rem 1rem;
            border: none;
            border-radius: 4px;
            font-size: 1rem;
            cursor: pointer;
        }
        .button:hover {
            background-color: #3700b3;
        }
        .card {
            background-color: white;
            border-radius: 8px;
            padding: 1rem;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            margin-bottom: 1rem;
        }
        footer {
            background-color: #333;
            color: white;
            text-align: center;
            padding: 1rem;
            margin-top: 2rem;
        }
    </style>
</head>
<body>
    <header>
        <h1>Media Recommendation System</h1>
        <nav>
            <a href="#home">Home</a>
            <a href="#features">Features</a>
            <a href="#about">About</a>
        </nav>
    </header>
    <main>
        <section id="home" class="section">
            <h2>Welcome to Media Recommendation System</h2>
            <p>Discover personalized anime recommendations based on your preferences. Login to get started.</p>
            <button class="button">Login with AniList</button>
        </section>
        <section id="features" class="section">
            <h2>Features</h2>
            <div class="card">
                <h3>Personalized Recommendations</h3>
                <p>Using advanced algorithms, we deliver tailored anime recommendations just for you.</p>
            </div>
            <div class="card">
                <h3>User-Friendly Interface</h3>
                <p>Navigate easily through your dashboard and explore recommendations with a clean UI.</p>
            </div>
            <div class="card">
                <h3>Data-Driven Insights</h3>
                <p>Analyze user preferences and trends to discover what you love.</p>
            </div>
        </section>
        <section id="about" class="section">
            <h2>About</h2>
            <p>This project integrates the AniList API and utilizes machine learning for recommendation generation. It’s built with Python, Flask, and modern web development practices.</p>
        </section>
    </main>
    <footer>
        <p>&copy; 2025 Media Recommendation System. All rights reserved.</p>
    </footer>
</body>
</html>
