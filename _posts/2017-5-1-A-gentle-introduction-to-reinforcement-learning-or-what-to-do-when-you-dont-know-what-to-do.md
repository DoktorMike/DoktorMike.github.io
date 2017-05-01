---
title: "A gentle introduction to reinforcement learning or what to do when you don't know what to do"
author: "Dr. Michael Green"
date: "May 1, 2017"
output: html_document
layout: post
published: true
status: publish
use_math: true
---


# Introduction
Today we're going to have a look at an interesting set of learning algorithms which does not require you to know the truth while you learn. As such this is a mix of unsupervised and supervised learning. The supervised part comes from the fact that you look in the rear view mirror after the actions have been taken and then adapt yourself based on how well you did.

```python
def discount_rewards(r, gamma=1-0.99):
    df = np.zeros_like(r)
    for t in range(len(r)):
        df[t] = np.npv(gamma, r[t:len(r)])
    return df

def sigmoid(x):
    return 1.0/(1.0+np.exp(-x))

def dsigmoid(x):
    a=sigmoid(x)
    return a*(1-a)

def decide(b, x):
    return sigmoid(np.vdot(b, x))

def loglikelihood(y, p):
    return y*np.log(p)+(1-y)*np.log(1-p)

def weighted_loglikelihood(y, p, dr):
    return (y*np.log(p)+(1-y)*np.log(1-p))*dr

def loss(y, p, dr):
	return -weighted_loglikelihood(y, p, dr)

def dloss(y, p, dr, x):
    return np.reshape(dr*( (1-np.array(y))*p - y*(1-np.array(p))), [len(y),1])*x
```


![plot of all possible solutions](/images/figure/solutiondistribution.png)

# Conclusion

Happy inferencing!
