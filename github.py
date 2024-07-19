#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NON INFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import requests
import json
import time

class GitHubEmailFinder:
    def __init__(self, token, location):
        self.token = token
        self.location = location
        self.api_url = "https://api.github.com"
        self.headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json"
        }

    def search_users_by_location(self):
        users = []
        page = 1

        while True:
            query = f"{self.api_url}/search/users?q=location:{self.location}&page={page}&per_page=100"
            response = requests.get(query, headers=self.headers)
            if response.status_code != 200:
                print(f"Failed to fetch users: {response.json()}")
                break

            data = response.json()
            users.extend(data['items'])

            if 'next' not in response.links:
                break

            page += 1
            time.sleep(2)  # To respect API rate limit

        return users

    def get_email_from_user(self, username):
        user_url = f"{self.api_url}/users/{username}"
        response = requests.get(user_url, headers=self.headers)
        if response.status_code == 200:
            user_data = response.json()
            email = user_data.get('email')
            if email:
                return email

            # If email is not in profile, check public events
            events_url = f"{self.api_url}/users/{username}/events/public"
            events_response = requests.get(events_url, headers=self.headers)
            if events_response.status_code == 200:
                events_data = events_response.json()
                for event in events_data:
                    commits = event.get('payload', {}).get('commits', [])
                    for commit in commits:
                        author = commit.get('author', {})
                        email = author.get('email')
                        if email:
                            return email
        return None

    def find_emails(self):
        users = self.search_users_by_location()
        user_emails = {}

        for user in users:
            email = self.get_email_from_user(user['login'])
            if email:
                user_emails[user['login']] = email
                print(f"Found email for {user['login']}: {email}")
            time.sleep(1)  # To respect API rate limit

        return user_emails


def main():
    token = "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"  # Replace with your GitHub token
    location = "United States"  # Specify the location

    finder = GitHubEmailFinder(token, location)
    emails = finder.find_emails()

    # Save emails to a file
    with open("emails.json", "w") as f:
        json.dump(emails, f, indent=4)


if __name__ == "__main__":
    main()
