import matplotlib.pyplot as plt
from IPython import display

def plot(scores, mean_scores, collisions, mean_collisions):
    plt.clf()  # Clear the current figure

    plt.subplot(2, 1, 1)
    plt.xlabel('Number of Games')
    plt.ylabel('Score')
    plt.plot(scores, label='Score')
    plt.plot(mean_scores, label='Mean Score')
    plt.legend()  # Show legend
    plt.text(len(scores)-1, scores[-1], str(scores[-1]))
    plt.text(len(mean_scores)-1, mean_scores[-1], str(mean_scores[-1]))

    plt.subplot(2, 1, 2)
    plt.xlabel('Number of Games')
    plt.ylabel('Collisions')
    plt.plot(collisions, label='Collisions')
    plt.plot(mean_collisions, label='Mean Collisions')
    plt.legend()  # Show legend
    plt.text(len(collisions)-1, collisions[-1], str(collisions[-1]))
    plt.text(len(mean_collisions)-1, mean_collisions[-1], str(mean_collisions[-1]))

    plt.tight_layout()  # Adjust layout to prevent overlap
    plt.pause(0.1)  # Pause to update the plot
    return
