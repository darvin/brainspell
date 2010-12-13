Brain Spell is the game about sorcerers' competition. Each player is a sorcerer which tries to summon a demon. To summon a demon, you need to spell its name, by printing it, using roboghosts.

Ghosts are execution pointers of [BrainFuck](http://en.wikipedia.org/wiki/Brainfuck) dialect programming language. Used dialect look similiar [Brainloller](http://esoteric.voxelperfect.net/wiki/Brainloller) - 2d dialect of Brainfuck.


You can use operators of BrainFuck and some additional operators:

 - `>` increment the data pointer (to point to the next cell to the right).
 - `<` decrement the data pointer (to point to the next cell to the left).
 - `+` increment (increase by one) value at the data pointer.
 - `-` decrementment (decrease by one) value at the data pointer.
 - `.` output a character, that matches data at the data pointer. ` ` matches `0`, `A` mathes `1`, ... , `Z` matches `26`
 - `,` gets letter from the current cell in the game map and stores integer that maches with data at the data pointer
 - `[` if the byte at the data pointer is zero, then instead of moving the instruction pointer forward to the next command, jump it forward to the command after the matching `]` command.
 - `]` if the byte at the data pointer is nonzero, then instead of moving the instruction pointer forward to the next command, jump it back to the command after the matching `[` command.
 - `/` turns the ghost clockwise
 - `\` turns the ghost anticlockwise

When searching for matching `]` operator, the north/east/south/west path is traversed the same way as the IP does.
When searching for matching `[` operator, the north/east/south/west path is traversed the opposite way as the IP does.
Also, each player can cast spells. Spells costs mana, mana restores every second.
