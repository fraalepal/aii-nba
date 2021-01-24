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
def sim_pearson(user1, user2):
    # Get the list of mutually rated items
    si = {}
    pref_user1 = Puntuacion.objects.filter(usuario=user1)
    pref_user2 = Puntuacion.objects.filter(usuario=user2)
    for item in pref_user1:
        for item2 in pref_user2:
            if item.jugador == item2.jugador:
                si[item.jugador] = 1

    # if they are no ratings in common, return 0
    if len(si) == 0: return 0

    # Sum calculations
    n = len(si)

    # Sums of all the preferences
    sum1 = sum([pref_user1.filter(jugador=it).first().valor for it in si])
    sum2 = sum([pref_user2.filter(jugador=it).first().valor for it in si])

    # Sums of the squares
    sum1Sq = sum([pow(pref_user1.filter(jugador=it).first().valor, 2) for it in si])
    sum2Sq = sum([pow(pref_user2.filter(jugador=it).first().valor, 2) for it in si])

    # Sum of the products
    pSum = sum([pref_user1.filter(jugador=it).first().valor * pref_user2.filter(jugador=it).first().valor for it in si])

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
def getRecommendations(user1, similarity=sim_pearson):
    totals = {}
    simSums = {}
    all = Puntuacion.objects.all()
    for other in all:
        # don't compare me to myself
        if other.usuario == user1: continue
        sim = similarity(user1, other.usuario)
        # ignore scores of zero or lower
        if sim <= 0: continue
        pref_user1 = Puntuacion.objects.filter(usuario=user1)
        pref_user2 = Puntuacion.objects.filter(usuario=other.usuario)
        for item in pref_user2:
            jugador = item.jugador
            # only score ropa I haven't seen yet
            if pref_user1.filter(jugador=jugador).first() == None:
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

def transformPrefs(prefs):
    result = {}
    for person in prefs:
        for item in prefs[person]:
            result.setdefault(item, {})
    
            # Flip item and person
            result[item][person] = prefs[person][item]
    return result


def calculateSimilarItems(prefs, n=10):
    # Create a dictionary of items showing which other items they
    # are most similar to.
    result = {}
    # Invert the preference matrix to be item-centric
    itemPrefs = transformPrefs(prefs)
    c = 0
    for item in itemPrefs:
        # Status updates for large datasets
        c += 1
        if c % 100 == 0: print ("%d / %d" % (c, len(itemPrefs)))
        # Find the most similar items to this one
        scores = topMatches(itemPrefs, item, n=n, similarity=sim_distance)
        result[item] = scores
    return result

def getRecommendedItems(prefs, itemMatch, user):
    userRatings = prefs[user]
    scores = {}
    totalSim = {}
    # Loop over items rated by this user
    for (item, rating) in userRatings.items():
        # Loop over items similar to this one
        for (similarity, item2) in itemMatch[item]:
            print (item2)
            # Ignore if this user has already rated this item
            if item2 in userRatings: continue
            # Weighted sum of rating times similarity
            scores.setdefault(item2, 0)
            scores[item2] += similarity * rating
            # Sum of all the similarities
            totalSim.setdefault(item2, 0)
            totalSim[item2] += similarity

    # Divide each total score by total weighting to get an average
    try:
        rankings = [(score / totalSim[item], item) for item, score in scores.items()]
    except ZeroDivisionError:
        rankings = []

    # Return the rankings from highest to lowest
    rankings.sort()
    rankings.reverse()
    return rankings

