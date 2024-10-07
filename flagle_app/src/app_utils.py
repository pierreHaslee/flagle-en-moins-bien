

def display_difficulty(diff):
    if diff == 0:
        return 'Beginner *(countries with pop.>50M)*'
    if diff == 1:
        return 'Easy *(countries with pop.>100k)*'
    if diff == 2:
        return 'Medium *(countries with pop.>30k)*'
    if diff == 3:
        return 'Hard *(countries with pop.>5k)*'
    if diff == 4:
        return 'Hardcore (everything territory with a flag)'