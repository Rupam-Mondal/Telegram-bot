import json

# Load the JSON data from the file
with open('channel_messages.json', 'r') as file:
    data = json.load(file)

# Open a new file to write the messages
with open('extracted_messages.txt', 'w', encoding='utf-8') as output_file:
    # Iterate through each item in the JSON data
    for message in data:
        if 'message' in message:  # Check if the 'message' field exists
            # Write the message to the new file
            output_file.write(message['message'] + '\n')

print("Messages have been successfully written to 'extracted_messages.txt'")


