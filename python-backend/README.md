# meetWhenAh
uvicorn telegram:app --host 0.0.0.0 --port 8001

//ngrok http --domain=jensenhyk.ngrok.dev 8001

zrok reserve public 8001 --unique-name when2meetbot
zrok reserve public 8001 --unique-name when2meetdesktop

#run this can alr
zrok share reserved when2meetbot //laptop
zrok share reserved when2meetdesktop //desktop