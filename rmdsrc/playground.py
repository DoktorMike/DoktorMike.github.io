import tensorflow as tf
import edward as ed
import pandas as pd

from edward.models import Normal, Bernoulli
from edward.stats import bernoulli, norm

mydf = pd.read_csv("../humanglobwarm.csv")

x = tf.placeholder(tf.float32)
z = Normal(mu=)
