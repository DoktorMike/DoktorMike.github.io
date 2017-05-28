---
title: "About identifiability and granularity"
author: "Dr. Michael Green"
date: "May 6, 2017"
output: html_document
layout: post
published: true
status: publish
use_math: true
---
 
 

 
# Motivation for this post
 
In time series modeling you typically run into issues concerning complexity versus utility. What I mean by that is that there may be questions you need the answer to but are afraid of the model complexity that comes along with it. This fear of complexity is something that relates to identifiability and the curse of dimensionality. Fortunately for us probabilistic programming can handle these things neatly. In this post we're going to look at a problem where we have a choice between a granular model and an aggregated one. We need to use a proper probabilistic model that we will sample in order to get the posterior information we are looking for.
 
# The generating model
 
In order to do this exercise we need to know what we're doing and as such we will generate the data we need by simulating a stochastic process. I'm not a big fan of this since simulated data will always be, well simulated, and as such not very realistic. Data in our real world is not random people. This is worth remembering, but as the clients I work with on a daily basis are not inclined to share their precious data, and academic data sets are pointless since they are almost exclusively too nice to represent any real challenge I resort to simulated data. It's enough to make my point. So without further ado I give you the generating model.
 
$$ \begin{align}
y_t &\sim N(\mu_t, 7)\\
\mu_t &= x_t + 7 z_t\\
x_t &\sim N(3, 1)\\
z_t &\sim N(1, 1)
\end{align} $$
 
which is basically a gaussian mixture model. So that represents the ground truth. The time series generated looks like this
 
![plot of chunk problemplot12](/images/figure/problemplot12-1.png)
 
where time is on the x axis and the response variable on the y axis. The first few lines of the generated data are presented below.
 

|  t|         y|        x|          z|
|--:|---------:|--------:|----------:|
|  0| 20.411003| 2.314330|  1.0381077|
|  1| 22.174020| 2.512780|  1.5292838|
|  2| -5.035160| 2.048367| -0.1099282|
|  3|  1.580412| 1.627389|  1.2106257|
|  4| -5.391217| 4.924959| -0.4488093|
|  5| -1.360732| 3.237641| -0.1645335|
 
So it's apparent that we have three variables in this data set; the response variable $y$, and the covariates $x$ and $z$ ($t$ is just an indicator of a fake time). So the real model is just a linear model of the two variables. Now say that instead we want to go about solving this problem and we have two individuals arguing about the best solution. Let's call them Mr. Granularity and Mr. Aggregation. Now Mr. Granularity is a fickle bastard as he always wants to split things into more fine grained buckets. Mr. Aggregation on the other hand is more kissable by nature. By that I'm refering to the Occam's razor version of kissable, meaning "Keep It Simple Sir" (KISS). 
 
This means that Mr. Granularity wants to estimate a parameter for each of the two variables while Mr. Aggregation wants to estimate one parameter for the sum of $x$ and $z$.
 
# Mr. Granularity's solution
 
So let's start out with the more complex solution. Mathematically Mr. Granularity defines the probabilistic model like this
 
$$ \begin{align}
y_t &\sim N(\mu_t, \sigma)\\
\mu_t &=\beta_x x_t + \beta_z z_t + \beta_0\\ 
\beta_x &\sim N(0, 5)\\
\beta_z &\sim N(0, 5)\\
\beta_0 &\sim N(0, 5)\\
\sigma &\sim U(0.01, \inf) 
\end{align} $$
 
which is implemented in Stan code below. There's nothing funky or noteworthy going on here. Just a simple linear model. 
 

 
 


















