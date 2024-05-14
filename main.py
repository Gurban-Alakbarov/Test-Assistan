import os
import csv
import time
from openai import OpenAI


OpenAI.api_key = os.getenv('OPENAI_API_KEY')
client = OpenAI()

#Create an assistant
my_assistant = client.beta.assistants.create(
    model="gpt-3.5-turbo-0125",
    instructions="You are a teacher. When given a topic, submit a question relevant to that topic.",
    name="Teacher",
    tools=[{"type": "code_interpreter"}],
)
print(f"This is the assistant object: {my_assistant} \n")

#Create a thread
my_thread = client.beta.threads.create()
print(f"This is the thread object: {my_thread} \n")

#Add a message to a thread
my_thread_message = client.beta.threads.messages.create(
  thread_id=my_thread.id,
  role="user",
  content="I need to solve `8x + 22 = 32`. Can you help me?",
)
print(f"This is the message object: {my_thread_message} \n")

#Run the assistant
my_run = client.beta.threads.runs.create(
  thread_id=my_thread.id,
  assistant_id=my_assistant.id,
  instructions="SINAM"
)
print(f"This is the run object: {my_run} \n")

#Periodically retrieve the run to check
while my_run.status in ["queued", "in_progress"]:
    keep_retrieving_run = client.beta.threads.runs.retrieve(
        thread_id=my_thread.id,
        run_id=my_run.id
    )
    print(f"Run status: {keep_retrieving_run.status}")

    if keep_retrieving_run.status == "completed":
        print("\n")

        #Retrieve the messages added
        all_messages = client.beta.threads.messages.list(
            thread_id=my_thread.id
        )

        print("------------------------------------------------------------ \n")

        user_message = my_thread_message.content
        assistant_message = all_messages.data[1].content

        print(f"User: {user_message}")
        print(f"Assistant: {assistant_message}")

        # Save the messages to a CSV file
        with open('response_messages.csv', 'w', newline='') as csvfile:
            fieldnames = ['Role', 'Message']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            writer.writerow({'Role': 'User', 'Message': user_message})
            writer.writerow({'Role': 'Assistant', 'Message': assistant_message})

        break
    elif keep_retrieving_run.status in ["queued", "in_progress"]:
        time.sleep(1)  #Adding a delay
    else:
        print(f"Run status: {keep_retrieving_run.status}")
        break
