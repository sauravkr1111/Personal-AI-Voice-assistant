
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
import random

wake_words = ["nova", "nov", "innova"]

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

def is_connected():
    try:
        requests.get("https://www.google.com", timeout=3)
        return True
    except:
        return False

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
    global active
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
        if not is_connected():
            print("No internet connection.")
            speak("No internet connection.")
            return
        search_query = c.lower().replace("search", "").strip()
        url = f"https://www.google.com/search?q={search_query}"
        webbrowser.open(url)
        print(f"Searching for {search_query} on Google.")
        speak(f"Searching for {search_query} on Google.")

    elif any(x in c.lower() for x in ["music","some music", "play anything"]):

        name, url = random.choice(list(musiclibrary.music.items()))

        webbrowser.open(url)
        print(f"Playing {name}")
        speak(f"Playing {name}")

    elif "play" in c.lower():
        if not is_connected():
            print("No internet connection.")
            speak("No internet connection.")
            return
        song = c.lower().replace("play", "").strip()

        for name, url in musiclibrary.music.items():
            if name in song:
                webbrowser.open(url)
                print(f"Playing {name}")
                speak(f"Playing {name}")
                return
        webbrowser.open(f"https://open.spotify.com/search/{song.replace(' ', '%20')}")
        print(f"searching {song} on spotify")
        speak(f"searching {song} on spotify")
        #speak("Sorry, I couldn't find that song.")

    elif "news" in c.lower():
        if not is_connected():
            print("No internet connection.")
            speak("No internet connection.")
            return
        
        response = requests.get(
            f"https://newsapi.org/v2/everything?q=india&language=en&sortBy=publishedAt&apiKey={news_api}",
            timeout=10
        )

        if response.status_code == 200:

            data = response.json()
            articles = data.get("articles", [])

            if not articles:
                print("No news found.")
                speak("No news found.")
                return
            i = 0
            print("Press 'q' to stop the news...")
            speak("Press 'q' to stop the news...")
            while i < len(articles):

                #listen 5 news
                for _ in range(5):
                    if msvcrt.kbhit():
                        key = msvcrt.getch().decode(errors="ignore").lower()

                        if key == "q":

                            print("Stopping news...")
                            speak("Stopping news")
                            break

                    if i >= len(articles):
                        break

                    print(f"{i+1}. {articles[i]['title']}")
                    speak(articles[i]["title"])
                    i += 1

                # After all news finished
                if i >= len(articles):
                    print("That's all for today's news.")
                    speak("That's all for today's news.")
                    break

                if key == "q":
                    break
                # Continue or not
                print("Do you want me to continue? Please say yes or no.")
                speak("Do you want me to continue? Please say yes or no.")

                try:
                    with sr.Microphone() as source:
                        print("Listening...")
                        audio = recognizer.listen(source, timeout=10, phrase_time_limit=3)

                    reply = recognizer.recognize_google(audio).lower()
                    print("Reply:", reply)

                    # Continue
                    if any(x in reply for x in ["yes", "continue", "go on", "sure", "ofcourse"]):
                        continue

                    # Stop news
                    elif any(x in reply for x in ["no", "stop"]):
                        print("Okay, stopping the news.")
                        speak("Okay, stopping the news.")
                        break

                    # Disable Nova
                    elif any(x in reply for x in ["exit", "quit", "stop", "deactivate", "sleep",]):
                        print("Deactivating Nova...")
                        speak("Deactivating Nova...")
                        active = False
                        return

                    else:
                        print("I will stop the news.")
                        speak("I will stop the news.")
                        break

                except sr.WaitTimeoutError:
                    print("No response received. Stopping the news.")
                    speak("No response received. Stopping the news.")
                    break

                except sr.UnknownValueError:
                    print("I didn't understand. Stopping the news.")
                    speak("I didn't understand. Stopping the news.")
                    break

    elif any(word in c.lower() for word in ["close", "shutdown", "goodbye"]):
        print("Goodbye!")
        speak("Goodbye!")
        sys.exit()
        #other commands will attend by gemini
    # else:
        # if not is_connected():
        #     print("No internet connection.")
        #     speak("No internet connection.")
        #     return
    #     response = aiProcess(c)
    #     print(response)
    #     speak(response)


    

if __name__ == "__main__":
    speak("Initializing Nova...")

    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source, duration=1)
    active = False
    while True:
        #Listen for the wake word "Nova"
        #obtain audio from the microphone
        print("Processing...")
        try:
            with sr.Microphone() as source:
                if active:
                    print("Listening...")
                    audio = recognizer.listen(source, timeout=None, phrase_time_limit=5)
                else:
                    print("Listening for wake word...")
                    audio = recognizer.listen(source, timeout=None, phrase_time_limit=3)

            text = recognizer.recognize_google(audio).lower()
            print(f"Heard: {text}")

            if not active:
                if any(word in text for word in wake_words):
                    active = True
                    command = text
                    for word in wake_words:
                        command = command.replace(word, "").strip()

                    #command = (command.replace("hey", "").strip())

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
                    command = command.replace(word, "").strip()
                #command = command.replace("hey", "").strip()

                
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
            
