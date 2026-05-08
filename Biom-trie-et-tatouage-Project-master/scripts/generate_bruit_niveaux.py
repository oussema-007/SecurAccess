import cv2
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

def add_gaussian_noise(image, mean=0, std=25):
    """Adds Gaussian noise to an image."""
    row, col, ch = image.shape
    gauss = np.random.normal(mean, std, (row, col, ch))
    noisy = image + gauss
    noisy = np.clip(noisy, 0, 255).astype(np.uint8)
    return noisy

def main():
    # Find the first available face image
    faces_dir = Path("data/faces")
    image_paths = list(faces_dir.rglob("*.jpg"))
    
    if not image_paths:
        print("[ERROR] No face images found in data/faces/")
        return
        
    img_path = str(image_paths[0])
    img = cv2.imread(img_path)
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
    # Generate noisy versions
    img_noise_low = add_gaussian_noise(img_rgb, std=25)
    img_noise_med = add_gaussian_noise(img_rgb, std=55)
    img_noise_high = add_gaussian_noise(img_rgb, std=100)
    
    # Create plot
    plt.figure(figsize=(12, 4))
    
    plt.subplot(1, 4, 1)
    plt.imshow(img_rgb)
    plt.title("Originale")
    plt.axis("off")
    
    plt.subplot(1, 4, 2)
    plt.imshow(img_noise_low)
    plt.title("Bruit (σ=25)")
    plt.axis("off")
    
    plt.subplot(1, 4, 3)
    plt.imshow(img_noise_med)
    plt.title("Bruit (σ=55)")
    plt.axis("off")
    
    plt.subplot(1, 4, 4)
    plt.imshow(img_noise_high)
    plt.title("Bruit (σ=100)")
    plt.axis("off")
    
    plt.tight_layout()
    
    output_path = Path("rapport_latex/images/bruit-niveaux.png")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"[SUCCESS] Image generated and saved at: {output_path}")

if __name__ == "__main__":
    main()
