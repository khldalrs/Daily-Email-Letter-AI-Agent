Imports and initialization
Next, create the file main.py in your project directory and copy and paste this code:

python
1

````python import json
2
import requests
3
import logging
4
​
5
import os
6
from dotenv import load_dotenv
7
​
8
logging.basicConfig(level=logging.INFO) # set log level
9
load_dotenv() # for reading API key from `.env` file.
10
​
11
# Sandbox API URL format: https://api.mailgun.net/v3/sandbox&lt;ID&gt;.mailgun.org/messages
12
MAILGUN_API_URL = "https://api.mailgun.net/v3/YOUR_DOMAIN_NAME/messages"
13
FROM_EMAIL_ADDRESS = "Sender Name &lt;SENDER_EMAIL_ID&gt;"
It uses Python's standard logging and configures it to INFO level with this code:

python
1
```python
2
logging.basicConfig(level=logging.INFO)
3
````

The load_dotenv() function comes from the python-dotenv library and is used to load environment variables from the .env file in your Python code. It is a good practice to store and read sensitive information such as credentials and API keys from the .env file.

MAILGUN_API_URL sets the API URL for your Python script, and indicates the sender's email ID. Both must use your email sending domain or the sandbox domain mentioned earlier.

Sending single emails using the Mailgun API
Let's first look at the most simple way of using Mailgun API: sending a single email. You can use it for one-off cases, like sending a reminder or a follow-up email to your high-value customer. This will allow you to track the email delivery as well.

Copy and paste the code below into your main.py file after the imports and initialization:

python
1

```python
2
def send_single_email(to_address: str, subject: str, message: str):
3
    try:
4
        api_key = os.getenv("MAILGUN_API_KEY")  # get API-Key from the `.env` file
5
​
6
        resp = requests.post(MAILGUN_API_URL, auth=("api", api_key),
7
                             data={"from": FROM_EMAIL_ADDRESS,
8
                                   "to": to_address, "subject": subject, "text": message})
9
        if resp.status_code == 200:  # success
10
            logging.info(f"Successfully sent an email to '{to_address}' via Mailgun API.")
11
        else:  # error
12
            logging.error(f"Could not send the email, reason: {resp.text}")
13
​
14
    except Exception as ex:
15
        logging.exception(f"Mailgun error: {ex}")
16
​
17
if __name__ == "__main__":
18
    send_single_email("Manish <manish@exanple.com>", "Single email test", "Testing Mailgun API for a single email")
19
```

This send_single_email(...) function takes three arguments: to_address, subject, and message. to_address is for a single email address, and the other two are for the email's subject and content.

The code reads the Mailgun API key from the .env file and uses it to make an API call to the specified API_URL. This API key acts as a unique identifier, allowing Mailgun to authenticate the API call and verify who is using its services.

You must use your unique API key to ensure proper authentication. The from email address used in this API call must also be associated with your valid domain or Mailgun's sandbox domain. If it doesn't, the call will fail with an error message.

The data parameters are sent via HTTP POST method to the API endpoint with the requests.post(...) call.

When the API call is successful, your email will be queued for delivery, and the API will return an HTTP-200 (OK) status. In case of an error, the API will return an error message with an appropriate HTTP status code. Both cases are appropriately logged by this code snippet.

if **name** == "**main**" shows how this function can be called in your script.

Running this script in your terminal will show the following:

Python script running in terminal
Sending bulk email with the Mailgun API
While you can use the send_single_email(...) function in a loop to send emails to multiple recipients, it's not the most efficient method due to network I/O delays. This approach may also encounter API rate limiting.

Instead, use Batch Sending for sending emails to multiple recipients. The code snippet below demonstrates how to use it in your Python script.

Copy and paste the send_batch_emails(...) function into your main.py file after the send_single_email(...) function, and modify the **main** part as shown below:

python
1

```python
2
def send_batch_emails(recipients: dict, subject: str, message: str):
3
    try:
4
        api_key = os.getenv("MAILGUN_API_KEY")  # get API-Key from the `.env` file
5
​
6
        to_address = list(recipients.keys())  # get only email addresses
7
        recipients_json = json.dumps(recipients)    # for API call
8
​
9
        logging.info(f"Sending email to {len(to_address)} IDs...")
10
        resp = requests.post(MAILGUN_API_URL, auth=("api", api_key),
11
                             data={"from": FROM_EMAIL_ADDRESS,
12
                                   "to": to_address, "subject": subject, "text": message,
13
                                   "recipient-variables": recipients_json})
14
        if resp.status_code == 200:  # success
15
            logging.info(f"Successfully sent email to {len(recipients)} recipients via Mailgun API.")
16
        else:   # error
17
            logging.error(f"Could not send emails, reason: {resp.text}")
18
    except Exception as ex:
19
        logging.exception(f"Mailgun error: {ex}")
20
​
21
if __name__ == "__main__":
22
    # send_single_email("Manish <manish@exanple.com>", "Single email test", "Testing Mailgun API for a single email")
23
    _recipients = {"manish@example.com": {"name": "Manish", "id": 1},
24
                   "jakkie@example.com": {"name": "Jakkie", "id": 2},
25
                   "elzet@example.com": {"name": "Elzet", "id": 3}}
