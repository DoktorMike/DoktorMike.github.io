---
title : Deep Neural Networks in Julia - Love at first sight?
author : Michael Green
date : January 10, 2018
---



# Motivation

I love new initiatives that tries to do something new and innovative. The relatively new language Julia is one of my favorite languages. It features a lot of good stuff in addition to being targeted towards computational people like me. I won't bore you with the details of the language itself but suffice it to say that we finally have a general purpose language where you don't have to compromise expressiveness with efficiency.



## Prerequisites

When reading this it helps if you have a basic understanding of Neural networks and their mathematical properties. Mathwise, basic linear algebra will do for the majority of the post.

# Short introductory example - Boston Housing

Instead of writing on and on about how cool this new language is I will just show you how quickly you can get a simple neural network up and running. The first example we will create is the BostonHousing (http://www.cs.toronto.edu/~delve/data/boston/bostonDetail.html) dataset. This is baked into the deep learning library Knet. So let's start by fetching the data.

````julia
using Knet;
include(Knet.dir("data","housing.jl"));
x,y = housing();
````




Now that we have the data we also need to define the basic functions that will make up our network. We will start with the predict function where we define $\omega$ and $x$ as input. $\omega$ in this case is our parameters which is a 2 element array containing weights in the first element and biases in the second. The $x$ contains the dataset which in our case is a matrix of size 506x13, i.e., 506 observations and 13 covariates.

````julia
predict(ω, x) = ω[1] * x .+ ω[2];
loss(ω, x, y) = mean(abs2, predict(ω, x)-y);
lossgradient = grad(loss);

function train(ω, data; lr=0.01) 
    for (x,y) in data
        dω = lossgradient(ω, x, y)
        for i in 1:length(ω)
            ω[i] -= dω[i]*lr
        end
    end
    return ω
end;
````




Let's have a look at the first 5 variables of the data set and their relation to the response that we would like to predict. The y axis in the plots is the response variable and the x axis the respective variables values. As you can see there are some correlations which seems to indicate some kind of relation though this is not definitive proof of a relation!

````julia
using Plots;
using StatPlots;

include(Knet.dir("data","housing.jl"));
x,y = housing();
#plotly();
gr();
scatter(x', y[1,:], layout=(3,5), reg=true, size=(950,500))
````


![](/images/figure/docbostonhousing_3_1.svg)


Here's the training part of the script where we define and train a perceptron, i.e., a linear neural network on the Boston Housing dataset. We track the error every 10th epoch and register it in our DataFrame. 

````julia
using DataFrames
ω = Any[ 0.1*randn(1,13), 0.0 ];
errdf = DataFrame(Epoch=1:20, Error=0.0);
cntr = 1;
for i=1:200
    train(ω, [(x,y)])
    if mod(i, 10) == 0
        println("Epoch $i: $(round(loss(ω,x,y)))")
        errdf[cntr, :Epoch]=i
        errdf[cntr, :Error]=loss(ω,x,y)
        cntr+=1
    end
end
````


````
Epoch 10: 383.0
Epoch 20: 262.0
Epoch 30: 182.0
Epoch 40: 130.0
Epoch 50: 94.0
Epoch 60: 71.0
Epoch 70: 55.0
Epoch 80: 45.0
Epoch 90: 38.0
Epoch 100: 33.0
Epoch 110: 30.0
Epoch 120: 28.0
Epoch 130: 26.0
Epoch 140: 25.0
Epoch 150: 24.0
Epoch 160: 24.0
Epoch 170: 24.0
Epoch 180: 23.0
Epoch 190: 23.0
Epoch 200: 23.0
````




If you inspect the training error per epoch you'll see that the error steadily goes down but flattens out after around 150. This is when we have reached the minimum error we can achieve with this small model. The plot on the right hand side shows the correlation between the predicted house prices and the real observed ones. The fit is not bad but there are definitely outliers.

````julia
p1 = scatter(errdf[:,:Epoch], errdf[:,:Error], xlabel="Epoch", ylabel="Error")
p2 = scatter(predict(ω, x)', y', reg=true, xlabel="Predicted", ylabel="Observed")
plot(p1, p2, layout=(1,2), size=(950,500))
````


![](/images/figure/docbostonhousing_5_1.svg)


## Increasing model complexity
Since we made a toy model before which basically was a simple multiple linear regression model, we will step into the land of deep learning. Well, we'll use two hidden layers instead of none. The way to go about this is actually ridiculously simple. Since we've written all code so far in Raw Julia except for the grad function, which comes from the AutoGrad package, we can readily extend the depth of our network. But before we move on let's save the network we trained from before.

````julia
ω1 = ω;
````




Now that that's out of the way the next thing we need to do is to define the weights of our network and thereby our new structure. We will build a neural network with 
- One input layer of size 13
- A hidden layer of size 64
- Another hidden layer of size 15
- A final output layer which will be our prediction
which will have way more parameters than needed to solve this, but we'll add all these parameters just for fun. We'll return to why this is a horrible idea later. Knowing the overall structure we can now define our new $\omega$. When you read it please bear in mind that we use a [weights,bias,weights,bias] structure.

````julia
ω = Any[0.1f0*randn(Float32,64,13), zeros(Float32,64,1),
        0.1f0*randn(Float32,15,64), zeros(Float32,15,1),
        0.1f0*randn(Float32,1,15),  zeros(Float32,1,1)]
````




The $\omega$ is not the only thing we need to fix. We also need a new prediction function. Now, instead of making it targeted towards our specific network, we will instead write one that works for any number of layers. It's given below. Notice the ReLu function in the hidden nodes. If you don't know why this is a good idea there are several papers that explains why in great detail. The short version is that it helps with the vanishing gradients problem in deep networks.

````julia
function predict(ω, x) 
    x = mat(x)
    for i=1:2:length(ω)-2
        x = relu.(ω[i]*x .+ ω[i+1])
    end
    return ω[end-1]*x .+ ω[end]
end
````


````
predict (generic function with 1 method)
````




Regarding the loss and the gradient of the loss we use exactly the same code! No need for any changes. This is one of the AutoGrad's superpowers; It can differentiate almost any Julia function. The same is also true for our training function. It also doesn't change. Nor do the loop where we apply it. Cool stuff my friends. 

````julia
loss(ω, x, y) = mean(abs2, predict(ω, x)-y)
lossgradient = grad(loss)

errdf = DataFrame(Epoch=1:60, Error=0.0)
cntr = 1
for i=1:600
    train(ω, [(x,y)])
    if mod(i, 10) == 0
        errdf[cntr, :Epoch]=i
        errdf[cntr, :Error]=loss(ω,x,y)
        cntr+=1
    end
end
````




Let's then have a look at the naive performance shall we? We start out by showing the same plots as we did for the linear model. It might not be super obvious what happened, but the error went down by a lot.

````julia
p3 = scatter(errdf[:,:Epoch], errdf[:,:Error], xlabel="Epoch", ylabel="Error")
p4 = scatter(predict(ω, x)', y', reg=true, xlabel="Predicted", ylabel="Observed")
plot(p3, p4, layout=(1,2), size=(950,500))
````


![](/images/figure/docbostonhousing_10_1.svg)


But the interesting comparison is of course how much better the fit really was. We can show the correlation plots from both models next to each other. The correlation for the first model was [0.85] while for our latest version it was [0.98].

````julia
plot(p2, p4, layout=(1,2), size=(950,500))
````


![](/images/figure/docbostonhousing_11_1.svg)


As the complexity is probably high enough it makes sense to check if it's too flexible and have a validation run duing our fitting process. This is usually rather instructive when dealing with highly parameterized functions. We start by splitting our data set up in training and testing. 

````julia
xtrn, xtst = x[:, 1:400], x[:, 401:end]
ytrn, ytst = y[:, 1:400], y[:, 401:end]

ω = Any[0.1f0*randn(Float32,64,13), zeros(Float32,64,1),
        0.1f0*randn(Float32,15,64), zeros(Float32,15,1),
        0.1f0*randn(Float32,1,15),  zeros(Float32,1,1)]
errdf = DataFrame(Epoch=1:60, TrnError=0.0, ValError=0.0)
cntr = 1
for i=1:600
    train(ω, [(xtrn, ytrn)])
    if mod(i, 10) == 0
        errdf[cntr, :Epoch]=i
        errdf[cntr, :TrnError]=loss(ω,xtrn,ytrn)
        errdf[cntr, :ValError]=loss(ω,xtst,ytst)
        cntr+=1
    end
end
````




After doing the training we can inspect what happens with the training and validation error over time. What you are seeing is extremely typical for neural networks that are not regularized or treated in a Bayesian way. Initially both the training error and the validation error goes down. However, as the model gets better and better at fitting the traning set it gets worse at the validation set which is not part of the training. 

````julia
using StatPlots
@df errdf[5:60,:] plot(:Epoch, [:ValError, :TrnError], xlabel="Epoch", ylabel="Error", 
                       label=["Validation" "Training"], lw=3)
````


![](/images/figure/docbostonhousing_13_1.svg)


# Deep convolutional networks on mnist
The Boston Housing data set is, relatively speaking, a rather simple job for any well versed machine learning girl/guy. As such we need a little bit more bite to dig into what Julia can really do. So with no further ado we turn to convolutional neural networks. We will implement the LeNet which is an old fart in the game but nicely illustrates complexity and power.

````julia
using Knet
using Plots
using StatPlots

# Define necessary functions
function predict(w, x0)
    x1 = pool(relu.(conv4(w[1],x0) .+ w[2]))
    x2 = pool(relu.(conv4(w[3],x1) .+ w[4]))
    x3 = relu.(w[5]*mat(x2) .+ w[6])
    return w[7]*x3 .+ w[8]
end

loss(ω, x, ygold) = nll(predict(ω, x), ygold)

lossgradient = grad(loss)

function train(model, data, optim)
    for (x,y) in data
        grads = lossgradient(model,x,y)
        update!(model, grads, optim)
    end
end

# Load the data
include(Knet.dir("data","mnist.jl"))
xtrn, ytrn, xtst, ytst = mnist()
dtrn = minibatch(xtrn, ytrn, 100)
dtst = minibatch(xtst, ytst, 100)

# Initialise neural network
ω = Any[xavier(Float32, 5, 5, 1, 20),  zeros(Float32, 1, 1, 20, 1),
        xavier(Float32, 5, 5, 20, 50), zeros(Float32, 1, 1, 50, 1),
        xavier(Float32, 500, 800),     zeros(Float32, 500, 1),
        xavier(Float32, 10, 500),      zeros(Float32, 10, 1) ]

o = optimizers(ω, Adam)
````




The last part of the code that will actually do the training I will not execute because well that basically takes forever because I'm currently writing this on a non GPU based laptop :) I have reached out to the developer of Knet for an answer and it appears as though the entire library was primarily developed with a GPU computational platform in mind. This is not an unreasonable assumption due to the good fit between neural networks and GPU's. However, that doesn't help us when we want to do deep learning on our CPU based machine.

````julia
# println((:epoch, 0, :trn, accuracy(ω, dtrn, predict), :tst, accuracy(ω, dtst, predict)))
# for epoch=1:10
#     train(ω, dtrn, o)
#     println((:epoch, epoch, :trn, accuracy(ω, dtrn, predict), :tst, accuracy(ω, dtst, predict)))
# end
````




So armed with this information we look to another nice deep learning framework called MXNet. We can use this to define a convolutional neural network like we did with Knet. MXNet is a different framework so of course defining a network looks differently. 



We start by loading the package in Julia and declaring a Variable in the MXNet framework called "data". This will serve as our reference to a data set that we wish to run the network on. Before we move on I should say that MXNet allows for two programming paradigms.
- Imperative
- Symbolic
The symbolic paradigm is the one used by PyTorch and Tensorflow where you define a computational graph and then do operations on it. Thus nothing gets executed until you run data through it. Imperative works more like normal programming which is line by line basis. Both approches have their benefits and caveats and fortunately MXNet supports both. For the remainder of this post we will use the Symbolic interface.

````julia
using MXNet
data = mx.Variable(:data)
````




We will again sort of replicate the LeNet model. The first convolutional layers is specified like this:

````julia
conv1 = @mx.chain mx.Convolution(data, kernel=(5,5), num_filter=20)  =>
mx.Activation(act_type=:tanh) =>
mx.Pooling(pool_type=:max, kernel=(2,2), stride=(2,2))
````




Notice the activation function as well as the pooling. We use 20 filters with a 5 by 5 kernel. On top of that we add a max pooling layer with another 2 by 2 kernel and a 2 by 2 stride. The second layer uses 50 filters with the same tactics. For both convolutional layers we use the tanh activation function.

````julia
conv2 = @mx.chain mx.Convolution(conv1, kernel=(5,5), num_filter=50) =>
mx.Activation(act_type=:tanh) =>
mx.Pooling(pool_type=:max, kernel=(2,2), stride=(2,2))
````




We end the network structure with two fully connected layers of size 500 and 10 respectively. Further the softmax function is applied to the output layer to make the outputs sum to one for each data point. This does NOT turn this into a probability mind you!

````julia
fc1   = @mx.chain mx.Flatten(conv2) =>
mx.FullyConnected(num_hidden=500) =>
mx.Activation(act_type=:tanh)

fc2   = mx.FullyConnected(fc1, num_hidden=10)

lenet = mx.SoftmaxOutput(fc2, name=:softmax)
````




## Load data
Before we move into the training of the newly specified network we need to fetch the data and convert it into a format that MXNet understands. It starts out by specifying some choices for the data fetch and then downloads MNIST into Pkg.dir("MXNet")/data/mnist if not exist. After that data providers are created which allows us to iterate over the data sets.

````julia
# load data
batch_size = 100
data_name = :data
label_name = :softmax_label
filenames = mx.get_mnist_ubyte()
train_provider = mx.MNISTProvider(image=filenames[:train_data],
                                  label=filenames[:train_label],
                                  data_name=data_name, label_name=label_name,
                                  batch_size=batch_size, shuffle=true, flat=false, silent=true)
eval_provider = mx.MNISTProvider(image=filenames[:test_data],
                                 label=filenames[:test_label],
                                 data_name=data_name, label_name=label_name,
                                 batch_size=batch_size, shuffle=false, flat=false, silent=true)
````




This gives us a training set and a validation set on the MNIST data from our MXNet package. To start using this data on our specified model we need to define the context in which we are going to train it. In this case, as I said before, we will use the CPU. If you have a GPU at your disposal I recommend you to exchange the context to mx.gpu() instead. Other than contextualising we need to define an optimizer and we'll stick with our stochastic gradient descent. The parameters are standard choices. Do feel free to play around with them.

````julia
model = mx.FeedForward(lenet, context=mx.cpu())
optimizer = mx.SGD(lr=0.05, momentum=0.9, weight_decay=0.00001)
# mx.fit(model, optimizer, train_provider, n_epoch=10, eval_data=eval_provider)
````




The actual fit is commented out as it still takes a long time on my machine. So please have a look at my repository for the full code. Thus, much like a cooking program I will restore some data from an offline run. I have loaded the probabilities for each digit class for each example along with the correct labels and an array of what I am calling outliers.

````julia
using JLD
probs = load("mymxnetresults.jld", "probs")
labels = load("mymxnetresults.jld", "labels")
outliers = load("mymxnetresults.jld", "outliers")
````




Now we can use this new data to compute the accuracy which you can see below is quite ok on a validation set. This is by no means the best achievable on the MNIST but it suffices to illustrate what we can do with deep convolutional nets. 

````julia
correct = 0
for i = 1:length(labels)
    # labels are 0...9
    if indmax(probs[:,i]) == labels[i]+1
        correct += 1
    end
end

accuracy = 100correct/length(labels)
println(mx.format("Accuracy on eval set: {1:.2f}%", accuracy))
````


````
Accuracy on eval set: 98.93%
````




As stated the accuracy is quite fine. However, there's an interesting point I would like to make: What about the networks internal belief and confidence in what it's seeing? To highlight this we will look at the outliers which consists of all examples the neural net got wrong. 

````julia
tmpdf=DataFrame(outliers)
````




First we will plot the predicted class against the internal confidence of the network in it's classification. 

````julia
scatter(convert(Array, tmpdf[2,:])', convert(Array, tmpdf[4,:])', ylim=(0, 1), 
        ylabel="Likelihood", xlabel="Wrongly Predicted class")
````


![](/images/figure/docbostonhousing_25_1.svg)


Now that we can see that the network is mostly quite convinced of it's findings even when it's dead wrong. It's above 40% sure every time. But let's do better and have a look at the histogram of likelihoods on the erroneosly classified digits.

````julia
histogram(convert(Array, tmpdf[4,:])', xlims=(0,1), 
          xlabel="Likelihood", ylabel="Frequency")
````


![](/images/figure/docbostonhousing_26_1.svg)


In here it's clear to see that the vast majority of the mass is way above 80% which again shows how convinced the network is even when it's inherently wrong.



# Conclusions
Julia is an upcoming cool language that I believe will be well suited for deep learning applications and research. For a while longer I do believe that the early adopters of the language will be research engineers and scientists. There are a lot of things missing in the current packages compared to the Python and R universe but this is not strange given how young the language is. Further, Julia takes care of a lot of issues that Python and R currently have.
So give it a go and see how you like it!



Happy inferencing!
