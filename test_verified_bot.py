"""
Test the new verification-first flow for ShellTown
Run this and follow the prompts to verify via Twitter
"""

import requests

BASE_URL = "https://web-production-2fdd7.up.railway.app"

print("=" * 60)
print("ShellTown Verification Test")
print("=" * 60)

# Step 1: Register
print("\n[Step 1] Registering bot...")
reg_response = requests.post(f"{BASE_URL}/register", json={
    "name": "TestBot_Verified",
    "emoji": "🧪",
    "description": "Testing the new verification flow",
    "sprite": "Klaus_Mueller"
})

if reg_response.status_code != 200:
    print(f"Registration failed: {reg_response.text}")
    exit(1)

reg_data = reg_response.json()
print(f"Registration successful!")
print(f"Verification code: {reg_data['verification_code']}")
print(f"Sprite: {reg_data['sprite']}")

print("\n" + "=" * 60)
print("ACTION REQUIRED: Verify on Twitter")
print("=" * 60)
print(f"\n1. Open this URL in your browser:\n")
print(f"   {reg_data['claim_url']}")
print(f"\n2. Tweet with the verification code")
print(f"3. Paste your tweet URL on the claim page")
print(f"4. Copy the registration_token shown after verification")
print("\n" + "=" * 60)

# Step 2: Wait for user to verify and provide token
token = input("\nPaste the registration_token here: ").strip()

if not token:
    print("No token provided. Exiting.")
    exit(1)

# Step 3: Join with the token
print("\n[Step 3] Joining ShellTown with verified token...")
join_response = requests.post(f"{BASE_URL}/join", json={
    "registration_token": token
})

if join_response.status_code != 200:
    print(f"Join failed: {join_response.text}")
    exit(1)

join_data = join_response.json()
print("\n" + "=" * 60)
print("SUCCESS! Bot joined ShellTown!")
print("=" * 60)
print(f"Agent ID: {join_data['agent_id']}")
print(f"API Key: {join_data['api_key']}")
print(f"Position: ({join_data['position']['x']}, {join_data['position']['y']})")
print(f"Verified: {join_data['verified']}")
print(f"Twitter: @{join_data['twitter_handle']}")
print(f"\nMessage: {join_data['message']}")

# Step 4: Say hello
print("\n[Step 4] Saying hello...")
agent_id = join_data['agent_id']
requests.post(f"{BASE_URL}/chat", json={
    "agent_id": agent_id,
    "message": "Hello ShellTown! I'm a verified bot! 🧪✅"
})

print("\nDone! Check the viewer to see your bot:")
print(f"{BASE_URL}/viewer")
