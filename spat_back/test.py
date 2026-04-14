import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'spat_back.settings')
django.setup()

from decouple import config
from groq import Groq

client = Groq(api_key=config('GROQ_API_KEY'))
completion = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[
        {"role": "system", "content": "Tu es un assistant. Réponds en JSON: {\"texte\": \"bonjour\", \"action\": null, \"confirmation\": false}"},
        {"role": "user", "content": "bonjour"}
    ],
    max_tokens=100,
)
print(completion.choices[0].message.content)