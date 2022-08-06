# Commands

`[Required]`: It means this argument is required.

`[Optional]?`: It means this argument is not required. (optional)

`[Multiple]*`: It means that this argument is required and there can be more than one if needed.

## play | p

Play the specified audio stream which is uri provided.

* `Alias: p`

* `Usage: play [uri]* ...`

## volume | vol

Set the volume of the player or return volume

* `Alias: vol`
* `Usage: volume [volume]?`

## nowplaying | np

Display the current playing song

* `Alias: np`
* `Usage: nowplaying`

## queue

## skip | sk

## stop

## pause | pa

## resume | re

## loop

## repeat

## position | pos

## search | s

Search keyword that user provided on Youtube/Bilibili

* `Alias: s`
* `Usage: search [keyword]` Search keyword on Youtube (by default).
* `Usage: search [-y | -yt | --youtube] [keyword]`  Search keyword on Youtube.
* `Usage: search [-b | --bilibili] [keyword]`  Search keyword on Bilibili.

## save | sa

save songs

* `Alias: sa`
* `Usage: save [name] - [uri]*`   Save uris that user provided.(char '-' is required)
* `Usage: save -c [name]`   For that who want to save current queue.

## exit

Close player.

* `Usage: exit`
