#!/usr/bin/env python3
"""
GitHub Profile Health Checker Script
This script analyzes your GitHub profile and recommends improvements.
"""

import os
import sys
import requests
import json
import datetime
from github import Github

# Configuration
GITHUB_USERNAME = "future-mind"

class ProfileHealthChecker:
    """GitHub Profile Health Checker class."""

    def __init__(self, username):
        self.username = username
        self.token = os.environ.get("GITHUB_TOKEN")
        self.github = Github(self.token) if self.token else Github()
        try:
            self.user = self.github.get_user(username)
        except Exception as e:
            print(f"Error fetching user data: {e}")
            sys.exit(1)
            
        self.issues = []
        self.recommendations = []
        
    def check_profile_completeness(self):
        """Check for profile completeness."""
        # Check for basic profile information
        if not self.user.name:
            self.issues.append("Missing name in profile")
            self.recommendations.append("Add your full name to your GitHub profile")
            
        if not self.user.bio:
            self.issues.append("Missing bio")
            self.recommendations.append("Add a brief bio that highlights your expertise and interests")
            
        if not self.user.email:
            self.issues.append("Missing public email")
            self.recommendations.append("Consider adding a public email for contact opportunities")
            
        if not self.user.blog:
            self.issues.append("Missing website/blog link")
            self.recommendations.append("Add a link to your personal website, blog, or LinkedIn profile")
            
        if not self.user.location:
            self.issues.append("Missing location")
            self.recommendations.append("Add your location for better discovery")
            
        if not self.user.avatar_url or "gravatar" in self.user.avatar_url:
            self.issues.append("Using default avatar")
            self.recommendations.append("Upload a professional profile picture")
    
    def check_repo_quality(self):
        """Check the quality of public repositories."""
        repos = list(self.user.get_repos())
        
        if not repos:
            self.issues.append("No public repositories")
            self.recommendations.append("Create and share public projects to showcase your skills")
            return
            
        readme_count = 0
        pinned_count = 0
        license_count = 0
        description_count = 0
        
        for repo in repos:
            # Check if repo has a README
            try:
                repo.get_contents("README.md")
                readme_count += 1
            except:
                pass
                
            # Check if repo has a description
            if repo.description:
                description_count += 1
                
            # Check if repo has a license
            if repo.license:
                license_count += 1
                
            # We can't directly check if a repo is pinned via API
        
        readme_percentage = (readme_count / len(repos)) * 100
        description_percentage = (description_count / len(repos)) * 100
        license_percentage = (license_count / len(repos)) * 100
        
        if readme_percentage < 70:
            self.issues.append(f"Only {readme_percentage:.1f}% of repositories have README files")
            self.recommendations.append("Add detailed README files to more repositories")
            
        if description_percentage < 70:
            self.issues.append(f"Only {description_percentage:.1f}% of repositories have descriptions")
            self.recommendations.append("Add clear, concise descriptions to your repositories")
            
        if license_percentage < 50:
            self.issues.append(f"Only {license_percentage:.1f}% of repositories have licenses")
            self.recommendations.append("Add appropriate licenses to your open-source projects")
    
    def check_contribution_activity(self):
        """Check contribution activity."""
        # This is a simplified version - GitHub's exact contribution count requires GraphQL API
        today = datetime.date.today()
        month_ago = today - datetime.timedelta(days=30)
        
        url = f"https://api.github.com/users/{self.username}/events"
        headers = {}
        if self.token:
            headers["Authorization"] = f"token {self.token}"
            
        response = requests.get(url, headers=headers)
        
        if response.status_code != 200:
            self.issues.append("Unable to check recent activity")
            return
            
        events = response.json()
        recent_events = [e for e in events if e["created_at"] >= month_ago.isoformat()]
        
        if len(recent_events) < 10:
            self.issues.append("Low contribution activity in the last month")
            self.recommendations.append("Increase your GitHub activity by committing code, opening issues, or contributing to discussions")
    
    def check_profile_readme(self):
        """Check if the user has a profile README and its quality."""
        try:
            special_repo = self.github.get_repo(f"{self.username}/{self.username}")
            readme = special_repo.get_contents("README.md")
            content = readme.decoded_content.decode('utf-8')
            
            # Check README length
            if len(content) < 500:
                self.issues.append("Profile README is too short")
                self.recommendations.append("Expand your profile README with more details about yourself, skills, and projects")
            
            # Check for common sections
            sections_to_check = ["about", "skills", "projects", "contact", "stats"]
            missing_sections = []
            
            for section in sections_to_check:
                if section.lower() not in content.lower():
                    missing_sections.append(section)
            
            if missing_sections:
                self.issues.append(f"Missing sections in profile README: {', '.join(missing_sections)}")
                self.recommendations.append(f"Add these sections to your profile README: {', '.join(missing_sections)}")
                
            # Check for badges
            if "![" not in content or "](https://" not in content:
                self.issues.append("No badges or stats in profile README")
                self.recommendations.append("Add badges and GitHub stats to make your profile more visually appealing")
                
        except Exception as e:
            self.issues.append("Missing profile README repository")
            self.recommendations.append("Create a repository named exactly like your username with a README.md file")

    def run_all_checks(self):
        """Run all profile health checks."""
        print(f"🔍 Running profile health checks for {self.username}...")
        
        self.check_profile_completeness()
        self.check_repo_quality()
        self.check_contribution_activity()
        self.check_profile_readme()
        
        print("\n✅ Profile Health Check Results:")
        if not self.issues:
            print("Congratulations! No issues found with your GitHub profile.")
        else:
            print(f"\n⚠️ Issues Found ({len(self.issues)}):")
            for i, issue in enumerate(self.issues, 1):
                print(f"{i}. {issue}")
            
            print(f"\n💡 Recommendations ({len(self.recommendations)}):")
            for i, rec in enumerate(self.recommendations, 1):
                print(f"{i}. {rec}")
                
        print("\nProfile health check complete! Implement the recommendations to improve your GitHub presence.")
        return len(self.issues) == 0

def main():
    """Main function to check GitHub profile health."""
    checker = ProfileHealthChecker(GITHUB_USERNAME)
    checker.run_all_checks()

if __name__ == "__main__":
    main()
