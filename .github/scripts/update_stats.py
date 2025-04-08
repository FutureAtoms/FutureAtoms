#!/usr/bin/env python3
"""
GitHub Profile README Updater Script
This script automatically updates your GitHub profile with the latest statistics,
achievements, and contributions.
"""

import os
import re
import json
import datetime
import requests
from github import Github

# Configuration
GITHUB_USERNAME = "FutureAtoms"
README_PATH = "README.md"

def get_github_stats():
    """Fetch GitHub statistics using the GitHub API."""
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        print("No GitHub token found. Using unauthenticated requests.")
        g = Github()
    else:
        g = Github(token)
    
    user = g.get_user(GITHUB_USERNAME)
    
    # Basic user stats
    stats = {
        "name": user.name or GITHUB_USERNAME,
        "followers": user.followers,
        "following": user.following,
        "public_repos": user.public_repos,
        "contributions_last_year": get_contributions_count(GITHUB_USERNAME),
        "stars_received": get_stars_received(g, GITHUB_USERNAME),
        "top_languages": get_top_languages(g, GITHUB_USERNAME),
        "achievements": generate_achievements(user),
    }
    
    return stats

def get_contributions_count(username):
    """Get the total number of contributions in the last year."""
    headers = {"Accept": "application/vnd.github.v3+json"}
    today = datetime.date.today()
    last_year = today - datetime.timedelta(days=365)
    
    url = f"https://api.github.com/users/{username}/events"
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        return 0
    
    # This is a simplified version - the real count would require more complex calculation
    # through GraphQL API which requires authentication
    return len(response.json())

def get_stars_received(g, username):
    """Count stars received across all repositories."""
    try:
        stars = 0
        for repo in g.get_user(username).get_repos():
            stars += repo.stargazers_count
        return stars
    except Exception as e:
        print(f"Error getting stars: {e}")
        return 0

def get_top_languages(g, username):
    """Get the most used languages across all repositories."""
    try:
        languages = {}
        for repo in g.get_user(username).get_repos():
            repo_langs = repo.get_languages()
            for lang, count in repo_langs.items():
                if lang in languages:
                    languages[lang] += count
                else:
                    languages[lang] = count
        
        # Sort by usage and take top 5
        sorted_languages = sorted(languages.items(), key=lambda x: x[1], reverse=True)[:5]
        return [lang for lang, _ in sorted_languages]
    except Exception as e:
        print(f"Error getting languages: {e}")
        return []

def generate_achievements(user):
    """Generate a list of achievements based on GitHub activity."""
    achievements = []
    
    # Example achievements logic
    if user.followers >= 100:
        achievements.append("🥇 Attracted 100+ followers on GitHub")
    
    if user.public_repos >= 10:
        achievements.append("📚 Created 10+ public repositories")
    
    # More achievement logic can be added here
    
    return achievements

def update_readme_achievements(stats):
    """Update the achievements section in the README."""
    with open(README_PATH, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Find achievements section
    achievements_pattern = r'(<!-- ACHIEVEMENTS:START -->).*(<!-- ACHIEVEMENTS:END -->)'
    achievements_section = "<!-- ACHIEVEMENTS:START -->\n"
    
    for achievement in stats['achievements']:
        achievements_section += f"- {achievement}\n"
    
    if not stats['achievements']:
        achievements_section += "- No achievements yet. Keep working! 💪\n"
    
    achievements_section += "<!-- ACHIEVEMENTS:END -->"
    
    updated_content = re.sub(
        achievements_pattern, 
        achievements_section, 
        content, 
        flags=re.DOTALL
    )
    
    with open(README_PATH, 'w', encoding='utf-8') as file:
        file.write(updated_content)

def main():
    """Main function to update the GitHub profile README."""
    print("Starting GitHub profile update...")
    
    # Get GitHub statistics
    stats = get_github_stats()
    print(f"Fetched stats for {stats['name']}")
    
    # Update README with achievements
    update_readme_achievements(stats)
    print("Updated README with latest achievements")
    
    print("GitHub profile update completed successfully!")

if __name__ == "__main__":
    main()
