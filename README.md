# Lec2Flash

Generating flash cards from your lecture notes! Upload text or markdown files to the website, and it will do its best to parse out facts and generate flashcards for your own studying. You can edit the flashcards if you want too!

In order to run:

Install requirements:

```
pip install -r requirements.txt
```

Install neo4j:

You can install neo4j with ```brew install neo4j``` (for macOs) or from the [Neo4j website](https://neo4j.com/). You'll need to run it in the background (```neo4j start```). If it is your first time, go to localhost:7474 and use the default login (username: 'neo4j', password: 'neo4j'). Change the password to 'password' when it prompts you, but keep the username as 'neo4j'.

You may need to install the spacy model ```en-core-web-lg``` as well. You can do this by running: 

```
python -m spacy download en-core-web-lg
```

You can then run the web app with:

``` ./run.sh```

Remember to run Neo4j in the background while running this! You should be able to stop it with ```neo4j stop```.
