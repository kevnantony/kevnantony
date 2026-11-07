import json, os, re 
from src.draw_ascii import generate_logo
from src.fetch_info import fetch_stats
from PIL import Image, ImageDraw, ImageFont
from github import Github

def generate_fetch(g:Github) -> str:
    with open("config.json", "r") as f:
        config = json.load(f)

    user = fetch_stats(g)
    pfp = generate_logo(g)


    header = config.get("header") or f"{user['username']}@github.com"
    stats = f"{header}\n{'-' * max(30, len(header))}\n"
    for stat in config['display_stats']:
        if stat in user:
            stats += f"{stat.replace('_', ' ').title()}: {user[stat]}\n"
    stats += f"\n{config['additional_info']}\n"

    pfp_lines = pfp.split("\n")
    stats_lines = stats.split("\n")

    max_lines = max(len(pfp_lines), len(stats_lines))
    pfp_lines += [""] * (max_lines - len(pfp_lines))
    stats_lines += [""] * (max_lines - len(stats_lines))

    combined = "\n".join(f"{pfp_line:<50} {stats_line}" for pfp_line, stats_line in zip(pfp_lines, stats_lines))
    
    return combined

def return_preffered_color() -> tuple:
    with open("config.json", "r") as f:
        config = json.load(f)
    
    color = config['preferred_color']
    color_map = {
        "red": (255, 0, 0),
        "green": (0, 128, 0),
        "blue": (0, 0, 255),
        "yellow": (255, 255, 0),
        "purple": (128, 0, 128),
        "orange": (255, 165, 0),
        "pink": (255, 192, 203),
        "white": (255, 255, 255),
        "lightblue": (173, 216, 230),
    }

    if color in color_map:
        return color_map[color]
    else:
        return color_map["lightblue"]


