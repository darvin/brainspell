Brain Spell it the game about sorcerers' competition. Each player is sorcerer that try to summon demon. To summon demon, you need to say it name. For this, you must print it, using roboghosts.

Ghosts are execution pointers of [BrainFuck](http://en.wikipedia.org/wiki/Brainfuck) programming language. You can use operators of BrainFuck and some additional operators:

 - `>` increment the data pointer (to point to the next cell to the right).
 - `<` decrement the data pointer (to point to the next cell to the left).
 - `+` increment (increase by one) value at the data pointer.
 - `-` decrementment (decrease by one) value at the data pointer.
 - `.` output a character, that matches data at the data pointer. ` ` matches `0`, `A` mathes `1`, ... , `Z` matches `26`
 - `,` gets letter from current cell in game map and stores integer that it maches to data at the data pointer
 - `[` if the byte at the data pointer is zero, then instead of moving the theinstruction pointer forward to the next command, jump it forward to the command after the matching `]` command.
 - `]` if the byte at the data pointer is nonzero, then insteadstead of moving the instruction pointer forward to the next command, jump it back to the command after the matching `[` command.
 - `/` turns ghost clockwise
 - `\` turns ghost anticlockwise

Also, each player can cast spells.
