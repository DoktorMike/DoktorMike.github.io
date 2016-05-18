---
title: "Implementing predictive sales modeling"
author: "Dr. Michael Green"
date: "May 18, 2016"
output: html_document
layout: post
published: true
status: publish
use_math: true
---


*S*ales modeling has long been used by clients and media
agencies around the world to create insights regarding their historical
performance. Most of the efforts have been focused around retrospective
projects measuring soft KPI’s, e.g., awareness, liking, penetration etc.
In this white paper we’re introducing a new paradigm for implementing a
real-time continuous sales modeling setup which can deliver updated
learnings and clear-cut recommendations at the time where they’re
needed.**

Background {#background .unnumbered}
==========

In todays media market, with an abundance of data yet few inferred
actionable insights, there’s no longer a question of whether or not you
should do sales modeling. Rather, it’s a question of how to get started.
To the modern CMO the concept of sales modeling, along it’s obvious
benefits, is well known. Since it’s based on the scientific method, an
implemented sales model can function as a fact based decision support
tool for marketeers. Yet, most businesses today does not currently use a
sales modeling agency. The reasons for this are many but most of them
can be nailed down to the following key hurdles:

Cost

:   Building a sales model requires a lot of resources in the shape of
    staff, data wrangling, and key stakeholders. Often you as a client
    is required to collect, consolidate, clean and deliver diverse data
    sources across your organization.

Complexity

:   The statistical modeling theory behind validating a model can be, to
    say the least, overwhelming for non specialists. For this reason you
    need dedicated fully trained data scientists to develop
    useful models.

Time consuming

:   Every useful model have a lot of parameters to tune. In traditional
    sales models these are tuned by experts every time a new project
    is launched. Tuning these parameters, while maintaining model
    robustness, is hard and usually requires weeks of the data
    scientist’s time.

Slow time-to-market

:   Typically a realistic sales modeling project takes between 4-6 weeks
    to deliver the results after the data has been aquired
    and validated. It’s not uncommon that by the time the CMO reads the
    report with the modeling insights the results are over 6 months old.

We live in exciting times. There’s more data, as well as affordable
computational power, available than ever before. As a consequence a new
statistical learning paradigm has started to blossom. This new paradigm
is called being Bayesian @kruschke2015doing and basically refers to the
way we make inferences from existing data. Now what’s really neat about
this approach is that it enables us to make explicit predictions taking
all the uncertainty into account from our parameters.

Being Bayesian is good {#being-bayesian-is-good .unnumbered}
----------------------

The ever increasing interest in Bayesian statistics @gelman2013bayesian
has led not only to extensive research in Bayesian methodology but also
to the use of the Bayesian paradigm to address tough challenges in
rather diverse domains such as astrophysics, weather forecasting, health
care policy, and of course media.

The hypotheses related to these challenges in media are typically
expressed through probability distributions for observable domain
specific data. These probability distributions depend on a set of
unknown quantities called parameters. Let’s call all of these parameters
$\theta$. In the Bayesian paradigm, current knowledge about the model
parameters is expressed by placing a probability distribution on the
parameters. This distribution is known as the “prior distribution”,
which is mathematically denoted by $p(\theta)$. The word stems from the
fact that it expresses our beliefs about the parameters prior to
observing any evidence(data) that supports it.

As data $y$ become available, the information they bring to the table
about the nature of the model parameters is expressed in something
called the “likelihood,” which is proportional to the distribution of
the observed data given the model parameters, written as
$p(y\vert\theta)$. In more plain English the likelihood tells us
something about how likely we are to observe that specific data given
the set of parameter values. As the data is fixed the only thing we can
vary are the parameters $\theta$, which means that the larger the
likelihood the more consistent our parameter choice is with the observed
data.

This information is then combined with the prior to produce an updated
probability distribution called the “posterior distribution,” on which
all Bayesian inference is based. Bayes’ Theorem, an elementary identity
in probability theory, states how the update is done mathematically: the
posterior is proportional to the prior times the likelihood, or more
precisely,

$$p\left(\theta\vert y\right)=\frac{p\left(\theta\right)p\left(y\vert\theta\right)}{\int_\theta p\left(\theta\right)p\left(y\vert\theta\right)d\theta}$$

Eventhough the posterior distribution is in principle always available,
the resulting analytic computations are often intractable in any
realistically complex model. It has been realized that the ability to
sample from this distribution is what we really want to be doing.

The remedy {#the-remedy .unnumbered}
==========

So far I hope you’ve all jumped on the Bayesian train and agree with me
that this provides us with an intuitive and scientifically correct
approach. There can be no inference without assumption. So how does all
of this help existing businesses jump the sales modeling hurdle? Well,
to be fair, the Bayesian approach is only part of the solution. Let’s
attach the obstacles one by one.

Cost {#cost .unnumbered}
----

Truth be told, there is no skipping the initial phase of consolidating
your data and chasing down the right people in your business
intelligence department. The key to keeping the costs to a minimum is
automation. This automation should consist of an ETL @wiki:etl process
running continuously in your environment. This makes sure that data is
gathered and consolidated as often as you need withouth manual
intervention. It could, and should, also contain the responsibility of
sending the data to the right place. Never, ever assign the task, of
sending data to your analytics partner, to a human. Us humans are
wonderful beings and excel at so many things. Keeping track of data and
being consistent however, is not one of them. Keep this in mind.

Complexity {#complexity .unnumbered}
----------

Before diving into the remedy and the solution let’s revisit why I claim
that building a predictive model is a complex process. After all, there
are numerous statistical softwares around that are able to produce a
model given any kind of data you throw at it, right? Well, not quite.
It’s true that all of that software can produce a model. It’s just that
without an expert tuning that model, what comes out of the process is
pure nonsense. Consider this; Any reasonably sized sales model contains
at least 30 to 60 variables accompanied by at least 60 to 180
parameters. Most sales models operate on weekly numbers allowing us to
get access to 156 observation points given that we collect the last
three years of history. Best case scenario you have 2.6 data points per
parameter providing a rather poor evidence base for your inference.
Worst case you end up with an underdetermined problem.
Underdetermination refers to situations where the evidence available is
insufficient to identify which belief we should hold about that
evidence. Basically it means that mathematically this problem is not
possible to solve. All of this can be solved today but it requires years
of training in the domain of statistical learning theory and machine
learning. Therefor it is wise to leave it to the experts.

Time consuming {#time-consuming .unnumbered}
--------------

Remember all of those parameters we talked about before? Well there’s
more to it and of why they are massively difficult to tune.

1.  They are mostly continuous parameters meaning that they have an
    infinite amount of values to assume. In practice they are not
    infinite though as they can be diveded into ranges that are for all
    purposes equal. This is called region of practical
    equivalence (ROPE).

2.  They are not independent which is short for saying that the specific
    value of one of them depends on one or several of the
    other parameters. This is not good news since it means that we
    cannot optimize them one by one.

3.  They introduce the curse of dimensionality into the mix. To
    understand what this is imagine we have one variable which can
    assume 10 possible values. This is known as a one dimensional
    problem and all we have to do is to evaluate each of the 10 values
    and select the best one. Easy enough. Now suppose we have another
    variable which can also assume 10 possible values. Now we have
    $10\times10=100$ possible configurations to search through.
    Following the same logic, imagine that we have $M$ variables each
    featuring D possible values. This would result in $D^M$
    possible configurations. Plugging our situation into this equation
    would yield $10^{30}$ possibilities. That’s 100 billion times as
    many configurations as there are grains of sand on earth.

Due to these challenges and the vast experience required to tune
statistical models it is something best left outsourced unless you have
a large team of highly skilled data scientists inhouse.

Slow time-to-market {#slow-time-to-market .unnumbered}
-------------------

Any running sales model is only as good as the just-in-time learnings it
can deliver. For this reason you need a platform where you can leverage
the insights from the model and turn it into actionable conclusions.
This platform should enable you to do the following:

-   Explaining what happened to sales last week and why by presenting
    you with a decomposition of the total sales into all the responsible
    sales drivers

-   Track the performance of your current campaigns in real hard core
    KPI’s such as sales, profit and revenue

-   Plan your future campaigns based on the predicted effect of your
    running sales model

-   Submit your campaign plan for execution

This requires that data is updated and delivered on a daily basis and
that the platform is able to refit, test and deploy the updated model
quickly. Then and only then are you truly sitting in your KPI cockpit
with an actionable overview of your media performance.

Conclusion {#conclusion .unnumbered}
==========

In this paper we discussed the major hurdles most companies are facing
today when implementing predictive sales modeling. These hurdles can be
overcome by replacing a lot of manual processes by automatic ETL jobs
and clever Bayesian modeling setups. Hopefully you’re convinced that
introducing sales modeling into your everyday decison making process is
a good idea. Trust me, it’ll be the smartest decision you’ll ever make.
