import tensorflow as tf
import edward as ed
import pandas as pd
import numpy as np
from ggplot import *
from edward.models import Normal, Bernoulli
import matplotlib.pyplot as plt

mydf = pd.read_csv("../humanglobwarm.csv")

N = mydf.shape[0]
D = mydf.shape[1]

#z = tf.placeholder(tf.float32)
x_mu = Normal(mu=tf.zeros(N), sigma=1*tf.ones([]))
x = Normal(mu=x_mu, sigma=0.1*tf.ones([]))

qx_mu = Normal(mu=tf.Variable(tf.zeros(N)), sigma=tf.nn.softplus(tf.Variable(tf.ones(N))))

x_train = mydf.get("Tempdev").reshape([N,1])
sess = ed.get_session()
data = {x: x_train[:,0]}
inference = ed.KLqp({x_mu: qx_mu}, data)

# Set up for samples from models
mus = []
for i in range(10):
    mus += [qx_mu.sample()]

mus = tf.stack(mus)

# Inference: Quick way - No Priors possible
# inference.run()

# Inference: More controlled way of inference running
inference.initialize(n_print=10, n_iter=600)
init = tf.global_variables_initializer()
init.run()

# Prior samples
outputs = mus.eval()
priordf=pd.DataFrame(outputs)
#mydf.to_csv("mydfprior.csv")
#priordf['Sample']=list(range(10))
priordf['Sample']=["Sample"+str(x) for x in list(range(10))]
ggplot(pd.melt(priordf, id_vars="Sample"), aes(y="value", x="variable", color="Sample")) + geom_line()

# Run Inference
for _ in range(inference.n_iter):
  info_dict = inference.update()
  inference.print_progress(info_dict)

inference.finalize()

# Posterior samples
outputs = mus.eval()
postdf=pd.DataFrame(outputs)
#mydf.to_csv("mydfpost.csv")
#postdf['Sample']=list(range(10))
postdf['Sample']=["Sample"+str(x) for x in list(range(10))]
ggplot(pd.melt(postdf, id_vars="Sample"), aes(y="value", x="variable", color="Sample")) + geom_line()
