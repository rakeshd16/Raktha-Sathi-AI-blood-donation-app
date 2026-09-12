from PIL import Image, ImageDraw, ImageFont

def create_icon(size, filename):
    # Create image with red background
    img = Image.new('RGB', (size, size), color='#d50000')
    draw = ImageDraw.Draw(img)
    
    # Draw white circle
    circle_radius = int(size * 0.365)
    center = size // 2
    draw.ellipse(
        [(center - circle_radius, center - circle_radius),
         (center + circle_radius, center + circle_radius)],
        fill='white'
    )
    
    # Draw red cross
    cross_width = int(size * 0.082)
    cross_length = int(size * 0.492)
    
    # Vertical bar
    draw.rectangle(
        [(center - cross_width // 2, center - cross_length // 2),
         (center + cross_width // 2, center + cross_length // 2)],
        fill='#d50000'
    )
    
    # Horizontal bar
    draw.rectangle(
        [(center - cross_length // 2, center - cross_width // 2),
         (center + cross_length // 2, center + cross_width // 2)],
        fill='#d50000'
    )
    
    # Save
    img.save(filename, 'PNG')
    print(f'Created {filename}')

# Generate icons
create_icon(192, 'static/icon-192.png')
create_icon(512, 'static/icon-512.png')
