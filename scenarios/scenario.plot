Client Server  Proxy
|        |       |
|--------------->| MESSAGE {
|        |       |   "type" : "REQUEST",
|        |       |   "method": "GET",
|        |       |   "url": "http://www.google.com",
|        |       |   "headers": {
|        |       |      "Host": "www.google.com",
|        |       |      "Accept-Language": "fr,fr-fr;q=0.8,en-us;q=0.5,en;q=0.3",
|        |       |      "Accept-Encoding": "gzip, deflate",
|        |       |      "Connection": "keep-alive",
|        |       |      "Cache-Control": "max-age=0"
|        |       |    }
|        |       | }
|--------------->| #
|        |<------| MESSAGE {"key": "value"}
|        |       |
|        |-----> | TITLE { "data": "value" }
|<---------------| RESPONSE
|        |       | Pas de fleches, c'est la suite du message précédent
|        |       |
|        |       | # Commentaire car commence par un #
|        |       |
|<-------------->| LINKS Je ne sais plus quoi mettre
|        |       |
|<-------|       | TEST
|        |------>| TEST "blabla"
|        |       |
|>------------>>>| Burp