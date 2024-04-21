import math
import random

def distance(p1, p2):
    return math.sqrt((p1.x - p2.x) ** 2 + (p1.y - p2.y) ** 2)

def collide(player, obs, dist=25):
    distance = math.sqrt((player.x - obs.x) ** 2 + (player.y - obs.y) ** 2)
    
    # Check if distance is less than or equal to dist
    if distance <= dist:
        return True
    else:
        return False

def normalize_vector(vector):
    # Calculate the magnitude of the vector
    magnitude = math.sqrt(vector[0] ** 2 + vector[1] ** 2)
    
    # Check if the magnitude is non-zero to avoid division by zero
    if magnitude != 0:
        # Normalize the vector by dividing each component by the magnitude
        normalized_vector = [vector[0] / magnitude, vector[1] / magnitude]
        return normalized_vector
    else:
        # If the magnitude is zero, return the original vector
        return vector
    
def generate_random_2d_vector():
    # Generate random angle between 0 and 2*pi radians
    angle = random.uniform(0, 2 * math.pi)
    
    # Calculate x and y components of the vector
    x = math.cos(angle)
    y = math.sin(angle)
    
    # Return the normalized vector
    magnitude = math.sqrt(x**2 + y**2)
    normalized_vector = (x / magnitude, y / magnitude)
    return normalized_vector

def calculate_angle(dx, dy):
    # Calculate the angle using arctangent function
    angle = math.atan2(dy, dx)
    
    # Convert angle from radians to degrees
    angle_degrees = math.degrees(angle)
    
    # Adjust angle to be in the range (0, 360)
    if angle_degrees < 0:
        angle_degrees += 360
    
    return angle_degrees
