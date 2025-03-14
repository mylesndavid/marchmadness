import numpy as np
import matplotlib.pyplot as plt

# Define the neural network class
class SimpleNeuralNetwork:
    def __init__(self):
        # Initialize weights and biases
        self.w1 = np.random.randn(2, 3)  # Weights: 2 inputs to 3 hidden neurons
        self.b1 = np.zeros((1, 3))       # Biases for hidden layer
        self.w2 = np.random.randn(3, 1)  # Weights: 3 hidden neurons to 1 output
        self.b2 = np.zeros((1, 1))       # Bias for output layer

    def relu(self, x):
        return np.maximum(0, x)

    def sigmoid(self, x):
        return 1 / (1 + np.exp(-x))

    def forward(self, X):
        # Forward pass
        self.z1 = np.dot(X, self.w1) + self.b1  # Hidden layer input
        self.a1 = self.relu(self.z1)            # Hidden layer output
        self.z2 = np.dot(self.a1, self.w2) + self.b2  # Output layer input
        self.a2 = self.sigmoid(self.z2)         # Output layer output
        return self.a2

# Create sample input data
X = np.array([[0.5, 0.8]])  # 1 sample with 2 features

# Initialize and run the network
nn = SimpleNeuralNetwork()
output = nn.forward(X)
print(f"Output of the network: {output}")

# Visualization of the network structure
def plot_neural_network():
    fig, ax = plt.subplots(figsize=(8, 6))

    # Define neuron positions
    layers = [
        [(0.1, 0.7), (0.1, 0.3)],           # Input layer (2 neurons)
        [(0.5, 0.8), (0.5, 0.5), (0.5, 0.2)],  # Hidden layer (3 neurons)
        [(0.9, 0.5)]                        # Output layer (1 neuron)
    ]

    # Draw neurons
    for layer in layers:
        for x, y in layer:
            circle = plt.Circle((x, y), 0.05, color='blue', fill=True)
            ax.add_patch(circle)

    # Draw connections
    for i in range(len(layers)):
        for n1 in layers[i]:
            if i < len(layers) - 1:
                for n2 in layers[i + 1]:
                    ax.plot([n1[0], n2[0]], [n1[1], n2[1]], 'k-', lw=0.5)

    # Labels
    ax.text(0.1, 0.75, 'Input 1', ha='center', va='bottom')
    ax.text(0.1, 0.35, 'Input 2', ha='center', va='bottom')
    ax.text(0.5, 0.85, 'H1', ha='center', va='bottom')
    ax.text(0.5, 0.55, 'H2', ha='center', va='bottom')
    ax.text(0.5, 0.25, 'H3', ha='center', va='bottom')
    ax.text(0.9, 0.55, 'Output', ha='center', va='bottom')

    # Set limits and remove axes
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    plt.title("Simple Neural Network Structure")
    plt.show()

# Call the visualization function
plot_neural_network()