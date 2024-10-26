import numpy as np
from PIL import Image
from cryptography.fernet import Fernet
import random

# Function to generate a random key
def generate_key():
    return Fernet.generate_key()

# Function to shuffle pixels in the image array
def shuffle_image(image_array):
    flat_image = image_array.flatten()
    indices = list(range(len(flat_image)))
    random.seed(42)  # Set seed for reproducibility
    random.shuffle(indices)  # Shuffle the indices
    shuffled_image = flat_image[indices]
    return shuffled_image, indices

# Function to decrypt an image
def decrypt_image(encrypted_bytes, key, shape, indices):
    # Create a Fernet cipher object
    cipher = Fernet(key)
    # Decrypt the image bytes
    decrypted_bytes = cipher.decrypt(encrypted_bytes)
    
    # Convert bytes back to numpy array
    decrypted_array = np.frombuffer(decrypted_bytes, dtype=np.uint8)
    
    # Create an array to hold the unshuffled image
    original_image = np.zeros_like(decrypted_array)
    original_image[indices] = decrypted_array  # Use indices to unshuffle
    return original_image.reshape(shape)

# Load the original color image
image = Image.open("lena.png").convert("RGB")  # Change to "RGB" for color images
image_array = np.array(image, dtype=np.uint8)

# Generate a random key for encryption
key = generate_key()

# Encrypt the image
shuffled_image, shuffle_indices = shuffle_image(image_array)  # Shuffle and get indices
cipher = Fernet(key)

# Flatten the shuffled image array and convert to bytes
image_bytes = shuffled_image.tobytes()
# Encrypt the image bytes
encrypted_bytes = cipher.encrypt(image_bytes)

# Save the encrypted image as a binary file
with open("encrypted_lena.bin", "wb") as f:
    f.write(encrypted_bytes)

# Save the encryption key securely
with open("encryption_key.key", "wb") as key_file:
    key_file.write(key)

# Save the shuffle indices for decryption
with open("shuffle_indices.npy", "wb") as indices_file:
    np.save(indices_file, shuffle_indices)

# Prepare to convert encrypted bytes back to an image for visual representation
encrypted_size = len(encrypted_bytes)
expected_size = image_array.size  # Total number of pixels in the original image

# Pad the encrypted data to ensure it matches the size of the original image
if encrypted_size < expected_size:
    padded_encrypted_bytes = np.pad(
        np.frombuffer(encrypted_bytes, dtype=np.uint8),
        (0, expected_size - encrypted_size), 
        'constant'
    )
else:
    padded_encrypted_bytes = np.frombuffer(encrypted_bytes, dtype=np.uint8)[:expected_size]

# Reshape to the original image shape
encrypted_image_array = padded_encrypted_bytes.reshape(image_array.shape)

# Save the encrypted image as a PNG file
encrypted_image_pil = Image.fromarray(encrypted_image_array)
encrypted_image_pil.save("encrypted_lena_image.png")

# Display the encrypted image
encrypted_image_pil.show(title="Encrypted Lena Image")

# Decrypt the image
decrypted_image = decrypt_image(encrypted_bytes, key, image_array.shape, shuffle_indices)

# Save the decrypted image
decrypted_image_pil = Image.fromarray(decrypted_image)
decrypted_image_pil.save("decrypted_lena.png")

# Display the decrypted image for verification
decrypted_image_pil.show(title="Decrypted Lena Image")
