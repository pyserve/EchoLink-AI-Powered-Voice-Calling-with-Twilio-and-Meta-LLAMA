# EchoLink-AI-Powered-Voice-Calling-with-Twilio-and-Meta-LLMA
*EchoLink is an AI-powered voice calling system leveraging Django, Twilio, and Meta LLMA. It enables seamless voice communication 
by integrating natural language processing capabilities from HuggingFace with Twilio's telephony services, 
providing a robust platform for interactive and intelligent voice interactions.*

## Requirements
1. Django/Python Web Server (Flask, etc.)
2. Twilio Account (Free Tiers)
3. HuggingFace (Access Token)
4. Ngrok Server

## Configuration
**Step 1: Setup Django project:** `pip install django`  

**Step 2: Install Ngrok server:** `pip install ngrok`  

**Step 3: Create a Twilio Account and Set up an TwiML App:**  

![image](https://github.com/user-attachments/assets/c4560b74-e0ce-4424-8fda-34e06f5b6792)  

![image](https://github.com/user-attachments/assets/0f13e9c7-7d0d-4963-97b6-e8e79b9fc634)  

> Don't forget to set request URL inside TwiML app to the Ngrok server URL after running it *(ngrok http 8000)*  
> Go to your Active number in Twilio Account and within configure tab, set up "Configure with" as "TwiML App" and select your new created app as "TwiML App".

![image](https://github.com/user-attachments/assets/0321bfd8-57f5-4ed4-b3bd-c3e4d867e453)  

> Add your friends or spare numbers to the verified list for calling during testing

![image](https://github.com/user-attachments/assets/8492cd9d-560f-479a-b959-a6caea412c2e)  


**Step 4: Create a HuggingFace Account and Create an Access Token:**  

## App Usage  
- Download the code folder and unzip it.  
- Open a command terminal inside this directory.  
- Run `pip install -r requirements.txt`
  
- Run Ngrok server `ngrok http 800` > must point to same address or port used by the web server
  
- Copy the ngrok domain url inside settings.py in project folder  
- Copy the ngrok full url into the voice configuration > Request Url inside the TwiML App
  
- Run the project's web server `python manage.py runserver`  
- Call your Twilio number from a registered number.  

## References and Documentation Links  
[https://www.twilio.com/docs/usage/api](url)
[https://docs.vocode.dev/welcome](url)
[https://ngrok.com/docs/](url)
[https://docs.djangoproject.com/en/5.0/](url)
[https://huggingface.co/docs](url)
