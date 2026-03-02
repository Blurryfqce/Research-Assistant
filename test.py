import requests

BASE_URL = "http://127.0.0.1:5000"
PDF_PATH = "parking.pdf"   # Hardcoded PDF file


def upload_pdf():
    print("Uploading PDF...")

    try:
        with open(PDF_PATH, "rb") as f:
            files = {"file": f}
            response = requests.post(f"{BASE_URL}/upload", files=files)
    except FileNotFoundError:
        print(f"Error: {PDF_PATH} not found in project folder.")
        return None

    if response.status_code != 200:
        print("Upload failed:")
        print(response.text)
        return None

    data = response.json()

    print("Upload successful.")
    print("\n--- Document Overview ---\n")
    print(data.get("overview", "No overview returned."))
    print("\n-------------------------\n")

    return data.get("upload_id")


def ask_question(upload_id):
    while True:
        question = input("Enter question (or type 'exit'): ")

        if question.lower() == "exit":
            break

        response = requests.post(
            f"{BASE_URL}/ask",
            json={
                "upload_id": upload_id,
                "question": question
            }
        )

        if response.status_code != 200:
            print("Error:")
            print(response.text)
            continue

        data = response.json()

        print("\n--- Answer ---\n")
        print(data.get("answer", "No answer returned."))
        print("\n--------------\n")


if __name__ == "__main__":
    upload_id = upload_pdf()

    if upload_id:
        ask_question(upload_id)