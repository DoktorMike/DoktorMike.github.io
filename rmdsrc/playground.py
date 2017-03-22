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

initpasmu = tf.zeros(N)+mydf["Passengers"].values.reshape(N)
# Define the model
z_mu = Normal(mu=initpasmu, sigma=1e6*tf.ones([]))
z = Normal(mu=z_mu, sigma=1e6*tf.ones([]))

x_mu = Normal(mu=tf.zeros(N), sigma=0.5*tf.ones([]))
x = Normal(mu=x_mu, sigma=0.1*tf.ones([]))

# VI placeholder
qz_mu = Normal(mu=tf.Variable(initpasmu), sigma=tf.nn.softplus(tf.Variable(1e6*tf.ones(N))))
qx_mu = Normal(mu=tf.Variable(tf.zeros(N)), sigma=tf.nn.softplus(tf.Variable(0.5*tf.ones(N))))

# Set up data and the inference method to Kullback Leibler
z_train = mydf.get("Passengers").reshape([N,1])+0.1
x_train = mydf.get("Tempdev").reshape([N,1])
sess = ed.get_session()
data = {x: x_train[:,0], z: z_train[:,0]}
inference = ed.KLqp({x_mu: qx_mu, z_mu: qz_mu}, data)

# Set up for samples from models
mus = []
for i in range(10):
    mus += [qz_mu.sample()]

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
priordf['Sample']=["Sample"+str(x) for x in list(range(10))]
priordf=pd.melt(priordf, id_vars="Sample")
ggplot(priordf, aes(y="value", x="variable", color="Sample")) + geom_line()
priordf['Type']='Prior'

# Run Inference
for _ in range(inference.n_iter):
  info_dict = inference.update()
  inference.print_progress(info_dict)

inference.finalize()

# Posterior samples
outputs = mus.eval()
postdf=pd.DataFrame(outputs)
postdf['Sample']=["Sample"+str(x) for x in list(range(10))]
postdf=pd.melt(postdf, id_vars="Sample")
ggplot(postdf, aes(y="value", x="variable", color="Sample")) + geom_line()
postdf['Type']='Posterior'

# One glorious data frame for export
tmpdf = pd.concat([priordf, postdf])
tmpdf.to_csv("errorcorrsamplesdf.csv")
