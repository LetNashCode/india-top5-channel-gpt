from tiktoktts import TTS

tts = TTS()

tts.SetVoice("en_female_ht_f08_wonderful_world")

result = tts.New("Hello world")

print(type(result))
print(result)

raise SystemExit
