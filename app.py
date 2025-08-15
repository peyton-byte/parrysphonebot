from flask import Flask, request, Response
from twilio.twiml.voice_response import VoiceResponse
import openai
import os

app = Flask(__name__)

def wants_transfer(speech):
    keywords = [
        "talk to someone", "real person", "speak with someone",
        "representative", "connect me", "talk to a human", "transfer me"
    ]
    return any(kw in speech.lower() for kw in keywords)

def caller_is_done(speech):
    keywords = ["no", "no thanks", "that's all", "i'm good", "i'm done"]
    return any(kw in speech.lower() for kw in keywords)

@app.route("/voice", methods=["POST"])
def voice():
    speech = request.form.get("SpeechResult", "").strip()
    response = VoiceResponse()

    lowered = speech.lower()

    if not speech:
        response.say("Thanks for calling Parrys in Hamilton. How can I help you today?", voice='Polly.Salli')
        response.listen()
        return Response(str(response), mimetype='text/xml')

    if caller_is_done(speech):
        response.say("Okay, have a nice day. Goodbye!", voice='Polly.Salli')
        response.hangup()
        return Response(str(response), mimetype='text/xml')

    if wants_transfer(speech):
        response.say("Okay, transferring you to a team member now.", voice='Polly.Salli')
        response.dial("+13158240002")
        return Response(str(response), mimetype='text/xml')

    # --- Instant Answers ---

    if "hour" in lowered or "open" in lowered or "time" in lowered:
        response.say("We're open from 8 to 6, Monday through Friday. Saturday 8 to 5, and Sunday 9 to 5.", voice='Polly.Salli')
        response.say("Is there anything else I can help you with?", voice='Polly.Salli')
        response.listen()
        return Response(str(response), mimetype='text/xml')

    if "address" in lowered or "location" in lowered or "where are you" in lowered:
        response.say("We're located at 100 Utica Street in Hamilton, New York.", voice='Polly.Salli')
        response.say("Is there anything else I can help you with?", voice='Polly.Salli')
        response.listen()
        return Response(str(response), mimetype='text/xml')

    if "pressure washer" in lowered:
        response.say("Yes, we rent pressure washers for 60 dollars per day.", voice='Polly.Salli')
        response.say("Is there anything else I can help you with?", voice='Polly.Salli')
        response.listen()
        return Response(str(response), mimetype='text/xml')

    if "shipping" in lowered or "ups" in lowered or "fedex" in lowered or "package" in lowered or "drop off" in lowered:
        response.say("We are a UPS Access Point. You can drop off UPS packages with a label. We also accept FedEx packages if they have prepaid labels.", voice='Polly.Salli')
        response.pause(length=1)
        response.say("If you need to ship something out, we can create a label for FedEx, including standard or overnight delivery. Please note that carriers only pick up during weekdays.", voice='Polly.Salli')
        response.say("Is there anything else I can help you with?", voice='Polly.Salli')
        response.listen()
        return Response(str(response), mimetype='text/xml')

    if "dry clean" in lowered or "dry cleaning" in lowered:
        response.say("Yes, we offer dry cleaning. Items go out and return every Wednesday morning.", voice='Polly.Salli')
        response.say("Is there anything else I can help you with?", voice='Polly.Salli')
        response.listen()
        return Response(str(response), mimetype='text/xml')

    if "screen repair" in lowered or "window repair" in lowered or "broken window" in lowered or "fix screen" in lowered:
        response.say("Yes, we repair window screens and single-pane windows as long as the frame is not damaged.", voice='Polly.Salli')
        response.say("Is there anything else I can help you with?", voice='Polly.Salli')
        response.listen()
        return Response(str(response), mimetype='text/xml')

    # --- GPT Fallback ---
    openai.api_key = os.environ.get("OPENAI_API_KEY")

    completion = openai.ChatCompletion.create(
        model="gpt-4o",
        max_tokens=80,
        messages=[
            {"role": "system", "content": """
You are a helpful, warm employee at Parrys Hardware in Hamilton, NY.
Keep responses short and clear.

Store hours: Mon–Fri 8 AM–6 PM, Sat 8–5, Sun 9–5
Address: 100 Utica Street, Hamilton, NY
Shipping: UPS Access Point (drop-off with label), FedEx drop-offs with prepaid labels. We create FedEx labels in-store. Pickup is weekdays only.
Dry Cleaning: Out and back every Wednesday morning.
Repairs: We repair screens and single-pane windows, only if the frame is not damaged.
Top rental pricing: Pressure washer $60, Floor sander $66, Tile saw $58, Appliance cart $15, Drywall lift $37
If unsure, suggest speaking to a team member.
"""},
            {"role": "user", "content": speech}
        ]
    )

    reply = completion.choices[0].message["content"]

    response.say(reply, voice='Polly.Salli')
    response.pause(length=1)
    response.say("Is there anything else I can help you with?", voice='Polly.Salli')
    response.listen()
    return Response(str(response), mimetype='text/xml')