26
​
27
    send_batch_emails(_recipients, "Hi, %recipient.name%!", "Testing Mailgun API. This email is sent via Mailgun API.")
28
```

Batch Sending uses a special parameter called Recipient Variables that lets you send personalized emails to multiple recipients in a single API call. Using Recipient Variables with Batch Sending ensures Mailgun sends individual emails to each recipient in the to field. Without it, each recipient will see all recipients' email addresses in the to field.

Here is one such recipient variable, with email addresses as keys and the corresponding "name" and "id" as values:

{"manish@example.com": {"name": "Manish", "id": 1},

"jakkie@example.com": {"name": "Jakkie", "id": 2},

"elzet@example.com": {"name": "Elzet", "id": 3}}

The send_batch_emails(...) function has three parameters: recipients, subject, and message. Note that recipients is a dictionary object representing the recipient variable discussed above.

The code first extracts email addresses from this dictionary using to_address = list(recipients.keys()), then converts the dictionary to JSON for API use with the recipients_json = json.dumps(recipients) call.

The recipients_json variable is passed in the API call for the recipient-variables field, which is used for personalizing the email subject and content. The subject is specified as follows:

"Hi, %recipient.name%!"

The Mailgun API correctly substitutes each recipient's name from the JSON while sending emails with %recipient.name%. So, in the example above, Manish, Jakkie, and Elzet will receive personalized subject lines—"Hi, Manish!" "Hi, Jakkie!", and "Hi, Elzet!". Similarly, you can personalize the email content using any %recipient.KEY-NAME% value.

The rest of the send_batch_emails(...) code is similar to the send_single_email(...) function, except that it sends multiple email recipients in a single API call.

Running this script will show the following:

Python script running in terminal
Keep in mind: The maximum number of recipients allowed in a single Mailgun Batch Sending API call is one thousand. You can find more about the Batch Sending API here.

Here's an example of how this email will appear in the recipient's inbox:

Email sent using Mailgun API
Additional features
The Mailgun API offers several additional features to make your life easier.

Sending HTML emails with attachments
The Mailgun API lets you send emails with attachments, whether with text or HTML content. You can use the same API endpoint (https://api.mailgun.net/v3/YOUR_DOMAIN_NAME/messages) with an additional 'attachment' passed to the files parameter, as shown below:

python
1

```python
2
files = {'attachment': open('weekly-report.csv', 'rb')}     # file you want to attach
3
resp = requests.post(MAILGUN_API_URL, auth=("api", api_key), files=files,
4
                     data={"from": FROM_EMAIL_ADDRESS,
5
                           "to": to_address, "subject": subject, "text": message})
6
```

Email delivery and tracking
Mailgun provides detailed email tracking, including when emails are delivered or opened, links are clicked, emails bounce, users unsubscribe, and emails are marked as spam. This data is made available via the control panel on the dashboard and through the API.

Mailgun also permanently saves emails if they can't be delivered (hard bounce) or if a recipient unsubscribes or marks the email as spam. In these cases, Mailgun won't try to send emails to those recipients again.

Email templates
The Mailgun API allows you to create HTML templates for standardizing your email layout and making them more appealing with predesigned layouts and standard content.

You can find templates in the left sidebar under the Sending menu:

Best practices
It's also important to keep some best practices in mind when you send emails programmatically.

Error handling
When your script uses a third-party API like Mailgun to send emails, you must handle potential errors related to network or API failures and API responses indicating errors to ensure your script works smoothly, can detect issues like invalid API keys or URLs, and knows when emails aren't sent by the Mailgun API. Without error handling, your script might fail silently, resulting in undelivered emails.

The code snippets above all provide for handling errors that might occur. Firstly, they check the response status code (resp.status_code). If it's not successful (HTTP 200), they log the error message so you can debug the issue.

Both the send_single_email(...) and send_batch_emails(...) functions also use a try-except block to ensure any exceptions are caught and logged correctly.

Email deliverability
Email deliverability means ensuring your emails land in the recipient's inbox, not their spam folder. You need a good sender reputation to achieve high deliverability. When we’re talking about building programmatic sending, there are a couple specific things we can look at to improve your email deliverability including authentication, and optimizing emails to be responsive. We’re talking about each below.

Authenticate your email
Use SPF, DKIM, and DMARC to validate your identity as a sender. Only send emails to verified subscribers who have opted in to receive them and regularly remove inactive subscribers and those who mark your emails as spam.

DMARC is becoming an industry requirements. Learn more about why, and what this authentication standard does in our post on the DMARC perspective.

Responsive emails
Most users access content on various devices like mobile phones, iPads, and tablets, and they expect your emails to be visually appealing and easy to read across different screens.

This requires that you use responsive design techniques, such as fluid layouts, CSS media queries, and optimized images. You should also test your emails on various devices, email clients, and screen sizes to verify that they display correctly.

Responsive design is particularly important if your emails contain a lot of HTML content with images or if you're using email templates. Mailgun's predefined templates are responsive by default.

Wrapping up
In this article, you learned how to send emails using a Python script and the Mailgun API. You also learned about Mailgun features like email tracking and templates and the importance of error handling, optimizing deliverability, and sending responsive emails.

Email geeks help other email geeks. You can find the code discussed in this tutorial in this GitHub repo.

Was this helpful? If so, be sure to subscribe to our newsletter for more tutorials, announcements, and industry insights.
