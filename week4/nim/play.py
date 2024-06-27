from nim import train, play

ai = train(10000)
for (state, action), q in ai.q.items():
    print(state, action, "->", q)

    
play(ai)
