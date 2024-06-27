import numpy


def sig(x):
    return 1 / (1 + numpy.exp(-x))


inputs = numpy.array([[2.0, 3.0]])
goal = numpy.array([[0, 1, 0]])
weights = numpy.zeros((len(goal[0]), len(inputs[0]))) + 0.1

step = 0.01

times = 100
for t in range(times):

    # outputs = sig(weights.dot(inputs.T))

    outputs = weights.dot(inputs.T)
    errors = outputs - goal.T
    weights -= weights * errors * inputs * step

    print('output:\n', outputs)
