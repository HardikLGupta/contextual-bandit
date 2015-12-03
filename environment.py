import sys
import csv
import numpy as np
import matplotlib.pyplot as plt
import time
import random
import logging
logger = logging.getLogger('Environment')

seed = int(time.time())
np.random.seed(seed)
logger.info('Numpy Random seed = {0}'.format(seed))

from functools import reduce

import colorama
colorama.init()

def red(s):
    return(colorama.Fore.RED + s.__str__() + colorama.Fore.WHITE)

def uni(x):
    return x/np.sqrt((x*x).sum())

class ucb_settings:
    def __init__(self, **s):
        self.__dict__ = s
        
    def __str__(self):
        return '\n'.join([str(k) + ' ' + str(v) for k, v in self.__dict__.items()])

def contextual_cascading_monkey(L=20, K=4, d=10, gamma=0.95, eps=0.1, v=0.35, disj=False):
    logger.info('Initializing environment "Monkey Contextual"')
    arms = [idx for idx in range(L)]
    x = {arm:np.random.uniform(0, 1, d) for arm in arms}
    theta = v * uni(np.random.uniform(0, 1, d))
    xt = {arm:x[arm] for arm in x}
    def environment(recommend=None):
        if recommend == None:
            for arm in xt:
                xt[arm] = uni(x[arm] + np.random.uniform(-v, v, d))
            return xt
        else:
            assert(len(recommend) <= K)
            print(sorted([theta.dot(xt[arm]) for arm in arms])[::-1])
            print(red([theta.dot(xt[arm]) for arm in recommend]))
            for c, arm in enumerate(recommend): 
                p = theta.dot(xt[arm]) + np.random.normal(0, eps)
                if (np.random.uniform(0, 1) < p) ^ disj:
                    return gamma ** c * int(not disj), c
            return int(disj), len(recommend)
    logger.info('Initialized environment "Monkey Contextual"')
    return environment, ucb_settings(arms=arms, K=K, d=d, gamma=gamma, theta=theta)

def movielens(candidates, userno=1):
    logger.info('Initializing environment "Movielens"')
    records = {}
    with open('ratings.csv') as fp:
        r = csv.reader(fp, delimiter=',', quotechar='"')
        for idx, tpl in enumerate(r):
            if idx == 0:
                continue
            user, movie, rate, _ = tpl
            if not int(movie) in candidates:
                continue 
            try:
                records[int(user)].append(int(movie))
            except:
                records[int(user)] = [int(movie)]
    with open('tags.csv') as fp:
        r = csv.reader(fp, delimiter=',', quotechar='"')
        for idx, tpl in enumerate(r):
            if idx == 0:
                continue
            user, movie, tag, _ = tpl
            if not int(movie) in candidates:
                continue
            try:
                records[int(user)].append(int(movie))
            except:
                records[int(user)] = [(int(movie))]

    total = len(records)
    # leave those who have viewed at least one candidates
    eligable_users = set(records.keys())
    logger.info('#Total eligabli users = {0}'.format(len(eligable_users)))
    logger.info('#Users participated ea/round = {0}'.format(userno))
    def environment(recommend):
        users = random.sample(eligable_users, userno)
        movies = reduce(set.union, [set(records[user]) for user in users])
        logger.debug('Received recommendation {0}'.format(recommend))
        logger.debug('User ctr history {0}'.format(movies))
        for idx, movie in enumerate(recommend):
            if movie in movies:
                return idx
        return float('Inf')
    logger.info('Initializing environment "Movielens" done')
    return environment

def movielens_chrono():
    print('Initializing environment "Movielens-chrono"')
    records = {}
    tts = []
    with open('ratings.csv') as fp:
        r = csv.reader(fp, delimiter=',', quotechar='"')
        for idx, tpl in enumerate(r):
            if idx == 0:
                continue
            user, movie, rate, t = tpl
            tts.append(int(t))
            try:
                records[int(user)].append((int(t), int(movie)))
            except:
                records[int(user)] = [((int(t), int(movie)))]
    with open('tags.csv') as fp:
        r = csv.reader(fp, delimiter=',',quotechar='"')
        for idx, tpl in enumerate(r):
            if idx == 0:
                continue
            user, movie, tag, t = tpl
            tts.append(int(t))
            try:
                records[int(user)].append((int(t), int(movie)))
            except:
                records[int(user)] = [((int(t), int(movie)))]

    stts = sorted(tts)
    start = stts[10000]
    end = stts[-1000]
    interval = 86400
    del tts
    del stts

    rng = np.random.RandomState(100)
    tt = max(records)
    for i in range(1, tt + 1):
        records[i] = sorted(records[i])

    t = [start]
    def environment(recommend):
        t[0] += interval
        user = rng.randint(tt) + 1
        movies = [x[1] for x in records[user] if x[1] < t[0]]
        print('Environment: Time: {0}'.format(time.strftime("%Y/%m/%d", time.localtime(t[0]))))
        print('Environment: Received recommendation {0}'.format(recommend))
        print('Environment: User ctr history {0}'.format(movies))
        for idx, movie in enumerate(recommend):
            if movie in movies:
                return idx
        return float('Inf')
    print('Initializing environment "Movielens-chrono" done')
    return environment
