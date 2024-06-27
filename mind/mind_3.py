import numpy


class Mind:
    def __init__(self, input_node, hidden_node, output_node, step, w_ih=None, w_ho=None):
        self.input_node = input_node
        self.hidden_node = hidden_node
        self.output_node = output_node

        self.step = step
        self.w_ih = w_ih
        self.w_ho = w_ho


step = 0.01

mind_1 = Mind(2, 5, 4, step)

inputs = numpy.array([[0.85, 0.32]])
goals = numpy.array([[0, 1, 0]])
mind_1.w_ih = numpy.zeros((mind_1.hidden_node, mind_1.input_node)) + 0.1
mind_1.w_ho = numpy.zeros((mind_1.output_node, mind_1.hidden_node)) + 0.1


times = 3
for t in range(times):
    # go
    hiddens = numpy.tanh(mind_1.w_ih.dot(inputs.T))
    outputs = numpy.tanh(mind_1.w_ho.dot(hiddens))

    print(outputs)

    # back
    e_ho = outputs - goals.T
    mind_1.w_ho -= mind_1.w_ho * e_ho * hiddens.T * step

    e_ih = mind_1.w_ho.T.dot(e_ho)
    mind_1.w_ih -= mind_1.w_ih * e_ih * inputs * step

print(mind_1.w_ih)
print(mind_1.w_ho)