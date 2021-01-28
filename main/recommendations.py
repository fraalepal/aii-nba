from main.models import Equipo, Jugador, Puntuacion
from collections import Counter
import shelve

#encoding:utf-8

from math import sqrt

# Returns a distance-based similarity score for person1 and person2
def sim_distance(prefs, person1, person2):
    # Get the list of shared_items
    si = {}
    for item in prefs[person1]: 
        if item in prefs[person2]: si[item] = 1

        # if they have no ratings in common, return 0
        if len(si) == 0: return 0

        # Add up the squares of all the differences
        sum_of_squares = sum([pow(prefs[person1][item] - prefs[person2][item], 2) 
                    for item in prefs[person1] if item in prefs[person2]])
        print(sum_of_squares)
        return 1 / (1 + sum_of_squares)

# Returns the Pearson correlation coefficient for p1 and p2
def sim_pearson(p1, p2):
    # Get the list of mutually rated items
    si = {}
    #Extraigo las preferencias de los usuarios y relleno la lita de jugadores mutuamente votados.
    pref_p1 = Puntuacion.objects.filter(usuario=p1)
    pref_p2 = Puntuacion.objects.filter(usuario=p2)
    for item in pref_p1:
        for item2 in pref_p2:
            if item.jugador == item2.jugador:
                si[item.jugador] = 1

    # if they are no ratings in common, return 0
    if len(si) == 0: return 0

    # Sum calculations
    n = len(si)

    # Sums of all the preferences
    sum1 = sum([pref_p1.filter(jugador=it).first().valor for it in si])
    sum2 = sum([pref_p2.filter(jugador=it).first().valor for it in si])

    # Sums of the squares
    sum1Sq = sum([pow(pref_p1.filter(jugador=it).first().valor, 2) for it in si])
    sum2Sq = sum([pow(pref_p2.filter(jugador=it).first().valor, 2) for it in si])

    # Sum of the products
    pSum = sum([pref_p1.filter(jugador=it).first().valor * pref_p2.filter(jugador=it).first().valor for it in si])

    # Calculate r (Pearson score)
    num = pSum - (sum1 * sum2 / n)
    den = sqrt((sum1Sq - pow(sum1, 2) / n) * (sum2Sq - pow(sum2, 2) / n))
    if den == 0: return 0

    r = num / den

    return r

# Returns the best matches for person from the prefs dictionary. 
# Number of results and similarity function are optional params.
def topMatches(prefs, person, n=5, similarity=sim_distance):
    scores = [(similarity(prefs, person, other), other) 
                for other in prefs if other != person]
    scores.sort()
    scores.reverse()
    return scores[0:n]

# Gets recommendations for a person by using a weighted average of every other user's rankings
def getRecommendations(person, similarity=sim_pearson):
    totals = {}
    simSums = {}
    #Extraigo las preferencias
    puntuaciones = Puntuacion.objects.all()
    for other in puntuaciones:
        # don't compare me to myself
        if other.usuario == person: continue
        sim = similarity(person, other.usuario)
        # ignore scores of zero or lower
        if sim <= 0: continue
        pref_p1 = Puntuacion.objects.filter(usuario=person)
        pref_p2 = Puntuacion.objects.filter(usuario=other.usuario)
        for item in pref_p2:
            jugador = item.jugador
            # only score jugadores I haven't seen yet
            if pref_p1.filter(jugador=jugador).first() == None:
                # Similarity * Score
                totals.setdefault(item.jugador.id, 0)
                totals[item.jugador.id] += item.valor * sim
                # Sum of similarities
                simSums.setdefault(item.jugador.id, 0)
                simSums[item.jugador.id] += sim

    # Create the normalized list
    rankings = [(total / simSums[item], item) for item, total in totals.items()]
    # Return the sorted list
    rankings.sort()
    rankings.reverse()
    return rankings


