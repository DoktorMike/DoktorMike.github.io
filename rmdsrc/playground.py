import tensorflow as tf
import edward as ed
import pandas as pd
import numpy as np
from ggplot import *
from edward.models import Normal, Bernoulli
import matplotlib.pyplot as plt

def visualise(X_data, y_data, w, b, n_samples=10):
  w_samples = w.sample(n_samples).eval()
  b_samples = b.sample(n_samples).eval()
  plt.scatter(X_data, y_data)
  inputs = np.linspace(1e6, 4e6, num=400)
  inputs = np.linspace(-3, 3, num=400)
  for ns in range(n_samples):
    output = inputs * w_samples[ns] + b_samples[ns]
    plt.plot(inputs, output)

mydf = pd.read_csv("../humanglobwarm.csv")
mydf["PassengersNorm"]=(mydf["Passengers"]-mydf["Passengers"].mean())/mydf["Passengers"].std()

N = mydf.shape[0]
D = mydf.shape[1]

#initpasmu = tf.zeros(N)+mydf["Passengers"].values.reshape(N)
# Define the model
#z_mu = Normal(mu=tf.zeros(N), sigma=1*tf.ones([]))
#z = Normal(mu=z_mu, sigma=1*tf.ones([]))

w = Normal(mu=1*tf.zeros([]), sigma=0.1 * tf.ones([]))
b = Normal(mu=1*tf.zeros([]), sigma=0.1 * tf.ones([]))

#x_mu = Normal(mu=tf.multiply(z_mu, w) + b, sigma=0.5*tf.ones([]))
#x = Normal(mu=x_mu, sigma=0.1*tf.ones([]))

z = tf.placeholder(tf.float32, [N, 1])
x = Normal(mu=tf.multiply(z, w) + b, sigma=0.1*tf.ones(1))

# VI placeholder
#qz_mu = Normal(mu=tf.Variable(tf.zeros(N)), sigma=tf.nn.softplus(tf.Variable(1*tf.ones(N))))
#qx_mu = Normal(mu=tf.Variable(tf.zeros(N)), sigma=tf.nn.softplus(tf.Variable(0.5*tf.ones(N))))
qw = Normal(mu=tf.Variable(tf.random_normal([1], 0, 1)),
            sigma=tf.nn.softplus(tf.Variable(1*tf.random_normal([1]))))
qb = Normal(mu=tf.Variable(tf.random_normal([1], 0, 1)),
            sigma=tf.nn.softplus(tf.Variable(1*tf.random_normal([1]))))
# Set up data and the inference method to Kullback Leibler
z_train = mydf.get("PassengersNorm").reshape([N,1])
x_train = mydf.get("Tempdev").reshape([N,1])
sess = ed.get_session()
data = {x: x_train[:,0], z: z_train[:,0]}
#inference = ed.KLqp({x_mu: qx_mu, z_mu: qz_mu, w: qw, b: qb}, data)
inference = ed.KLqp({w: qw, b: qb}, data)

# Set up for samples from models
mus = []
for i in range(10):
    mus += [qw.sample()]

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
#ggplot(priordf, aes(y="value", x="variable", color="Sample")) + geom_line()
priordf['Type']='Prior'

visualise(mydf["PassengersNorm"], mydf["Tempdev"], w, b)
plt.show()

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
#ggplot(postdf, aes(y="value", x="variable", color="Sample")) + geom_line()
postdf['Type']='Posterior'

visualise(mydf["PassengersNorm"], mydf["Tempdev"], qw, qb)
plt.show()

# One glorious data frame for export
tmpdf = pd.concat([priordf, postdf])
tmpdf.to_csv("errorcorrsamplesdf.csv")
