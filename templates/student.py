import requests

# Define the URL where your Flask app is running
BASE_URL = "http://127.0.0.1:5000"  # Change if using a different host/port

def get_student_data(name):
    """Fetch and display student data from the Flask app."""
    response = requests.get(f"{BASE_URL}/student/{name}")

    if response.status_code == 200:
        print("\n✅ Student Data Retrieved:")
        print(response.text)  # Display response content
    else:
        print(f"\n❌ Error: {response.status_code} - {response.text}")

if __name__ == "__main__":
    student_name = input("Enter student name: ").strip()
    get_student_data(student_name)