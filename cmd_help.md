# Commands

`[Required]`: It means this argument is required.

`[Optional]?`: It means this argument is not required. (optional)

`[Multiple]*`: It means that this argument is required and there can be more than one if needed.

## play | p

Play the specified audio stream which is uri provided.

* `Command: play | p`

* `Usage: play [uri]* ...`

## volume | vol

Set the volume of the player or return volume

* `Command: volume | vol`
* `Usage: volume [volume]?`

## nowplaying | np

Display the current playing song

* `Command: nowplaying | np`
* `Usage: nowplaying`

## queue | q

Display songs in the queue.

* `Command: queue | q`
* `Usage: queue`

## clear

Clear the queue.

* `Command: clear`
* `Usage: clear`

## skip | sk

Skip the current playing song.

! This command will make the current song no longer be repeated or looped.

* `Command: skip | sk`
* `Usage: skip`

## stop

Easier way to run command `skip` and `clear` simultaneously.

* `Command: stop`
* `Usage: stop`

## pause | pa

## resume | re

## loop

## repeat

## position | pos

## search | s

Search keyword that user provided on Youtube/Bilibili

* `Command: search | s`
* `Usage: search [keyword]` Search keyword on Youtube (by default).
* `Usage: search [-y | -yt | --youtube] [keyword]`  Search keyword on Youtube.
* `Usage: search [-b | --bilibili] [keyword]`  Search keyword on Bilibili.

## save | sa

save songs

* `Command: save | sa`
* `Usage: save [name] - [uri]*`   Save uris that user provided.(char '-' is required)
* `Usage: save -c [name]`   For that who want to save current queue.

## exit

Close player.

* `Usage: exit`
