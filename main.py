
import speech_recognition as sr
import webbrowser
import pyttsx3
import requests
import msvcrt
import musiclibrary
import sys
from gtts import gTTS
from google import genai
import pygame
import os
import time
import uuid
from websites import websites
from greetings import greetings

wake_words = ["nova", "nov"]

def aiProcess(command):
    with open("gemini_api.txt", "r") as f:
        gemini_api = f.read().strip()

    client = genai.Client(api_key=gemini_api)

    response = client.models.generate_content(
        model="gemini-2.5-flash",

        config={
        "system_instruction": """
You are Nova, a personal AI assistant created by Saurav Kumar.
Never reveal that you are Gemini or Google.
Always introduce yourself as Nova.
"""
    },
        contents=command
    )

    return response.text

with open("news_api.txt", "r") as f:
        news_api = f.read().strip()

recognizer = sr.Recognizer()
engine = pyttsx3.init()


def speak_old(text):
    engine.say(text)
    engine.runAndWait()

pygame.mixer.init()
def speak(text):
    filename = f"{uuid.uuid4()}.mp3"

    tts = gTTS(text, lang="en")
    tts.save(filename)

    pygame.mixer.music.load(filename)
    pygame.mixer.music.play()

    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)

    pygame.mixer.music.stop()
    pygame.mixer.music.unload()

    time.sleep(0.1)
    if os.path.exists(filename):
        os.remove(filename)

if not os.path.exists("yes.mp3"):
    gTTS(text="Yes", lang="en").save("yes.mp3")

def play_audio(filename):
    pygame.mixer.music.load(filename)
    pygame.mixer.music.play()

    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)

    pygame.mixer.music.stop()
    pygame.mixer.music.unload()
    time.sleep(0.05)

def processCommand(c):
    #print("processCommand:", repr(c))
    print(f"Command: {c}")


    if "open" in c.lower():

        search_query = c.lower().replace("open", "").strip()
        site = search_query.replace(" ", "").replace(".com", "").replace(".in", "").strip()
        if site in websites:
            url = websites[site]
        else:
            url = f"https://www.{site}.com"

        webbrowser.open(url)
        print(f"Opening {search_query}.")
        speak(f"Opening {search_query}.")

    elif "search" in c.lower():
        search_query = c.lower().replace("search", "").strip()
        url = f"https://www.google.com/search?q={search_query}"
        webbrowser.open(url)
        print(f"Searching for {search_query} on Google.")
        speak(f"Searching for {search_query} on Google.")

    elif "play" in c.lower():
        song = c.lower().replace("play", "").strip()
        if song in musiclibrary.music:
            url = musiclibrary.music[song]
            webbrowser.open(url)
            print(f"Playing {song}.")
            speak(f"Playing {song}.")

    elif "news" in c.lower():
        #print("News block entered")
        r = requests.get(f"https://newsapi.org/v2/everything?q=india&language=en&sortBy=publishedAt&apiKey={news_api}", timeout=10)
        #print("Status Code:", r.status_code)
        
        if r.status_code == 200:
            #parse the JSON response
            data = r.json()

            #Extract the articles from the response
            articles = data.get("articles", [])
            print("Total Articles:", len(articles))
            #Speak the headlines of the articles
            print("Press 'q' to stop the news...")
            speak("Press 'q' to stop the news...")
            i = 1
            for article in articles:
                
                if msvcrt.kbhit():
                    key = msvcrt.getch().decode(errors="ignore").lower()

                    if key == "q":
                        print("Stopping news...")
                        speak("Stopping news")
                        break

                print(f"{i}. {article['title']}")
                speak(article['title'])
                i += 1
    elif "close nova" in c.lower():
        print("Goodbye!")
        speak("Goodbye!")
        sys.exit()
        #other commands will attend by gemini
    # else:
    #     response = aiProcess(c)
    #     print(response)
    #     speak(response)


    

if __name__ == "__main__":
    speak("Initializing Nova...")

    r = sr.Recognizer()
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source, duration=1)
    active = False
    while True:
        #Listen for the wake word "Nova"
        #obtain audio from the microphone
        print("Processing...")
        try:
            with sr.Microphone() as source:
                if active:
                    print("Listening...")
                    audio = r.listen(source, timeout=None, phrase_time_limit=5)
                else:
                    print("Listening for wake word...")
                    audio = r.listen(source, timeout=None, phrase_time_limit=3)

            text = r.recognize_google(audio).lower()
            print(f"Heard: {text}")

            if not active:
                if any(word in text for word in wake_words):
                    active = True
                    command = text
                    for word in wake_words:
                        command = command.replace(word, "")

                    command = (command.replace("hey", "").strip())

                    if command in greetings:
                        play_audio(greetings[command])
                    elif command:
                        processCommand(command)
                    else:
                        play_audio(greetings[command])

                continue

             # -------- Active Mode --------

            if text in greetings:
                play_audio(greetings[text])
                continue

            if any(word in text for word in wake_words):
                command = text
                for word in wake_words:
                    command = command.replace(word, "")
                command = command.replace("hey", "").strip()

                
                if command in greetings:
                    play_audio(greetings[command])

                elif command in ["exit", "quit", "stop", "deactivate", "sleep",]:
                    active = False
                    print("Deactivating Nova...")
                    speak("Deactivating Nova...")
                    continue
                elif command:
                    processCommand(command)   
                else:
                    play_audio(greetings[command])                
                continue

            if text in ["exit", "quit", "stop", "deactivate", "sleep",]:
                active = False
                print("Deactivating Nova...")
                speak("Deactivating Nova...")
                continue


            processCommand(text)

        except sr.UnknownValueError:
            continue

        except Exception as e:
            print(f"Error: {type(e).__name__}: {e}")
            