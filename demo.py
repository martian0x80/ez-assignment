#!/usr/bin/env python3
"""
Demo script for the Secure File Sharing System
This script demonstrates the complete workflow of the API
"""

import requests
import json
import os
from io import BytesIO


class FileSharingDemo:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.ops_token = None
        self.client_token = None
        
    def print_step(self, step, description):
        """Print a formatted step"""
        print(f"\n{'='*60}")
        print(f"STEP {step}: {description}")
        print(f"{'='*60}")
    
    def create_ops_user(self):
        """Create an Ops user"""
        self.print_step(1, "Creating Ops User")
        
        data = {
            "email": "ops@demo.com",
            "username": "ops_demo",
            "password": "demo123",
            "user_type": "ops"
        }
        
        response = requests.post(f"{self.base_url}/auth/create-ops-user", json=data)
        
        if response.status_code == 200:
            print("✅ Ops user created successfully")
            print(f"   Email: {data['email']}")
            print(f"   Username: {data['username']}")
        else:
            print(f"❌ Failed to create Ops user: {response.text}")
            return False
        
        return True
    
    def create_client_user(self):
        """Create a Client user"""
        self.print_step(2, "Creating Client User")
        
        data = {
            "email": "client@demo.com",
            "username": "client_demo",
            "password": "demo123",
            "user_type": "client"
        }
        
        response = requests.post(f"{self.base_url}/auth/signup", json=data)
        
        if response.status_code == 200:
            print("✅ Client user created successfully")
            print(f"   Email: {data['email']}")
            print(f"   Username: {data['username']}")
            print("   📧 Check console for verification token")
        else:
            print(f"❌ Failed to create Client user: {response.text}")
            return False
        
        return True
    
    def login_ops_user(self):
        """Login as Ops user"""
        self.print_step(3, "Logging in as Ops User")
        
        data = {
            "email": "ops@demo.com",
            "password": "demo123"
        }
        
        response = requests.post(f"{self.base_url}/auth/login", json=data)
        
        if response.status_code == 200:
            self.ops_token = response.json()["access_token"]
            print("✅ Ops user logged in successfully")
            print(f"   Token: {self.ops_token[:20]}...")
        else:
            print(f"❌ Failed to login Ops user: {response.text}")
            return False
        
        return True
    
    def login_client_user(self):
        """Login as Client user"""
        self.print_step(4, "Logging in as Client User")
        
        data = {
            "email": "client@demo.com",
            "password": "demo123"
        }
        
        response = requests.post(f"{self.base_url}/auth/login", json=data)
        
        if response.status_code == 200:
            self.client_token = response.json()["access_token"]
            print("✅ Client user logged in successfully")
            print(f"   Token: {self.client_token[:20]}...")
        else:
            print(f"❌ Failed to login Client user: {response.text}")
            print("   Note: Client users need email verification first")
            return False
        
        return True
    
    def upload_file(self):
        """Upload a file as Ops user"""
        self.print_step(5, "Uploading File (Ops User)")
        
        if not self.ops_token:
            print("❌ Ops user not logged in")
            return False
        
        # Create a test file
        test_content = b"This is a test document content for demonstration purposes."
        files = {
            'file': ('demo_document.docx', BytesIO(test_content), 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
        }
        
        headers = {"Authorization": f"Bearer {self.ops_token}"}
        
        response = requests.post(f"{self.base_url}/files/upload", files=files, headers=headers)
        
        if response.status_code == 200:
            print("✅ File uploaded successfully")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Failed to upload file: {response.text}")
            return False
        
        return True
    
    def list_files(self):
        """List files as Client user"""
        self.print_step(6, "Listing Files (Client User)")
        
        if not self.client_token:
            print("❌ Client user not logged in")
            return False
        
        headers = {"Authorization": f"Bearer {self.client_token}"}
        
        response = requests.get(f"{self.base_url}/files/list", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Files listed successfully")
            print(f"   Total files: {data['total']}")
            for file in data['files']:
                print(f"   - {file['original_filename']} (ID: {file['id']})")
        else:
            print(f"❌ Failed to list files: {response.text}")
            return False
        
        return True
    
    def get_download_link(self):
        """Get download link for a file"""
        self.print_step(7, "Getting Download Link (Client User)")
        
        if not self.client_token:
            print("❌ Client user not logged in")
            return False
        
        headers = {"Authorization": f"Bearer {self.client_token}"}
        
        # Get download link for the first file (assuming file ID 1)
        response = requests.get(f"{self.base_url}/files/download/1", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Download link generated successfully")
            print(f"   Download link: {data['download_link']}")
            return data['download_link']
        else:
            print(f"❌ Failed to get download link: {response.text}")
            return None
    
    def download_file(self, download_link):
        """Download file using the secure link"""
        self.print_step(8, "Downloading File (Using Secure Link)")
        
        if not download_link:
            print("❌ No download link provided")
            return False
        
        response = requests.get(download_link)
        
        if response.status_code == 200:
            print("✅ File downloaded successfully")
            print(f"   Content length: {len(response.content)} bytes")
            print(f"   Content preview: {response.content[:50]}...")
        else:
            print(f"❌ Failed to download file: {response.text}")
            return False
        
        return True
    
    def test_unauthorized_access(self):
        """Test unauthorized access scenarios"""
        self.print_step(9, "Testing Unauthorized Access")
        
        # Test Ops user trying to list files
        if self.ops_token:
            headers = {"Authorization": f"Bearer {self.ops_token}"}
            response = requests.get(f"{self.base_url}/files/list", headers=headers)
            print(f"   Ops user listing files: {'❌ Denied' if response.status_code == 401 else '⚠️  Unexpected success'}")
        
        # Test Client user trying to upload files
        if self.client_token:
            headers = {"Authorization": f"Bearer {self.client_token}"}
            test_content = b"Test content"
            files = {'file': ('test.txt', BytesIO(test_content), 'text/plain')}
            response = requests.post(f"{self.base_url}/files/upload", files=files, headers=headers)
            print(f"   Client user uploading file: {'❌ Denied' if response.status_code == 401 else '⚠️  Unexpected success'}")
        
        # Test access without token
        response = requests.get(f"{self.base_url}/files/list")
        print(f"   Access without token: {'❌ Denied' if response.status_code == 401 else '⚠️  Unexpected success'}")
    
    def run_demo(self):
        """Run the complete demo"""
        print("🚀 Starting Secure File Sharing System Demo")
        print("This demo will showcase the complete workflow of the API")
        
        try:
            # Test if server is running
            response = requests.get(f"{self.base_url}/docs")
            if response.status_code != 200:
                print(f"❌ Server is not running at {self.base_url}")
                print("   Please start the server first: python -m app.main")
                return
            
            # Run demo steps
            if not self.create_ops_user():
                return
            
            if not self.create_client_user():
                return
            
            if not self.login_ops_user():
                return
            
            if not self.upload_file():
                return
            
            # Note: Client login might fail due to email verification requirement
            if not self.login_client_user():
                print("   ⚠️  Client login failed - this is expected if email verification is required")
                print("   You can manually verify the email or modify the user in the database")
                return
            
            if not self.list_files():
                return
            
            download_link = self.get_download_link()
            if download_link:
                self.download_file(download_link)
            
            self.test_unauthorized_access()
            
            print(f"\n{'='*60}")
            print("🎉 Demo completed successfully!")
            print(f"{'='*60}")
            print("\n📋 Summary:")
            print("✅ Created Ops and Client users")
            print("✅ Demonstrated role-based access control")
            print("✅ Uploaded and downloaded files securely")
            print("✅ Tested unauthorized access prevention")
            print("\n🔗 API Documentation: http://localhost:8000/docs")
            
        except requests.exceptions.ConnectionError:
            print(f"❌ Cannot connect to server at {self.base_url}")
            print("   Please make sure the server is running: python -m app.main")
        except Exception as e:
            print(f"❌ Demo failed with error: {e}")


if __name__ == "__main__":
    demo = FileSharingDemo()
    demo.run_demo() 