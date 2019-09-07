# in-browser-ascii-mmo

### in short
A python based in browser mmo with ascii based graphics.
The world is "round" and populated by islands with npc characters on them.

### these features already work
- A seed based generation for islands, npcs and monsters
- Multiplayer support with pvp, chat and trading
- Harvesting resources such as woodcutting and mining
- Buying and selling items from stores
- Storing earned money to banks
- A wear system, including armor, ships and weapons
- Adding additional items, resources, enemies, npcs is easy with the config file
- Multiple servernode support and a centralized login server with database connection to save gamestate



### these are under construction
- different types of shops, each specializing in specific item types
- food to recover health, harvesting and buying it

### future ideas
- different types of areas such as civilized and monster populated areas, restrict specific npc and monster types to these areas
- map that shows positions of islands and the types of the areas, possibly represented by assigning 1 pixel to 1 tile
- islands that are larger than one gametile?


### Dependencies (python3 modules)
- argon2-cffi
- websocket & websocket-client
- psycopg2-binary
- tornado
