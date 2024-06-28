# meetWhenAh
uvicorn telegram:app --host 0.0.0.0 --port 8001

//ngrok http --domain=jensenhyk.ngrok.dev 8001

zrok reserve public 8001 --unique-name when2meetbot
zrok reserve public 8001 --unique-name when2meetdesktop

#run this can alr
zrok share reserved when2meetbot //laptop
zrok share reserved when2meetdesktop //desktop

#AWS lambda functions
- to generate the layer (python dependencies) run 1-install.sh and then 2-install.sh
- then, zip the rest of the contents of the folder and upload as function. Ensure you get the lambda_handler uncommented