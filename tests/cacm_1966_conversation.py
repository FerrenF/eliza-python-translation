cacm_1966_conversation = [
    # // --- exact conversation quoted in Weizenbaum's 1966 CACM article ---

    { "Men are all alike.",
      "IN WHAT WAY" },

    { "They're always bugging us about something or other.",
      "CAN YOU THINK OF A SPECIFIC EXAMPLE" },

    { "Well, my boyfriend made me come here.",
      "YOUR BOYFRIEND MADE YOU COME HERE" },

    { "He says I'm depressed much of the time.",
      "I AM SORRY TO HEAR YOU ARE DEPRESSED" },

    { "It's true. I am unhappy.",
      "DO YOU THINK COMING HERE WILL HELP YOU NOT TO BE UNHAPPY" },

    { "I need some help, that much seems certain.",
      "WHAT WOULD IT MEAN TO YOU IF YOU GOT SOME HELP" },

    { "Perhaps I could learn to get along with my mother.",
      "TELL ME MORE ABOUT YOUR FAMILY" },

    { "My mother takes care of me.",
      "WHO ELSE IN YOUR FAMILY TAKES CARE OF YOU" },

    { "My father.",
      "YOUR FATHER" },

    { "You are like my father in some ways.",
      "WHAT RESEMBLANCE DO YOU SEE" },

    # // In the CACM article, the following prompt contained no comma.
    # // Without the comma, this simulation responds "WHAT MAKES YOU
    # // THINK I AM NOT VERY AGGRESSIVE BUT YOU THINK I DON'T WANT YOU TO
    # // NOTICE THAT". I assume the comma got lost from the CACM article.
    # //{ "You are not very aggressive, but I think you don't want me to notice that.",
    # //
    # // UPDATE: We now have a version of Weizenbaum's original MAD-SLIP
    # // source code where we see that the word "BUT" is also considered
    # // to be a delimiter. So I was wrong to assume a missing comma.
    { "You are not very aggressive but I think you don't want me to notice that.",
      "WHAT MAKES YOU THINK I AM NOT VERY AGGRESSIVE" },

    { "You don't argue with me.",
      "WHY DO YOU THINK I DON'T ARGUE WITH YOU" },

    { "You are afraid of me.",
      "DOES IT PLEASE YOU TO BELIEVE I AM AFRAID OF YOU" },

    { "My father is afraid of everybody.",
      "WHAT ELSE COMES TO MIND WHEN YOU THINK OF YOUR FATHER" },

    { "Bullies.",
      "DOES THAT HAVE ANYTHING TO DO WITH THE FACT THAT YOUR BOYFRIEND MADE YOU COME HERE" },

    # // --- end of 1966 CACM article conversation ---
];