def gen_image(g: Github):
    width, initial_height = 1200, 550
    ascii_width = 450
    text_margin = 60
    
    bg_color = (0, 0, 0)
    value_color = return_preffered_color()
    text_color = (255, 255, 255)
    font_size = 16

    font = None
    font_paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
        "/usr/share/fonts/truetype/ubuntu/UbuntuMono-R.ttf",
        "/usr/share/fonts/liberation-mono/LiberationMono-Regular.ttf",
        "monospace",
        "consola.ttf"
    ]
    
    fetch = generate_fetch(g)
    image = Image.new("RGB", (width, initial_height), bg_color)
    draw = ImageDraw.Draw(image)
    for font_path in font_paths:
        try:
            font = ImageFont.truetype(font_path, font_size)
            break
        except IOError:
            continue
    
    if font is None:
        print("No suitable fonts found. Aborting!")
        return
        

    lines = fetch.split("\n")
    ascii_lines = [line[:50] for line in lines]
    info_lines = [line[50:].strip() for line in lines]

    y_offset = 10
    line_spacing = font_size + 4
    for ascii_line in ascii_lines:
        draw.text((10, y_offset), ascii_line, fill=value_color, font=font)
        y_offset += line_spacing

    y_offset = 10
    x_text = ascii_width + text_margin
    max_text_width = width - ascii_width - (text_margin * 2)

    for info_line in info_lines:
        if info_line:
            parts = info_line.split(':', 1)
            if len(parts) == 2:
                title = parts[0] + ':'
                value = parts[1].strip()
                
                title_width = font.getlength(title)
                draw.text((x_text, y_offset), title, fill=value_color, font=font)
                
                x_value = x_text + title_width + 5
                remaining_width = max_text_width - title_width - 5
                
                words = value.split()
                line = []
                x_current = x_value
                
                for word in words:
                    test_line = ' '.join(line + [word])
                    text_width = font.getlength(test_line)
                    
                    if text_width <= remaining_width:
                        line.append(word)
                    else:
                        if line:
                            draw.text((x_current, y_offset), ' '.join(line), fill=text_color, font=font)
                            y_offset += line_spacing
                            line = [word]
                            x_current = x_text + text_margin
                        else:
                            draw.text((x_current, y_offset), word, fill=text_color, font=font)
                            y_offset += line_spacing
                if line:
                    draw.text((x_current, y_offset), ' '.join(line), fill=text_color, font=font)
                y_offset += line_spacing
            else:
                words = info_line.split()
                line = []
                x_current = x_text
                
                for word in words:
                    test_line = ' '.join(line + [word])
                    text_width = font.getlength(test_line)
                    
                    if text_width <= max_text_width:
                        line.append(word)
                    else:
                        if line:
                            draw.text((x_current, y_offset), ' '.join(line), fill=text_color, font=font)
                            y_offset += line_spacing
                            line = [word]
                            x_current = x_text
                        else:
                            draw.text((x_current, y_offset), word, fill=text_color, font=font)
                            y_offset += line_spacing
                            x_current = x_text
                
                if line:
                    draw.text((x_current, y_offset), ' '.join(line), fill=text_color, font=font)
                y_offset += line_spacing

    # Check if the text goes out of bounds and adjust the image height if necessary
    if y_offset > initial_height:
        new_height = y_offset + 20  
        image = Image.new("RGB", (width, new_height), bg_color)
        draw = ImageDraw.Draw(image)
        
        # Redraw the text on the new image
        y_offset = 10
        for ascii_line in ascii_lines:
            draw.text((10, y_offset), ascii_line, fill=value_color, font=font)
            y_offset += line_spacing

        y_offset = 10
        for info_line in info_lines:
            if info_line:
                parts = info_line.split(':', 1)
                if len(parts) == 2:
                    title = parts[0] + ':'
                    value = parts[1].strip()
                    
                    title_width = font.getlength(title)
                    draw.text((x_text, y_offset), title, fill=value_color, font=font)
                    
                    x_value = x_text + title_width + 5
                    remaining_width = max_text_width - title_width - 5
                    
                    words = value.split()
                    line = []
                    x_current = x_value
                    
                    for word in words:
                        test_line = ' '.join(line + [word])
                        text_width = font.getlength(test_line)
                        
                        if text_width <= remaining_width:
                            line.append(word)
                        else:
                            if line:
                                draw.text((x_current, y_offset), ' '.join(line), fill=text_color, font=font)
                                y_offset += line_spacing
                                line = [word]
                                x_current = x_text + text_margin
                            else:
                                draw.text((x_current, y_offset), word, fill=text_color, font=font)
                                y_offset += line_spacing
                    if line:
                        draw.text((x_current, y_offset), ' '.join(line), fill=text_color, font=font)
                        y_offset += line_spacing
                else:
                    words = info_line.split()
                    line = []
                    x_current = x_text
                    
                    for word in words:
                        test_line = ' '.join(line + [word])
                        text_width = font.getlength(test_line)
                        
                        if text_width <= max_text_width:
                            line.append(word)
                        else:
                            if line:
                                draw.text((x_current, y_offset), ' '.join(line), fill=text_color, font=font)
                                y_offset += line_spacing
                                line = [word]
                                x_current = x_text
                            else:
                                draw.text((x_current, y_offset), word, fill=text_color, font=font)
                                y_offset += line_spacing
                                x_current = x_text
                    
                    if line:
                        draw.text((x_current, y_offset), ' '.join(line), fill=text_color, font=font)
                        y_offset += line_spacing

    # prompt_y = new_height - line_spacing if y_offset > initial_height else initial_height - line_spacing
    # x_prompt = 10
    # draw.text((x_prompt, prompt_y), g.get_user().login, fill=value_color, font=font)
    # x_prompt += font.getlength(g.get_user().login)
    # draw.text((x_prompt, prompt_y), "@", fill=(255,255,255), font=font) 
    # x_prompt += font.getlength("@")
    # draw.text((x_prompt, prompt_y), "github", fill=value_color, font=font)  
    # x_prompt += font.getlength("githubdotcom")
    # draw.text((x_prompt, prompt_y), ": $", fill=text_color, font=font)

    os.makedirs("out", exist_ok=True)
    image.save("out/fetch.png")
    #image.show()

def generate_readme(g: Github):
        gen_image(g)
        
        image_pattern = r'<div align=\'center\'>\s*<img src=\'out/fetch\.png\' alt=\'Github Fetch\'>\s*</div>'
        image_content = "\n## Example Output\n<div align='center'>\n  <img src='out/fetch.png' alt='Github Fetch'>\n</div>\n"
        
        try:
            with open("README.md", "r", encoding="utf-8") as f:
                content = f.read()
                
            start_comment = "<!--- START OF DELETION --->"
            end_comment = "<!--- END OF DELETION --->"
            pattern = re.compile(f"{start_comment}.*?{end_comment}", re.DOTALL)
            content = re.sub(pattern, "", content)
            
            with open("config.json", "r") as f:
                config = json.load(f)
            append_automatic = config.get("append_automatic", True)
            
            if append_automatic and not re.search(image_pattern, content):
                content = content.rstrip() + "\n\n" + image_content
        except FileNotFoundError:
            content = image_content
        
        with open("README.md", "w", encoding="utf-8") as f:
            f.write(content)